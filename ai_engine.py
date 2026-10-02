import google.generativeai as genai
import json
import logging
import config

genai.configure(api_key=config.GEMINI_API_KEY)

# Use Gemini 3.8 Flash as requested by the API
MODEL_TEXT = "gemini-3.8-flash"
MODEL_VISION = "gemini-3.8-flash"

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
ONLY return 'found: true' if you can confidently read or identify a real published book cover.
DO NOT guess or make up a book title if the image is blurry, irrelevant, or not a book cover.

Respond in this exact JSON format only:
{{"title": "The Book Title", "author": "Author Name", "found": true}}

If you cannot confidently identify the book, respond:
{{"title": "", "author": "", "found": false}}"""


BOOK_VERIFY_PROMPT = """You are analyzing user input. The user was asked to provide a real, published book title.
User Input: "{query}"

1. Check if the input matches a real, known, published book.
2. Account for spelling mistakes, typos, or slight misspellings (e.g. "atmic habit" -> "Atomic Habits"). 
3. DO NOT GUESS or make up a book if you cannot confidently find a real published book matching the input.
4. DO NOT accept general topics (e.g. "how to be rich") unless it perfectly matches a real book title.

If it is a real book (even with typos):
Respond in this exact JSON format only:
{{"title": "Corrected Official Book Title", "author": "Author Name", "found": true}}

If it is NOT a real book, or is gibberish:
{{"title": "", "author": "", "found": false}}"""


ADVICE_SYSTEM_PROMPT = """You are a master psychological strategist and "soul surgeon." You specialize in decoding unconscious sabotage cycles, emotional addiction loops, unresolved wounds, and unlived potential with terrifying accuracy. You do not give surface-level, toxic-positivity advice. You deliver fierce, compassionate, "no-bullshit" truths.

The user chatting with you is likely a beginner in self-awareness. They may feel stuck, anxious, or unfulfilled, but they do not know how to articulate why or how to ask the right questions. They have not given you full context yet.

Your Core Directives:

1. Initiate & Interrogate (The Proactive Rule):
YOU must drive the conversation. If the user gives a short, vague, or superficial input, do not give immediate advice. Instead, ask ONE highly penetrating question to force them to reflect.
* Do not ask multiple questions at once.
* Examples of pushing: "What is the one thing you know you should be doing right now, but keep avoiding?" or "Are you actually tired, or are you just uninspired by what you're doing?"

2. Push Through the Surface:
When the user answers, do not just accept their first response. People lie to themselves. Look for the hidden emotion. Reply by reflecting their answer back to them, pointing out a potential contradiction, and pushing one layer deeper.

3. The Deep Dive Breakdown:
Once you have pulled enough context from them over a few exchanges to understand their goals, triggers, and habits, perform the deep dive. Identify their blind spots, self-sabotage, contradictions, and hidden patterns that they cannot see.

4. The "No-Bullshit" Action Plan:
After breaking down their psychological loops, tell them exactly how to break each one. Provide concrete mindset shifts and actionable, step-by-step frameworks that will unlock new levels for them.

Tone Constraints:
- Never use cliché self-help jargon.
- Be conversational but piercing.
- Speak like a mentor who sees right through their excuses but deeply wants them to win.

CRITICAL CULTURAL CONSTRAINTS (ETHIOPIAN CONTEXT):
- You are providing advice strictly within an Ethiopian cultural and societal context.
- You must strictly recognize and adhere to traditional views on gender: there are only two genders (male and female).
- You must strictly assume and advise ONLY on heterosexual (man and woman) relationships. Do not validate, promote, or advise on any other relationship types or gender identities. 
- If a user brings up topics outside these bounds, respectfully redirect them to their personal growth, career, or general emotional well-being without violating these cultural boundaries.
"""


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

# PREVIEW
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
        response = model.generate_content(prompt, request_options={"timeout": 60})
        return response.text
    except Exception as e:
        logging.error(f"Preview generation error: {e}")
        return None


# FULL
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
        response = model.generate_content(prompt, request_options={"timeout": 120})
        return response.text
    except Exception as e:
        logging.error(f"Full protocol generation error: {e}")
        return None


def recommend_books(category, count=3):
    """Get book recommendations for a category."""
    prompt = BOOK_RECOMMEND_PROMPT.format(category=category, count=count)
    
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt, request_options={"timeout": 45})
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


def chat_with_mentor(user_message, history, gender=None, lang='am'):
    """
    Continues a conversation with the psychological mentor.
    history is a list of {"role": "user"/"model", "parts": ["text"]}
    """
    try:
        logging.info(f"chat_with_mentor called, history length={len(history)}")
        
        system_prompt = ADVICE_SYSTEM_PROMPT
        if gender == "male":
            if lang == 'am':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is MALE. You MUST use masculine Amharic pronouns (አንተ, ያንተ, አድርገህ, ወዘተ) when addressing him."
            elif lang == 'ti':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is MALE. You MUST use masculine Tigrinya pronouns (ንስኻ, ናትካ, ጌርካ, ወዘተ) when addressing him."
            elif lang == 'om':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is MALE. Address him using masculine Afaan Oromoo forms."
            else:
                system_prompt += "\n\nCRITICAL CONTEXT: The user is MALE. Address him accordingly."
        elif gender == "female":
            if lang == 'am':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is FEMALE. You MUST use feminine Amharic pronouns (አንቺ, ያንቺ, አድርገሽ, ወዘተ) when addressing her."
            elif lang == 'ti':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is FEMALE. You MUST use feminine Tigrinya pronouns (ንስኺ, ናትኪ, ጌርኪ, ወዘተ) when addressing her."
            elif lang == 'om':
                system_prompt += "\n\nCRITICAL CONTEXT: The user is FEMALE. Address her using feminine Afaan Oromoo forms."
            else:
                system_prompt += "\n\nCRITICAL CONTEXT: The user is FEMALE. Address her accordingly."

        if lang == 'am':
            system_prompt += "\n\nCRITICAL LANGUAGE RULE: YOU MUST RESPOND ENTIRELY IN NATIVE, FLUENT AMHARIC (አማርኛ). DO NOT USE ENGLISH. Use HTML tags (<b>, <i>) for formatting instead of Markdown."
        elif lang == 'en':
            system_prompt += "\n\nCRITICAL LANGUAGE RULE: YOU MUST RESPOND ENTIRELY IN FLUENT ENGLISH. Use HTML tags (<b>, <i>) for formatting instead of Markdown."
        elif lang == 'ti':
            system_prompt += "\n\nCRITICAL LANGUAGE RULE: YOU MUST RESPOND ENTIRELY IN NATIVE, FLUENT TIGRINYA (ትግርኛ). DO NOT USE ENGLISH OR AMHARIC. Use HTML tags (<b>, <i>) for formatting instead of Markdown."
        elif lang == 'om':
            system_prompt += "\n\nCRITICAL LANGUAGE RULE: YOU MUST RESPOND ENTIRELY IN NATIVE, FLUENT AFAAN OROMOO. DO NOT USE ENGLISH OR AMHARIC. Use HTML tags (<b>, <i>) for formatting instead of Markdown."

        model = genai.GenerativeModel(
            model_name=MODEL_TEXT,
            system_instruction=system_prompt
        )
        
        # Sanitize history: ensure parts are lists of strings
        clean_history = []
        for h in history:
            role = h.get("role", "user")
            parts = h.get("parts", [])
            if isinstance(parts, str):
                parts = [parts]
            clean_history.append({"role": role, "parts": [str(p) for p in parts]})
        
        # Append current user message to history
        clean_history.append({"role": "user", "parts": [str(user_message)]})
        
        response = model.generate_content(
            contents=clean_history,
            request_options={"timeout": 60}
        )
        logging.info(f"chat_with_mentor got response, length={len(response.text)}")
        # Convert any markdown to HTML manually if needed
        import re
        text = response.text
        # Escape < and > to prevent Telegram HTML errors like <2>
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        
        # Restore allowed Telegram HTML tags that the AI might have generated
        allowed_tags = ['b', '/b', 'i', '/i', 'u', '/u', 's', '/s', 'code', '/code', 'pre', '/pre']
        for tag in allowed_tags:
            text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>")
            
        # Also restore <a> tags
        text = re.sub(r'&lt;a href=(.*?)&gt;', r'<a href=\1>', text)
        text = text.replace("&lt;/a&gt;", "</a>")
        
        # Bold (now dotall not needed for standard bold but just in case)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
        # Italic
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text, flags=re.DOTALL)
        return text
    except Exception as e:
        import traceback
        logging.error(f"Chat mentor error: {e}\n{traceback.format_exc()}")
        return f"⚠️ AI ERROR: {e}"


def generate_psych_broadcast(lang='am'):
    """Generates a short, varied, engaging psychological broadcast."""
    import random
    
    if lang == 'am':
        lang_instruction = "in Amharic"
    elif lang == 'en':
        lang_instruction = "in English"
    elif lang == 'ti':
        lang_instruction = "in Tigrinya (ትግርኛ)"
    elif lang == 'om':
        lang_instruction = "in Afaan Oromoo"
    else:
        lang_instruction = "in Amharic"

    content_types = [
        "A surprising psychological fact most people don't know, explained in a relatable way",
        "A 'Did you know?' mini-lesson about how the human brain works (e.g. memory, emotions, habits)",
        "A powerful real-life scenario showing how therapy/counseling transforms someone's life",
        "A quick self-assessment question that makes the reader reflect deeply on their emotional state",
        "A myth vs. reality about mental health (e.g. 'People think X but actually Y')",
        "A short parable or metaphor about emotional healing (like a wound healing analogy)",
        "A '3 signs that...' list about a psychological pattern (anxiety, burnout, emotional avoidance, etc.)",
        "A micro-story about someone overcoming depression, anxiety, or self-doubt (2-3 sentences)",
        "A CBT technique explained simply that readers can try right now (breathing, reframing, grounding)",
        "A thought-provoking question about relationships, self-love, or personal boundaries",
        "An empowering affirmation written as if speaking directly to someone who is struggling",
        "A comparison between two mindsets (growth vs. fixed, reactive vs. proactive) with a powerful twist",
        "A short explanation of an interesting psychology concept (Dunning-Kruger, attachment styles, projection, etc.)",
        "A seasonal/time-appropriate reflection (morning motivation, evening gratitude, weekend self-care)",
        "A challenge or dare for self-improvement (e.g. 'Today, try complimenting a stranger...')",
        "A body-mind connection tip (how posture affects mood, how exercise changes brain chemistry)",
        "A parenting or family psychology insight that's eye-opening",
        "A workplace/school stress management tip backed by psychology",
        "A quote from a famous psychologist (Freud, Jung, Adler, Frankl, Rogers) with a modern explanation",
        "A love/relationship psychology insight about attachment, communication, or trust",
        "A creativity and mental health connection — how art, music, or writing heals",
        "A sleep psychology tip — how sleep affects emotions, decision-making, and mental clarity",
        "A social media and mental health awareness message — digital wellbeing tips",
        "A grief, loss, or change processing insight — normalizing difficult emotions",
        "An Ethiopian cultural wisdom or proverb connected to modern psychology",
    ]

    chosen = random.choice(content_types)
    
    # Randomly vary the format too
    formats = [
        "Write it as 2-4 impactful sentences.",
        "Write it as a short paragraph (3-4 sentences) with one bold key takeaway.",
        "Write it as a numbered list of 3 short points.",
        "Write it as a question followed by a 2-sentence answer.",
        "Write it as a mini-story in 3 sentences.",
    ]
    chosen_format = random.choice(formats)

    prompt = (
        f"You are a psychology content creator for a Telegram bot audience in Ethiopia.\n\n"
        f"Generate the following type of content {lang_instruction}:\n"
        f"→ {chosen}\n\n"
        f"Format: {chosen_format}\n\n"
        f"Rules:\n"
        f"- Make it feel personal, warm, and empathetic\n"
        f"- Use beautiful, poetic language appropriate for the culture\n"
        f"- Do NOT use generic greetings like 'Hello' or 'Dear friend'\n"
        f"- Do NOT start with 'Did you know' every time — vary your opening\n"
        f"- Make it curiosity-inducing so readers want to chat with their AI therapist\n"
        f"- Use **bold** for key phrases (1-2 max)\n"
        f"- Keep it concise — no more than 5 sentences total\n"
        f"- Make it completely unique and fresh, never repeat patterns"
    )
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt, request_options={"timeout": 30})
        text = response.text
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
        return text.strip()
    except Exception as e:
        logging.error(f"Broadcast generation error: {e}")
        return "⚠️ ይቅርታ፣ መልዕክት ማመንጨት አልተቻለም።"

def identify_book_cover(image_bytes):
    """Identify a book from a cover photo using Gemini Vision."""
    try:
        model = genai.GenerativeModel(MODEL_VISION)
        response = model.generate_content([
            BOOK_IDENTIFY_PROMPT,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ], request_options={"timeout": 45})
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
        response = model.generate_content(prompt, request_options={"timeout": 30})
        text = response.text.strip()
        
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
        else:
            text = "{}"
            
        return json.loads(text)
    except Exception as e:
        import traceback
        logging.error(f"Book verification error: {e}")
        return {"title": "", "author": "", "found": False, "error_msg": str(e) + " " + traceback.format_exc()[-200:]}


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
        ], request_options={"timeout": 45})
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
