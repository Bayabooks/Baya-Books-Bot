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
1. NATIVE, FLAWLESS GRAMMAR: Do NOT write in English and translate. Think directly in {language_display}. Use natural phrasing, native idioms, and culturally resonant expressions. The grammar must feel deeply authentic, not robotic or translated.
2. THE ANTI-ROBOT RULE: NEVER mechanically repeat the user's inputs back to them. Weave their demographics SUBTLY into the narrative. Speak like a wise, empathetic mentor.
3. FLUID & CREATIVE STRUCTURE: DO NOT use a rigid template. Design the structure creatively based on the specific genre and philosophy of the book. Create unique, inspiring headings in {language_display}.
4. FORMATTING & EMOJIS (CRITICAL): 
   - ALWAYS use double line breaks (`

`) to separate paragraphs and list items. 
   - DO NOT use inline bullet points or inline emojis. Put them on a new line!
   - Use Emojis (🎯, 💡, 🔥, 🚀, etc.) generously.
   - 🚫 ABSOLUTELY NO ASTERISKS (*). NEVER use `**` for bolding. 
   - 🚫 ABSOLUTELY NO DASHES (- or —).
   - 🚫 NEVER use the hash sign (`#` or `###`).
   - ✅ To make titles and subtitles bold, YOU MUST USE HTML TAGS ONLY: `<b>Title Here</b>`.
5. STRICT ETHIOPIAN CULTURAL ALIGNMENT: Align deeply with Ethiopian cultural, social, and religious values. 
6. MASSIVE LENGTH & UNCOMPROMISING QUALITY: This must be a comprehensive, master-level guide. Expand deeply on every concept. DOUBLE the size of a normal response. Write extensively (at least 1500 words). Provide granular details, exact routines, and deep psychological rewiring.
7. RAW TEXT: Output the raw text directly. Do not wrap in markdown code blocks.

### CONTENT REQUIREMENTS (Weave these creatively):
- **The Core Premise:** Connect the book's philosophy directly to their goal.
- **The Paradigm Shift:** Detail the toxic mindset stopping them, and provide the empowering belief.
- **Granular Execution:** Design massive, detailed daily habits and routines.
- **The Empowerment Manifesto:** A visceral, highly motivational closing statement that makes them feel unstoppable.

Write exactly as this wise mentor. Make it profound and extremely detailed."""


PREVIEW_PROMPT = """You are a World-Class Elite Life Strategist. Generate a tantalizing, psychologically powerful, and deeply amusing teaser/preview for a custom life guide based on the book. 
Output MUST be 100% in {language_display} with NATIVE, natural grammar. Do not translate English idioms; use authentic {language_display} phrasing.

Book: {book_title}
Age: {age_range}
Gender: {gender_display}
Location: {location}
Goal: {goal}
Specific Change: {specific_change}
Language: {language_display}

FORMATTING STRICT RULES:
- 🚫 NO ASTERISKS (* or **). Use <b> tags for bolding: <b>Title</b>.
- 🚫 NO DASHES (- or —).
- 🚫 NO HASHES (#).
- ALWAYS use double line breaks (

) to separate thoughts.

YOUR MISSION:
Write a brilliant, psychologically penetrating opening that deeply analyzes their situation using the book's philosophy. 
Amuse the customer, validate their struggles, and build massive curiosity about the solution. 
Then, right as you are about to reveal the ultimate secret, the tactical plan, or the "one thing" they must do to achieve their goal, SUBTLY CUT IT OFF with an ellipsis (...) to leave them desperate for the full guide. Do not write a conclusion.

Make every sentence carry profound weight and intrigue. Output raw text."""


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


BOOK_VERIFY_PROMPT = """You are analyzing user input. The user was asked to provide a book title.
User Input: "{query}"

If the input looks like a plausible book title, a known published book, or even a specific topic they want a guide on, ACCEPT IT.
Only reject it (found: false) if it is absolute gibberish, keyboard mashing, or completely nonsensical text.

Respond in this exact JSON format only:
{{"title": "Cleaned Title", "author": "Author (if known, else empty)", "found": true}}

If it is absolute gibberish, respond:
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
