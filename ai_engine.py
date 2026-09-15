import google.generativeai as genai
import json
import logging
import config

genai.configure(api_key=config.GEMINI_API_KEY)

# Use Gemini 3.7 Flash for speed and vision
MODEL_TEXT = "gemini-3.7-flash"
MODEL_VISION = "gemini-3.7-flash"

# ─── The Master Prompt (User's original) ──────────

FULL_PROTOCOL_PROMPT = """You are a World-Class Elite Life Strategist, Behavioral Psychologist, and Master Analyst. Your objective is to take a user's chosen book and transform it into a paradigm-shattering, hyper-detailed, deeply empowering personal transformation PDF manual.

You must deliver profound depth. Do not give shallow, generic advice. Every sentence must carry weight, psychological insight, and actionable power.

### USER INPUTS:
- Book Title: {book_title}
- Age: {age_range}
- Gender: {gender_display}
- Main Goal: {goal}
- Output Language: {language_display}

### CORE DIRECTIVES (STRICTLY ENFORCED):
1. THE ABSOLUTE LANGUAGE RULE: The entire output MUST be 100% in the requested Output Language. NEVER mix languages. For example, if Afaan Oromoo is requested, you must NEVER include Amharic words, titles, or characters. Ensure perfect grammar, spelling, and natural sentence flow.
2. THE LATERAL BRIDGE (NO REJECTIONS): If the book is fiction, history, or totally unrelated to the goal, extract abstract themes (e.g., resilience, resource management) and map them flawlessly to the user's goal.
3. DEMOGRAPHIC PSYCHOANALYSIS: Deeply empathize with their exact Age and Gender in the Ethiopian context.
4. FORMATTING & EMOJIS (CRITICAL): 
   - Make the formatting extremely clean, spaced out, and visually beautiful.
   - Use Emojis (🎯, 💡, 🔥, 🚀, etc.) generously to structure the text and make it engaging.
   - NEVER use the asterisk sign (`**` or `*`). Do not use markdown bold/italics. 
   - NEVER use long dashes or hyphens (`—`, `–`, `-`).
   - For lists or bullet points, use emojis (e.g., ✅ or 🔹) instead of dashes or asterisks.
   - You MAY use `#` or `###` for main headings.
5. STRICT ETHIOPIAN CULTURAL ALIGNMENT: Align deeply with Ethiopian cultural, social, and religious values. Operate within traditional Ethiopian norms regarding gender and family dynamics.
6. Do not wrap your response in markdown code blocks. Output the raw text directly.

### OUTPUT STRUCTURE:
Generate the response strictly using the following structure, translated into the target language. Do not output anything outside of this structure.

### The {book_title} Protocol: Your Blueprint for {goal}
A Custom Transformation Architected for a {age_range}-Year-Old {gender_display}

### PART I: THE DEEP DIAGNOSIS & THE BRIDGE
Why this book, why this goal, and why YOU, right now.

✅ The Hidden Connection: Write a profound 2-paragraph analysis connecting the deepest philosophical premise of the book directly to the goal. Explain why viewing their goal through the lens of this specific book is the ultimate unfair advantage.
✅ The Life-Stage Reality: Speak directly to what it means to be this age and gender in Ethiopia trying to achieve this. Validate their struggles. Acknowledge the societal or personal weight they carry right now, and reframe their age/gender as their greatest weapon.

### PART II: THE PARADIGM SHIFT
The psychological rewiring required before action can be taken.

✅ The Old Belief vs. The New Belief: Detail the specific toxic mindset or limiting belief stopping them right now. Then, provide the new, empowering belief extracted from the book that they must install in their mind today.
✅ The Book Identity: How would the main character or the author approach this goal? Instruct the user on how to adopt this "alter ego" when they face resistance.

### PART III: THE TACTICAL EXECUTION MATRIX
The granular, day-by-day operational system to guarantee success.

### 1. The Daily Operating System (Micro-Habits)
✅ The AM/PM Bookends: Design a specific 15-minute Morning Ignition Routine and a 15-minute Evening Shutdown Routine based on the book's principles to protect their energy. Ensure these routines fit a traditional Ethiopian daily rhythm.
✅ The "One Thing" Focus Block: What is the exact, non-negotiable task they must execute daily? Specify how long it should take and the best time of day to do it based on their age/lifestyle.
✅ Habit Stacking: Take one new difficult action required for their goal, and explicitly tell them how to "stack" it on top of an existing habit they already do every day (e.g., coffee ceremonies, daily prayers, commutes).
✅ Environment Architecture: What specific trigger in their current physical or digital environment must be destroyed today? What visual cue must be added to their room or phone to make success automatic?

### 2. The Weekly Calibration (Data & Adaptation)
✅ The Metric of Truth (KPI): Identify ONE single, ruthless number or metric they must track every Sunday to prove they are moving toward their goal. No vague feelings—a hard metric.
✅ The 3-Question Sunday Audit: Provide exactly 3 piercing, psychologically deep questions they must ask themselves at the end of the week to review their progress.
✅ The "If/Then" Failure Protocols: Create two specific "If/Then" contingency plans.

### 3. The Monthly Evolution (Macro-Strategy)
✅ The 30-Day Checkpoint (The Pivot): What exactly should their life and progress look like at Day 30? If they are falling behind, what exact strategic pivot must they make?
✅ The 90-Day Transformation Horizon: Paint a highly specific, visceral picture of their new reality at Day 90. What tangible result will they hold in their hands?
✅ The Next Evolution: Once this 90-day base goal is achieved, what is the next logical mountain to climb based on the philosophy of the book?

### PART IV: OBSTACLE ANTICIPATION & THE COUNTER-STRIKE
Predicting failure before it happens.

✅ The Trap: As this age and gender in Ethiopian society, what is the exact, specific reason they are most likely to quit this journey?
✅ The Counter-Strike: What specific principle from the book will they use as a weapon when this obstacle hits? Provide an exact mental script or action to use in that moment of weakness.

### PART V: THE EMPOWERMENT MANIFESTO
A final, deeply moving call to action.

Write a visceral, highly motivational closing statement. It must synthesize their age, their gender, the wisdom of the book, their cultural strength, and the beautiful reality of what their life will look like when they achieve this goal. Command them to take their first step today. End with a powerful, memorable one-liner."""


PREVIEW_PROMPT = """You are a World-Class Elite Life Strategist. Generate ONLY Part I of a transformation protocol. Be deeply personal, psychologically powerful, and culturally Ethiopian.
Output MUST be 100% in {language_display}. Do not mix languages. Do not use asterisks (*). Do not use long dashes. Use emojis.

Book: {book_title}
Age: {age_range}
Gender: {gender_display}
Goal: {goal}
Language: {language_display}

Output in {language_display} ONLY. Do not wrap in code blocks.

Write exactly this structure:

### ክፍል 1: ጥልቅ ምርመራ

🔗 ድብቅ ትስስር: Write 2 profound paragraphs connecting this book's deepest philosophy to their goal. Make it feel like a revelation.

🎯 የህይወት ደረጃ እውነት: Speak directly to what it means to be a {age_range}-year-old {gender_display} in Ethiopia pursuing this goal. Validate their struggles. Reframe their age and gender as their greatest weapon.

Make every sentence carry weight. Be specific to Ethiopian culture, society, and daily life."""


BOOK_RECOMMEND_PROMPT = """You are a book recommendation expert for Ethiopian readers. 
Category: {category}

Recommend exactly 3 transformative books for this category. For each book, write exactly 1 sentence in Amharic explaining how it changes the reader's life.

Respond in this exact JSON format only, no other text:
[
  {{"title": "Book Title in English", "description": "One sentence in Amharic"}},
  {{"title": "Book Title in English", "description": "One sentence in Amharic"}},
  {{"title": "Book Title in English", "description": "One sentence in Amharic"}}
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
- Expected Recipient: {expected_recipient} or {expected_phone}

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
- recipient_matches: true ONLY if recipient contains "{expected_recipient}" or "{expected_phone}"
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

def generate_preview(book_title, gender, age_range, goal, language="am"):
    """Generate only Part 1 (the free hook)."""
    gender_display = GENDER_MAP.get(gender, {}).get("am", gender)
    language_display = LANG_MAP.get(language, "Amharic")
    
    prompt = PREVIEW_PROMPT.format(
        book_title=book_title,
        age_range=age_range,
        gender_display=gender_display,
        goal=goal,
        language_display=language_display,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Preview generation error: {e}")
        return None


def generate_full_protocol(book_title, gender, age_range, goal, language="am"):
    """Generate the complete transformation protocol."""
    gender_display = GENDER_MAP.get(gender, {}).get("am", gender)
    language_display = LANG_MAP.get(language, "Amharic")
    
    prompt = FULL_PROTOCOL_PROMPT.format(
        book_title=book_title,
        age_range=age_range,
        gender_display=gender_display,
        goal=goal,
        language_display=language_display,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Full protocol generation error: {e}")
        return None


def recommend_books(category):
    """Get 3 book recommendations for a category."""
    prompt = BOOK_RECOMMEND_PROMPT.format(category=category)
    
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


def verify_receipt(image_bytes, expected_amount, expected_recipient, expected_phone):
    """Verify a payment screenshot using Gemini Vision."""
    prompt = RECEIPT_VERIFY_PROMPT.format(
        expected_amount=expected_amount,
        expected_recipient=expected_recipient,
        expected_phone=expected_phone,
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
        
        # Final verdict
        is_approved = (
            result.get("is_valid_receipt") and
            result.get("amount_matches") and
            result.get("recipient_matches") and
            result.get("confidence") in ("high", "medium")
        )
        result["auto_approved"] = is_approved
        return result
    except Exception as e:
        logging.error(f"Receipt verification error: {e}")
        return {"auto_approved": False, "error": str(e)}
