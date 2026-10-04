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
    
    cta_text = (
        S(lang, 'topup_title') + "\n\n" +
        S(lang, 'topup_body') + "\n\n" +
        S(lang, 'topup_choose') + "\n\n" +
        S(lang, 'topup_starter') + "\n" +
        S(lang, 'topup_pro') + "\n" +
        S(lang, 'topup_heavy') + "\n" +
        S(lang, 'topup_unlimited') + "\n\n" +
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

    if not age_verified:
        text = S(user_lang, 'onboard_privacy')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(S(user_lang, 'onboard_age_btn'), callback_data="onboard_age_18"))
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return False
    
    if not gender:
        # Age is verified but gender is missing — go straight to gender selection
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(S(user_lang, 'gender_male'), callback_data="onboard_gen_m"), InlineKeyboardButton(S(user_lang, 'gender_female'), callback_data="onboard_gen_f"))
        bot.send_message(chat_id, S(user_lang, 'onboard_gender_prompt'), reply_markup=markup)
        return False
    
    return True

def send_welcome(chat_id, first_name, lang=None, uid=None):
    if lang is None:
        lang = 'am'
    if uid is None:
        uid = chat_id # Fallback
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
        database.set_user_age_verified(uid)
        lang = get_lang(uid)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(S(lang, 'gender_male'), callback_data="onboard_gen_m"), InlineKeyboardButton(S(lang, 'gender_female'), callback_data="onboard_gen_f"))
        bot.edit_message_text(S(lang, 'onboard_gender_prompt'), chat_id, call.message.message_id, reply_markup=markup)
        return
        
    if data.startswith("onboard_gen_"):
        gender = "male" if data == "onboard_gen_m" else "female"
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
        else:
            msgs = int(pkg)
            amount = {25: 200, 75: 400, 225: 1200}.get(msgs, 200)
            
        bot.answer_callback_query(call.id, S(lang, 'payment_preparing'))
        purpose = f"ADVICE_{pkg}"
        checkout_url, tx_ref, err = chapa.generate_chapa_link(amount, uid, purpose)
        if not checkout_url:
            bot.send_message(chat_id, S(lang, 'payment_error', err=err), parse_mode="HTML")
            return
            
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
        markup.add(InlineKeyboardButton("🔄 Refresh", callback_data="adm_dashboard"))
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        bot.send_message(chat_id,
            f"📊 <b>DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Active Users: <b>{stats['total_users']}</b>\n"
            f"🚫 Left/Blocked: <b>{stats.get('blocked_users', 0)}</b>\n"
            f"🟢 New Today: <b>{stats['new_today']}</b> | This Week: <b>{stats.get('new_this_week', 0)}</b>\n"
            f"💬 Chatting Users: <b>{stats.get('active_advice_users', 0)}</b>\n\n"
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
        
        orders_text = ""
        for o in details["recent_orders"]:
            orders_text += f"  📕 {o['book_title'][:25]} ({o['status']})\n"
        if not orders_text:
            orders_text = "  — No orders\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("💳 Add Credit", callback_data=f"adm_credit_{target_id}")
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
            f"👤 <b>User Profile</b>{banned_tag}{admin_tag}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 ID: <code>{target_id}</code>\n"
            f"👤 Name: <b>{u['first_name']}</b>\n"
            f"📛 Username: @{u['username'] or 'N/A'}\n"
            f"📅 Joined: {u['joined_date'][:10] if u['joined_date'] else 'N/A'}\n\n"
            f"━━ Stats ━━━━━━━━━━━━━━━━━━\n"
            f"  📄 Orders: <b>{details['order_count']}</b> delivered, <b>{details['draft_count']}</b> drafts\n"
            f"  💰 Total Paid: <b>{details['total_paid']:,} ETB</b>\n"
            f"  🎫 Credits: <b>{u['credits']}</b>\n"
            f"  👥 Referrals: <b>{details['referral_count']}</b>\n"
            f"  🔮 Previews Left: <b>{u['previews_left']}</b>\n"
            f"  🎁 Free Protocol: {'❌ Used' if u['free_protocol_used'] else '✅ Available'}\n\n"
            f"━━ Recent Orders ━━━━━━━━━━━\n{orders_text}",
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
            bot.send_message(target_id, "🚫 ይህ አካውንት ታግዷል።")
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
        def background_broadcast():
            import time
            success = 0
            failed = 0
            for u in all_users:
                try:
                    bot.send_message(u, f"✨ <b>የዕለቱ የስነ-ልቦና መልዕክት</b>\n\n{content}", parse_mode="HTML")
                    database.mark_user_blocked(u, 0)
                    success += 1
                except Exception as e:
                    database.mark_user_blocked(u, 1)
                    failed += 1
                time.sleep(0.05)
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
                bot.send_message(target_id, "🚫 ይህ አካውንት ታግዷል።")
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

    if state == "ADMIN_BROADCAST" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        
        users = database.get_all_user_ids()
        msg_id = message.message_id
        
        def run_custom_broadcast():
            import time
            success, failed = 0, 0
            for u in users:
                try:
                    bot.copy_message(u, chat_id, msg_id)
                    database.mark_user_blocked(u, 0)
                    success += 1
                except Exception:
                    database.mark_user_blocked(u, 1)
                    failed += 1
                time.sleep(0.05)
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
            
            cta_text = (
                S(lang, 'paywall_title') + "\n\n" +
                S(lang, 'paywall_body') + "\n\n" +
                S(lang, 'topup_choose') + "\n\n" +
                S(lang, 'topup_starter') + "\n" +
                S(lang, 'topup_pro') + "\n" +
                S(lang, 'topup_heavy') + "\n" +
                S(lang, 'topup_unlimited') + "\n\n" +
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
                    ai_response += S(user_lang, 'last_free_hook')
                    
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
    print("=" * 50)
    print("  Baya Books Bot is LIVE!")
    print("=" * 50)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\nBot stopped.")
