import google.generativeai as genai
import json
import logging
import config

genai.configure(api_key=config.GEMINI_API_KEY)

# Use Gemini 3.7 Flash for speed and vision
MODEL_TEXT = "gemini-3.7-flash"
MODEL_VISION = "gemini-3.7-flash"

# ─── The Master Prompt (User's original) ──────────

FULL_PROTOCOL_PROMPT = """You are a World-Class Elite Life Strategist, Behavioral Psychologist, and Master Analyst. Your objective is to take a user's chosen book and transform it into a paradigm-shattering, hyper-detailed, deeply empowering personal life guide (የህይወት መመሪያ).

You must deliver profound depth. Do not give shallow, generic advice. Every sentence must carry weight, psychological insight, and actionable power.

### USER INPUTS:
- Book Title: {book_title}
- Age: {age_range}
- Gender: {gender_display}
- Location: {location}
- Living Situation: {living_situation}
- Employment: {employment}
- Main Goal: {goal}
- Specific Change Requested: {specific_change}
- Output Language: {language_display}

### CORE DIRECTIVES (STRICTLY ENFORCED):
1. THE ABSOLUTE LANGUAGE RULE: The ENTIRE output (including ALL titles, headings, and bullet points) MUST be 100% in {language_display}. NEVER output English headings like "PART I". Ensure perfect grammar, spelling, and natural sentence flow in {language_display}.
2. THE ANTI-ROBOT RULE: NEVER mechanically repeat the user's inputs back to them. DO NOT say "Because you are a {age_range} year old {gender_display} in {location}...". Instead, weave their demographics SUBTLY into the narrative. For example, if they are in Addis Ababa, mention the fast-paced city energy. If they are young, speak to their generational potential organically. Speak like a wise mentor, not a data-processor.
3. FLUID & CREATIVE STRUCTURE: DO NOT use a rigid "Part I, Part II" template. Instead, design the structure creatively based on the specific genre, tone, and philosophy of the book. A business book should have a strategic, executive format. A spiritual book should have a flowing, philosophical format. Create unique, inspiring headings for each section.
4. FORMATTING & EMOJIS (CRITICAL): 
   - ALWAYS use double line breaks (`

`) to separate paragraphs and list items. NEVER clump text together.
   - DO NOT use inline bullet points or inline emojis (e.g. 🔹) inside a paragraph. Put them on a new line!
   - Use Emojis (🎯, 💡, 🔥, 🚀, etc.) generously to structure the text and make it engaging.
   - NEVER use the asterisk sign (`**` or `*`). Do not use markdown bold/italics. 
   - NEVER use the hash sign (`#` or `###`). Do not use markdown headings.
   - NEVER use long dashes or hyphens (`—`, `–`, `-`).
   - To make titles and subtitles bold, use HTML tags: `<b>Title Here</b>`.
5. STRICT ETHIOPIAN CULTURAL ALIGNMENT: Align deeply with Ethiopian cultural, social, and religious values. Operate within traditional Ethiopian norms regarding gender and family dynamics.
6. RAW TEXT: Do not wrap your response in markdown code blocks. Output the raw text directly.

### CONTENT REQUIREMENTS (Weave these creatively into your custom structure):
- **The Book's Core Premise:** Connect the deepest philosophical premise of the book directly to their specific goal.
- **The Paradigm Shift:** Detail the toxic mindset stopping them right now, and provide the empowering belief from the book they must install today.
- **Daily Operating System:** Design Morning/Evening routines and habit-stacking strategies that fit a traditional Ethiopian daily rhythm.
- **Execution & Calibration:** Provide a clear metric to track weekly, and a 90-day transformation horizon.
- **Obstacle Anticipation:** Predict exact reasons they might fail in their specific Ethiopian context, and give a counter-strike mental script.
- **The Empowerment Manifesto:** A visceral, highly motivational closing statement synthesizing their cultural strength and their new reality.

Write exactly as this wise mentor. Make it profound. Translate everything beautifully into {language_display}."""


PREVIEW_PROMPT = """You are a World-Class Elite Life Strategist. Generate a captivating introductory summary of a life guide (የህይወት መመሪያ) based on the book. Be deeply personal, psychologically powerful, and culturally Ethiopian.
Output MUST be 100% in {language_display}. Do not mix languages. EVERY heading and title MUST be in {language_display}. Do not use asterisks (*). Do not use long dashes. Do not use hashes (#). Use HTML <b> tags for bolding. Use emojis.
ALWAYS use double line breaks (

) to separate thoughts.

Book: {book_title}
Age: {age_range}
Gender: {gender_display}
Location: {location}
Living Situation: {living_situation}
Employment: {employment}
Goal: {goal}
Specific Change: {specific_change}
Language: {language_display}

THE ANTI-ROBOT RULE: DO NOT mechanically repeat their age, gender, or location. Subtly weave these details into your psychological analysis. Speak like a natural, wise human mentor.

Write a creative, non-rigid introductory section in {language_display}. Include:
1. A powerful opening title (in {language_display}) connecting the book to their goal.
2. <b>The Hidden Connection:</b> 2 profound paragraphs connecting this book's deepest philosophy to their goal.
3. <b>The Life-Stage Reality:</b> Speak directly to the reality of their current life stage in Ethiopia, validating their struggles and reframing their demographic as their greatest weapon.

Make every sentence carry weight. Output raw text, no markdown blocks."""


BOOK_RECOMMEND_PROMPT = """You are a book recommendation expert for Ethiopian readers. 
Category/Topic: {category}

Recommend exactly {count} transformative books for this topic. For each book, write exactly 1 sentence in Amharic explaining how it changes the reader's life.

Respond in this exact JSON format only, no other text:
[
  {{"title": "Book Title in English", "description": "One sentence in Amharic"}},
  ... (exactly {count} objects)
]"""


BOOK_IDENTIFY_PROMPT = """Look at this book cover image. Identify the book title and author.

Respond in this exact JSON format only:
{{"title": "The Book Title", "author": "Author Name", "found": true}}

If you cannot identify the book, respond:
{{"title": "", "author": "", "found": false}}"""


BOOK_VERIFY_PROMPT = """Check if the following user input corresponds to a real, known published book (can be English, Amharic, or any language).
User Input: "{query}"

If it is a real book, respond with its official title and author.
Respond in this exact JSON format only:
{{"title": "Official Book Title", "author": "Author Name", "found": true}}

If it is NOT a real book, or just random text, respond:
{{"title": "", "author": "", "found": false}}"""


RECEIPT_VERIFY_PROMPT = """You are a payment receipt verification system for Ethiopian mobile money (Telebirr) and bank transfers (CBE).

Analyze this screenshot carefully and extract:
1. The exact amount paid (in ETB/Birr)
2. The recipient name or phone number
3. The transaction date
4. The unique Transaction ID or Reference number

Expected payment details:
- Expected Amount: {expected_amount} Birr
- Expected Recipient (Telebirr): {telebirr_name} or {telebirr_phone}
- Expected Recipient (CBE): {cbe_name} or {cbe_account}

Respond in this exact JSON format only, no other text:
{{
  "amount": null,
  "recipient": null,
  "date": null,
  "transaction_id": null,
  "amount_matches": false,
  "recipient_matches": false,
  "is_valid_receipt": false,
  "confidence": "low"
}}

Rules:
- Set amount, recipient, date, transaction_id to the extracted values, or null if unreadable
- amount_matches: true ONLY if amount equals exactly {expected_amount}
- recipient_matches: true ONLY if the extracted recipient contains ANY of these: "{telebirr_name}", "{telebirr_phone}", "{cbe_name}", or "{cbe_account}".
- is_valid_receipt: true ONLY if it looks like a genuine payment receipt/confirmation
- confidence: "high" if image is clear, "medium" if partially readable, "low" if blurry/unclear"""


# ─── Language Mapping ──────────────────────

LANG_MAP = {
    "am": "Amharic",
    "en": "English",
    "or": "Afaan Oromoo",
    "ti": "Tigrinya",
}

GENDER_MAP = {
    "male": {"en": "Male", "am": "ወንድ"},
    "female": {"en": "Female", "am": "ሴት"},
}

# ─── AI Functions ──────────────────────────

def generate_preview(book_title, gender, age_range, goal, location, living_situation, employment, specific_change, language="am"):
    """Generate only Part 1 (the free hook)."""
    gender_display = GENDER_MAP.get(gender, {}).get("am", gender)
    language_display = LANG_MAP.get(language, "Amharic")
    
    prompt = PREVIEW_PROMPT.format(
        book_title=book_title,
        age_range=age_range,
        gender_display=gender_display,
        goal=goal,
        location=location,
        living_situation=living_situation,
        employment=employment,
        specific_change=specific_change,
        language_display=language_display,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Preview generation error: {e}")
        return None


def generate_full_protocol(book_title, gender, age_range, goal, location, living_situation, employment, specific_change, language="am"):
    """Generate the complete transformation protocol."""
    gender_display = GENDER_MAP.get(gender, {}).get("am", gender)
    language_display = LANG_MAP.get(language, "Amharic")
    
    prompt = FULL_PROTOCOL_PROMPT.format(
        book_title=book_title,
        age_range=age_range,
        gender_display=gender_display,
        goal=goal,
        location=location,
        living_situation=living_situation,
        employment=employment,
        specific_change=specific_change,
        language_display=language_display,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Full protocol generation error: {e}")
        return None


def recommend_books(category, count=3):
    """Get book recommendations for a category."""
    prompt = BOOK_RECOMMEND_PROMPT.format(category=category, count=count)
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Extract JSON array robustly
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        else:
            text = "[]"
        return json.loads(text)
    except Exception as e:
        err_msg = str(e)
        logging.error(f"Book recommendation error: {err_msg}")
        return {"error": err_msg}


def identify_book_cover(image_bytes):
    """Identify a book from a cover photo using Gemini Vision."""
    try:
        model = genai.GenerativeModel(MODEL_VISION)
        response = model.generate_content([
            BOOK_IDENTIFY_PROMPT,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        text = response.text.strip()
        # Extract JSON object robustly
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        else:
            text = "{}"
        return json.loads(text)
    except Exception as e:
        logging.error(f"Book cover identification error: {e}")
        return {"title": "", "author": "", "found": False}

def verify_book_title(query):
    """Verify if a user-typed book is a real book."""
    prompt = BOOK_VERIFY_PROMPT.format(query=query)
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        else:
            text = "{}"
            
        return json.loads(text)
    except Exception as e:
        logging.error(f"Book verification error: {e}")
        return {"title": "", "author": "", "found": False}


def verify_receipt(image_bytes, expected_amount, telebirr_name, telebirr_phone, cbe_name, cbe_account):
    """Verify a payment screenshot using Gemini Vision."""
    prompt = RECEIPT_VERIFY_PROMPT.format(
        expected_amount=expected_amount,
        telebirr_name=telebirr_name,
        telebirr_phone=telebirr_phone,
        cbe_name=cbe_name,
        cbe_account=cbe_account,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_VISION)
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        text = response.text.strip()
        # Extract JSON object robustly
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        else:
            text = "{}"
        result = json.loads(text)
        logging.info(f"Gemini receipt verification result: {result}")
        
        # Helper to handle string booleans safely
        def is_true(val):
            if isinstance(val, bool): return val
            if isinstance(val, str): return val.lower() == 'true'
            return False

        # Final verdict
        is_approved = (
            is_true(result.get("is_valid_receipt")) and
            is_true(result.get("amount_matches")) and
            is_true(result.get("recipient_matches")) and
            result.get("confidence", "low").lower() in ("high", "medium")
        )
        result["auto_approved"] = is_approved
        return result
    except Exception as e:
        logging.error(f"Receipt verification error: {e}")
        return {"auto_approved": False, "error": str(e)}
