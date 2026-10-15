import os
try:
    import certifi
    os.environ.setdefault("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH", certifi.where())
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except Exception:
    pass

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


RECEIPT_VERIFY_PROMPT = """You are an expert Ethiopian payment receipt verification system (CBE Mobile Banking, CBE Birr, Telebirr, and Bank Transfer receipts/SMS confirmations).

Current System Context:
- Today's Date: {today_date} (Current Year: {current_year}). Any receipt dated today ({today_date}) or recently within {current_year} is CURRENT and REAL-TIME, NOT a future date!
- Ethiopian Banking Context: Commercial Bank of Ethiopia (CBE) modern mobile banking receipts legitimately display transaction breakdowns including 'Reason: MB Transfer', 'Service Charge', 'VAT (15%)', and 'Disaster Recovery (5%)'. These are 100% genuine official CBE banking fields in Ethiopia, NOT anomalies.
- Account Suffixes: In CBE Mobile Banking, account numbers are frequently displayed as 'ETB-XXXX' where XXXX is the last 4 digits (e.g. 'ETB-4765' represents 1000073164765, and 'ETB-7878' represents 1000326477878). Both full account numbers and 'ETB-XXXX' suffix forms are valid!

Analyze this image/screenshot carefully and extract:
1. The exact amount paid (in ETB / Birr)
2. The recipient name, account number, or phone number
3. The transaction date / time
4. The unique Transaction ID or Reference number (e.g. CBE Ref starting with FT..., or Telebirr Transaction No.)

Expected payment details:
- Expected Amount: {expected_amount} Birr/ETB
- Accepted Recipient Accounts: 1000073164765 (or ETB-4765) or 1000326477878 (or ETB-7878){extra_cbe}
- Accepted Recipient Phones: 0912689900 or 0912338058 (+251912689900, +251912338058){extra_phone}
- Accepted Recipient Names: "Behailu Getachew", "Behailu Getachew Urga", "በኃይሉ ጌታቸው", "Michael Getachew", "ሚካኤል ጌታቸው"{extra_names}

Respond in this exact JSON format only, no other text or markdown codeblocks:
{{
  "is_valid_receipt": false,
  "amount_matches": false,
  "recipient_matches": false,
  "amount": null,
  "recipient": null,
  "date": null,
  "transaction_id": null,
  "confidence": "low",
  "reason": "Brief summary in English explaining what was detected or why it failed"
}}

Rules:
- is_valid_receipt: true ONLY if the image looks like a genuine, completed payment receipt, transfer confirmation, or bank SMS. Set false if it is a pending transfer, a balance inquiry, a blank image, or completely illegible.
- anti_tamper_check: Inspect closely for any signs of Photoshop or digital tampering (e.g. font mismatch, pasted text, pixel halos around the amount, or altered digits). Note: Official CBE layout with 'Disaster Recovery (5%)' is genuine and NOT tampering.
- amount_matches: true ONLY if the extracted amount equals exactly {expected_amount} (or within standard rounding, e.g. 200.00).
- recipient_matches: true ONLY if the extracted recipient account (including ETB-4765 or ETB-7878), phone, or name contains ANY of the accepted accounts, phones, or names listed above.
- transaction_id: The extracted transaction/reference ID (e.g. FT..., CI..., etc.), or null if not visible.
- confidence: "high" if the text is sharp and clearly visible with zero tampering; "medium" if readable with minor compression; "low" if blurry, cropped, ambiguous, or suspected of tampering."""


# ─── Language Mapping ──────────────────────

LANG_MAP = {
    "am": "Amharic",
    "en": "English",
    "om": "Afaan Oromoo",
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
        
        # Sanitize history: ensure alternating roles and clean strings
        raw_turns = []
        for h in history:
            role = h.get("role", "user")
            parts = h.get("parts", [])
            if isinstance(parts, str):
                parts = [parts]
            text_part = "\n".join(str(p) for p in parts if str(p).strip())
            if text_part:
                raw_turns.append({"role": role, "parts": [text_part]})
                
        # Append current user message
        if user_message and str(user_message).strip():
            raw_turns.append({"role": "user", "parts": [str(user_message).strip()]})
        
        # Merge consecutive turns of same role and ensure first turn is user
        clean_history = []
        for turn in raw_turns:
            role = turn["role"]
            text_content = turn["parts"][0]
            if clean_history and clean_history[-1]["role"] == role:
                clean_history[-1]["parts"] = [clean_history[-1]["parts"][0] + "\n\n" + text_content]
            else:
                clean_history.append({"role": role, "parts": [text_content]})
                
        if clean_history and clean_history[0]["role"] == "model":
            clean_history.insert(0, {"role": "user", "parts": ["[የዕለቱ የጋራ መልዕክት / Daily Broadcast]"]})
            
        response = model.generate_content(
            contents=clean_history,
            request_options={"timeout": 120}
        )
        
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            logging.warning(f"Gemini response has no content or was filtered: {getattr(response, 'prompt_feedback', None)}")
            return None

        text = response.text
        logging.info(f"chat_with_mentor got response, length={len(text)}")
        # Convert any markdown to HTML manually if needed
        import re
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
        return None


class PsychBroadcast(str):
    """String subclass containing structured broadcast metadata."""
    def __new__(cls, text, title=None, quote=None, tiktok_desc=None):
        instance = super().__new__(cls, text)
        instance.title = title or "የዕለቱ የስነ-ልቦና ማስታወሻ"
        instance.quote = quote or text
        instance.tiktok_desc = tiktok_desc or ""
        return instance

    def get(self, key, default=None):
        if key == "title": return self.title
        if key == "quote": return self.quote
        if key == "tiktok_desc": return self.tiktok_desc
        if key == "text": return str(self)
        return default


def generate_psych_broadcast(lang='am'):
    """Generates a short, varied, engaging psychological broadcast with a hook title, quote, and TikTok description."""
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

    prompt = (
        f"You are a master psychological content creator and viral social media copywriter for an Ethiopian audience.\n\n"
        f"Topic: {chosen}\n"
        f"Output Language: {lang_instruction}\n\n"
        f"Generate a JSON response with exactly these 3 fields:\n"
        f"1. \"title\": A very catchy, curiosity-inducing hook title (3 to 6 words) {lang_instruction}. "
        f"It must grab immediate attention and make people stop scrolling (e.g. 'ከራስህ ጋር የምትጣላበት ትልቁ ምክንያት' or 'ብዙዎች የማያውቁት የሰላም ሚስጥር'). "
        f"Do NOT use generic labels like 'ምክር' or 'የስነ-ልቦና እውነት'. Make it an irresistible hook.\n"
        f"2. \"quote\": The core profound psychological insight/quote (2 to 3 sentences) {lang_instruction} to put visually on the social card board. Make it deep, paradigm-shifting, and memorable.\n"
        f"3. \"tiktok_desc\": A catchy, intriguing social media / TikTok description {lang_instruction} (2 to 3 sentences). "
        f"CRITICAL RULE: DO NOT repeat the quote text from the card! Instead, hook the viewer, acknowledge an unspoken internal struggle, make them stay to read the card, and ask an engaging question that drives comments.\n\n"
        f"Return ONLY valid JSON format:\n"
        f"{{\n"
        f"  \"title\": \"Catchy Hook Title\",\n"
        f"  \"quote\": \"Profound quote for card board...\",\n"
        f"  \"tiktok_desc\": \"Intriguing description that hooks viewers and makes them stay...\"\n"
        f"}}"
    )
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt, request_options={"timeout": 30})
        text = response.text.strip()
        
        # Extract JSON object robustly
        data = None
        s_idx = text.find('{')
        e_idx = text.rfind('}')
        if s_idx != -1 and e_idx != -1:
            try:
                data = json.loads(text[s_idx:e_idx+1])
            except Exception:
                data = None
                
        if data and isinstance(data, dict) and "title" in data and "quote" in data:
            title = str(data.get("title", "")).strip()
            quote = str(data.get("quote", "")).strip()
            tiktok_desc = str(data.get("tiktok_desc", "")).strip()
        else:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if len(lines) > 1:
                title = lines[0].lstrip("#* -")
                quote = "\n\n".join(lines[1:])
            else:
                title = "የዕለቱ የስነ-ልቦና ማስታወሻ"
                quote = text
            tiktok_desc = "በካርዱ ላይ ያለውን በጥሞና አንብበው። ለአንተስ በዚህ ጉዳይ ላይ ምን ተሰማህ? አስተያየትህን በኮሜንት አጋራን።"

        import re
        title = re.sub(r'[*_#]', '', title).strip()
        quote = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', quote, flags=re.DOTALL).strip()
        full_text = f"<b>{title}</b>\n\n{quote}"
        return PsychBroadcast(full_text, title=title, quote=quote, tiktok_desc=tiktok_desc)
    except Exception as e:
        logging.error(f"Broadcast generation error: {e}")
        return PsychBroadcast("⚠️ ይቅርታ፣ መልዕክት ማመንጨት አልተቻለም።", title="የዕለቱ የስነ-ልቦና ማስታወሻ", quote="⚠️ ይቅርታ፣ መልዕክት ማመንጨት አልተቻለም።", tiktok_desc="")

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


def verify_receipt(image_bytes, expected_amount, telebirr_name=None, telebirr_phone=None, cbe_name=None, cbe_account=None):
    """Verify a payment screenshot using Gemini Vision."""
    extra_cbe = f" or {cbe_account}" if cbe_account and str(cbe_account) not in ("1000073164765", "1000326477878") else ""
    extra_phone = f" or {telebirr_phone}" if telebirr_phone and str(telebirr_phone) not in ("0912689900", "0912338058") else ""
    extra_names = ""
    if telebirr_name and str(telebirr_name) not in ("Michael Getachew", "Behailu Getachew", "በኃይሉ ጌታቸው"):
        extra_names += f', "{telebirr_name}"'
    if cbe_name and str(cbe_name) not in ("Michael Getachew", "Behailu Getachew", "በኃይሉ ጌታቸው"):
        extra_names += f', "{cbe_name}"'

    from datetime import datetime
    now = datetime.now()
    today_date = now.strftime("%b %d, %Y")
    current_year = now.year

    prompt = RECEIPT_VERIFY_PROMPT.format(
        expected_amount=expected_amount,
        extra_cbe=extra_cbe,
        extra_phone=extra_phone,
        extra_names=extra_names,
        today_date=today_date,
        current_year=current_year,
    )
    
    try:
        model = genai.GenerativeModel(MODEL_VISION)
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ], request_options={"timeout": 35})
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
        
        # Determine reference ID
        tx_id = result.get("transaction_id")
        if tx_id and str(tx_id).strip() and str(tx_id).lower() not in ("none", "null", "unknown"):
            result["ref_id"] = str(tx_id).strip()
        else:
            import uuid
            result["ref_id"] = f"GEMINI_{uuid.uuid4().hex[:8].upper()}"
            
        return result
    except Exception as e:
        logging.error(f"Receipt verification error: {e}")
        return {"auto_approved": False, "error": str(e), "reason": f"Verification error: {str(e)}"}


def generate_creative_giveaway_caption(secret_word, word_insight, winners_block, tiktok_name="የአዕምሮ ምግቦች"):
    """
    Uses Gemini AI to generate a creative, viral, captivating Amharic TikTok post caption
    for the daily secret word giveaway announcement.
    """
    clean_w = str(secret_word or "").strip().strip("«»\"' ").strip()
    prompt = (
        f"You are a master Ethiopian TikTok content creator, psychologist, and viral copywriter for 'የአዕምሮ ምግቦች' and 'Baya Books'.\n\n"
        f"Context:\n"
        f"- Daily Secret Positive Word: «{clean_w}»\n"
        f"- Core Psychological Insight: {word_insight}\n"
        f"- Top 5 Winners List:\n{winners_block}\n\n"
        f"Write an extraordinarily creative, inspiring, and engaging Amharic TikTok/Telegram caption.\n"
        f"Structure required:\n"
        f"1. A powerful, curiosity-inducing hook headline (e.g. ✨ የአዕምሮ ምግብ | የዕለቱ ሚስጥራዊ ቃል እና አሸናፊዎች 🏆).\n"
        f"2. Reveal today's secret word with excitement: 🎯 የዛሬው ሚስጥራዊ ቃል፦ «{clean_w}» ነበር።\n"
        f"3. 🧠 ስለ ቃሉ ጥልቅ የስነ-ልቦና ትምህርት (የአዕምሮ ምግብ): Write 2-3 deep, wise, emotionally resonant sentences explaining why this word transforms human psychology, self-worth, and inner peace. DO NOT just say 'አዎ አንተ ... ነህ'. Give real wisdom that touches the heart.\n"
        f"4. 💬 Interactive Challenge: An engaging call-to-action asking viewers to comment «{clean_w}» or answer an introspective question (this drives TikTok algorithm comments).\n"
        f"5. Celebrate the 5 winners warmly using the provided winners list.\n"
        f"6. Announcement: Next round starts tomorrow morning at 10:00 AM (ጠዋት 4:00)! Follow @{tiktok_name.replace('@','')} so you don't miss tomorrow's word.\n"
        f"7. Call-to-action to play in Telegram bot: @bayabooks_bot (Link in Bio).\n"
        f"8. 5-7 popular Ethiopian hashtags: #yeaemromgboch #bayabooks #የአዕምሮምግቦች #ስነልቦና #ሳይኮሎጂ #ethiopia #habesha #fyp\n\n"
        f"Output ONLY the final Amharic text ready to copy. No markdown code blocks, no English explanations."
    )
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt, request_options={"timeout": 20})
        text = response.text.strip()
        if text and len(text) > 120:
            return text
    except Exception as e:
        logging.error(f"Error generating creative giveaway caption: {e}")
    return None


def generate_creative_card_and_caption(secret_word, winners_block, tiktok_name="የአዕምሮ ምግቦች"):
    """
    Uses Gemini AI to generate:
    1. A profound 1-2 sentence psychological quote for the 1:1 card below the secret word (NEVER repeating or defining the word).
    2. A full viral TikTok post caption.
    Returns dict: {"card_quote": "...", "caption": "..."}
    """
    clean_w = str(secret_word or "").strip().strip("«»\"' ").strip()
    prompt = (
        f"You are a master Ethiopian psychologist, philosopher, and social media copywriter for 'የአዕምሮ ምግቦች' and 'Baya Books'.\n\n"
        f"Daily Positive Word: «{clean_w}»\n"
        f"Top 5 Winners:\n{winners_block}\n\n"
        f"Generate a JSON response with two fields in fluent, native Amharic:\n"
        f"1. \"card_quote\": A short, deeply touching, poetic and inspiring psychological quote (1 to 2 sentences, 100-160 Amharic characters) to be displayed on a 1:1 image card directly BELOW the word «{clean_w}».\n"
        f"CRITICAL RULE FOR card_quote: DO NOT REPEAT THE WORD «{clean_w}»! DO NOT start with '{clean_w} ማለት...'. Provide deep, soul-stirring wisdom (የአዕምሮ ምግብ) about inner strength, peace, resilience, or human greatness that gives goosebumps.\n\n"
        f"2. \"caption\": A complete, highly engaging Amharic TikTok post caption including viral hook, word reveal, comment challenge, winners list, announcement for 10:00 AM reset, and hashtags.\n\n"
        f"Return ONLY valid JSON format:\n"
        f"{{\n"
        f"  \"card_quote\": \"...\",\n"
        f"  \"caption\": \"...\"\n"
        f"}}"
    )
    try:
        model = genai.GenerativeModel(MODEL_TEXT)
        response = model.generate_content(prompt, request_options={"timeout": 20})
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        data = json.loads(text)
        if data.get("card_quote") and data.get("caption"):
            return data
    except Exception as e:
        logging.error(f"Error in generate_creative_card_and_caption: {e}")
    return None


