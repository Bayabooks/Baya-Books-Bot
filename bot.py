import os
# SSL fix for local Windows development only (not needed on Render)
if os.environ.get("DEV_MODE"):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

import logging
import uuid
import chapa
import json
from urllib.parse import urlparse, parse_qs
import threading
import tempfile
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
import config
import database
import ai_engine
import telegraph_generator
import receipt_verifier
import lang
from lang import S

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)

logging.info("================ BOT STARTING ===============")

if not config.BOT_TOKEN:
    print("ERROR: BOT_TOKEN missing in .env!"); exit(1)
if not config.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY missing in .env!"); exit(1)

bot = TeleBot(config.BOT_TOKEN)

# ══════════════════════════════════════════
#  CONVERSATION STATE MANAGER
# ══════════════════════════════════════════
user_sessions = {}  # {user_id: {state, data...}}
session_lock = threading.RLock()

def get_session(user_id):
    with session_lock:
        if user_id not in user_sessions:
            user_sessions[user_id] = {"state": "IDLE", "data": {}}
        return user_sessions[user_id]

def set_state(user_id, state, **kwargs):
    with session_lock:
        s = get_session(user_id)
        s["state"] = state
        s["data"].update(kwargs)

def clear_state(user_id):
    with session_lock:
        user_sessions[user_id] = {"state": "IDLE", "data": {}}

def get_lang(uid):
    """Get user's language, default 'am'."""
    try:
        return database.get_bot_language(uid) or 'am'
    except:
        return 'am'

# ══════════════════════════════════════════
#  CATEGORIES & GOALS (Amharic)
# ══════════════════════════════════════════
CATEGORIES = [
    ("cat_1", "🧠", "ልማድ እና ዲሲፕሊን", "Habits & Discipline"),
    ("cat_2", "💰", "ገንዘብ እና ሀብት", "Wealth & Money"),
    ("cat_3", "❤️", "ፍቅር እና ግንኙነት", "Love & Relationships"),
    ("cat_4", "🕊️", "የህይወት ዓላማ እና ሰላም", "Purpose & Inner Peace"),
    ("cat_5", "🎯", "ትኩረት እና ውጤታማነት", "Focus & Productivity"),
    ("cat_6", "🦁", "በራስ መተማመን", "Confidence & Mindset"),
    ("cat_7", "👑", "አመራር እና ተፅዕኖ", "Leadership & Influence"),
    ("cat_8", "🩹", "ስነ-ልቦናዊ ፈውስ", "Healing & Letting Go"),
    ("cat_9", "⚡", "ጤና እና ሀይል", "Health & Energy"),
    ("cat_10", "🚀", "ቢዝነስ እና ስራ ፈጠራ", "Business & Entrepreneurship"),
]

SUBCATEGORIES = {
    "cat_1": [
        ("sub_1_1", "መጥፎ ልማድን ማቋረጥ", "Breaking Bad Habits"),
        ("sub_1_2", "የዕለት ተዕለት ሩቲን መገንባት", "Building Daily Routines"),
        ("sub_1_3", "ዲሲፕሊን እና ቁርጠኝነት", "Developing Willpower")
    ],
    "cat_2": [
        ("sub_2_1", "ገንዘብ ማጠራቀም እና ማስተዳደር", "Saving & Budgeting"),
        ("sub_2_2", "ኢንቨስትመንት እና ሀብት ማፍራት", "Investing & Wealth Creation"),
        ("sub_2_3", "የገንዘብ ስነ-ልቦና", "Financial Mindset")
    ],
    "cat_3": [
        ("sub_3_1", "ትክክለኛ አጋር ማግኘት", "Finding the Right Partner"),
        ("sub_3_2", "ትዳር እና ግንኙነትን ማጠናከር", "Strengthening Relationships"),
        ("sub_3_3", "ማህበራዊ ክህሎት እና ጓደኝነት", "Social Skills & Friendship")
    ],
    "cat_4": [
        ("sub_4_1", "የህይወት ትርጉምን ማግኘት", "Finding Meaning in Life"),
        ("sub_4_2", "ጭንቀት እና ሀሳብን ማሸነፍ", "Overcoming Anxiety & Stress"),
        ("sub_4_3", "ውስጣዊ ሰላም እና መንፈሳዊነት", "Inner Peace & Mindfulness")
    ],
    "cat_5": [
        ("sub_5_1", "የጊዜ አጠቃቀም", "Time Management"),
        ("sub_5_2", "ጥልቅ ትኩረት (Deep Work)", "Deep Work & Focus"),
        ("sub_5_3", "ማንዛዛትን ማቆም (Procrastination)", "Overcoming Procrastination")
    ],
    "cat_6": [
        ("sub_6_1", "የበታችነት ስሜትን ማሸነፍ", "Overcoming Self-Doubt"),
        ("sub_6_2", "በሰው ፊት መናገር እና ድፍረት", "Public Speaking & Social Confidence"),
        ("sub_6_3", "የአሸናፊነት አስተሳሰብ", "Resilient Mindset")
    ],
    "cat_7": [
        ("sub_7_1", "ሰዎችን መምራት እና ማስተዳደር", "Managing Teams"),
        ("sub_7_2", "ማሳመን እና ድርድር", "Persuasion & Negotiation"),
        ("sub_7_3", "ተፅዕኖ ፈጣሪነት እና ካሪዝማ", "Charisma & Influence")
    ],
    "cat_8": [
        ("sub_8_1", "ከትልቅ ህመም (Trauma) ማገገም", "Overcoming Trauma"),
        ("sub_8_2", "ይቅርታ እና ያለፈውን መተው", "Forgiveness & Moving On"),
        ("sub_8_3", "ሀዘንን እና መለያየትን ማለፍ", "Dealing with Grief & Loss")
    ],
    "cat_9": [
        ("sub_9_1", "አካላዊ ብቃት እና ስፖርት", "Fitness & Exercise"),
        ("sub_9_2", "አመጋገብ እና ጤና", "Diet & Nutrition"),
        ("sub_9_3", "እረፍት እና ከፍተኛ ሀይል", "Sleep & High Energy")
    ],
    "cat_10": [
        ("sub_10_1", "አዲስ ቢዝነስ መጀመር", "Starting a Startup"),
        ("sub_10_2", "ማርኬቲንግ እና ሽያጭ", "Marketing & Sales"),
        ("sub_10_3", "ቢዝነስን ማሳደግ (Scaling)", "Scaling & Strategy")
    ]
}

GOALS = [
    ("goal_1", "🚀", "ቢዝነስ መጀመር"),
    ("goal_2", "💰", "ገንዘብ ማጠራቀም"),
    ("goal_3", "🦁", "በራስ መተማመን"),
    ("goal_4", "🧠", "ጤናማ ልማድ መገንባት"),
    ("goal_5", "😌", "ውጥረትን ማሸነፍ"),
    ("goal_6", "💼", "ስራ ማግኘት/ማሻሻል"),
    ("goal_7", "❤️", "ግንኙነት ማሻሻል"),
    ("goal_8", "🎯", "ትኩረት እና ዲሲፕሊን"),
    ("goal_9", "🕊️", "የህይወት ዓላማ ማግኘት"),
    ("goal_10", "💪", "ከሱስ መላቀቅ"),
]

AGE_RANGES = [
    ("age_1", "🎓", "15-19"),
    ("age_2", "⚡", "20-24"),
    ("age_3", "🔥", "25-29"),
    ("age_4", "💼", "30-39"),
    ("age_5", "👑", "40-49"),
    ("age_6", "🕊️", "50+"),
]


# Display value translations for user-facing messages
GENDER_DISPLAY = {"male": "ወንድ", "female": "ሴት"}
LIVING_DISPLAY = {"Alone": "ብቻ", "With Family": "ከቤተሰብ ጋር"}
LOCATION_DISPLAY = {"Ethiopia": "ኢትዮጵያ", "Abroad": "ውጭ ሀገር"}

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════

def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def is_admin(user):
    if user.username and user.username.lower() == config.ADMIN_USERNAME:
        return True
    return database.is_sub_admin(user.id)

def is_owner(user):
    return bool(user.username and user.username.lower() == config.ADMIN_USERNAME)

def is_admin_uid(uid):
    user_data = database.get_user(uid)
    if user_data and user_data['username'] and user_data['username'].lower() == config.ADMIN_USERNAME:
        return True
    return database.is_sub_admin(uid)

def get_admin_id():
    try:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (config.ADMIN_USERNAME,))
        row = c.fetchone()
        conn.close()
        return row["user_id"] if row else None
    except Exception:
        return None

def check_channel_member(user_id):
    """Check if user follows the channel."""
    try:
        member = bot.get_chat_member(f"@{config.CHANNEL_USERNAME}", user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

def send_join_channel_msg(chat_id, uid=None):
    """Tell user to join channel first."""
    lang_code = get_lang(uid) if uid else 'am'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(S(lang_code, 'join_channel_btn'), url=f"https://t.me/{config.CHANNEL_USERNAME}"))
    markup.add(InlineKeyboardButton(S(lang_code, 'joined_check_btn'), callback_data="check_joined"))
    bot.send_message(
        chat_id,
        S(lang_code, 'join_channel_title') + "\n\n" + S(lang_code, 'join_channel_hint'),
        parse_mode="HTML", reply_markup=markup,
    )

def notify_admin(text):
    admin_id = get_admin_id()
    if admin_id:
        try:
            bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            pass

# ══════════════════════════════════════════
#  DEBUG LOG COMMAND
# ══════════════════════════════════════════
@bot.message_handler(commands=["getlogs"])
def cmd_getlogs(message):
    if not is_admin(message.from_user):
        return
    try:
        import os
        if not os.path.exists("app.log"):
            # Check render stdout? We might not have app.log
            # Just read the recent python logs if available, or tell admin
            bot.reply_to(message, "No app.log file found.")
            return
        with open("app.log", "r") as f:
            lines = f.readlines()
            logs = "".join(lines[-40:])
            bot.reply_to(message, f"<pre>{html.escape(logs[-3500:])}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, str(e))

# ══════════════════════════════════════════
#  /topup COMMAND (Manual Advice Paywall)
# ══════════════════════════════════════════
@bot.message_handler(commands=["topup", "buy_advice"])
def cmd_topup(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    lang = get_lang(uid)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(S(lang, 'topup_btn_starter'), callback_data="buy_advice_25"))
    markup.add(InlineKeyboardButton(S(lang, 'topup_btn_pro'), callback_data="buy_advice_75"))
    markup.add(InlineKeyboardButton(S(lang, 'topup_btn_heavy'), callback_data="buy_advice_225"))
    markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited'), callback_data="buy_advice_unlimited"))
    markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited_month'), callback_data="buy_advice_unlimited_month"))
    
    cta_text = (
        S(lang, 'topup_title') + "\n\n" +
        S(lang, 'topup_body') + "\n\n" +
        S(lang, 'topup_choose') + "\n\n" +
        S(lang, 'topup_starter') + "\n" +
        S(lang, 'topup_pro') + "\n" +
        S(lang, 'topup_heavy') + "\n" +
        S(lang, 'topup_unlimited') + "\n" +
        S(lang, 'topup_unlimited_month') + "\n\n" +
        S(lang, 'topup_cta')
    )
    bot.send_message(chat_id, cta_text, parse_mode="HTML", reply_markup=markup)

# ══════════════════════════════════════════
#  /add_advice COMMAND (Admin Only)
# ══════════════════════════════════════════
@bot.message_handler(commands=["add_advice", "give_advice"])
def cmd_add_advice(message):
    if not is_admin(message.from_user):
        return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "Usage: /add_advice <user_id> <amount>\nExample: /add_advice 123456789 120")
        return
    try:
        target_uid = int(args[1])
        amount = int(args[2])
        database.add_advice_messages(target_uid, amount)
        bot.reply_to(message, f"✅ Added {amount} advice messages to user {target_uid}.")
        try:
            bot.send_message(target_uid, S(get_lang(target_uid), 'gift_notification', amount=amount), parse_mode="HTML")
        except:
            bot.reply_to(message, "(Note: User blocked the bot or ID is invalid, so they didn't receive the notification, but balance was updated if they exist).")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ══════════════════════════════════════════
#  /start COMMAND
# ══════════════════════════════════════════
@bot.message_handler(commands=["start"])
def cmd_start(message):
    user = message.from_user
    args = message.text.split()

    # Check for referral deep link
    referred_by = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user.id and database.is_new_user(user.id):
                referred_by = referrer_id
        except ValueError:
            pass

    database.add_user(user.id, user.username or "Unknown", user.first_name or "User", referred_by)

    if referred_by:
        database.record_referral(referred_by, user.id)
        # Check if they hit 5 uncredited referrals
        ref_count = database.get_uncredited_referral_count(referred_by)
        if ref_count >= 5:
            database.add_credits(referred_by, 1)
            database.mark_n_referrals_credited(referred_by, 5)
            try:
                bot.send_message(referred_by, "🎉 <b>እንኳን ደስ አሎት!</b>\n\n5 ጓደኞችዎ ስለተቀላቀሉ 1 ነጻ የመመሪያ ክሬዲት አግኝተዋል!\n\n/new ይጫኑ እና መመሪያዎን ያዘጋጁ!", parse_mode="HTML")
            except Exception:
                pass

    # Channel check
    if not is_admin(user) and not check_channel_member(user.id):
        send_join_channel_msg(message.chat.id, user.id)
        return

    if check_onboarding(message.chat.id, user.id, user.first_name):
        send_welcome(message.chat.id, user.first_name)

def check_onboarding(chat_id, user_id, first_name):
    age_verified, gender = database.get_onboarding_status(user_id)
    
    # Ensure user exists in DB (handles DB wipe on Render)
    if not database.get_user(user_id):
        database.add_user(user_id, "Unknown", first_name or "User")
    
    # Check if language is set
    user_lang = database.get_bot_language(user_id)
    if not user_lang:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="setlang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
        )
        markup.add(
            InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data="setlang_ti"),
            InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data="setlang_om"),
        )
        bot.send_message(chat_id, S('am', 'lang_select_prompt'), parse_mode="HTML", reply_markup=markup)
        return False

    # Age + Gender combined in one fast step
    if not age_verified or not gender:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(S(user_lang, 'gender_male'), callback_data="onboard_gen_m"),
            InlineKeyboardButton(S(user_lang, 'gender_female'), callback_data="onboard_gen_f")
        )
        bot.send_message(chat_id, S(user_lang, 'onboard_age_gender_prompt'), parse_mode="HTML", reply_markup=markup)
        return False
    
    return True

def send_welcome(chat_id, first_name, lang=None, uid=None):
    if uid is None:
        uid = chat_id # Fallback
    if lang is None:
        lang = get_lang(uid)
    bot.send_message(
        chat_id, 
        S(lang, 'welcome_text', name=html.escape(first_name)), 
        parse_mode="HTML", 
        reply_markup=get_bottom_markup(lang, uid)
    )

def get_bottom_markup(lang='am', uid=None):
    """Build the localized bottom keyboard."""
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, is_persistent=True)
    m.add(
        KeyboardButton(S(lang, 'menu_continue')),
        KeyboardButton(S(lang, 'menu_mypage'))
    )
    m.add(
        KeyboardButton(S(lang, 'menu_invite')),
        KeyboardButton(S(lang, 'menu_lang'))
    )
    if uid and is_admin_uid(uid):
        m.add(
            KeyboardButton(S(lang, 'menu_support')),
            KeyboardButton("⚙️ Dashboard")
        )
    else:
        m.add(
            KeyboardButton(S(lang, 'menu_support'))
        )
    m.add(
        KeyboardButton(S(lang, 'menu_feedback'))
    )
    return m

# ══════════════════════════════════════════
#  /help & /mylibrary COMMANDS
# ══════════════════════════════════════════
@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        "📖 <b>Baya Books እንዴት እንጠቀማለን?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ መጽሐፍ ይምረጡ ወይም እኛ እንምረጥልዎ\n"
        "2️⃣ ጥቂት ጥያቄዎችን ይመልሱ\n"
        "3️⃣ ነጻ ማሳያ ያንብቡ\n"
        f"4️⃣ ሙሉ PDF ይዘዙ ({config.PRICE_SINGLE} ብር)\n"
        "5️⃣ ግላዊ መመሪያዎን ያውርዱ!\n\n"
        "📚 /mylibrary — ያዘዙዋቸው PDFs\n"
        "🔗 /referral — ጓደኞችን ይጋብዙ\n"
        "🆕 /new — አዲስ PDF ይጀምሩ\n\n"
        "ለማንኛውም ጥያቄ @Bayabooks ያናግሩን!",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["mylibrary"])
def cmd_library(message):
    if not check_channel_member(message.from_user.id):
        send_join_channel_msg(message.chat.id, message.from_user.id); return

    orders = database.get_user_orders(message.from_user.id)
    if not orders:
        bot.send_message(message.chat.id, "📚 ገና ምንም PDF አልተዘጋጀልዎም።\n\n/new ይጫኑ ለመጀመር!")
        return

    lines = []
    for i, o in enumerate(orders, 1):
        date = o["delivered_date"][:10] if o["delivered_date"] else "N/A"
        lines.append(f"  {i}. 📕 {o['book_title']} ({date})")

    markup = InlineKeyboardMarkup()
    for i, o in enumerate(orders, 1):
        if o["pdf_file_id"]:
            markup.add(InlineKeyboardButton(f"📥 {i}. {o['book_title']}", callback_data=f"redownload_{o['id']}"))

    bot.send_message(
        message.chat.id,
        f"📚 <b>ቤተ-መጽሐፍትዎ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        + "\n".join(lines) + "\n\n📥 ለማውረድ ከታች ይጫኑ",
        parse_mode="HTML", reply_markup=markup,
    )

@bot.message_handler(commands=["referral"])
def cmd_referral(message):
    ref_count = database.get_uncredited_referral_count(message.from_user.id)
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"

    bot.send_message(
        message.chat.id,
        f"🎉 <b>ጓደኛዎን ይጋብዙ፣ ነጻ መመሪያ ያግኙ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 5 ጓደኞችዎን ይህን ሊንክ ተጠቅመው\n"
        f"ቦቱን ሲቀላቀሉ — እርስዎ ነጻ 1 መመሪያ ያገኛሉ!\n\n"
        f"🔗 <b>የእርስዎ ሊንክ:</b>\n<code>{link}</code>\n\n"
        f"📊 ያጋበዙት: <b>{ref_count}</b>/5\n",
        parse_mode="HTML"
    )

@bot.message_handler(commands=["new"])
def cmd_new(message):
    if not check_channel_member(message.from_user.id):
        send_join_channel_msg(message.chat.id, message.from_user.id); return
    clear_state(message.from_user.id)
    if check_onboarding(message.chat.id, message.from_user.id, message.from_user.first_name):
        send_welcome(message.chat.id, message.from_user.first_name)

@bot.message_handler(commands=["reset_advice"])
def cmd_reset_advice(message):
    if is_admin(message.from_user):
        database.save_advice_history(message.from_user.id, '[]')
        bot.reply_to(message, "🔄 <b>Advice Chat History Reset successfully.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ Admin only command.")

# ══════════════════════════════════════════
@bot.message_handler(commands=["wipe_all_data_confirm"])
def cmd_wipe_data(message):
    if not is_admin(message.from_user): return
    database.factory_reset()
    bot.reply_to(message, "⚠️ <b>FACTORY RESET COMPLETE</b>\n\nAll users, orders, and payments have been permanently deleted from the database. The system is completely fresh for official launch.", parse_mode="HTML")

@bot.message_handler(commands=["ban"])
def cmd_ban(message):
    if not is_admin(message.from_user): return
    try:
        target_id = int(message.text.split()[1])
        database.ban_user(target_id)
        bot.reply_to(message, f"✅ User {target_id} has been BANNED.")
        try: bot.send_message(target_id, S(get_lang(target_id), 'banned'))
        except: pass
    except:
        bot.reply_to(message, "Usage: /ban <user_id>")

@bot.message_handler(commands=["unban"])
def cmd_unban(message):
    if not is_admin(message.from_user): return
    try:
        target_id = int(message.text.split()[1])
        database.unban_user(target_id)
        bot.reply_to(message, f"✅ User {target_id} has been UNBANNED.")
        try: bot.send_message(target_id, "✅ አካውንትዎ ተከፍቷል! /start ይጫኑ ለመጀመር።")
        except: pass
    except:
        bot.reply_to(message, "Usage: /unban <user_id>")

# ══════════════════════════════════════════
#  /nudge COMMAND — Re-engage stuck users
# ══════════════════════════════════════════
@bot.message_handler(commands=["nudge"])
def cmd_nudge(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!"); return
    
    stuck = database.get_stuck_users()
    if not stuck:
        bot.reply_to(message, "✅ No stuck users! Everyone has completed onboarding.")
        return
    
    bot.reply_to(message, f"🔄 Nudging <b>{len(stuck)}</b> users who haven't completed onboarding...", parse_mode="HTML")
    
    import threading, time
    def run_nudge():
        sent, failed = 0, 0
        for u in stuck:
            uid = u['user_id']
            name = u['first_name'] or 'there'
            u_lang = u.get('bot_language') or 'am'
            try:
                # Send a warm, curiosity-inducing re-engagement nudge
                nudge_texts = {
                    'am': f"👋 ሰላም <b>{name}</b>፣ በመሃል ተቋርጦብዎት ነው?\n\nመስማት የሚፈልጉትን ሳይሆን፣ አሁን ላይ <b>ሊሰሙት የሚገባዎትን እውነት</b> የሚነግርዎት AI እርስዎን እየጠበቀ ነው።\n\nወደ ሚስጥራዊው የውይይት ገፅ ለመግባት...\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                    'en': f"👋 Hi <b>{name}</b>, got interrupted halfway?\n\nThe AI that tells you <b>the truth you need to hear</b> (not just what you want to hear) is waiting for you.\n\nTo enter the confidential chat...\n<b>Please select your gender 👇</b>",
                    'ti': f"👋 ሰላም <b>{name}</b>፡ ኣብ መንጎ ተቋሪጹካ ድዩ?\n\nክትሰምዖ ዝደለኻዮ ሳይኮን፡ <b>ሕጂ ክትሰምዖ ዝግባእ ሓቂ</b> ዝነግረካ AI እናተጸበየካ እዩ።\n\nናብቲ ምስጢራዊ ዕላል ንምእታው...\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                    'om': f"👋 Akkam <b>{name}</b>, gidduutti si jalaa citee?\n\nAI'n waan dhagahuu barbaaddu osoo hin taane, <b>dhugaa ammaa dhagahuu qabdu</b> sitti himu si eegaa jira.\n\nMarii iccitii ta'e kana jalqabuuf...\n<b>Maaloo saala keessan filadhaa 👇</b>",
                }
                text = nudge_texts.get(u_lang, nudge_texts['am'])
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton(S(u_lang, 'gender_male'), callback_data="onboard_gen_m"),
                    InlineKeyboardButton(S(u_lang, 'gender_female'), callback_data="onboard_gen_f")
                )
                bot.send_message(uid, text, parse_mode="HTML", reply_markup=markup)
                database.append_bot_message_to_history(uid, text)
                database.mark_nudge_sent(uid, "nudge_onboard_sent")
                sent += 1
            except Exception:
                database.mark_user_blocked(uid, 1)
                failed += 1
            time.sleep(0.07)
        try:
            bot.send_message(message.chat.id, f"✅ <b>Nudge Complete!</b>\n✔️ {sent} sent\n❌ {failed} failed", parse_mode="HTML")
        except: pass
    
    threading.Thread(target=run_nudge, daemon=True).start()

# ══════════════════════════════════════════
#  /fix_msgs COMMAND — Reset strange message counts
# ══════════════════════════════════════════
@bot.message_handler(commands=["fix_msgs"])
def cmd_fix_msgs(message):
    if not is_admin(message.from_user): return
    
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET advice_messages_left = 5 WHERE advice_messages_left > 5 AND advice_messages_left <= 15 AND user_id NOT IN (SELECT user_id FROM payments)")
    fixed = c.rowcount
    conn.commit()
    conn.close()
    
    bot.reply_to(message, f"✅ Fixed {fixed} users who had abnormally high message counts back to 5 free messages.")

# ══════════════════════════════════════════
#  /investigate COMMAND — Check last users
# ══════════════════════════════════════════
@bot.message_handler(commands=["investigate"])
def cmd_investigate(message):
    if not is_admin(message.from_user): return
    
    conn = database.get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT user_id, first_name, username, joined_date, advice_messages_left, referred_by 
        FROM users 
        ORDER BY joined_date DESC 
        LIMIT 20
    ''')
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        bot.reply_to(message, "No users found in database.")
        return
        
    res = "🔍 **Investigation of Last 20 Users:**\n\n"
    for r in rows:
        uid = r['user_id']
        name = r['first_name']
        msgs = r['advice_messages_left']
        ref = r['referred_by']
        date = r['joined_date']
        
        # Check if they have payment records
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM payments WHERE user_id = ?", (uid,))
        payments = c.fetchone()[0]
        
        # Check received credits/gifts (if any)
        c.execute("SELECT credits FROM users WHERE user_id = ?", (uid,))
        credits = c.fetchone()[0]
        conn.close()
        
        res += f"👤 <b>{name}</b> (<code>{uid}</code>)\n"
        res += f"📅 Joined: {date}\n"
        res += f"💬 Msgs Left: <b>{msgs}</b>\n"
        res += f"🔗 Referred By: {ref if ref else 'None'}\n"
        res += f"💳 Payments: {payments} | 🎁 Credits: {credits}\n"
        res += "━━━━━━━━━━━━━━━━\n"
        
    bot.reply_to(message, res, parse_mode="HTML")

# ══════════════════════════════════════════
#  /clean COMMAND — Rapidly purge ghost users
# ══════════════════════════════════════════
@bot.message_handler(commands=["clean"])
def cmd_clean(message):
    if not is_admin(message.from_user): return
    
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE bot_blocked = 0 AND (gender IS NULL OR gender = '')")
    stuck = [r[0] for r in c.fetchall()]
    conn.close()
    
    bot.reply_to(message, f"🧹 Starting background ghost clean on <b>{len(stuck)}</b> stuck users...", parse_mode="HTML")
    
    import threading, time
    def run_clean():
        cleaned = 0
        for uid in stuck:
            try:
                # Silently test if bot is blocked without sending a message
                bot.send_chat_action(uid, "typing")
            except Exception:
                database.mark_user_blocked(uid, 1)
                cleaned += 1
            time.sleep(0.05) # Prevent rate limits
        try:
            bot.send_message(message.chat.id, f"✅ <b>Cleanup Complete!</b>\n🗑 Filtered out <b>{cleaned}</b> ghost users from the dashboard.", parse_mode="HTML")
        except: pass
        
    threading.Thread(target=run_clean, daemon=True).start()

# ══════════════════════════════════════════
#  /icebreaker COMMAND — Nudge silent users
# ══════════════════════════════════════════
@bot.message_handler(commands=["icebreaker"])
def cmd_icebreaker(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!"); return
    
    silent = database.get_silent_users()
    if not silent:
        bot.reply_to(message, "✅ No silent users! Everyone who onboarded has chatted.")
        return
    
    bot.reply_to(message, f"❄️ Breaking the ice for <b>{len(silent)}</b> users who haven't chatted...", parse_mode="HTML")
    
    import threading, time
    def run_icebreaker():
        sent, failed = 0, 0
        for u in silent:
            uid = u['user_id']
            name = u['first_name'] or 'there'
            u_lang = u.get('bot_language') or 'am'
            try:
                ice_texts = {
                    'am': f"👋 ሰላም <b>{name}</b>፣ በሩን ከፍተው ገብተዋል ግን ዝምታን መርጠዋል።\n\nብዙ ጊዜ ከየት መጀመር እንዳለብን ግራ ሲገባን ዝም እንላለን። የተስተካከለ ፅሁፍ ማዘጋጀት አይጠበቅብዎትም — አሁን ላይ የሚሰማዎትን ስሜት በአንድ ቃል፣ ወይም «ሰላም» በማለት ብቻ ይፃፉልኝ።\n\nእኔ እዚህ ያለሁት ላዳምጥዎት ነው። 👇",
                    'en': f"👋 Hi <b>{name}</b>, you opened the door but stayed silent.\n\nOften we stay quiet because we don't know where to start. You don't need a perfectly crafted message — just type 'Hi', or send a single word about how you feel right now.\n\nI'm here to listen. 👇",
                    'ti': f"👋 ሰላም <b>{name}</b>፡ ማዕጾ ኸፊጥካ ኣቲኻ ግን ስቕታ መሪጽካ።\n\nመብዛሕትኡ ግዜ ካበይ ከም እንጅምር ምስ ዝጠፍኣና ስቕ ንብል። እተስተኻኸለ ጽሑፍ ምድላው ኣየድልየካን እዩ — ሕጂ ዝስመዓካ ዘሎ ስምዒት ብሓደ ቃል፡ ወይ ድማ «ሰላም» ብምባል ጥራይ ጸሓፈለይ።\n\nኣነ ንዓኻ ንምስማዕ ኣብዚ ኣለኹ። 👇",
                    'om': f"👋 Akkam <b>{name}</b>, balbala banteet seente garuu cal'isuu filatte.\n\nYeroo baay'ee eessaa akka jalqabnu yeroo nutti bitaacha'u ni cal'isna. Barreeffama sirreeffame qopheessuun sirraa hin eegamu — miira amma sitti dhaga'amu jecha tokkoon, ykn «Akkam» jechuun qofa naaf barreessi.\n\nAni si dhaggeeffachuuf asan jira. 👇",
                }
                text = ice_texts.get(u_lang, ice_texts['am'])
                bot.send_message(uid, text, parse_mode="HTML")
                database.append_bot_message_to_history(uid, text)
                database.mark_nudge_sent(uid, "nudge_silent_sent")
                sent += 1
            except Exception:
                database.mark_user_blocked(uid, 1)
                failed += 1
            time.sleep(0.07)
        try:
            bot.send_message(message.chat.id, f"✅ <b>Icebreaker Complete!</b>\n✔️ {sent} sent\n❌ {failed} failed", parse_mode="HTML")
        except: pass
    
    threading.Thread(target=run_icebreaker, daemon=True).start()

# ══════════════════════════════════════════
#  /revive COMMAND — Nudge Trial Ended users
# ══════════════════════════════════════════
@bot.message_handler(commands=["revive"])
def cmd_revive(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!"); return
    
    ended = database.get_trial_ended_users()
    if not ended:
        bot.reply_to(message, "✅ No trial-ended users found.")
        return
    
    bot.reply_to(message, f"🔮 Sending cliffhanger revival to <b>{len(ended)}</b> users who exhausted their trial...", parse_mode="HTML")
    
    import threading, time
    def run_revive():
        sent, failed = 0, 0
        for u in ended:
            uid = u['user_id']
            name = u['first_name'] or 'there'
            u_lang = u.get('bot_language') or 'am'
            try:
                # Psychological cliffhanger hook
                revive_texts = {
                    'am': f"👋 ሰላም <b>{name}</b>፣ ያለፈውን ውይይታችንን መለስ ብዬ እያየሁት ነበር።\n\nስለተወያየንበት ጉዳይ አንድ ያልነገርኩዎት ትልቅ ነገር አለ። እስካሁን ያወራነው የችግሩን ገፅታ (Surface) ብቻ ነው፤ ዋናው ስር ያለው ግን ሌላ ቦታ ነው።\n\nውይይታችንን አቋርጠን መፍትሄውን ሳልነግርዎት በመቅረቴ ቅር ብሎኛል። መፍትሄውን ለማወቅ እና የጀመርነውን ለመጨረስ... 👇",
                    'en': f"👋 Hi <b>{name}</b>, I was looking back at our previous chat.\n\nThere's one major thing I haven't told you about what we discussed. So far, we only scratched the surface of the problem. The real root is somewhere else entirely.\n\nIt bothers me that we stopped before I could give you the actual solution. To find out the solution and finish what we started... 👇",
                    'ti': f"👋 ሰላም <b>{name}</b>፡ ነቲ ሕሉፍ ዕላልና ምልስ ኢለ እርእዮ ነይረ።\n\nብዛዕባ ዝተመያየጥናሉ ጉዳይ ሓደ ዘይነገርኩኻ ዓቢ ነገር ኣሎ። ክሳብ ሕጂ ዘውራዕናዮ ገጽታ ናይቲ ጸገም ጥራይ እዩ፣ እቲ ቀንዲ ሱር ግን ካልእ ቦታ እዩ ዘሎ።\n\nመፍትሒኡ ከይነገርኩኻ ዕላልና ብምቁራጹ ጓህዩኒ። መፍትሒኡ ንምፍላጥን ዝጀመርናዮ ንምውዳእን... 👇",
                    'om': f"👋 Akkam <b>{name}</b>, marii keenya darbe deebi'een ilaalaa ture.\n\nWaa'ee dhimma irratti mari'annee sana wanta guddaa tokko kanin sitti hin himin jira. Hanga ammaatti kan haasofne fuula rakkinichaa qofa; hundeen rakkinichaa garuu iddoo biraa jira.\n\nFurmaata isaa osoo sitti hin himin mariin keenya addaan cituun isaa na gaddisiiseera. Furmaata isaa beekuu fi waan jalqabne xumuruuf... 👇",
                }
                text = revive_texts.get(u_lang, revive_texts['am'])
                
                # Attach the Paywall / TopUp buttons directly to the message
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_starter'), callback_data="buy_advice_25"))
                markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_pro'), callback_data="buy_advice_75"))
                markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_heavy'), callback_data="buy_advice_225"))
                markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_unlimited'), callback_data="buy_advice_unlimited"))
                markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_unlimited_month'), callback_data="buy_advice_unlimited_month"))
                
                bot.send_message(uid, text, parse_mode="HTML", reply_markup=markup)
                database.append_bot_message_to_history(uid, text)
                database.mark_nudge_sent(uid, "nudge_revive_sent")
                sent += 1
            except Exception:
                database.mark_user_blocked(uid, 1)
                failed += 1
            time.sleep(0.07)
        try:
            bot.send_message(message.chat.id, f"✅ <b>Revival Complete!</b>\n✔️ {sent} sent\n❌ {failed} failed", parse_mode="HTML")
        except: pass
    
    threading.Thread(target=run_revive, daemon=True).start()

#  /bayacontrol COMMAND
# ══════════════════════════════════════════
@bot.message_handler(commands=["bayacontrol"])
def cmd_admin(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ የ Admin መብት የለዎትም!"); return
    show_admin_menu(message.chat.id, message.from_user)

def show_admin_menu(chat_id, user):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Dashboard", callback_data="adm_dashboard"),
        InlineKeyboardButton("🔍 User Lookup", callback_data="adm_search"),
    )
    markup.add(
        InlineKeyboardButton("📢 Custom Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("🤖 Auto Psych Broadcast", callback_data="adm_auto_broadcast_init"),
    )
    markup.add(
        InlineKeyboardButton("💳 Add Credit/Msgs", callback_data="admin_credit"),
        InlineKeyboardButton("👑 Sub-Admins", callback_data="adm_subadmin_menu"),
    )
    markup.add(
        InlineKeyboardButton("🚫 Ban/Unban", callback_data="adm_ban_menu"),
        InlineKeyboardButton("🔙 VIP Manager", callback_data="adm_vip_menu"),
    )
    
    total_users = database.get_total_user_count()
    bot.send_message(
        chat_id,
        f"👑 <b>Baya Books Admin Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"{'🛡️ Owner' if is_owner(user) else '👮 Sub-Admin'}\n\n"
        f"Select an action:",
        parse_mode="HTML", reply_markup=markup,
    )

def enforce_preview_quota(uid, chat_id, call_id=None):
    if uid == get_admin_id():
        return True
    previews_left, timer_start = database.get_preview_quota(uid)
    if previews_left > 0:
        return True
        
    if call_id:
        bot.answer_callback_query(call_id, "🚫 የነጻ ምርመራ ኮታዎ አልቋል!", show_alert=True)
        
    from datetime import datetime, timedelta
    try:
        start_dt = datetime.fromisoformat(timer_start)
    except:
        start_dt = datetime.now() - timedelta(hours=24)
        
    time_left = (start_dt + timedelta(hours=24)) - datetime.now()
    if time_left.total_seconds() < 0:
        time_left = timedelta(seconds=0)
        
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💳 100 ብር - 5 ነጻ ምርመራ ይግዙ", callback_data="buy_previews"),
        InlineKeyboardButton("📖 የጀመሩትን መመሪያ ይግዙ", callback_data="show_drafts")
    )
    
    bot.send_message(
        chat_id,
        f"🚫 <b>የነጻ ምርመራ ኮታዎ አልቋል! (5/5)</b>\n\n"
        f"⏳ በድጋሚ 5 ነጻ ምርመራ ለማግኘት: <b>{hours} ሰዓት ከ {minutes} ደቂቃ</b> ይጠብቁ።\n\n"
        f"<b>ወይም አሁኑኑ ይክፈቱ፡</b>\n"
        f"1️⃣ 100 ብር በመክፈል 5 ተጨማሪ ምርመራዎችን ያግኙ\n"
        f"2️⃣ <b>የጀመሩትን ሙሉ መመሪያ ይግዙ!</b>\n(ሙሉውን ሲገዙ ተጨማሪ 5 ምርመራ በቦነስ ያገኛሉ!)\n",
        parse_mode="HTML", reply_markup=markup
    )
    return False

# ══════════════════════════════════════════
#  CALLBACK HANDLER (The Brain)
# ══════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    uid = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id

    # Ban check
    if database.is_banned(uid):
        bot.answer_callback_query(call.id, S(get_lang(uid), 'banned'), show_alert=True)
        return

    # ── Channel Join Check ───────────────────

    if data.startswith("setlang_"):
        lang_code = data.split("_")[1]
        database.set_bot_language(uid, lang_code)
        bot.answer_callback_query(call.id, S(lang_code, 'lang_changed'))
        safe_delete_message(chat_id, call.message.message_id)
        # Check if this is during onboarding or a language change
        age_verified, gender = database.get_onboarding_status(uid)
        if not age_verified or not gender:
            # During onboarding
            check_onboarding(chat_id, uid, call.from_user.first_name)
        else:
            # Language change - refresh menu and re-send last AI message in new language
            send_welcome(chat_id, call.from_user.first_name, lang_code)
        return

    if data == "check_joined":
        lang = get_lang(uid)
        if check_channel_member(uid):
            bot.answer_callback_query(call.id, S(lang, 'joined_success'))
            safe_delete_message(chat_id, call.message.message_id)
            if check_onboarding(chat_id, uid, call.from_user.first_name):
                send_welcome(chat_id, call.from_user.first_name, lang)
        else:
            bot.answer_callback_query(call.id, S(lang, 'joined_fail'), show_alert=True)
        return

    # ── Onboarding ───────────────────────────
    if data == "onboard_age_18":
        # Legacy: just set age and re-show gender step
        database.set_user_age_verified(uid)
        lang = get_lang(uid)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(S(lang, 'gender_male'), callback_data="onboard_gen_m"),
            InlineKeyboardButton(S(lang, 'gender_female'), callback_data="onboard_gen_f")
        )
        prompt = S(lang, 'onboard_age_gender_prompt')
        bot.edit_message_text(prompt, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        return
        
    if data.startswith("onboard_gen_"):
        gender = "male" if data == "onboard_gen_m" else "female"
        # Set both age AND gender in one tap (frictionless combined step)
        database.set_user_age_verified(uid)
        database.set_user_gender(uid, gender)
        bot.delete_message(chat_id, call.message.message_id)
        send_welcome(chat_id, call.from_user.first_name, get_lang(uid))
        return

    # ── Re-download PDF ──────────────────────
    if data.startswith("redownload_"):
        order_id = int(data.replace("redownload_", ""))
        order = database.get_order(order_id)
        if order and order["pdf_file_id"] and order["user_id"] == uid:
            bot.answer_callback_query(call.id)
            bot.send_document(chat_id, order["pdf_file_id"])
        else:
            bot.answer_callback_query(call.id, "❌ ፋይሉ አልተገኘም!", show_alert=True)
        return

    # ── Legacy/Deprecated Callbacks ────────
    legacy_prefixes = ['buy_draft_', 'cat_', 'sub_', 'pick_', 'age_', 'liv_', 'loc_', 'lang_', 'gen_']
    legacy_exact = ['has_book', 'get_advice', 'choose_for_me', 'show_drafts', 'buy_previews', 'confirm_book', 'retry_book', 'buy_now', 'pay_single', 'use_credit']
    is_legacy = data in legacy_exact
    for prefix in legacy_prefixes:
        if data.startswith(prefix) and not data.startswith('onboard_gen_'):
            is_legacy = True
            break
    if is_legacy:
        lang = get_lang(uid)
        bot.answer_callback_query(call.id, S(lang, 'legacy_redirect'), show_alert=True)
        clear_state(uid)
        if check_onboarding(chat_id, uid, call.from_user.first_name):
            send_welcome(chat_id, call.from_user.first_name, lang)
        return

    if data == "claim_referrals":
        lang = get_lang(uid)
        count = database.get_uncredited_referral_count(uid)
        if count >= 10:
            database.mark_n_referrals_credited(uid, n=count)
            database.add_advice_messages(uid, count)
            bot.answer_callback_query(call.id, S(lang, 'claim_success', count=count), show_alert=True)
            bot.delete_message(chat_id, call.message.message_id)
            send_welcome(chat_id, call.from_user.first_name, lang)
        else:
            bot.answer_callback_query(call.id, S(lang, 'claim_fail'), show_alert=True)
        return
    if data == "confirm_reset":
        lang = get_lang(uid)
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(S(lang, 'reset_yes'), callback_data="reset_account"),
            InlineKeyboardButton(S(lang, 'reset_no'), callback_data="cancel_reset")
        )
        bot.edit_message_text(
            S(lang, 'reset_confirm'),
            chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup
        )
        return

    if data == "cancel_reset":
        bot.edit_message_text(S(get_lang(uid), 'reset_cancelled'), chat_id, call.message.message_id)
        return

    if data == "show_topup":
        bot.answer_callback_query(call.id)
        cmd_topup(call.message)
        return

    if data.startswith("buy_advice_"):
        lang = get_lang(uid)
        pkg = data.replace("buy_advice_", "")
        if pkg == "unlimited":
            amount = 1800
        elif pkg == "unlimited_month":
            amount = 4900
        else:
            msgs = int(pkg)
            amount = {25: 200, 75: 400, 225: 1200}.get(msgs, 200)
            
        bot.answer_callback_query(call.id, S(lang, 'payment_preparing'))
        purpose = f"ADVICE_{pkg}"
        checkout_url, tx_ref, err = chapa.generate_chapa_link(amount, uid, purpose)
        if not checkout_url:
            bot.send_message(chat_id, S(lang, 'payment_error', err=err), parse_mode="HTML")
            return
            
        # Log the intent (Abandoned Cart tracking)
        database.record_payment(uid, None, amount, tx_ref, 'PENDING_CHECKOUT', status='pending')
            
        markup = InlineKeyboardMarkup()
        from telebot.types import WebAppInfo
        markup.add(InlineKeyboardButton(S(lang, 'btn_pay_now'), web_app=WebAppInfo(url=checkout_url)))
        
        bot.send_message(
            chat_id,
            S(lang, 'payment_title') + "\n━━━━━━━━━━━━━━━━━━━━\n\n" +
            S(lang, 'payment_instructions', amount=amount),
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    if data == "reset_account":
        database.reset_user_onboarding(uid)
        clear_state(uid)
        bot.answer_callback_query(call.id, S(get_lang(uid), 'reset_done'), show_alert=True)
        
        # Start a thread to wipe the last 500 bot messages for a clean visual slate
        def wipe_chat_history(chat, start_msg_id):
            import time
            consecutive_failures = 0
            for i in range(start_msg_id, max(0, start_msg_id - 500), -1):
                try:
                    bot.delete_message(chat, i)
                    consecutive_failures = 0
                except Exception:
                    consecutive_failures += 1
                    if consecutive_failures > 20:
                        break
                time.sleep(0.02)
        threading.Thread(target=wipe_chat_history, args=(chat_id, call.message.message_id), daemon=True).start()
        
        # Check onboarding again, which will prompt the 18+ age question
        check_onboarding(chat_id, uid, call.from_user.first_name)
        return

    if data.startswith("tip_"):
        lang = get_lang(uid)
        amount = int(data.split("_")[1])
        bot.answer_callback_query(call.id, S(lang, 'payment_preparing'))
        
        checkout_url, tx_ref, err = chapa.generate_chapa_link(amount, uid, "TIP")
        if not checkout_url:
            bot.send_message(chat_id, S(lang, 'payment_error', err=err), parse_mode="HTML")
            return
            
        markup = InlineKeyboardMarkup()
        from telebot.types import WebAppInfo
        markup.add(InlineKeyboardButton(S(lang, 'tip_pay_btn', amount=amount), web_app=WebAppInfo(url=checkout_url)))
        
        bot.send_message(
            chat_id,
            S(lang, 'tip_payment_text', amount=amount),
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    # ══════════════════════════════════════════
    #  ADMIN DASHBOARD CALLBACKS
    # ══════════════════════════════════════════
    
    if data == "adm_dashboard":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "📊 Loading...")
        stats = database.get_analytics()
        stages = database.get_user_stage_stats()
        total = stats["male_count"] + stats["female_count"]
        m_pct = f"{stats['male_count']/total*100:.0f}%" if total > 0 else "0%"
        f_pct = f"{stats['female_count']/total*100:.0f}%" if total > 0 else "0%"

        # Recent payments summary
        recent_pay_text = ""
        for p in stats.get("recent_payments", [])[:5]:
            ptype = {"Tip": "☕", "Advice": "🧠", "Other": "📦"}.get(p.get("type", ""), "📦")
            recent_pay_text += f"  {ptype} {p['name']} — <b>{p['amount']:,} ብር</b> ({p['date'][:10] if p['date'] else 'N/A'})\n"
        if not recent_pay_text:
            recent_pay_text = "  — No payments yet\n"

        markup = InlineKeyboardMarkup()
        
        # Add Auto-Nudge Toggle
        auto_nudge_status = database.get_setting("auto_nudge", "OFF")
        nudge_btn_text = "🤖 Auto-Nudge: ON 🟢" if auto_nudge_status == "ON" else "🤖 Auto-Nudge: OFF 🔴"
        markup.add(InlineKeyboardButton(nudge_btn_text, callback_data="toggle_auto_nudge"))
        
        markup.add(InlineKeyboardButton("🔄 Refresh", callback_data="adm_dashboard"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        bot.send_message(chat_id,
            f"📊 <b>DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Active Users: <b>{stats['total_users']}</b>\n"
            f"🚫 Left/Blocked: <b>{stats.get('blocked_users', 0)}</b>\n"
            f"🟢 New Today: <b>{stats['new_today']}</b> | This Week: <b>{stats.get('new_this_week', 0)}</b>\n"
            f"💬 Chatting Users: <b>{stats.get('active_advice_users', 0)}</b>\n\n"
            f"━━ 🔽 User Funnel ━━━━━━━━━━━\n"
            f"  🚧 Stuck in onboarding: <b>{stages['stuck_onboarding']}</b>\n"
            f"  😶 Onboarded, never chatted: <b>{stages['onboarded_no_chat']}</b>\n"
            f"  💬 In free trial: <b>{stages['in_trial']}</b>\n"
            f"  ⏰ Trial ended (not paid): <b>{stages['trial_ended']}</b>\n"
            f"  💳 Paid users: <b>{stages['paid_users']}</b>\n"
            f"  👑 VIP active: <b>{stages['vip_users']}</b>\n\n"
            f"━━ 💰 Revenue ━━━━━━━━━━━━\n"
            f"  📅 Today: <b>{stats['today_revenue']:,} ETB</b>\n"
            f"  📆 Weekly: <b>{stats['weekly_revenue']:,} ETB</b>\n"
            f"  📅 Monthly: <b>{stats.get('monthly_revenue', 0):,} ETB</b>\n"
            f"  💵 All-Time: <b>{stats['total_revenue']:,} ETB</b>\n"
            f"  🧾 Transactions: <b>{stats.get('total_transactions', 0)}</b>\n\n"
            f"━━ 👥 Gender ━━━━━━━━━━━━━━\n"
            f"  👨 Male: {m_pct} | 👩 Female: {f_pct}\n\n"
            f"━━ 💳 Recent Payments ━━━━━━\n{recent_pay_text}",
            parse_mode="HTML", reply_markup=markup,
        )
        return
    if data == "toggle_auto_nudge":
        if not is_admin(call.from_user): return
        current = database.get_setting("auto_nudge", "OFF")
        new_val = "OFF" if current == "ON" else "ON"
        database.set_setting("auto_nudge", new_val)
        bot.answer_callback_query(call.id, f"Auto-Nudge turned {new_val}")
        
        # Simulate clicking the dashboard button to refresh it
        call.data = "adm_dashboard"
        safe_delete_message(chat_id, call.message.message_id)
        return handle_callback(call)

    if data.startswith("adm_reply_"):
        if not is_admin(call.from_user): return
        target_uid = data.split("_")[2]
        set_state(uid, f"ADMIN_REPLY_{target_uid}")
        bot.send_message(chat_id, f"📝 <b>Reply to User {target_uid}</b>\n\nType your message below (/cancel to abort):", parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if data.startswith("adm_view_user_"):
        if not is_admin(call.from_user): return
        target_uid = int(data.split("_")[3])
        # Redirect to the full profile view
        call.data = f"adm_lookup_{target_uid}"
        data = call.data
        # Fall through to adm_lookup_ handler below

    if data.startswith("adm_record_pay_"):
        if not is_admin(call.from_user): return
        target_uid = int(data.split("_")[3])
        set_state(uid, f"ADMIN_RECORD_PAY_{target_uid}")
        bot.send_message(chat_id, f"💵 <b>Record Manual Payment</b>\n\nEnter the amount paid by user <code>{target_uid}</code> in ETB:\n\n<i>(Type /cancel to abort)</i>", parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if data.startswith("adm_add_msgs_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        amount = int(parts[4])
        database.add_advice_messages(target_uid, amount)
        bot.answer_callback_query(call.id, f"Added {amount} messages to {target_uid}", show_alert=True)
        bot.send_message(target_uid, S(get_lang(target_uid), 'gift_notification', amount=amount), parse_mode="HTML")
        return

    if data.startswith("adm_make_vip_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        days = int(parts[4])
        from datetime import datetime, timedelta
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        conn = database.get_connection(); c = conn.cursor()
        c.execute("UPDATE users SET vip_expiry = ? WHERE user_id = ?", (expiry, target_uid))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, f"Made VIP for {days} days", show_alert=True)
        bot.send_message(target_uid, f"🎉 <b>እንኳን ደስ አለዎት!</b>\nለ {days} ቀናት VIP ሆነዋል!", parse_mode="HTML")
        return

    if data.startswith("adm_ban_"):
        if not is_admin(call.from_user): return
        target_uid = int(data.split("_")[2])
        conn = database.get_connection(); c = conn.cursor()
        c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (target_uid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, f"User {target_uid} banned", show_alert=True)
        return

    if data.startswith("adm_unban_"):
        if not is_admin(call.from_user): return
        target_uid = int(data.split("_")[2])
        conn = database.get_connection(); c = conn.cursor()
        c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (target_uid,))
        conn.commit(); conn.close()
        bot.answer_callback_query(call.id, f"User {target_uid} unbanned", show_alert=True)
        return

    if data == "adm_back":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        show_admin_menu(chat_id, call.from_user)
        return
    
    # ── Admin: User Search ────────────────────
    if data == "adm_search":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_SEARCH_USER")
        bot.send_message(chat_id, "🔍 <b>User Lookup</b>\n\nEnter User ID, @username, or name:\n(/cancel to exit)", parse_mode="HTML")
        return
    
    # ── Admin: User Lookup (from inline button) ─
    if data.startswith("adm_lookup_"):
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_lookup_", ""))
        bot.answer_callback_query(call.id, "🔍 Loading...")
        details = database.get_user_details(target_id)
        if not details:
            bot.send_message(chat_id, "❌ User not found.")
            return
        u = details["user"]
        banned_tag = " 🚫 BANNED" if database.is_banned(target_id) else ""
        admin_tag = " 👑" if database.is_sub_admin(target_id) else ""
        vip_tag = " 💎 VIP" if database.is_vip(target_id) else ""
        
        # Gender display
        gender_str = {"male": "👨 Male", "female": "👩 Female"}.get(u.get('gender'), '❓ Unknown')
        
        # VIP expiry
        vip_expiry = u.get('vip_expiry') or 'N/A'
        if vip_expiry != 'N/A':
            vip_expiry = vip_expiry[:10]
        
        # Advice messages
        msgs_left = u.get('advice_messages_left', 0)
        
        # Recent payments text
        payments_text = ""
        for p in details.get("recent_payments", []):
            tx = p['tx_ref'] or ''
            ptype = '☕ Tip' if 'TIP' in tx else '🧠 Advice' if 'ADVICE' in tx else '📦 Other'
            payments_text += f"  {ptype} — <b>{p['amount']:,} ETB</b> ({p['payment_date'][:10] if p['payment_date'] else 'N/A'})\n"
        if not payments_text:
            payments_text = "  — No payments yet\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("↩️ Reply", callback_data=f"adm_reply_{target_id}"),
            InlineKeyboardButton("💵 Add Payment", callback_data=f"adm_record_pay_{target_id}")
        )
        markup.add(
            InlineKeyboardButton("🎁 +5 Msgs", callback_data=f"adm_add_msgs_{target_id}_5"),
            InlineKeyboardButton("🎁 +10 Msgs", callback_data=f"adm_add_msgs_{target_id}_10")
        )
        markup.add(
            InlineKeyboardButton("🎁 +25 Msgs", callback_data=f"adm_add_msgs_{target_id}_25"),
            InlineKeyboardButton("🎁 +75 Msgs", callback_data=f"adm_add_msgs_{target_id}_75")
        )
        markup.add(
            InlineKeyboardButton("👑 VIP 7d", callback_data=f"adm_make_vip_{target_id}_7"),
            InlineKeyboardButton("👑 VIP 30d", callback_data=f"adm_make_vip_{target_id}_30")
        )
        if database.is_banned(target_id):
            markup.add(InlineKeyboardButton("✅ Unban", callback_data=f"adm_unban_{target_id}"))
        else:
            markup.add(InlineKeyboardButton("🚫 Ban", callback_data=f"adm_ban_{target_id}"))
        if is_owner(call.from_user):
            if database.is_sub_admin(target_id):
                markup.add(InlineKeyboardButton("👮 Remove Sub-Admin", callback_data=f"adm_rmsub_{target_id}"))
            else:
                markup.add(InlineKeyboardButton("👮 Make Sub-Admin", callback_data=f"adm_mksub_{target_id}"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        bot.send_message(chat_id,
            f"👤 <b>User Profile</b>{banned_tag}{admin_tag}{vip_tag}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 ID: <code>{target_id}</code>\n"
            f"👤 Name: <b>{u['first_name']}</b>\n"
            f"📛 Username: @{u.get('username') or 'N/A'}\n"
            f"{gender_str} | 🌐 {u.get('bot_language', 'am').upper()}\n"
            f"📅 Joined: {u['joined_date'][:10] if u.get('joined_date') else 'N/A'}\n\n"
            f"━━ 💬 Advice ━━━━━━━━━━━━━━\n"
            f"  📩 Messages Left: <b>{msgs_left}</b>\n"
            f"  💎 VIP Until: <b>{vip_expiry}</b>\n\n"
            f"━━ 💰 Payments ━━━━━━━━━━━━\n"
            f"  💵 Total Paid: <b>{details['total_paid']:,} ETB</b> ({details['payment_count']} transactions)\n"
            f"  👥 Referrals: <b>{details['referral_count']}</b>\n\n"
            f"━━ 💳 Recent Payments ━━━━━━\n{payments_text}",
            parse_mode="HTML", reply_markup=markup,
        )
        return
    
    # ── Admin: Quick Credit from profile ──────
    if data.startswith("adm_credit_"):
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_credit_", ""))
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_CREDIT_AMOUNT", target_id=target_id)
        bot.send_message(chat_id, f"💳 How many credits to add for user <code>{target_id}</code>?\n(/cancel to exit)", parse_mode="HTML")
        return
    
    # ── Admin: Ban User ──────────────────────
    if data.startswith("adm_ban_") and data != "adm_ban_menu":
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_ban_", ""))
        database.ban_user(target_id)
        bot.answer_callback_query(call.id, "🚫 User banned!")
        bot.send_message(chat_id, f"🚫 User <code>{target_id}</code> has been <b>BANNED</b>.", parse_mode="HTML")
        try:
            bot.send_message(target_id, S(get_lang(target_id), 'banned'))
        except: pass
        return
    
    # ── Admin: Unban User ────────────────────
    if data.startswith("adm_unban_"):
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_unban_", ""))
        database.unban_user(target_id)
        bot.answer_callback_query(call.id, "✅ User unbanned!")
        bot.send_message(chat_id, f"✅ User <code>{target_id}</code> has been <b>UNBANNED</b>.", parse_mode="HTML")
        try:
            bot.send_message(target_id, "✅ አካውንትዎ ተከፍቷል! /start ይጫኑ ለመጀመር።")
        except: pass
        return
    
    # ── Admin: Ban Menu ──────────────────────
    if data == "adm_ban_menu":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        banned = database.get_banned_users()
        text = "🚫 <b>Ban Manager</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        if banned:
            text += "<b>Currently Banned:</b>\n"
            for b in banned:
                text += f"  🚫 {b['first_name']} (@{b['username'] or 'N/A'}) — <code>{b['user_id']}</code>\n"
            text += "\n"
        else:
            text += "No banned users.\n\n"
        text += "To ban: Enter User ID below\nTo unban: Click the user above"
        
        markup = InlineKeyboardMarkup()
        for b in (banned or []):
            markup.add(InlineKeyboardButton(f"✅ Unban {b['first_name']}", callback_data=f"adm_unban_{b['user_id']}"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        set_state(uid, "ADMIN_BAN_USER")
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return
    
    # ── Admin: Sub-Admin Menu ────────────────
    if data == "adm_subadmin_menu":
        if not is_owner(call.from_user):
            bot.answer_callback_query(call.id, "❌ Only the owner can manage sub-admins.", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        subs = database.get_all_sub_admins()
        text = "👑 <b>Sub-Admin Manager</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        if subs:
            text += "<b>Current Sub-Admins:</b>\n"
            for s in subs:
                text += f"  👮 {s['first_name']} (@{s['username'] or 'N/A'}) — <code>{s['user_id']}</code>\n"
            text += "\n"
        else:
            text += "No sub-admins yet.\n\n"
        text += "Enter a User ID to add as sub-admin:\n(/cancel to exit)"
        
        markup = InlineKeyboardMarkup()
        for s in (subs or []):
            markup.add(InlineKeyboardButton(f"❌ Remove {s['first_name']}", callback_data=f"adm_rmsub_{s['user_id']}"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        set_state(uid, "ADMIN_ADD_SUBADMIN")
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return
    
    # ── Admin: Make Sub-Admin ────────────────
    if data.startswith("adm_mksub_"):
        if not is_owner(call.from_user):
            bot.answer_callback_query(call.id, "❌ Only the owner.", show_alert=True)
            return
        target_id = int(data.replace("adm_mksub_", ""))
        database.add_sub_admin(target_id)
        bot.answer_callback_query(call.id, "👮 Sub-Admin added!")
        bot.send_message(chat_id, f"👮 User <code>{target_id}</code> is now a <b>Sub-Admin</b>.", parse_mode="HTML")
        try:
            bot.send_message(target_id, "👑 <b>Congratulations!</b>\n\nYou have been granted Sub-Admin privileges!\nType /bayacontrol to access the admin panel.", parse_mode="HTML")
        except: pass
        return
    
    # ── Admin: Remove Sub-Admin ──────────────
    if data.startswith("adm_rmsub_"):
        if not is_owner(call.from_user):
            bot.answer_callback_query(call.id, "❌ Only the owner.", show_alert=True)
            return
        target_id = int(data.replace("adm_rmsub_", ""))
        database.remove_sub_admin(target_id)
        bot.answer_callback_query(call.id, "✅ Sub-Admin removed.")
        bot.send_message(chat_id, f"✅ User <code>{target_id}</code> is no longer a Sub-Admin.", parse_mode="HTML")
        return
    
    

    # ── Admin: VIP Manager ───────────────────
    if data == "adm_vip_menu":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_VIP_USER")
        bot.send_message(chat_id, "👑 <b>VIP Manager</b>\n\nEnter User ID to grant VIP:\n(/cancel to exit)", parse_mode="HTML")
        return

    # ── Admin: Auto Psych Broadcast ──────────
    if data in ["adm_auto_broadcast_init", "adm_auto_refresh"]:
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "🧠 Generating profound message...", show_alert=False)
        bot.send_chat_action(chat_id, 'typing')
        psych_text = ai_engine.generate_psych_broadcast()
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Verify & Broadcast", callback_data="adm_confirm_auto_broadcast"))
        markup.add(InlineKeyboardButton("🔄 Refresh (Generate New)", callback_data="adm_auto_refresh"))
        markup.add(InlineKeyboardButton("🔙 Cancel", callback_data="adm_back"))
        
        msg = f"💡 <b>Auto Psychology Broadcast Preview</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{psych_text}\n\n<i>(This is what users will see. Verify or refresh.)</i>"
        
        if data == "adm_auto_refresh":
            bot.edit_message_text(msg, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=markup)
        return

    if data == "adm_confirm_auto_broadcast":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "✅ Broadcasting...", show_alert=False)
        
        # Extract the actual text generated
        original = call.message.text
        # Remove the headers and footers
        try:
            parts = original.split("━━━━━━━━━━━━━━━━━━━━\n\n")
            if len(parts) > 1:
                content = parts[1].split("\n\n(This is what")[0].strip()
            else:
                content = original
        except:
            content = original

        # Create broadcast thread
        all_users = database.get_all_user_ids()
        
        # Post to Telegram channel
        try:
            channel_msg = f"✨ <b>የዕለቱ የስነ-ልቦና መልዕክት</b>\n\n{content}\n\n👇\nhttps://t.me/bayabooks_bot"
            bot.send_message("@BAYABOOKS1", channel_msg, parse_mode="HTML")
        except Exception as e:
            import logging
            logging.error(f"Failed to post to channel: {e}")

        # Post to Facebook Page (if configured)
        try:
            import os
            fb_token = os.environ.get("FB_PAGE_ACCESS_TOKEN")
            fb_page_id = os.environ.get("FB_PAGE_ID")
            
            if fb_token and fb_page_id:
                import requests
                import re
                # Facebook uses plain text, so strip HTML tags
                clean_content = re.sub('<[^<]+>', '', content)
                fb_msg = f"✨ የዕለቱ የስነ-ልቦና መልዕክት\n\n{clean_content}\n\n👇\nhttps://t.me/bayabooks_bot"
                
                fb_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
                payload = {
                    "message": fb_msg,
                    "access_token": fb_token
                }
                res = requests.post(fb_url, data=payload, timeout=10)
                if res.status_code != 200:
                    bot.send_message(chat_id, f"⚠️ <b>Facebook Post Failed:</b>\n<code>{res.text}</code>", parse_mode="HTML")
                else:
                    bot.send_message(chat_id, "✅ Successfully posted to Facebook Page!")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ <b>Facebook Error:</b> {str(e)}")
            import logging
            logging.error(f"Failed to post to Facebook: {e}")

        def background_broadcast():
            import time
            success = 0
            failed = 0
            for u in all_users:
                try:
                    bot.send_message(u, f"✨ <b>የዕለቱ የስነ-ልቦና መልዕክት</b>\n\n{content}", parse_mode="HTML")
                    # Refresh keyboard for this user
                    try:
                        u_lang = database.get_bot_language(u) or 'am'
                        bot.send_message(u, "​", reply_markup=get_bottom_markup(u_lang, u))
                        # Append the broadcast to the user's AI history so the AI has context!
                        database.append_bot_message_to_history(u, content)
                    except Exception:
                        pass
                    database.mark_user_blocked(u, 0)
                    success += 1
                except Exception as e:
                    database.mark_user_blocked(u, 1)
                    failed += 1
                time.sleep(0.07)
            try: bot.send_message(chat_id, f"✅ <b>Auto-Broadcast Complete!</b>\n✔️ {success} Delivered\n❌ {failed} Failed (Marked as Blocked/Left)", parse_mode="HTML")
            except: pass
            
        threading.Thread(target=background_broadcast, daemon=True).start()
        bot.edit_message_text(f"🚀 <b>Broadcast Started!</b>\nSending to {len(all_users)} users in the background...\n\nMessage:\n{content}", chat_id, call.message.message_id, parse_mode="HTML")
        return

    # ── Admin: Broadcast ─────────────────────
    if data == "admin_broadcast":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_BROADCAST")
        bot.send_message(chat_id, "📢 <b>Broadcast</b>\n\nመልዕክቱን ይፃፉ (/cancel ለመሰረዝ):", parse_mode="HTML")
        return

    # ── Admin: Credit Top-Up ─────────────────
    if data == "admin_credit":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_CREDIT_USER")
        bot.send_message(chat_id, "💳 <b>ክሬዲት ጨምር</b>\n\nየደንበኛውን User ID ያስገቡ:", parse_mode="HTML")
        return

    


def show_tip_cta(chat_id, uid):
    """Show tip/donation options to the user."""
    lang = get_lang(uid)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(S(lang, 'tip_pay_btn', amount=500), callback_data="tip_500"),
               InlineKeyboardButton(S(lang, 'tip_pay_btn', amount=1000), callback_data="tip_1000"))
    markup.add(InlineKeyboardButton(S(lang, 'tip_pay_btn', amount=5000), callback_data="tip_5000"),
               InlineKeyboardButton(S(lang, 'tip_pay_btn', amount=10000), callback_data="tip_10000"))
    bot.send_message(
        chat_id,
        S(lang, 'tip_title') + "\n━━━━━━━━━━━━━━━━━━━━\n\n" +
        S(lang, 'tip_body'),
        parse_mode="HTML", reply_markup=markup,
    )

# ══════════════════════════════════════════
#  INTERVIEW FLOW HELPERS
# ══════════════════════════════════════════
def ask_gender(chat_id, book_title):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("👨 ወንድ", callback_data="gen_m"),
        InlineKeyboardButton("👩 ሴት", callback_data="gen_f"),
    )
    bot.send_message(
        chat_id,
        f"✨ <b>ድንቅ ምርጫ!</b>\n\n"
        f"📖 <i>{html.escape(book_title)}</i>\n\n"
        f"ለእርስዎ ብቻ የተዘጋጀ መመሪያ ለመስራት "
        f"ጥቂት ጥያቄዎች ልጠይቅዎ።\n\n"
        f"👤 <b>ጾታዎ?</b>",
        parse_mode="HTML", reply_markup=markup,
    )

def ask_age(chat_id):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(f"{emoji} {label}", callback_data=aid) for aid, emoji, label in AGE_RANGES]
    markup.add(*buttons)
    bot.send_message(
        chat_id, 
        "🎂 <b>የዕድሜ ክልልዎን ይምረጡ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━", 
        parse_mode="HTML", reply_markup=markup
    )

def ask_location(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇪🇹 ኢትዮጵያ ውስጥ", callback_data="loc_ethiopia"),
        InlineKeyboardButton("🌍 ከኢትዮጵያ ውጪ", callback_data="loc_abroad")
    )
    bot.send_message(
        chat_id,
        "📍 <b>የት ነው የሚኖሩት?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML", reply_markup=markup
    )

def ask_living_situation(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👤 ብቻዬን", callback_data="liv_alone"),
        InlineKeyboardButton("👨‍👩‍👧‍👦 ከቤተሰብ ጋር", callback_data="liv_family")
    )
    bot.send_message(
        chat_id,
        "🏠 <b>የአኗኗር ሁኔታዎ ምን ይመስላል?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML", reply_markup=markup
    )

def ask_specific_change(chat_id):
    bot.send_message(
        chat_id,
        "✍️ <b>በመጨረሻም...</b>\n\n"
        "አንድ ማግኘት፣ መቀየር ወይም ማስወገድ የሚፈልጉት ነገር ምንድን ነው?\n\n"
        "<i>(እባክዎ በአጭሩ ይፃፉልን)</i>",
        parse_mode="HTML"
    )

def ask_language(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )
    markup.add(
        InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data="lang_or"),
        InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data="lang_ti"),
    )
    bot.send_message(chat_id, "🌍 <b>PDF ቅጂዎን በየትኛው ቋንቋ ይፈልጋሉ?</b>", parse_mode="HTML", reply_markup=markup)

# ══════════════════════════════════════════
#  PREVIEW & PDF GENERATION
# ══════════════════════════════════════════
# ══════════════════════════════════════════
#  PAYMENT HANDLING
# ══════════════════════════════════════════
# ══════════════════════════════════════════
#  TEXT & PHOTO MESSAGE HANDLER
# ══════════════════════════════════════════
@bot.message_handler(content_types=["text", "photo", "document"])
def handle_messages(message):
    uid = message.from_user.id
    session = get_session(uid)
    state = session["state"]
    chat_id = message.chat.id

    # Ban check
    if database.is_banned(uid):
        bot.reply_to(message, S(get_lang(uid), 'banned'))
        return

    # ── Admin States ─────────────────────────
    # ── Admin: Search User (text input) ──────
    if state == "ADMIN_SEARCH_USER" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        results = database.search_users(message.text.strip())
        if not results:
            bot.send_message(chat_id, "❌ No users found. Try again or /cancel")
            return
        text = f"🔍 <b>Search Results ({len(results)})</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        markup = InlineKeyboardMarkup(row_width=1)
        for u in results:
            text += f"👤 {u['first_name']} (@{u['username'] or 'N/A'}) — <code>{u['user_id']}</code>\n"
            markup.add(InlineKeyboardButton(f"👤 {u['first_name']} ({u['user_id']})", callback_data=f"adm_lookup_{u['user_id']}"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        clear_state(uid)
        return
    
    # ── Admin: Record Manual Payment ─────────
    if str(state).startswith("ADMIN_RECORD_PAY_") and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        target_uid = int(state.split("_")[3])
        try:
            amount = float(message.text.strip())
            if amount <= 0:
                raise ValueError
            import uuid
            tx_ref = f"MANUAL_ADVICE_{uuid.uuid4().hex[:8]}"
            database.record_payment(
                user_id=target_uid,
                order_id=None,
                amount=amount,
                tx_ref=tx_ref,
                receipt_file_id="MANUAL_ADMIN",
                status="approved"
            )
            bot.send_message(chat_id, f"✅ Successfully recorded <b>{amount:,.0f} ETB</b> for user <code>{target_uid}</code>.\n\n⚠️ <i>Remember to give them their messages or VIP package using the buttons on their profile!</i>", parse_mode="HTML")
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ Please enter a valid positive number for the amount (e.g. 400).")
        return

    # ── Admin: Ban User (text input) ─────────
    if state == "ADMIN_BAN_USER" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        try:
            target_id = int(message.text.strip())
            target = database.get_user(target_id)
            if not target:
                bot.send_message(chat_id, "❌ User not found!"); return
            database.ban_user(target_id)
            bot.send_message(chat_id, f"🚫 <b>{target['first_name']}</b> (<code>{target_id}</code>) has been <b>BANNED</b>.", parse_mode="HTML")
            try:
                bot.send_message(target_id, S(get_lang(target_id), 'banned'))
            except: pass
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ Please enter a valid User ID number.")
        return
    
    # ── Admin: Add Sub-Admin (text input) ────
    if state == "ADMIN_ADD_SUBADMIN" and is_owner(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        try:
            target_id = int(message.text.strip())
            target = database.get_user(target_id)
            if not target:
                bot.send_message(chat_id, "❌ User not found!"); return
            database.add_sub_admin(target_id)
            bot.send_message(chat_id, f"👮 <b>{target['first_name']}</b> (<code>{target_id}</code>) is now a <b>Sub-Admin</b>.", parse_mode="HTML")
            try:
                bot.send_message(target_id, "👑 <b>Congratulations!</b>\n\nYou have been granted Sub-Admin privileges!\nType /bayacontrol to access the admin panel.", parse_mode="HTML")
            except: pass
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ Please enter a valid User ID number.")
        return
    
    # ── Admin: VIP Grant (text input) ────────
    if state == "ADMIN_VIP_USER" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        try:
            target_id = int(message.text.strip())
            target = database.get_user(target_id)
            if not target:
                bot.send_message(chat_id, "❌ User not found!"); return
            database.set_vip(target_id, days=30)
            bot.send_message(chat_id, f"👑 <b>{target['first_name']}</b> (<code>{target_id}</code>) is now <b>VIP for 30 days</b>.", parse_mode="HTML")
            try:
                bot.send_message(target_id, "👑 <b>VIP Status Activated!</b>\n\nYou now have unlimited free protocols for 30 days!", parse_mode="HTML")
            except: pass
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ Please enter a valid User ID number.")
        return

    if state == "FEEDBACK":
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        lang = get_lang(uid)
        user_info = message.from_user
        admin_id = get_admin_id()
        feedback_text = message.text or ""
        # Forward to admin anonymously
        if admin_id:
            try:
                gender_str = "👨 Male" if database.get_onboarding_status(uid)[1] == "male" else "👩 Female"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("↩️ Reply", callback_data=f"adm_reply_{uid}"),
                    InlineKeyboardButton("🔍 View User", callback_data=f"adm_view_user_{uid}")
                )
                markup.add(
                    InlineKeyboardButton("🎁 +5 Msgs", callback_data=f"adm_add_msgs_{uid}_5"),
                    InlineKeyboardButton("🎁 +10 Msgs", callback_data=f"adm_add_msgs_{uid}_10")
                )
                markup.add(
                    InlineKeyboardButton("🎁 +25 Msgs", callback_data=f"adm_add_msgs_{uid}_25"),
                    InlineKeyboardButton("🎁 +75 Msgs", callback_data=f"adm_add_msgs_{uid}_75")
                )
                markup.add(
                    InlineKeyboardButton("👑 VIP (7 Days)", callback_data=f"adm_make_vip_{uid}_7"),
                    InlineKeyboardButton("👑 VIP (30 Days)", callback_data=f"adm_make_vip_{uid}_30")
                )
                markup.add(
                    InlineKeyboardButton("🚫 Ban", callback_data=f"adm_ban_{uid}"),
                    InlineKeyboardButton("✅ Unban", callback_data=f"adm_unban_{uid}")
                )
                
                header = (
                    f"💬 <b>New Feedback</b>\n━━━━━━━━━━━━━━\n"
                    f"👤 {user_info.first_name} ({gender_str})\n"
                    f"🌐 Lang: {lang}\n"
                    f"🆔 ID: <code>{uid}</code>"
                )
                
                if message.text:
                    bot.send_message(
                        admin_id,
                        f"{header}\n\n<i>{message.text}</i>",
                        parse_mode="HTML",
                        reply_markup=markup
                    )
                else:
                    # Send header with buttons, then copy the user's media (photo, etc.)
                    bot.send_message(admin_id, header, parse_mode="HTML", reply_markup=markup)
                    bot.copy_message(admin_id, chat_id, message.message_id)
            except Exception as e:
                pass
        bot.send_message(chat_id, S(lang, 'feedback_thanks'), parse_mode="HTML")
        clear_state(uid)
        return

    if str(state).startswith("ADMIN_REPLY_") and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        target_uid = int(state.split("_")[2])
        try:
            bot.copy_message(target_uid, chat_id, message.message_id)
            bot.send_message(chat_id, f"✅ Message sent to user {target_uid}.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Failed to send: {e}")
        clear_state(uid)
        return

    if state == "ADMIN_BROADCAST" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        
        users = database.get_all_user_ids()
        msg_id = message.message_id
        broadcast_text = message.text or message.caption
        
        def run_custom_broadcast():
            import time
            success, failed = 0, 0
            for u in users:
                try:
                    bot.copy_message(u, chat_id, msg_id)
                    # Also refresh keyboard for this user
                    try:
                        u_lang = database.get_bot_language(u) or 'am'
                        bot.send_message(u, "​", reply_markup=get_bottom_markup(u_lang, u))
                        # Append the broadcast to history
                        if broadcast_text:
                            database.append_bot_message_to_history(u, broadcast_text)
                    except Exception:
                        pass
                    database.mark_user_blocked(u, 0)
                    success += 1
                except Exception:
                    database.mark_user_blocked(u, 1)
                    failed += 1
                time.sleep(0.07)
            try:
                bot.send_message(chat_id, f"✅ <b>Broadcast Complete!</b>\n✔️ {success} Delivered\n❌ {failed} Failed (Marked as Blocked/Left)", parse_mode="HTML")
            except: pass
            
        threading.Thread(target=run_custom_broadcast, daemon=True).start()
        bot.send_message(chat_id, f"🚀 <b>Broadcast Started!</b>\nSending to {len(users)} users in the background...", parse_mode="HTML")
        clear_state(uid); return

    if state == "ADMIN_CREDIT_USER" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ ተሰርዟል።"); return
        try:
            target_id = int(message.text.strip())
            target = database.get_user(target_id)
            if not target:
                bot.send_message(chat_id, "❌ ተጠቃሚ አልተገኘም!"); return
            set_state(uid, "ADMIN_CREDIT_AMOUNT", target_id=target_id)
            bot.send_message(chat_id, f"👤 {target['first_name']} (@{target['username']})\n💳 ክሬዲት: {target['credits']}\n\nስንት ክሬዲት ይጨምር?")
        except ValueError:
            bot.send_message(chat_id, "❌ User ID ቁጥር ብቻ ያስገቡ!")
        return

    if state == "ADMIN_CREDIT_AMOUNT" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ ተሰርዧል."); return
        try:
            amount = int(message.text.strip())
            target_id = session["data"]["target_id"]
            database.add_credits(target_id, amount)
            new_balance = database.get_credits(target_id)
            bot.send_message(chat_id, f"✅ {amount} ክሬዲት ተጨምሯል!\n📊 አዲስ ቀሪ: {new_balance}")
            bot.send_message(target_id, f"🎉 <b>{amount} PDF ክሬዲት ተጨምሮልዎታል!</b>\n📊 ቀሪ: {new_balance}\n\n/new ይጫኑ ለመጀመር!", parse_mode="HTML")
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ ቁጥር ብቻ ያስገቡ!")
        return

    
    # ── Channel check for non-admin ──────────
    if not is_admin(message.from_user) and not check_channel_member(uid):
        send_join_channel_msg(chat_id, uid); return

    # ── Bottom Menu Handlers ─────────────────
    # Catch old cached buttons from previous users (no emoji prefix) and refresh their keyboard
    if message.text and not message.text.startswith("/"):
        old_buttons = ["ምክክራችንን እንቀጥል", "የኔ ገፅ", "ጓደኛ ይጋብዙ", "ቡድኑን ያበረታቱ", "ቋንቋ ቀይር", "የስነ-ልቦና ምክር"]
        is_old_button = any(ob in message.text for ob in old_buttons)
        has_menu_emoji = any(e in message.text for e in ["🧠", "👤", "🎁", "☕", "🌐"])
        if is_old_button and not has_menu_emoji:
            # Old cached keyboard — refresh it
            user_lang = get_lang(uid)
            if not database.get_bot_language(uid):
                # They never picked a language — ask them
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="setlang_am"),
                    InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
                )
                markup.add(
                    InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data="setlang_ti"),
                    InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data="setlang_om"),
                )
                bot.send_message(chat_id, S('am', 'lang_select_prompt'), parse_mode="HTML", reply_markup=markup)
                return
            send_welcome(chat_id, message.from_user.first_name, user_lang)
            return

    if message.text and ("🧠" in message.text or "የስነ-ልቦና ምክር" in message.text):
        if "የስነ-ልቦና ምክር" in message.text:
            # Their Telegram client has the old keyboard cached. Send welcome to update it.
            send_welcome(chat_id, message.from_user.first_name, get_lang(uid))
            return
            
        history_str = database.get_advice_history(uid)
        last_ai_msg = None
        if history_str:
            try:
                history = json.loads(history_str)
                for item in reversed(history):
                    if item.get("role") == "model":
                        last_ai_msg = item.get("parts", [""])[0]
                        break
            except Exception:
                pass
                
        if last_ai_msg:
            try:
                chunks = [last_ai_msg[i:i+4000] for i in range(0, len(last_ai_msg), 4000)]
                for chunk in chunks:
                    bot.send_message(chat_id, chunk, parse_mode="HTML")
            except Exception:
                import re as re_mod
                clean = re_mod.sub(r'<[^>]+>', '', last_ai_msg)
                clean_chunks = [clean[i:i+4000] for i in range(0, len(clean), 4000)]
                for chunk in clean_chunks:
                    bot.send_message(chat_id, chunk)
        else:
            bot.send_message(chat_id, S(get_lang(uid), 'no_history_prompt'), parse_mode="HTML")
        return
        
    if message.text and "👤" in message.text:
        is_vip = database.is_vip(uid)
        lang = get_lang(uid)
        if is_vip:
            user_data = database.get_user(uid)
            expiry_str = user_data["vip_expiry"] if user_data else ""
            formatted_expiry = ""
            if expiry_str:
                try:
                    from datetime import datetime
                    d = datetime.fromisoformat(expiry_str)
                    formatted_expiry = f" {d.strftime('%Y-%m-%d')}"
                except: pass
            msgs_display = S(lang, 'unlimited_display', date=formatted_expiry)
        else:
            msgs = database.get_advice_messages_left(uid)
            msgs_display = f"<b>{msgs}</b>"
            
        count = database.get_uncredited_referral_count(uid)
        markup = InlineKeyboardMarkup()
        if count >= 10:
            markup.add(InlineKeyboardButton(S(lang, 'btn_claim'), callback_data="claim_referrals"))
        markup.add(InlineKeyboardButton(S(lang, 'btn_topup'), callback_data="show_topup"))
        markup.add(InlineKeyboardButton(S(lang, 'btn_reset'), callback_data="confirm_reset"))
            
        bot.send_message(
            chat_id,
            S(lang, 'mypage_title') + "\n━━━━━━━━━━━━━━━━━━━━\n" +
            S(lang, 'mypage_msgs_left', msgs=msgs_display) + "\n\n" +
            S(lang, 'mypage_referrals', count=count) + "\n" +
            S(lang, 'mypage_referral_hint') + "\n\n" +
            S(lang, 'mypage_reset_info') + "\n" +
            S(lang, 'mypage_reset_warn') + "\n\n" +
            S(lang, 'mypage_topup_hint'),
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    if message.text and "🎁" in message.text:
        lang = get_lang(uid)
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start=ref_{uid}"
        count = database.get_uncredited_referral_count(uid)
        
        markup = None
        if count >= 10:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(S(lang, 'btn_claim'), callback_data="claim_referrals"))
            
        bot.send_message(
            chat_id,
            S(lang, 'invite_title') + "\n\n" +
            S(lang, 'invite_count', count=count) + "\n" +
            S(lang, 'invite_hint') + "\n\n" +
            S(lang, 'invite_link') + "\n<code>" + link + "</code>",
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    if message.text and "☕" in message.text:
        show_tip_cta(chat_id, uid)
        return

    if message.text and "🌐" in message.text:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="setlang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
        )
        markup.add(
            InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data="setlang_ti"),
            InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data="setlang_om"),
        )
        bot.send_message(chat_id, S(get_lang(uid), 'lang_select_prompt'), parse_mode="HTML", reply_markup=markup)
        return

    if message.text and "⚙️" in message.text and is_admin_uid(uid):
        show_admin_menu(chat_id, message.from_user)
        return

    if message.text and "💬" in message.text:
        lang = get_lang(uid)
        set_state(uid, "FEEDBACK")
        bot.send_message(chat_id, S(lang, 'feedback_prompt'), parse_mode="HTML")
        return

    # ── Advice Chat Mode (All other text) ─────────────────────
    if message.text:
        # Ignore commands
        if message.text.startswith("/"):
            return
            
        # Enforce onboarding first
        if not check_onboarding(chat_id, uid, message.from_user.first_name):
            return
            
        # Check quota
        msgs_left = database.get_advice_messages_left(uid)
        is_vip = database.is_vip(uid)
        is_adm = is_admin(message.from_user)
        
        if msgs_left <= 0 and not is_vip and not is_adm:
            lang = get_lang(uid)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_starter'), callback_data="buy_advice_25"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_pro'), callback_data="buy_advice_75"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_heavy'), callback_data="buy_advice_225"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited'), callback_data="buy_advice_unlimited"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited_month'), callback_data="buy_advice_unlimited_month"))
            
            cta_text = (
                S(lang, 'paywall_title') + "\n\n" +
                S(lang, 'paywall_body') + "\n\n" +
                S(lang, 'topup_choose') + "\n\n" +
                S(lang, 'topup_starter') + "\n" +
                S(lang, 'topup_pro') + "\n" +
                S(lang, 'topup_heavy') + "\n" +
                S(lang, 'topup_unlimited') + "\n" +
                S(lang, 'topup_unlimited_month') + "\n\n" +
                S(lang, 'topup_cta')
            )
            bot.send_message(chat_id, cta_text, parse_mode="HTML", reply_markup=markup)
            return

        try:
            bot.send_chat_action(chat_id, 'typing')
        except Exception:
            pass
            
        user_text = message.text.strip()
        
        def process_advice_chat():
            import time
            stop_typing = threading.Event()
            def keep_typing():
                while not stop_typing.is_set():
                    try:
                        bot.send_chat_action(chat_id, 'typing')
                    except:
                        pass
                    stop_typing.wait(4)
            
            typing_thread = threading.Thread(target=keep_typing, daemon=True)
            typing_thread.start()
            
            try:
                # Load history from DB for persistent conversations
                try:
                    history_str = database.get_advice_history(uid)
                    history = json.loads(history_str) if history_str else []
                except Exception:
                    history = []
                
                # Get user gender
                _, user_gender = database.get_onboarding_status(uid)
                user_lang = get_lang(uid)

                # Get AI response
                ai_response = ai_engine.chat_with_mentor(user_text, history, gender=user_gender, lang=user_lang)
                
                stop_typing.set()
                
                if not ai_response:
                    bot.send_message(chat_id, S(user_lang, 'ai_error'))
                    return
                
                # Deduct quota (everyone counts down, but VIP/Admin bypass block)
                database.consume_advice_message(uid)
                
                # Check if this was the last free message — append punchy hook
                remaining_after = database.get_advice_messages_left(uid)
                if remaining_after <= 0 and not is_vip and not is_adm:
                    hook_key = 'last_free_hook_f' if user_gender == 'female' else 'last_free_hook_m'
                    ai_response += S(user_lang, hook_key)
                    
                # Update history and save back to DB
                history.append({"role": "user", "parts": [user_text]})
                history.append({"role": "model", "parts": [ai_response]})
                try:
                    database.save_advice_history(uid, json.dumps(history, ensure_ascii=False))
                except Exception as e:
                    logging.error(f"Failed to save advice history: {e}")
                
                # Send response
                try:
                    # Telegram message limit is 4096. We chunk to 4000 to be safe.
                    chunks = [ai_response[i:i+4000] for i in range(0, len(ai_response), 4000)]
                    for chunk in chunks:
                        bot.send_message(chat_id, chunk, parse_mode="HTML")
                except Exception:
                    # Fallback: strip all HTML tags and send plain chunks
                    import re as re_mod
                    clean = re_mod.sub(r'<[^>]+>', '', ai_response)
                    clean_chunks = [clean[i:i+4000] for i in range(0, len(clean), 4000)]
                    for chunk in clean_chunks:
                        bot.send_message(chat_id, chunk)
            except Exception as e:
                stop_typing.set()
                logging.error(f"ADVICE THREAD CRASH: {e}")
                import traceback
                logging.error(traceback.format_exc())
                try:
                    bot.send_message(chat_id, f"⚠️ THREAD ERROR: {e}")
                except:
                    pass
                
        try:
            threading.Thread(target=process_advice_chat, daemon=True).start()
        except Exception as e:
            logging.error(f"Failed to start thread: {e}")
            bot.send_message(chat_id, S(get_lang(uid), 'tech_error', err=str(e)))
        return

    # ── Book Input (title or photo) ──────────
    if message.photo or message.document:
        bot.reply_to(message, S(get_lang(uid), 'text_only'))
        return

    # ── Catch-all: Forward to admin ──────────
    if not is_admin(message.from_user) and not message.text:
        bot.reply_to(message, '✅ መልዕክትዎ ደርሶናል!')
        return
# ══════════════════════════════════════════
#  WEBHOOK HTTP SERVER (Render & Chapa)
# ══════════════════════════════════════════

def process_chapa_success(tx_ref):
    if database.is_tx_ref_used(tx_ref):
        return
    parts = tx_ref.split("-")
    if len(parts) >= 3:
        try:
            uid = int(parts[1])
            purpose = parts[2]
        except ValueError:
            return
    else:
        return
        
    chat_id = uid
    order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
    
    if purpose.startswith("ADVICE_"):
        pkg = purpose.split("_")[1]
        lang = get_lang(uid)
        if pkg == "unlimited":
            payment_amount = 1800
            database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK", status='approved')
            database.set_vip(uid, days=7)
            bot.send_message(chat_id, S(lang, 'payment_success_unlimited'), parse_mode="HTML")
        elif pkg == "unlimited_month":
            payment_amount = 4900
            database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK", status='approved')
            database.set_vip(uid, days=30)
            bot.send_message(chat_id, S(lang, 'payment_success_unlimited_month'), parse_mode="HTML")
        else:
            msgs = int(pkg)
            payment_amount = {25: 200, 75: 400, 225: 1200}.get(msgs, 200)
            database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK", status='approved')
            database.add_advice_messages(uid, msgs)
            bot.send_message(chat_id, S(lang, 'payment_success_msgs', msgs=msgs), parse_mode="HTML")
    elif purpose == "TIP":
        # Verify the actual amount from the Chapa transaction
        lang = get_lang(uid)
        tip_success, tip_data = chapa.verify_chapa_payment(tx_ref)
        tip_amount = int(float(tip_data.get("amount", 0))) if tip_success and tip_data else 0
        database.record_payment(uid, order_id, tip_amount, tx_ref, "CHAPA_WEBHOOK_TIP", status='approved')
        bot.send_message(chat_id, S(lang, 'tip_received'), parse_mode="HTML")

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/admin_dashboard'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            try:
                with open('admin_dashboard.html', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(b"Admin Dashboard not found.")
            return

        if self.path.startswith('/admin/data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if token != config.ADMIN_USERNAME:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
                return
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            stats = database.get_analytics()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
            return

        if self.path.startswith('/admin/advice_history'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                parsed_url = urlparse(self.path)
                qs = parse_qs(parsed_url.query)
                uid = int(qs.get('uid', [0])[0])
                history_str = database.get_advice_history(uid)
                if not history_str or history_str == '[]':
                    self.wfile.write(b"No psychology readings found for this user.")
                    return
                history = json.loads(history_str)
                html_out = "<ul>"
                for msg in history:
                    role = msg.get("role", "user")
                    text = msg.get("parts", [""])[0]
                    color = "blue" if role == "user" else "green"
                    html_out += f"<li class='mb-2'><strong class='text-{color}-600'>{role.upper()}:</strong> {html.escape(text)}</li>"
                html_out += "</ul>"
                self.wfile.write(html_out.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"Error: {e}".encode('utf-8'))
            return

        if self.path == '/app':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                with open('webapp.html', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(b"App UI not found.")
            return

        if self.path.startswith('/auto-verify/'):
            tx_ref = self.path.split('/')[-1]
            success, _ = chapa.verify_chapa_payment(tx_ref)
            if success:
                process_chapa_success(tx_ref)
            
            # Redirect user back to bot
            bot_username = bot.get_me().username
            self.send_response(302)
            self.send_header('Location', f'https://t.me/{bot_username}')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Baya Books Bot is running!")
            
    def do_POST(self):
        if self.path == '/chapa-webhook':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.end_headers()
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                tx_ref = data.get('tx_ref')
                if tx_ref:
                    # Double check via API to prevent spoofing
                    success, _ = chapa.verify_chapa_payment(tx_ref)
                    if success:
                        process_chapa_success(tx_ref)
            except Exception as e:
                logging.error(f"Webhook error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
def main():
    threading.Thread(target=run_dummy_server, daemon=True).start()
    threading.Thread(target=auto_nudge_daemon, daemon=True).start()
    print("=" * 50)
    print("  Baya Books Bot is LIVE!")
    print("=" * 50)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

def auto_nudge_daemon():
    import time
    while True:
        try:
            if database.get_setting("auto_nudge", "OFF") == "ON":
                # 1. Onboarding Nudge
                stuck = database.get_stuck_users()
                for u in stuck:
                    uid, name, u_lang = u['user_id'], u['first_name'] or 'there', u.get('bot_language') or 'am'
                    nudge_count = u.get('nudge_count', 0)
                    
                    if nudge_count == 0:
                        text = {
                            'am': f"👋 ሰላም <b>{name}</b>፣ በመሃል ተቋርጦብዎት ነው?\n\nመስማት የሚፈልጉትን ሳይሆን፣ አሁን ላይ <b>ሊሰሙት የሚገባዎትን እውነት</b> የሚነግርዎት AI እርስዎን እየጠበቀ ነው።\n\nወደ ሚስጥራዊው የውይይት ገፅ ለመግባት...\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                            'en': f"👋 Hi <b>{name}</b>, got interrupted halfway?\n\nThe AI that tells you <b>the truth you need to hear</b> (not just what you want to hear) is waiting for you.\n\nTo enter the confidential chat...\n<b>Please select your gender 👇</b>",
                            'ti': f"👋 ሰላም <b>{name}</b>፡ ኣብ መንጎ ተቋሪጹካ ድዩ?\n\nክትሰምዖ ዝደለኻዮ ሳይኮን፡ <b>ሕጂ ክትሰምዖ ዝግባእ ሓቂ</b> ዝነግረካ AI እናተጸበየካ እዩ።\n\nናብቲ ምስጢራዊ ዕላል ንምእታው...\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                            'om': f"👋 Akkam <b>{name}</b>, gidduutti si jalaa citee?\n\nAI'n waan dhagahuu barbaaddu osoo hin taane, <b>dhugaa ammaa dhagahuu qabdu</b> sitti himu si eegaa jira.\n\nMarii iccitii ta'e kana jalqabuuf...\n<b>Maaloo saala keessan filadhaa 👇</b>",
                        }.get(u_lang, "")
                    elif nudge_count == 1:
                        text = {
                            'am': f"እውነቱን ለመጋፈጥ ዝግጁ ስላልሆኑ ነው ጥለው የሄዱት? አብዛኛው ሰው የውሸት ማባበያን ይመርጣል። እርስዎ የተለዩ ከሆኑ፣ የጀመሩትን ይጨርሱ።\n\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                            'en': f"Did you walk away because you're not ready for the truth? Most people prefer comforting lies. If you're different, finish what you started.\n\n<b>Please select your gender 👇</b>",
                            'ti': f"ነቲ ሓቂ ክትገጥሞ ድሉው ስለዘይኮንካ ዲኻ ገዲፍካዮ ኬድካ? መብዛሕትኡ ሰብ ናይ ሓሶት መደዓዓሲ እዩ ዝመርጽ። ንስኻ ፍሉይ እንተኾንካ፡ ዝጀመርካዮ ወድእ።\n\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                            'om': f"Dhugaa jiru fudhachuuf qophii waan hin taaneef dhiistee deemtee? Namoonni baay'een soba isaan jajjabeessu filatu. Ati adda yoo taate, waan jalqabde xumuri.\n\n<b>Maaloo saala keessan filadhaa 👇</b>",
                        }.get(u_lang, "")
                    elif nudge_count == 2:
                        text = {
                            'am': f"እርስዎን የሚጠብቁ ያልተመለሱ ጥያቄዎች አሉ። እርስዎ ያላስተዋሏቸው የባህሪዎ ገጽታዎች አሉ። ይህንን ለማወቅ እንቅፋት የሆነው ፕሮፋይልዎን አለማሟላትዎ ብቻ ነው።\n\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                            'en': f"There are answers waiting for you. Patterns in your behavior you haven't noticed. The only thing standing in the way is you completing your profile.\n\n<b>Please select your gender 👇</b>",
                            'ti': f"ዝጽበዩኻ ዘይተመለሱ ሕቶታት ኣለዉ። ዘየስተውዓልካሎም ናይ ባህሪኻ መዳያት ኣለዉ። ነዚ ንምፍላጥ ዕንቅፋት ኮይኑ ዘሎ ፕሮፋይልካ ዘይምምላእ ጥራይ እዩ።\n\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                            'om': f"Deebiiwwan si eegaa jiran tu jiru. Amala kee keessatti wantoota ati hin hubatin jiru. Kana beekuuf gufuun jiru profaayilii kee guutuu dhiisuu kee qofa.\n\n<b>Maaloo saala keessan filadhaa 👇</b>",
                        }.get(u_lang, "")
                    elif nudge_count == 3:
                        text = {
                            'am': f"ማደግ ሁሌም ምቾት ይነሳል። ችላ ብሎ ባሉበት መቆየት ግን ቀላል ነው። አሁን እያደረጉ ያሉት እሱን ነው? ወደ ፊት እርምጃ ይውሰዱ።\n\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                            'en': f"Growth is uncomfortable. It’s easier to ignore it and stay exactly where you are. Is that what you're doing right now? Step up.\n\n<b>Please select your gender 👇</b>",
                            'ti': f"ምዕባይ ወትሩ ምቾት ይኸልእ እዩ። ዕሽሽ ኢልካ ኣብ ዘለኻዮ ምጽናሕ ግን ቀሊል እዩ። ሕጂ ትገብሮ ዘለኻ እዚ ድዩ? ናብ ቅድሚት ስጉምቲ ውሰድ።\n\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                            'om': f"Guddachuun yeroo hunda mijataa miti. Dhiisanii bakka jiranitti hafuun garuu salphaadha. Amma waan gochaa jirtu kanaa? Tarkaanfii gara fuulduraa fudhadhu.\n\n<b>Maaloo saala keessan filadhaa 👇</b>",
                        }.get(u_lang, "")
                    else:
                        text = {
                            'am': f"ይህ ለመጨረሻ ጊዜ የማስታውስዎ ነው። የስነ-ልቦና ትንታኔው ተዘጋጅቷል። የመጀመሪያውን እርምጃ ካልወሰዱ ምንም የሚቀየር ነገር የለም። ምርጫው የእርስዎ ነው።\n\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>",
                            'en': f"This is the last time I'll ask. The insights are ready. If you don't take the first step, nothing changes. The choice is yours.\n\n<b>Please select your gender 👇</b>",
                            'ti': f"እዚ ንመወዳእታ ግዜ ዝዝክረካ ዘለኹ እዩ። ናይ ስነ-ኣእምሮ ትንታነ ተዳልዩ ኣሎ። ነቲ ናይ መጀመርታ ስጉምቲ እንተዘይ ወሲድካዮ ዝቕየር ነገር የለን። ምርጫ ናትካ እዩ።\n\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>",
                            'om': f"Kun yeroo dhumaatiif kanan si yaadachiisuudha. Qorannoon xiin-sammuu qophaa'eera. Tarkaanfii jalqabaa yoo hin fudhanne wanti jijjiiramu hin jiru. Filannoon kan keeti.\n\n<b>Maaloo saala keessan filadhaa 👇</b>",
                        }.get(u_lang, "")
                    if not text: text = "👋 " + name
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        InlineKeyboardButton(S(u_lang, 'gender_male'), callback_data="onboard_gen_m"),
                        InlineKeyboardButton(S(u_lang, 'gender_female'), callback_data="onboard_gen_f")
                    )
                    try:
                        bot.send_message(uid, text, parse_mode="HTML", reply_markup=markup)
                        database.append_bot_message_to_history(uid, text)
                        database.mark_nudge_sent(uid, "nudge_onboard_sent")
                    except:
                        database.mark_user_blocked(uid, 1)
                    time.sleep(0.1)

                # 2. Silent Users Nudge (Icebreaker)
                silent = database.get_silent_users()
                for u in silent:
                    uid, name, u_lang = u['user_id'], u['first_name'] or 'there', u.get('bot_language') or 'am'
                    text = {
                        'am': f"👋 ሰላም <b>{name}</b>፣ በሩን ከፍተው ገብተዋል ግን ዝምታን መርጠዋል።\n\nብዙ ጊዜ ከየት መጀመር እንዳለብን ግራ ሲገባን ዝም እንላለን። የተስተካከለ ፅሁፍ ማዘጋጀት አይጠበቅብዎትም — አሁን ላይ የሚሰማዎትን ስሜት በአንድ ቃል፣ ወይም «ሰላም» በማለት ብቻ ይፃፉልኝ።\n\nእኔ እዚህ ያለሁት ላዳምጥዎት ነው። 👇",
                        'en': f"👋 Hi <b>{name}</b>, you opened the door but stayed silent.\n\nOften we stay quiet because we don't know where to start. You don't need a perfectly crafted message — just type 'Hi', or send a single word about how you feel right now.\n\nI'm here to listen. 👇",
                        'ti': f"👋 ሰላም <b>{name}</b>፡ ማዕጾ ኸፊጥካ ኣቲኻ ግን ስቕታ መሪጽካ።\n\nመብዛሕትኡ ግዜ ካበይ ከም እንጅምር ምስ ዝጠፍኣና ስቕ ንብል። እተስተኻኸለ ጽሑፍ ምድላው ኣየድልየካን እዩ — ሕጂ ዝስመዓካ ዘሎ ስምዒት ብሓደ ቃል፡ ወይ ድማ «ሰላም» ብምባል ጥራይ ጸሓፈለይ።\n\nኣነ ንዓኻ ንምስማዕ ኣብዚ ኣለኹ። 👇",
                        'om': f"👋 Akkam <b>{name}</b>, balbala banteet seente garuu cal'isuu filatte.\n\nYeroo baay'ee eessaa akka jalqabnu yeroo nutti bitaacha'u ni cal'isna. Barreeffama sirreeffame qopheessuun sirraa hin eegamu — miira amma sitti dhaga'amu jecha tokkoon, ykn «Akkam» jechuun qofa naaf barreessi.\n\nAni si dhaggeeffachuuf asan jira. 👇",
                    }.get(u_lang, "")
                    try:
                        bot.send_message(uid, text, parse_mode="HTML")
                        database.append_bot_message_to_history(uid, text)
                        database.mark_nudge_sent(uid, "nudge_silent_sent")
                    except:
                        database.mark_user_blocked(uid, 1)
                    time.sleep(0.1)

                # 3. Trial Ended Nudge (Revive)
                ended = database.get_trial_ended_users()
                for u in ended:
                    uid, name, u_lang = u['user_id'], u['first_name'] or 'there', u.get('bot_language') or 'am'
                    text = {
                        'am': f"👋 ሰላም <b>{name}</b>፣ ያለፈውን ውይይታችንን መለስ ብዬ እያየሁት ነበር።\n\nስለተወያየንበት ጉዳይ አንድ ያልነገርኩዎት ትልቅ ነገር አለ። እስካሁን ያወራነው የችግሩን ገፅታ (Surface) ብቻ ነው፤ ዋናው ስር ያለው ግን ሌላ ቦታ ነው።\n\nውይይታችንን አቋርጠን መፍትሄውን ሳልነግርዎት በመቅረቴ ቅር ብሎኛል። መፍትሄውን ለማወቅ እና የጀመርነውን ለመጨረስ... 👇",
                        'en': f"👋 Hi <b>{name}</b>, I was looking back at our previous chat.\n\nThere's one major thing I haven't told you about what we discussed. So far, we only scratched the surface of the problem. The real root is somewhere else entirely.\n\nIt bothers me that we stopped before I could give you the actual solution. To find out the solution and finish what we started... 👇",
                        'ti': f"👋 ሰላም <b>{name}</b>፡ ነቲ ሕሉፍ ዕላልና ምልስ ኢለ እርእዮ ነይረ።\n\nብዛዕባ ዝተመያየጥናሉ ጉዳይ ሓደ ዘይነገርኩኻ ዓቢ ነገር ኣሎ። ክሳብ ሕጂ ዘውራዕናዮ ገጽታ ናይቲ ጸገም ጥራይ እዩ፣ እቲ ቀንዲ ሱር ግን ካልእ ቦታ እዩ ዘሎ።\n\nመፍትሒኡ ከይነገርኩኻ ዕላልና ብምቁራጹ ጓህዩኒ። መፍትሒኡ ንምፍላጥን ዝጀመርናዮ ንምውዳእን... 👇",
                        'om': f"👋 Akkam <b>{name}</b>, marii keenya darbe deebi'een ilaalaa ture.\n\nWaa'ee dhimma irratti mari'annee sana wanta guddaa tokko kanin sitti hin himin jira. Hanga ammaatti kan haasofne fuula rakkinichaa qofa; hundeen rakkinichaa garuu iddoo biraa jira.\n\nFurmaata isaa osoo sitti hin himin mariin keenya addaan cituun isaa na gaddisiiseera. Furmaata isaa beekuu fi waan jalqabne xumuruuf... 👇",
                    }.get(u_lang, "")
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_starter'), callback_data="buy_advice_25"))
                    markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_pro'), callback_data="buy_advice_75"))
                    markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_heavy'), callback_data="buy_advice_225"))
                    markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_unlimited'), callback_data="buy_advice_unlimited"))
                    markup.add(InlineKeyboardButton(S(u_lang, 'topup_btn_unlimited_month'), callback_data="buy_advice_unlimited_month"))
                    try:
                        bot.send_message(uid, text, parse_mode="HTML", reply_markup=markup)
                        database.append_bot_message_to_history(uid, text)
                        database.mark_nudge_sent(uid, "nudge_revive_sent")
                    except:
                        database.mark_user_blocked(uid, 1)
                    time.sleep(0.1)

                    time.sleep(0.1)

                # 4. Abandoned Checkout Nudge
                abandoned = database.get_abandoned_checkouts()
                for p in abandoned:
                    uid, name, u_lang = p['user_id'], p['first_name'] or 'there', p.get('bot_language') or 'am'
                    payment_id = p['id']
                    
                    text = {
                        'am': f"👋 ሰላም <b>{name}</b>፣ ክፍያዎን ለመፈጸም ተቸግረዋል?\n\nየክፍያ መንገዱ ግራ ካጋባዎት፣ በቀጥታ በሚከተሉት አማራጮች መክፈል ይችላሉ፡\n🏦 CBE (ንግድ ባንክ): <code>1000073164765</code>\n📱 ቴሌብር (Telebirr): <code>0912689900</code>\n👤 በኃይሉ ጌታቸው (Behailu Getachew)\n\nከከፈሉ በኋላ፣ አካውንትዎን ለማስከፈት ከታች ባለው ሜኑ <b>'💬 አስተያየትዎን ይስጡ'</b> የሚለውን በመጫን ደረሰኝዎን ይላኩልን።",
                        'en': f"👋 Hi <b>{name}</b>, did you have trouble completing your payment?\n\nIf the payment gateway was confusing, you can pay directly via:\n🏦 CBE: <code>1000073164765</code>\n📱 Telebirr: <code>0912689900</code>\n👤 Behailu Getachew\n\nAfter paying, just send your receipt using the <b>'💬 Give Feedback'</b> button on the bottom menu to activate your account.",
                        'ti': f"👋 ሰላም <b>{name}</b>፡ ክፍሊትኩም ንምፍጻም ተጸጊምኩም ዶ?\n\nእቲ ናይ ክፍሊት መንገዲ እንተደኣ ኣደናጊሩኩም፡ ብቐጥታ በዞም ዝስዕቡ ኣማራጺታት ክትከፍሉ ትኽእሉ ኢኹም፡\n🏦 CBE: <code>1000073164765</code>\n📱 Telebirr: <code>0912689900</code>\n👤 በኃይሉ ጌታቸው (Behailu Getachew)\n\nምስ ከፈልኩም፡ ካብ ታሕቲ ዘሎ ሜኑ <b>'💬 ርእይቶኹም ሃቡ'</b> ዝብል ብምጥዋቕ ቅዳሕ (ደረሰኝ) ስደዱልና።",
                        'om': f"👋 Akkam <b>{name}</b>, Kaffaltii keessan raawwachuuf rakkattanii?\n\nTarsiimoon kaffaltii yoo isin burjaajesse, kallattiin filannoowwan kanaan kaffaluu dandeessu:\n🏦 CBE: <code>1000073164765</code>\n📱 Telebirr: <code>0912689900</code>\n👤 Behailu Getachew\n\nErga kaffaltanii booda, akkawuntii keessan banuuf baafata armaan gadii irraa <b>'💬 Yaada keessan kennaa'</b> kan jedhu tuquun nagahee (receipt) keessan nuuf ergaa.",
                    }.get(u_lang, "")
                    
                    try:
                        bot.send_message(uid, text, parse_mode="HTML")
                        database.mark_checkout_nudged(payment_id)
                    except:
                        # If blocked, we still mark it so we don't try again
                        database.mark_checkout_nudged(payment_id)
                    time.sleep(0.1)

        except Exception as e:
            print("Auto-nudge daemon error:", e)
        time.sleep(60)  # Sleep 1 minute to check for carts faster

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\\nBot stopped.")
