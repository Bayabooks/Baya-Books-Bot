import os
# SSL fix for local Windows development only (not needed on Render)
if os.environ.get("DEV_MODE"):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

import logging
import uuid
import json
import time
import re
from urllib.parse import urlparse, parse_qs
import threading
import tempfile
import html
import gzip
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    BotCommand, BotCommandScopeChat, BotCommandScopeDefault
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

ADMIN_PREVIEW_QUOTE = {}

def get_lang(uid):
    """Get user's language, default 'am'."""
    try:
        return database.get_bot_language(uid) or 'am'
    except:
        return 'am'

def get_full_name(user):
    """Build full Telegram display name (first_name + last_name)."""
    if not user:
        return "User"
    parts = [getattr(user, "first_name", None), getattr(user, "last_name", None)]
    full = " ".join(str(p).strip() for p in parts if p and str(p).strip())
    return full or "User"

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
    if not user:
        return False
    username = (user.username or "").lower().lstrip('@')
    if username == config.ADMIN_USERNAME:
        return True
    if hasattr(config, "SUB_ADMINS") and username in config.SUB_ADMINS:
        return True
    return database.is_sub_admin(user.id)

def is_owner(user):
    return is_admin(user)

def is_admin_uid(uid):
    if not uid:
        return False
    try:
        uid = int(uid)
    except (ValueError, TypeError):
        pass
    user_data = database.get_user(uid)
    if user_data:
        username = (user_data.get('username') or "").lower().lstrip('@')
        if username == config.ADMIN_USERNAME:
            return True
        if hasattr(config, "SUB_ADMINS") and username in config.SUB_ADMINS:
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

def get_all_admin_ids():
    admin_ids = set()
    owner_id = get_admin_id()
    if owner_id:
        admin_ids.add(owner_id)
    try:
        sub_admins = database.get_all_sub_admins()
        for sa in sub_admins:
            if sa and sa.get('user_id'):
                admin_ids.add(sa['user_id'])
    except Exception as e:
        logging.error(f"Error fetching sub_admins from db: {e}")
    if hasattr(config, "SUB_ADMINS") and config.SUB_ADMINS:
        try:
            conn = database.get_connection()
            c = conn.cursor()
            for sa_name in config.SUB_ADMINS:
                c.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (sa_name,))
                row = c.fetchone()
                if row and row["user_id"]:
                    admin_ids.add(row["user_id"])
            conn.close()
        except Exception as e:
            logging.error(f"Error resolving config.SUB_ADMINS: {e}")
    return list(admin_ids)

import hmac

def is_valid_admin_token(token):
    if not token:
        return False
    token_str = str(token).strip()
    
    # 1. Cryptographic admin secret comparison
    if hasattr(config, "ADMIN_SECRET_KEY") and config.ADMIN_SECRET_KEY:
        if hmac.compare_digest(token_str, config.ADMIN_SECRET_KEY):
            return True

    # 2. Sub-Admin verification
    token_clean = token_str.lower().lstrip('@')
    if hasattr(config, "SUB_ADMINS") and token_clean in config.SUB_ADMINS:
        return True
    try:
        sub_admins = database.get_all_sub_admins()
        for sa in sub_admins:
            sa_uname = (sa.get('username') or "").lower().lstrip('@')
            sa_uid = str(sa.get('user_id') or "")
            if token_clean == sa_uname or token_str == sa_uid:
                return True
    except Exception as e:
        logging.error(f"Error checking admin token: {e}")
    if is_admin_uid(token_str):
        return True
    return False

ADMIN_MENU_COMMANDS = [
    BotCommand("dashboard", "🌐 Unified Web Admin Dashboard"),
    BotCommand("author", "✍️ Author & Publisher Portal"),
    BotCommand("rentals", "📚 Manage rented books & extensions"),
    BotCommand("lookup", "🔍 Look up user (Profile, Books, Balance)"),
    BotCommand("investigate", "🕵️ Audit report of last 20 users"),
    BotCommand("clean", "🧹 Purge ghost & blocked users"),
    BotCommand("debug_carts", "🛒 Check abandoned checkouts"),
    BotCommand("del_last", "🗑️ Delete last payment record"),
    BotCommand("getlogs", "📋 View recent server logs"),
    BotCommand("reset_advice", "🔄 Reset my conversation history"),
    BotCommand("refresh_menus", "🔄 Push new menu to all users"),
    BotCommand("bayacontrol", "⚙️ Admin Control Panel"),
]

DEFAULT_USER_COMMANDS = [
    BotCommand("start", "🚀 Start / Restart the bot"),
    BotCommand("topup", "💎 Top up / Buy packages"),
    BotCommand("mylibrary", "📚 My Books & Library"),
    BotCommand("author", "✍️ Author & Publisher Portal"),
]

def setup_admin_menu(uid):
    """Sets the left menu commands specifically for an admin/sub-admin chat."""
    try:
        if uid:
            bot.set_my_commands(ADMIN_MENU_COMMANDS, scope=BotCommandScopeChat(chat_id=int(uid)))
    except Exception as e:
        logging.error(f"Failed to set admin commands for {uid}: {e}")

def setup_global_commands():
    """Sets the default command list for all users and pushes admin menu to all registered admins."""
    try:
        bot.set_my_commands(DEFAULT_USER_COMMANDS, scope=BotCommandScopeDefault())
    except Exception as e:
        logging.error(f"Failed to set default commands: {e}")
    try:
        admin_id = get_admin_id()
        if admin_id:
            setup_admin_menu(admin_id)
        sub_admins = database.get_all_sub_admins()
        for sa in sub_admins:
            setup_admin_menu(sa['user_id'])
    except Exception as e:
        logging.error(f"Failed to configure admin menus on startup: {e}")

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
    for adm_id in get_all_admin_ids():
        try:
            bot.send_message(adm_id, text, parse_mode="HTML")
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
    if is_admin(message.from_user) or is_admin_uid(uid):
        bot.send_message(
            chat_id,
            "👑 <b>Admin Access Active</b>\n━━━━━━━━━━━━━━━━━━━━\n\nYou have unlimited, free access to all books, psychology advice, and bot features without payment!",
            parse_mode="HTML"
        )
        return
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

    database.add_user(user.id, user.username or "Unknown", get_full_name(user), referred_by)

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

    if is_admin(user):
        setup_admin_menu(user.id)

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
    
    # Library Mini App Button (Active for all users)
    lib_url = f"{config.BASE_URL}/app?uid={uid}" if uid else f"{config.BASE_URL}/app"
    m.add(
        KeyboardButton("📚 መጻሕፍት ቤት (Library)", web_app=WebAppInfo(url=lib_url))
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
    uid = message.from_user.id
    if not check_channel_member(uid):
        send_join_channel_msg(message.chat.id, uid); return

    if is_admin_uid(uid):
        ubooks = get_all_book_keys()
        urentals = {}
        uexpired = []
    else:
        ubooks, urentals, uexpired = database.get_user_books_state(uid)
    orders = database.get_user_orders(uid)

    lines = []
    for bk in ubooks:
        bt = BOOK_TITLES.get(bk, bk)
        if bk in urentals:
            lines.append(f"  ⏳ <b>{bt}</b> (ኪራይ — ቀሪ {urentals[bk]} ቀናት)")
        else:
            lines.append(f"  ✅ <b>{bt}</b> (ሙሉ መጽሐፍ)")
    for bk in uexpired:
        bt = BOOK_TITLES.get(bk, bk)
        lines.append(f"  ⏰ <b>{bt}</b> (የኪራይ ጊዜው ያለፈ)")
    for i, o in enumerate(orders, 1):
        date = o["delivered_date"][:10] if o["delivered_date"] else "N/A"
        lines.append(f"  📕 {o['book_title']} ({date})")

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "📚 መጻሕፍት ቤት ክፈት (Open Library)",
            web_app=WebAppInfo(url=f"{config.BASE_URL}/app?uid={uid}")
        )
    )
    for i, o in enumerate(orders, 1):
        if o["pdf_file_id"]:
            markup.add(InlineKeyboardButton(f"📥 {i}. {o['book_title']}", callback_data=f"redownload_{o['id']}"))

    body = "\n".join(lines) if lines else "📚 ገና የገዙት ወይም የተከራዩት መጽሐፍ የለም። ከታች ያለውን ቁልፍ ተጭነው መጻሕፍት ቤቱን ይጎብኙ!"
    bot.send_message(
        message.chat.id,
        f"📚 <b>ቤተ-መጻሕፍትዎ (My Library)</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{body}",
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
        database.set_last_mentor_message(message.from_user.id, None)
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

@bot.message_handler(commands=["del_last"])
def cmd_del_last(message):
    if not is_admin(message.from_user): return
    conn = database.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, amount, status FROM payments WHERE status = 'approved' ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row:
        c.execute("DELETE FROM payments WHERE id = ?", (row['id'],))
        conn.commit()
        bot.reply_to(message, f"✅ Removed last payment from dashboard! (Amount: {row['amount']}, Status: {row['status']})")
    else:
        bot.reply_to(message, "No payments found to delete.")
    conn.close()

class DynamicBookTitles(dict):
    def get(self, key, default=None):
        if not key:
            return default if default is not None else ''
        k_str = str(key).strip().lower()
        val = super().get(k_str)
        if val:
            return val
        try:
            conn = database.get_connection()
            c = conn.cursor()
            c.execute("SELECT title FROM author_books WHERE book_key = ?", (k_str,))
            row = c.fetchone()
            conn.close()
            if row and row['title']:
                return row['title']
        except Exception:
            pass
        return default if default is not None else key

    def __getitem__(self, key):
        return self.get(key, key)

BOOK_TITLES = DynamicBookTitles({
    "narcissist": "የናርስሲስቶች ወጥመድ",
    "boundaries": "ድንበርህን አብጅ",
    "buyback": "ጊዜህን አስመልስ (Buy Back Your Time)",
    "meaning": "የህይወት ትርጉም"
})

def get_all_book_keys():
    keys = list(BOOK_TITLES.keys())
    try:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT book_key FROM author_books")
        for row in c.fetchall():
            if row and row['book_key'] and row['book_key'] not in keys:
                keys.append(row['book_key'])
        conn.close()
    except Exception:
        pass
    return keys

def notify_user_book_unlocked(uid, book_key, days=None):
    b_title = BOOK_TITLES.get(book_key, book_key)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "📚 መጽሐፉን አሁኑኑ አንብብ (Open Book)",
            web_app=WebAppInfo(url=f"{config.BASE_URL}/app?uid={uid}")
        )
    )
    if days:
        txt = (
            f"🎉 <b>እንኳን ደስ አለዎት!</b>\n\n"
            f"📖 <b>«{b_title}»</b> ሙሉ መጽሐፍ <b>ለ {days} ቀናት (ኪራይ)</b> ተከፍቶልዎታል!\n\n"
            f"ከታች ያለውን ቁልፍ ተጭነው በ<b>'📖 የኔ መጻሕፍት'</b> ስር ሙሉውን መጽሐፍ ማንበብ ይችላሉ 👇"
        )
    else:
        txt = (
            f"🎉 <b>እንኳን ደስ አለዎት!</b>\n\n"
            f"📖 <b>«{b_title}»</b> ሙሉ መጽሐፍ <b>ለዘላለም</b> ተከፍቶልዎታል!\n\n"
            f"ከታች ያለውን ቁልፍ ተጭነው በ<b>'📖 የኔ መጻሕፍት'</b> ስር ሙሉውን መጽሐፍ ማንበብ ይችላሉ 👇"
        )
    try:
        bot.send_message(uid, txt, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to notify user {uid} of unlocked book: {e}")

def get_payment_item_summary(tx_ref):
    if not tx_ref:
        return "Unknown Item"
    parts = tx_ref.split("-")
    purpose = parts[2] if len(parts) >= 3 else ""
    if purpose.startswith("BOOKRENT_"):
        bkey = purpose.replace("BOOKRENT_", "")
        bt = BOOK_TITLES.get(bkey, bkey)
        return f"⏳ Book Rental (10d): {bt}"
    elif purpose.startswith("BOOKEXT_"):
        bkey = purpose.replace("BOOKEXT_", "")
        bt = BOOK_TITLES.get(bkey, bkey)
        return f"➕ Book Extension (+5d): {bt}"
    elif purpose.startswith("BOOK_"):
        bkey = purpose.replace("BOOK_", "")
        bt = BOOK_TITLES.get(bkey, bkey)
        return f"💎 Book Full Purchase: {bt}"
    elif purpose.startswith("ADVICE_"):
        pkg = purpose.split("_")[1]
        return f"🧠 Advice Package ({pkg})"
    elif purpose == "TIP":
        return "☕ Tip / Support"
    return purpose or "Unknown Item"

def fulfill_payment(uid, tx_ref, order_id=None, receipt_ref=None):
    """
    Approves payment in database, unlocks the purchased item/package,
    and sends the success message to the customer.
    Returns (success, item_summary).
    """
    if not order_id:
        import uuid
        order_id = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
        
    database.approve_payment(tx_ref, order_id, receipt_ref=receipt_ref)
    
    parts = tx_ref.split("-")
    purpose = parts[2] if len(parts) >= 3 else ""
    item_summary = get_payment_item_summary(tx_ref)
    lang = get_lang(uid)
    chat_id = uid
    
    try:
        if purpose.startswith("BOOKRENT_"):
            book_key = purpose.replace("BOOKRENT_", "")
            database.unlock_book(uid, book_key, days=10)
            notify_user_book_unlocked(uid, book_key, days=10)
        elif purpose.startswith("BOOKEXT_"):
            book_key = purpose.replace("BOOKEXT_", "")
            database.unlock_book(uid, book_key, days=5)
            notify_user_book_unlocked(uid, book_key, days=5)
        elif purpose.startswith("BOOK_"):
            book_key = purpose.replace("BOOK_", "")
            database.unlock_book(uid, book_key, days=None)
            notify_user_book_unlocked(uid, book_key, days=None)
        elif purpose.startswith("ADVICE_"):
            pkg = purpose.split("_")[1]
            if pkg == "unlimited":
                database.set_vip(uid, days=7)
                bot.send_message(chat_id, S(lang, 'payment_success_unlimited'), parse_mode="HTML")
            elif pkg == "unlimited_month":
                database.set_vip(uid, days=30)
                bot.send_message(chat_id, S(lang, 'payment_success_unlimited_month'), parse_mode="HTML")
            else:
                msgs = int(pkg)
                database.add_advice_messages(uid, msgs)
                bot.send_message(chat_id, S(lang, 'payment_success_msgs', msgs=msgs), parse_mode="HTML")
        elif purpose == "TIP":
            bot.send_message(chat_id, S(lang, 'tip_received'), parse_mode="HTML")
        return True, item_summary
    except Exception as e:
        logging.error(f"Error in fulfill_payment for {uid}: {e}")
        return False, item_summary

_book_prompt_lock = threading.Lock()
_last_book_prompt = {}

def send_book_checkout_prompt(uid_int, book_key, mode):
    try:
        import time as _time
        now_ts = _time.time()
        with _book_prompt_lock:
            prev = _last_book_prompt.get(uid_int)
            if prev and prev[0] == book_key and prev[1] == mode and (now_ts - prev[2]) < 5.0:
                return True
            _last_book_prompt[uid_int] = (book_key, mode, now_ts)

        rand_suffix = uuid.uuid4().hex[:6].upper()
        b_title = BOOK_TITLES.get(book_key, book_key)
        if mode == 'rent':
            amount = 149
            plan_label = "የ 10 ቀናት ኪራይ (149 ብር)"
            tx_ref = f"BAYA-{uid_int}-BOOKRENT_{book_key}-MANUAL-{rand_suffix}"
        elif mode == 'extend':
            amount = 49
            plan_label = "ተጨማሪ 5 ቀናት ኪራይ (49 ብር)"
            tx_ref = f"BAYA-{uid_int}-BOOKEXT_{book_key}-MANUAL-{rand_suffix}"
        else:
            amount = 399
            plan_label = "ሙሉ መጽሐፍ ግዢ — ለዘላለም (399 ብር)"
            tx_ref = f"BAYA-{uid_int}-BOOK_{book_key}-MANUAL-{rand_suffix}"

        database.record_payment(uid_int, 0, amount, tx_ref, "PENDING_CHECKOUT", status="pending")

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📖 ወደ መጻሕፍት ቤት ተመለስ (Library)", web_app=WebAppInfo(url=f"{config.BASE_URL}/app?uid={uid_int}"))
        )

        msg_text = (
            f"📚 <b>የተመረጠው መጽሐፍ ዝርዝር</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 <b>መጽሐፍ:</b> «{b_title}»\n"
            f"💳 <b>የተመረጠው ዓይነት:</b> {plan_label}\n"
            f"💰 <b>የሚከፈለው ዋጋ:</b> {amount} ብር\n\n"
            f"🏦 <b>CBE (ንግድ ባንክ):</b> <code>1000073164765</code>\n"
            f"🏦 <b>CBE Birr (ሲቢኢ ብር):</b> <code>0912689900</code>\n"
            f"📱 <b>ቴሌብር (Telebirr):</b> <code>0912689900</code>\n"
            f"👤 <b>ስም:</b> በኃይሉ ጌታቸው\n\n"
            f"📸 <b>የከፈሉበትን የ{amount} ብር ደረሰኝ (Screenshot) በቀጥታ እዚሁ ቻት ላይ ይላኩልን!</b> ሲስተማችን በሰከንዶች ውስጥ አረጋግጦ መጽሐፉን ይከፍትልዎታል።"
        )
        bot.send_message(uid_int, msg_text, parse_mode="HTML", reply_markup=markup)
        return True
    except Exception as e:
        logging.error(f"Failed to send book checkout prompt to {uid_int}: {e}")
        return False

@bot.message_handler(commands=["unlock_book"])
def cmd_unlock_book(message):
    if not is_admin(message.from_user):
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(
            message,
            "Usage: <code>/unlock_book @username narcissist</code> (permanent) or <code>/unlock_book @username narcissist 10</code> (10-day rental)",
            parse_mode="HTML"
        )
        return
    target = args[1].strip()
    book_key = args[2].strip().lower()
    days = int(args[3]) if len(args) >= 4 and args[3].isdigit() else None
    try:
        uid = int(target)
    except ValueError:
        u_rec = database.get_user_by_username(target.lstrip('@'))
        uid = u_rec['user_id'] if u_rec else None
    if not uid:
        bot.reply_to(message, f"❌ User <code>{target}</code> not found.", parse_mode="HTML")
        return
    database.unlock_book(uid, book_key, days=days)
    b_title = BOOK_TITLES.get(book_key, book_key)
    mode_str = f"for {days} days (Rental)" if days else "Permanently (Full)"
    bot.reply_to(message, f"✅ Unlocked <b>{b_title}</b> {mode_str} for user <code>{uid}</code>!", parse_mode="HTML")
    notify_user_book_unlocked(uid, book_key, days=days)

@bot.message_handler(commands=["add_subadmin"])
def cmd_add_subadmin(message):
    if not is_owner(message.from_user):
        bot.reply_to(message, "❌ Only the owner can add sub-admins.")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: <code>/add_subadmin @username</code> or <code>/add_subadmin user_id</code>", parse_mode="HTML")
        return
    target = args[1].strip()
    uid = database.add_sub_admin_by_identifier(target)
    if uid:
        setup_admin_menu(uid)
        bot.reply_to(message, f"✅ User <code>{target}</code> (ID: <code>{uid}</code>) is now a <b>Sub-Admin</b>!", parse_mode="HTML")
        try:
            bot.send_message(
                uid,
                "👑 <b>እንኳን ደስ አሎት! የ Sub-Admin መብት ተሰጥቶዎታል።</b>\n\nከታች ባለው ሜኑ <b>'⚙️ Dashboard'</b> እና <b>'📚 መጻሕፍት ቤት (Library)'</b> ማግኘት ይችላሉ። እንዲሁም /bayacontrol ን መጠቀም ይችላሉ!",
                parse_mode="HTML",
                reply_markup=get_bottom_markup(get_lang(uid), uid)
            )
        except:
            pass
    else:
        bot.reply_to(message, f"❌ User <code>{target}</code> not found in database. Make sure they have messaged or started the bot first!", parse_mode="HTML")

@bot.message_handler(commands=["remove_subadmin"])
def cmd_remove_subadmin(message):
    if not is_owner(message.from_user):
        bot.reply_to(message, "❌ Only the owner can remove sub-admins.")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: <code>/remove_subadmin @username</code> or <code>/remove_subadmin user_id</code>", parse_mode="HTML")
        return
    target = args[1].strip()
    try:
        uid = int(target)
    except ValueError:
        user_rec = database.get_user_by_username(target.lstrip('@'))
        uid = user_rec['user_id'] if user_rec else None
    if uid:
        database.remove_sub_admin(uid)
        try:
            bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=uid))
        except:
            pass
        bot.reply_to(message, f"✅ Sub-Admin removed for <code>{target}</code>.", parse_mode="HTML")
        try:
            bot.send_message(
                uid,
                "Sub-Admin privileges removed.",
                reply_markup=get_bottom_markup(get_lang(uid), uid)
            )
        except:
            pass
    else:
        bot.reply_to(message, f"❌ User <code>{target}</code> not found.", parse_mode="HTML")

#  /bayacontrol COMMAND
# ══════════════════════════════════════════
@bot.message_handler(commands=["bayacontrol"])
def cmd_admin(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ የ Admin መብት የለዎትም!"); return
    uid = message.from_user.id
    setup_admin_menu(uid)
    # Refresh persistent bottom menu for admin & sub-admins with Dashboard & Library buttons!
    bot.send_message(
        message.chat.id,
        "👑 <b>Admin Menu</b>",
        parse_mode="HTML",
        reply_markup=get_bottom_markup(get_lang(uid), uid)
    )
    show_admin_menu(message.chat.id, message.from_user)

@bot.message_handler(commands=["lookup", "find"])
def cmd_lookup_user(message):
    if not is_admin(message.from_user):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        set_state(message.from_user.id, "ADMIN_SEARCH_USER")
        bot.send_message(
            message.chat.id,
            "🔍 <b>User Lookup</b>\n\n"
            "Send any of the following:\n"
            "• 👤 <b>Telegram Name</b> (e.g. <code>Selam</code> or <code>ሰላም</code>)\n"
            "• 📛 <b>@username</b> or <code>t.me/username</code>\n"
            "• 🆔 <b>User ID</b>\n"
            "• ↩️ Or <b>forward a message</b> from the user\n\n"
            "<i>(/cancel to exit)</i>",
            parse_mode="HTML"
        )
        return
    perform_admin_user_lookup(message.chat.id, message.from_user, query_text=parts[1].strip())

def send_admin_user_profile(chat_id, target_id, caller_user):
    details = database.get_user_details(target_id)
    if not details:
        bot.send_message(chat_id, "❌ User not found.")
        return False
    u = details["user"]
    banned_tag = " 🚫 BANNED" if database.is_banned(target_id) else ""
    admin_tag = " 👑" if database.is_sub_admin(target_id) else ""
    vip_tag = " 💎 VIP" if database.is_vip(target_id) else ""

    gender_str = {"male": "👨 Male", "female": "👩 Female"}.get(u.get('gender'), '❓ Unknown')

    vip_expiry = u.get('vip_expiry') or 'N/A'
    if vip_expiry != 'N/A':
        vip_expiry = vip_expiry[:10]

    msgs_left = u.get('advice_messages_left', 0)

    ubooks, urentals, uexpired = database.get_user_books_state(target_id)
    if ubooks or uexpired:
        books_lines = []
        for bk in ubooks:
            bt = BOOK_TITLES.get(bk, bk)
            if bk in urentals:
                books_lines.append(f"  ⏳ {bt} (Rental: {urentals[bk]}d left)")
            else:
                books_lines.append(f"  ✅ {bt} (Full)")
        for bk in uexpired:
            bt = BOOK_TITLES.get(bk, bk)
            books_lines.append(f"  ⏰ {bt} (Expired Rental)")
        books_text = "\n".join(books_lines) + "\n"
    else:
        books_text = "  — No books unlocked\n"

    payments_text = ""
    for p in details.get("recent_payments", []):
        tx = p['tx_ref'] or ''
        ptype = '☕ Tip' if 'TIP' in tx else '🧠 Advice' if 'ADVICE' in tx else '📚 Book' if 'BOOK' in tx else '📦 Other'
        payments_text += f"  {ptype} — <b>{p['amount']:,} ETB</b> ({p['payment_date'][:10] if p['payment_date'] else 'N/A'})\n"
    if not payments_text:
        payments_text = "  — No payments yet\n"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("↩️ Reply", callback_data=f"adm_reply_{target_id}"),
        InlineKeyboardButton("💵 Add Payment", callback_data=f"adm_record_pay_{target_id}")
    )
    markup.add(
        InlineKeyboardButton("📚 Push Book (Free / 10d Rent)", callback_data=f"adm_push_book_menu_{target_id}")
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
    if is_owner(caller_user):
        if database.is_sub_admin(target_id):
            markup.add(InlineKeyboardButton("👮 Remove Sub-Admin", callback_data=f"adm_rmsub_{target_id}"))
        else:
            markup.add(InlineKeyboardButton("👮 Make Sub-Admin", callback_data=f"adm_mksub_{target_id}"))
    markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))

    uname_disp = f"@{u['username']}" if u.get('username') and u.get('username') != 'Unknown' else "N/A"
    bot.send_message(
        chat_id,
        f"👤 <b>User Profile</b>{banned_tag}{admin_tag}{vip_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"👤 Name: <b>{html.escape(str(u.get('first_name') or 'User'))}</b>\n"
        f"📛 Username: {html.escape(uname_disp)}\n"
        f"{gender_str} | 🌐 {u.get('bot_language', 'am').upper()}\n"
        f"📅 Joined: {u['joined_date'][:10] if u.get('joined_date') else 'N/A'}\n\n"
        f"━━ 📚 Books ━━━━━━━━━━━━━━━\n{books_text}\n"
        f"━━ 💬 Advice ━━━━━━━━━━━━━━\n"
        f"  📩 Messages Left: <b>{msgs_left}</b>\n"
        f"  💎 VIP Until: <b>{vip_expiry}</b>\n\n"
        f"━━ 💰 Payments ━━━━━━━━━━━━\n"
        f"  💵 Total Paid: <b>{details['total_paid']:,} ETB</b> ({details['payment_count']} transactions)\n"
        f"  👥 Referrals: <b>{details['referral_count']}</b>\n\n"
        f"━━ 💳 Recent Payments ━━━━━━\n{payments_text}",
        parse_mode="HTML",
        reply_markup=markup,
    )
    return True

def perform_admin_user_lookup(chat_id, caller_user, query_text="", forwarded_msg=None):
    """Search by Telegram Name, @username, User ID, or forwarded message."""
    if forwarded_msg is not None:
        fwd_user = getattr(forwarded_msg, "forward_from", None)
        fwd_origin = getattr(forwarded_msg, "forward_origin", None)
        if not fwd_user and fwd_origin:
            fwd_user = getattr(fwd_origin, "sender_user", None)
        if fwd_user and getattr(fwd_user, "id", None):
            # Sync their latest name/username if they exist in DB
            database.sync_user_profile(fwd_user.id, getattr(fwd_user, "username", None), get_full_name(fwd_user))
            if database.get_user(fwd_user.id):
                send_admin_user_profile(chat_id, fwd_user.id, caller_user)
                return True
            query_text = get_full_name(fwd_user)
        else:
            sender_name = getattr(forwarded_msg, "forward_sender_name", None)
            if not sender_name and fwd_origin:
                sender_name = getattr(fwd_origin, "sender_user_name", None)
            if sender_name:
                query_text = sender_name

    query_text = (query_text or "").strip()
    if not query_text:
        bot.send_message(chat_id, "❌ Please send a Telegram name, @username, User ID, or forward a message from the user (/cancel to exit).")
        return False

    results = database.search_users(query_text)
    if not results:
        bot.send_message(
            chat_id,
            f"❌ No users found matching <b>{html.escape(query_text)}</b>.\n\n"
            f"Try part of their Telegram name, @username, or User ID (or /cancel):",
            parse_mode="HTML"
        )
        return False

    if len(results) == 1:
        send_admin_user_profile(chat_id, results[0]["user_id"], caller_user)
        return True

    text = f"🔍 <b>Search Results for \"{html.escape(query_text)}\" ({len(results)})</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    markup = InlineKeyboardMarkup(row_width=1)
    for u in results:
        fname = u.get("first_name") or "User"
        uname = u.get("username")
        uname_str = f"@{uname}" if uname and uname != "Unknown" else "no username"
        g_icon = {"male": "👨", "female": "👩"}.get(u.get("gender"), "👤")
        text += f"{g_icon} <b>{html.escape(str(fname))}</b> ({html.escape(uname_str)}) — <code>{u['user_id']}</code>\n"
        btn_label = f"{g_icon} {fname} ({uname_str}) — {u['user_id']}"
        markup.add(InlineKeyboardButton(btn_label[:60], callback_data=f"adm_lookup_{u['user_id']}"))
    markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    return True

def run_refresh_all_menus(chat_id_to_report):
    users = database.get_all_user_ids()
    total = len(users)
    bot.send_message(
        chat_id_to_report,
        f"🔄 <b>Starting Silent Menu Refresh for all {total} users...</b>\n"
        f"Keyboards will be updated silently without sending announcement messages.",
        parse_mode="HTML"
    )

    def worker():
        import time
        from telebot.apihelper import ApiTelegramException
        success, failed = 0, 0
        for u in users:
            try:
                u_lang = database.get_bot_language(u) or 'am'
                # Silently deliver updated persistent reply keyboard and delete temporary message immediately
                sent = bot.send_message(
                    u,
                    "🔄",
                    reply_markup=get_bottom_markup(u_lang, u),
                    disable_notification=True
                )
                try:
                    bot.delete_message(u, sent.message_id)
                except Exception:
                    pass
                success += 1
                database.mark_user_blocked(u, 0)
            except ApiTelegramException as ate:
                if ate.error_code == 429:
                    retry_after = getattr(ate, 'result_json', {}).get('parameters', {}).get('retry_after', 3)
                    time.sleep(retry_after)
                    try:
                        sent = bot.send_message(
                            u,
                            "🔄",
                            reply_markup=get_bottom_markup(u_lang, u),
                            disable_notification=True
                        )
                        try:
                            bot.delete_message(u, sent.message_id)
                        except Exception:
                            pass
                        success += 1
                        database.mark_user_blocked(u, 0)
                    except Exception:
                        failed += 1
                else:
                    failed += 1
                    database.mark_user_blocked(u, 1)
            except Exception:
                failed += 1
                database.mark_user_blocked(u, 1)
            time.sleep(0.08)  # Safe delay to prevent rate limits
            
        try:
            bot.send_message(
                chat_id_to_report,
                f"✅ <b>All Keyboards Refreshed Silently!</b>\n\n"
                f"✔️ <b>{success}</b> users refreshed\n"
                f"❌ <b>{failed}</b> users skipped (blocked/inactive)\n\n"
                f"<i>No messages or notifications were sent to users.</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()

@bot.message_handler(commands=["refresh_menus", "refresh_menu"])
def cmd_refresh_menus(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!")
        return
    run_refresh_all_menus(message.chat.id)

@bot.message_handler(commands=["dashboard", "admin_dashboard"])
def cmd_open_admin_dashboard(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!")
        return
    dash_url = f"{config.BASE_URL}/admin_dashboard?token={config.ADMIN_SECRET_KEY}"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Open Admin Dashboard", web_app=WebAppInfo(url=dash_url)),
        InlineKeyboardButton("🌐 Open in Web Browser", url=dash_url),
        InlineKeyboardButton("📚 Rentals Manager", callback_data="adm_rentals_menu")
    )
    bot.send_message(
        message.chat.id,
        "👑 <b>BAYA SUITE UNIFIED ADMIN DASHBOARD</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Tap below to launch the all-in-one web management suite:\n\n"
        "• <b>Analytics & Finance:</b> Real-time revenue & KPIs\n"
        "• <b>Rentals Manager:</b> Extend, convert, or revoke\n"
        "• <b>User Directory:</b> Inspect profiles & advice quota\n"
        "• <b>Payments Audit:</b> Search, verify, or delete logs\n"
        "• <b>Cart Recovery:</b> Automated customer nudges\n"
        "• <b>Broadcast Center:</b> HTML editor with live preview\n"
        "• <b>System Maintenance:</b> Server logs & ghost cleanup",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.message_handler(commands=["author", "publish", "authors"])
def cmd_author_portal(message):
    uid = message.from_user.id
    username = message.from_user.username
    author = database.get_author_by_telegram_id(uid, username)
    
    if author:
        if not author.get('telegram_id'):
            conn = database.get_connection()
            c = conn.cursor()
            c.execute("UPDATE authors SET telegram_id = ? WHERE author_id = ?", (uid, author['author_id']))
            conn.commit()
            conn.close()
            
        portal_url = f"{config.BASE_URL}/author_dashboard?token={author['access_token']}"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🚀 Launch Author Dashboard", web_app=WebAppInfo(url=portal_url)),
            InlineKeyboardButton("🌐 Open in Web Browser", url=portal_url)
        )
        pen_name = author.get('pen_name') or author.get('name') or 'Author'
        bot.reply_to(
            message,
            f"✍️ <b>WELCOME TO YOUR AUTHOR DASHBOARD</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Hello, <b>{pen_name}</b>!\n\n"
            f"• <b>Author Key:</b> <code>{author['access_token']}</code>\n"
            f"• <b>Royalty Rate:</b> <code>{author.get('royalty_percentage', 70)}%</code>\n\n"
            f"Tap below to view your sales analytics, submit new books, and request payouts:",
            parse_mode="HTML",
            reply_markup=markup
        )
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("💬 Apply as Author (@bayabooks)", url="https://t.me/bayabooks"),
            InlineKeyboardButton("🌐 Visit Author Portal", url=f"{config.BASE_URL}/author_dashboard")
        )
        bot.reply_to(
            message,
            f"✍️ <b>BAYA BOOKS AUTHOR & PUBLISHER PROGRAM</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Are you an author looking to publish and sell digital books across Ethiopia?\n\n"
            f"💎 <b>70% Author Royalty Share:</b> Transparent and fair.\n"
            f"📖 <b>High Reader Reach:</b> Bot & Telegram Mini App distribution.\n"
            f"⚡ <b>Flexible Models:</b> Full purchases & 5/10-day rentals.\n"
            f"💳 <b>Automated Payouts:</b> Fast withdrawals to CBE & Telebirr.\n\n"
            f"To register and receive your Author Access Key, contact our publisher team:",
            parse_mode="HTML",
            reply_markup=markup
        )

@bot.message_handler(commands=["rentals", "manage_rentals", "book_rentals"])
def cmd_manage_rentals(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ Admin only!")
        return
    send_rentals_admin_dashboard(message.chat.id, user=message.from_user)

def send_rentals_admin_dashboard(chat_id, user=None, call=None):
    data = database.get_all_rentals_management_data()
    s = data["summary"]
    
    text = (
        f"📚 <b>RENTED BOOKS MANAGEMENT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📖 <b>Active Rentals:</b> <code>{s['active_rentals']}</code>\n"
        f"⏳ <b>Expiring Soon (≤48h):</b> <code>{s['expiring_soon_rentals']}</code>\n"
        f"⌛ <b>Expired Rentals:</b> <code>{s['expired_rentals']}</code>\n"
        f"👑 <b>Lifetime Purchases:</b> <code>{s['lifetime_purchases']}</code>\n"
        f"📊 <b>Total Book Records:</b> <code>{s['total_records']}</code>\n\n"
        f"<i>Select a category to view readers, extend days, or grant access:</i>"
    )
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"🟢 Active ({s['active_rentals']})", callback_data="adm_rent_list_active_0"),
        InlineKeyboardButton(f"⏳ Expiring ({s['expiring_soon_rentals']})", callback_data="adm_rent_list_expiring_soon_0"),
    )
    markup.add(
        InlineKeyboardButton(f"⌛ Expired ({s['expired_rentals']})", callback_data="adm_rent_list_expired_0"),
        InlineKeyboardButton(f"👑 Lifetime ({s['lifetime_purchases']})", callback_data="adm_rent_list_lifetime_0"),
    )
    markup.add(
        InlineKeyboardButton("➕ Grant Book / Rental", callback_data="adm_rent_grant_start"),
    )
    markup.add(
        InlineKeyboardButton(
            "🌐 Open Web Rentals Dashboard",
            web_app=WebAppInfo(url=f"{config.BASE_URL}/admin_dashboard?token={config.ADMIN_SECRET_KEY}#rentals")
        )
    )
    markup.add(
        InlineKeyboardButton("🔄 Refresh", callback_data="adm_rentals_menu"),
        InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back")
    )
    
    if call:
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def send_rentals_list_page(chat_id, category, page, call=None):
    data = database.get_all_rentals_management_data()
    all_rentals = data["rentals"]
    
    filtered = [r for r in all_rentals if r["status"] == category]
    total_items = len(filtered)
    page_size = 6
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))
    
    cat_titles = {
        "active": "🟢 Active Rentals",
        "expiring_soon": "⏳ Expiring Soon (≤48h)",
        "expired": "⌛ Expired Rentals",
        "lifetime": "👑 Lifetime Purchases"
    }
    header_title = cat_titles.get(category, "Books")
    
    text = (
        f"📚 <b>{header_title}</b> (Page {page + 1}/{total_pages})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Total: <b>{total_items}</b> records\n\n"
        f"<i>Tap any reader below to extend days, convert to lifetime, or manage:</i>"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    page_items = filtered[page * page_size : (page + 1) * page_size]
    
    for r in page_items:
        uid = r["user_id"]
        bkey = r["book_key"]
        fname = r["first_name"] or "User"
        btitle = r["book_title"].split("(")[0].strip()
        
        if r["status"] == "lifetime":
            badge = "👑 Full"
        elif r["status"] == "expiring_soon":
            badge = f"⏳ {r['hours_left']}h left"
        elif r["status"] == "active":
            badge = f"🟢 {r['days_left']}d left"
        else:
            badge = "⌛ Expired"
            
        btn_text = f"{fname} — {btitle} ({badge})"
        markup.add(InlineKeyboardButton(btn_text[:55], callback_data=f"adm_rent_det_{uid}_{bkey}"))
        
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"adm_rent_list_{category}_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"adm_rent_list_{category}_{page + 1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
        
    markup.add(InlineKeyboardButton("🔙 Back to Rentals Menu", callback_data="adm_rentals_menu"))
    
    if call:
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def send_rental_detail_card(chat_id, target_uid, bkey, call=None):
    data = database.get_all_rentals_management_data()
    match = None
    for r in data["rentals"]:
        if r["user_id"] == target_uid and r["book_key"] == bkey:
            match = r
            break
            
    if not match:
        bot.send_message(chat_id, "❌ Rental record not found or already revoked.")
        return
        
    uname_str = f"@{match['username']}" if match['username'] else "No username"
    blocked_str = " (⚠️ User blocked bot)" if match['bot_blocked'] else ""
    
    text = (
        f"📖 <b>Reader Rental Details</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Reader: <b>{html.escape(match['first_name'])}</b> ({uname_str})\n"
        f"🆔 User ID: <code>{target_uid}</code>{blocked_str}\n"
        f"📚 Book: <b>{match['book_title']}</b>\n"
        f"🏷️ Status: <b>{match['status_label']}</b>\n"
        f"📅 Started On: <code>{match['purchased_at'][:16] if match['purchased_at'] else 'N/A'}</code>\n"
        f"⏳ Expiration: <code>{match['expires_at'][:16] if match['expires_at'] else 'Permanent (Lifetime)'}</code>\n\n"
        f"<i>Select an action below:</i>"
    )
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ +5 Days Ext", callback_data=f"adm_rent_act_{target_uid}_{bkey}_ext5"),
        InlineKeyboardButton("➕ +10 Days Ext", callback_data=f"adm_rent_act_{target_uid}_{bkey}_ext10"),
    )
    if match["status"] != "lifetime":
        markup.add(
            InlineKeyboardButton("👑 Make Lifetime (Full)", callback_data=f"adm_rent_act_{target_uid}_{bkey}_life"),
            InlineKeyboardButton("🔔 Send Reminder", callback_data=f"adm_rent_act_{target_uid}_{bkey}_nudge"),
        )
        markup.add(
            InlineKeyboardButton("⌛ Expire Now", callback_data=f"adm_rent_act_{target_uid}_{bkey}_exp"),
            InlineKeyboardButton("🗑️ Revoke Book", callback_data=f"adm_rent_act_{target_uid}_{bkey}_rev"),
        )
    else:
        markup.add(
            InlineKeyboardButton("🗑️ Revoke Book", callback_data=f"adm_rent_act_{target_uid}_{bkey}_rev"),
        )
    markup.add(InlineKeyboardButton("🔙 Back to Rentals", callback_data="adm_rentals_menu"))
    
    if call:
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

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
        InlineKeyboardButton("📱 TikTok Card Creator (4:5)", callback_data="adm_tiktok_init"),
        InlineKeyboardButton("💳 Add Credit/Msgs", callback_data="admin_credit"),
    )
    markup.add(
        InlineKeyboardButton("👑 Sub-Admins", callback_data="adm_subadmin_menu"),
        InlineKeyboardButton("🚫 Ban/Unban", callback_data="adm_ban_menu"),
    )
    markup.add(
        InlineKeyboardButton("👑 VIP Manager", callback_data="adm_vip_menu"),
        InlineKeyboardButton("📚 Manage Rented Books", callback_data="adm_rentals_menu"),
    )
    markup.add(
        InlineKeyboardButton("🔄 Refresh All Keyboards", callback_data="adm_refresh_menus"),
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
    if is_admin_uid(uid):
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
    database.sync_user_profile(uid, call.from_user.username, get_full_name(call.from_user))

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
            
        bot.answer_callback_query(call.id)
        purpose = f"ADVICE_{pkg}"
        import uuid
        tx_ref = f"BAYA-{uid}-{purpose}-MANUAL-{uuid.uuid4().hex[:6]}"
        
        database.record_payment(uid, None, amount, tx_ref, 'PENDING_CHECKOUT', status='pending')

        text = f"📱 <b>ክፍያ - {amount} ብር (Payment)</b>\n━━━━━━━━━━━━━━━━━━━━\n\nእባክዎ <b>{amount} ብር</b> በቀጥታ በሚከተሉት አማራጮች ያስገቡ (Please transfer to):\n\n🏦 <b>CBE (ንግድ ባንክ):</b> <code>1000073164765</code>\n🏦 <b>CBE Birr (ሲቢኢ ብር):</b> <code>0912689900</code>\n📱 <b>ቴሌብር (Telebirr):</b> <code>0912689900</code>\n👤 <b>ስም:</b> በኃይሉ ጌታቸው (Behailu Getachew)\n\n✅ <b>ከከፈሉ በኋላ (After Paying)፡</b>\nየከፈሉበትን ደረሰኝ (Screenshot) በቀጥታ እዚሁ ቻት ላይ ይላኩልን። ሲስተማችን በሰከንዶች ውስጥ አረጋግጦ አካውንትዎን ይከፍትልዎታል! (Send the screenshot here to unlock instantly!)"

        bot.send_message(chat_id, text, parse_mode="HTML")
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
        bot.answer_callback_query(call.id)
        import uuid
        tx_ref = f"BAYA-{uid}-TIP-MANUAL-{uuid.uuid4().hex[:6]}"
        
        database.record_payment(uid, None, amount, tx_ref, 'PENDING_CHECKOUT', status='pending')

        text = f"☕ <b>ስጦታ - {amount} ብር (Tip)</b>\n━━━━━━━━━━━━━━━━━━━━\n\nእባክዎ <b>{amount} ብር</b> በቀጥታ በሚከተሉት አማራጮች ያስገቡ (Please transfer to):\n\n🏦 <b>CBE (ንግድ ባንክ):</b> <code>1000073164765</code>\n🏦 <b>CBE Birr (ሲቢኢ ብር):</b> <code>0912689900</code>\n📱 <b>ቴሌብር (Telebirr):</b> <code>0912689900</code>\n👤 <b>ስም:</b> በኃይሉ ጌታቸው (Behailu Getachew)\n\n✅ <b>ከከፈሉ በኋላ (After Paying)፡</b>\nየከፈሉበትን ደረሰኝ (Screenshot) በቀጥታ እዚሁ ቻት ላይ ይላኩልን። ሲስተማችን አረጋግጦ ስጦታዎን ይቀበላል! (Send the screenshot here!)"

        bot.send_message(chat_id, text, parse_mode="HTML")
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
            ptype = {"Tip": "☕", "Advice": "🧠", "Book": "📚", "Other": "📦"}.get(p.get("type", ""), "📦")
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
            f"💬 Chatting Users: <b>{stats.get('active_advice_users', 0)}</b>\n"
            f"📚 Books Unlocked: <b>{stats.get('total_books_unlocked', 0)}</b> (⏳ Active Rentals: <b>{stats.get('active_book_rentals', 0)}</b>)\n\n"
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

    if data.startswith("adm_reply_"):
        if not is_admin(call.from_user): return
        target_uid = data.split("_")[2]
        set_state(uid, f"ADMIN_REPLY_{target_uid}")
        bot.send_message(chat_id, f"📝 <b>Reply to User {target_uid}</b>\n\nType your message below (/cancel to abort):", parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if data.startswith("adm_rec_appr_"):
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return
        parts = data.split("_")
        target_uid = int(parts[3])
        pending_id = int(parts[4])
        
        payment = database.get_payment(pending_id)
        if not payment:
            bot.answer_callback_query(call.id, "❌ Payment record not found.", show_alert=True)
            return
        if payment["status"] == "approved":
            bot.answer_callback_query(call.id, "⚠️ Already approved!", show_alert=True)
            try:
                bot.edit_message_caption(
                    caption=(call.message.caption or "") + "\n\n⚠️ <i>(Already approved earlier)</i>",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return
            
        admin_uname = f"@{call.from_user.username}" if call.from_user.username else (call.from_user.first_name or "Admin")
        import uuid
        tx_ref = payment["tx_ref"]
        order_id = payment["order_id"] or f"ORDER-{uuid.uuid4().hex[:8].upper()}"
        receipt_ref = f"MANUAL_ADMIN_{call.from_user.id}"
        
        success, item_summary = fulfill_payment(target_uid, tx_ref, order_id=order_id, receipt_ref=receipt_ref)
        bot.answer_callback_query(call.id, f"✅ Approved for user {target_uid}!", show_alert=True)
        
        new_caption = (
            f"✅ <b>Approved by {admin_uname}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 User ID: <code>{target_uid}</code>\n"
            f"📦 Item: <b>{item_summary}</b>\n"
            f"💵 Amount: <b>{payment['amount']:,} ETB</b>\n"
            f"🧾 Status: <b>Activated</b>"
        )
        try:
            bot.edit_message_caption(
                caption=new_caption,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="HTML",
                reply_markup=None
            )
        except Exception as e:
            logging.error(f"Failed to edit admin review caption: {e}")
        return

    if data.startswith("adm_rec_rej_"):
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return
        parts = data.split("_")
        target_uid = int(parts[3])
        pending_id = int(parts[4])
        
        payment = database.get_payment(pending_id)
        if payment and payment["status"] == "approved":
            bot.answer_callback_query(call.id, "⚠️ Already approved! Cannot reject.", show_alert=True)
            return
            
        database.reject_payment(pending_id)
        admin_uname = f"@{call.from_user.username}" if call.from_user.username else (call.from_user.first_name or "Admin")
        bot.answer_callback_query(call.id, f"❌ Rejected payment {pending_id}", show_alert=True)
        
        target_lang = get_lang(target_uid)
        try:
            bot.send_message(target_uid, S(target_lang, 'receipt_rejected_user'), parse_mode="HTML")
        except Exception as e:
            logging.error(f"Failed to notify user {target_uid} of payment rejection: {e}")
            
        new_caption = (
            f"❌ <b>Rejected by {admin_uname}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 User ID: <code>{target_uid}</code>\n"
            f"💵 Amount: <b>{payment['amount'] if payment else 'N/A'} ETB</b>\n"
            f"🧾 Status: <b>Rejected (User Notified)</b>"
        )
        try:
            bot.edit_message_caption(
                caption=new_caption,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="HTML",
                reply_markup=None
            )
        except Exception as e:
            logging.error(f"Failed to edit admin review caption: {e}")
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
        database.set_vip(target_uid, days=days)
        bot.answer_callback_query(call.id, f"Made VIP for {days} days", show_alert=True)
        bot.send_message(target_uid, f"🎉 <b>እንኳን ደስ አለዎት!</b>\nለ {days} ቀናት VIP ሆነዋል!", parse_mode="HTML")
        return

    if data.startswith("adm_push_book_menu_"):
        if not is_admin(call.from_user): return
        target_uid = int(data.replace("adm_push_book_menu_", ""))
        bot.answer_callback_query(call.id)
        ubooks, _, uexpired = database.get_user_books_state(target_uid)
        active_or_exp = set(ubooks + uexpired)
        markup = InlineKeyboardMarkup(row_width=3)
        for bkey, btitle in BOOK_TITLES.items():
            short_t = btitle.split("(")[0].strip()
            markup.add(
                InlineKeyboardButton(f"💎 {short_t} (Full)", callback_data=f"adm_pushbook_{target_uid}_{bkey}_0"),
                InlineKeyboardButton(f"⏳ 10d Rent", callback_data=f"adm_pushbook_{target_uid}_{bkey}_10"),
                InlineKeyboardButton(f"➕ +5d Ext", callback_data=f"adm_pushbook_{target_uid}_{bkey}_5")
            )
            if bkey in active_or_exp:
                markup.add(
                    InlineKeyboardButton(f"⏰ Expire {short_t}", callback_data=f"adm_pushbook_{target_uid}_{bkey}_-1"),
                    InlineKeyboardButton(f"🗑 Revoke {short_t}", callback_data=f"adm_pushbook_{target_uid}_{bkey}_-99")
                )
        markup.add(InlineKeyboardButton("🔙 Back to User", callback_data=f"adm_lookup_{target_uid}"))
        bot.send_message(
            chat_id,
            f"📚 <b>Push Book to User <code>{target_uid}</code></b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Choose a book to unlock for this customer:\n"
            f"• <b>Full</b> = Permanent Full Book (399 ETB)\n"
            f"• <b>10d Rent</b> = 10-Day Rental (149 ETB)\n"
            f"• <b>+5d Ext</b> = +5 Days Extension (49 ETB)",
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    if data.startswith("adm_pushbook_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[2])
        bkey = parts[3]
        days = int(parts[4]) if len(parts) > 4 else 0
        b_title = BOOK_TITLES.get(bkey, bkey)
        if days == -99:
            database.remove_user_book(target_uid, bkey)
            bot.answer_callback_query(call.id, f"🗑 Revoked {b_title}!", show_alert=True)
            bot.send_message(chat_id, f"🗑 <b>Book Revoked!</b>\n📖 <b>{b_title}</b> removed from user <code>{target_uid}</code>.", parse_mode="HTML")
            return
        elif days < 0:
            database.unlock_book(target_uid, bkey, days=-1)
            bot.answer_callback_query(call.id, f"⏰ Marked {b_title} as Expired Rental!", show_alert=True)
            bot.send_message(chat_id, f"⏰ <b>Rental Expired!</b>\n📖 <b>{b_title}</b> set to expired state for user <code>{target_uid}</code>.", parse_mode="HTML")
            return
        rent_days = days if days != 0 else None
        database.unlock_book(target_uid, bkey, days=rent_days)
        mode_label = f"{days}-Day Rental" if rent_days else "Full Permanent"
        bot.answer_callback_query(call.id, f"✅ Pushed {b_title} ({mode_label})!", show_alert=True)
        bot.send_message(
            chat_id,
            f"✅ <b>Book Pushed!</b>\n📖 <b>{b_title}</b> ({mode_label}) unlocked for user <code>{target_uid}</code>.",
            parse_mode="HTML"
        )
        notify_user_book_unlocked(target_uid, bkey, days=rent_days)
        return

    if data == "adm_back":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        show_admin_menu(chat_id, call.from_user)
        return

    if data == "adm_refresh_menus":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "🔄 Starting refresh...", show_alert=False)
        run_refresh_all_menus(chat_id)
        return

    # ── Admin: Rented Books Management ────────
    if data == "adm_rentals_menu":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        send_rentals_admin_dashboard(chat_id, call=call)
        return

    if data.startswith("adm_rent_list_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        cat = parts[3]
        page = int(parts[4])
        bot.answer_callback_query(call.id)
        send_rentals_list_page(chat_id, cat, page, call=call)
        return

    if data.startswith("adm_rent_det_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        bkey = parts[4]
        bot.answer_callback_query(call.id)
        send_rental_detail_card(chat_id, target_uid, bkey, call=call)
        return

    if data.startswith("adm_rent_act_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        bkey = parts[4]
        act = parts[5]
        b_title = BOOK_TITLES.get(bkey, bkey)
        
        if act == "ext5":
            new_exp = database.extend_rental_days(target_uid, bkey, 5)
            bot.answer_callback_query(call.id, f"✅ Extended +5 days (Expires: {new_exp[:10] if new_exp else 'N/A'})", show_alert=True)
            try:
                bot.send_message(target_uid, f"🎉 <b>የንባብ ጊዜ ተራዝሟል!</b>\n\n📖 የ <b>«{b_title}»</b> የኪራይ ጊዜዎ በ <b>+5 ቀናት</b> ተራዝሟል!\nመልካም ንባብ! 📚✨", parse_mode="HTML")
            except Exception: pass
            send_rental_detail_card(chat_id, target_uid, bkey, call=call)
            return
        elif act == "ext10":
            new_exp = database.extend_rental_days(target_uid, bkey, 10)
            bot.answer_callback_query(call.id, f"✅ Extended +10 days (Expires: {new_exp[:10] if new_exp else 'N/A'})", show_alert=True)
            try:
                bot.send_message(target_uid, f"🎉 <b>የንባብ ጊዜ ተራዝሟል!</b>\n\n📖 የ <b>«{b_title}»</b> የኪራይ ጊዜዎ በ <b>+10 ቀናት</b> ተራዝሟል!\nመልካም ንባብ! 📚✨", parse_mode="HTML")
            except Exception: pass
            send_rental_detail_card(chat_id, target_uid, bkey, call=call)
            return
        elif act == "life":
            database.convert_book_to_lifetime(target_uid, bkey)
            bot.answer_callback_query(call.id, f"👑 Converted to Lifetime!", show_alert=True)
            try:
                bot.send_message(target_uid, f"👑 <b>የቋሚ ባለቤትነት ስጦታ!</b>\n\n📖 የ <b>«{b_title}»</b> መጽሐፍ <b>ለዘላለም በቋሚነት (Lifetime)</b> ተከፍቶልዎታል!\nበማንኛውም ጊዜ ገብተው ሙሉውን መጽሐፍ ማንበብ ይችላሉ! 📚✨", parse_mode="HTML")
            except Exception: pass
            send_rental_detail_card(chat_id, target_uid, bkey, call=call)
            return
        elif act == "nudge":
            try:
                nudge_txt = (
                    f"⏳ <b>የመጽሐፍ ኪራይ ማሳሰቢያ</b>\n\n"
                    f"ውድ አንባቢ፣ የ <b>«{b_title}»</b> መጽሐፍ የኪራይ ጊዜዎ በቅርቡ ያበቃል!\n\n"
                    f"ንባብዎን ሳይቋረጥ ለመቀጠል ወይም በቋሚነት ለመግዛት ቦቱን ይጠቀሙ ወይም አስተዳዳሪውን ያነጋግሩ። 📚"
                )
                bot.send_message(target_uid, nudge_txt, parse_mode="HTML")
                bot.answer_callback_query(call.id, "🔔 Reminder sent to reader!", show_alert=True)
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Failed to send (User blocked): {e}", show_alert=True)
            return
        elif act == "exp":
            database.expire_book_rental_now(target_uid, bkey)
            bot.answer_callback_query(call.id, "⌛ Rental marked as expired!", show_alert=True)
            send_rental_detail_card(chat_id, target_uid, bkey, call=call)
            return
        elif act == "rev":
            database.remove_user_book(target_uid, bkey)
            bot.answer_callback_query(call.id, "🗑️ Book access revoked!", show_alert=True)
            send_rentals_admin_dashboard(chat_id, call=call)
            return

    if data == "adm_rent_grant_start":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_RENT_GRANT_UID")
        bot.send_message(chat_id, "➕ <b>Grant Book / Rental</b>\n\nEnter the <b>Telegram User ID</b> of the reader:\n\n<i>(/cancel to abort)</i>", parse_mode="HTML")
        return

    if data.startswith("adm_rent_gbook_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        bkey = parts[4]
        b_title = BOOK_TITLES.get(bkey, bkey)
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⏳ 10 Days (Standard)", callback_data=f"adm_rent_gdur_{target_uid}_{bkey}_10"),
            InlineKeyboardButton("⏳ 5 Days (Short)", callback_data=f"adm_rent_gdur_{target_uid}_{bkey}_5"),
        )
        markup.add(
            InlineKeyboardButton("📅 30 Days (Extended)", callback_data=f"adm_rent_gdur_{target_uid}_{bkey}_30"),
            InlineKeyboardButton("👑 Lifetime (Permanent)", callback_data=f"adm_rent_gdur_{target_uid}_{bkey}_0"),
        )
        markup.add(InlineKeyboardButton("🔙 Back to Rentals", callback_data="adm_rentals_menu"))
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            f"📚 Book: <b>{b_title}</b>\n"
            f"👤 Target: <code>{target_uid}</code>\n\n"
            f"Choose duration:",
            parse_mode="HTML",
            reply_markup=markup
        )
        return

    if data.startswith("adm_rent_gdur_"):
        if not is_admin(call.from_user): return
        parts = data.split("_")
        target_uid = int(parts[3])
        bkey = parts[4]
        days = int(parts[5])
        b_title = BOOK_TITLES.get(bkey, bkey)
        
        rent_days = days if days > 0 else None
        database.unlock_book(target_uid, bkey, days=rent_days)
        mode_label = f"{days}-Day Rental" if rent_days else "Full Permanent (Lifetime)"
        
        bot.answer_callback_query(call.id, f"✅ Granted {b_title} ({mode_label})!", show_alert=True)
        bot.send_message(
            chat_id,
            f"✅ <b>Access Granted Successfully!</b>\n\n"
            f"📖 Book: <b>{b_title}</b>\n"
            f"⏳ Access: <b>{mode_label}</b>\n"
            f"👤 Reader ID: <code>{target_uid}</code>",
            parse_mode="HTML"
        )
        notify_user_book_unlocked(target_uid, bkey, days=rent_days)
        return
    
    # ── Admin: User Search ────────────────────
    if data == "adm_search":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_SEARCH_USER")
        bot.send_message(
            chat_id,
            "🔍 <b>User Lookup</b>\n\n"
            "Send any of the following:\n"
            "• 👤 <b>Telegram Name</b> (e.g. <code>Selam</code> or <code>ሰላም</code>)\n"
            "• 📛 <b>@username</b> or <code>t.me/username</code>\n"
            "• 🆔 <b>User ID</b>\n"
            "• ↩️ Or <b>forward a message</b> from the user\n\n"
            "<i>(/cancel to exit)</i>",
            parse_mode="HTML"
        )
        return
    
    # ── Admin: User Lookup (from inline button) ─
    if data.startswith("adm_lookup_"):
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_lookup_", ""))
        bot.answer_callback_query(call.id, "🔍 Loading...")
        send_admin_user_profile(chat_id, target_id, call.from_user)
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
            bot.send_message(
                target_id,
                "👑 <b>Congratulations!</b>\n\nYou have been granted Sub-Admin privileges!\nUse the new bottom menu buttons (⚙️ Dashboard & 📚 Library) or type /bayacontrol.",
                parse_mode="HTML",
                reply_markup=get_bottom_markup(get_lang(target_id), target_id)
            )
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
        bot.answer_callback_query(call.id, "🧠 Generating visual quote card...", show_alert=False)
        bot.send_chat_action(chat_id, 'typing')
        psych_obj = ai_engine.generate_psych_broadcast()
        
        hook_title = getattr(psych_obj, "title", "የዕለቱ የስነ-ልቦና ማስታወሻ")
        quote_text = getattr(psych_obj, "quote", str(psych_obj))
        tiktok_desc = getattr(psych_obj, "tiktok_desc", "")

        # Clean text for quote card
        clean_title = re.sub(r'<[^<]+>', '', hook_title).strip()
        clean_quote = re.sub(r'<[^<]+>', '', quote_text).strip()
        clean_tiktok_desc = re.sub(r'<[^<]+>', '', tiktok_desc).strip()

        ADMIN_PREVIEW_QUOTE[chat_id] = {
            "title": clean_title,
            "quote": clean_quote,
            "tiktok_desc": clean_tiktok_desc,
            "full_text": str(psych_obj)
        }
        
        card_bytes = None
        try:
            import quote_card
            card_bytes = quote_card.generate_quote_card(clean_quote, hook_title=clean_title)
        except Exception as e:
            logging.error(f"Failed to generate quote card in preview: {e}")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🚀 Verify & Broadcast (Card + Post)", callback_data="adm_confirm_auto_broadcast"))
        markup.add(InlineKeyboardButton("🔄 Refresh (Generate New)", callback_data="adm_auto_refresh"))
        markup.add(InlineKeyboardButton("🔙 Cancel", callback_data="adm_back"))
        
        caption_text = f"💡 <b>Auto Psychology Broadcast Preview</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<b>{clean_title}</b>\n\n{clean_quote}\n\n<i>(This visual quote card will be broadcasted to the Channel, Bot users, and Facebook!)</i>"
        
        if data == "adm_auto_refresh":
            safe_delete_message(chat_id, call.message.message_id)

        if card_bytes:
            import io
            bio = io.BytesIO(card_bytes)
            bio.name = "baya_quote_preview.png"
            bot.send_photo(chat_id, bio, caption=caption_text, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, caption_text, parse_mode="HTML", reply_markup=markup)
        return

    if data == "adm_confirm_auto_broadcast":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "🚀 Broadcasting photo card...", show_alert=False)
        
        # Extract the actual text generated
        original = call.message.caption or call.message.text or ""
        try:
            parts = original.split("━━━━━━━━━━━━━━━━━━━━\n\n")
            if len(parts) > 1:
                content = parts[1]
                for delim in ["\n\n<i>(This visual quote", "\n\n(This visual quote", "\n\n<i>(This is what", "\n\n(This is what"]:
                    if delim in content:
                        content = content.split(delim)[0]
                content = content.strip()
            else:
                content = original
        except Exception:
            content = original

        clean_content = re.sub(r'<[^<]+>', '', content).strip()
        
        preview_data = ADMIN_PREVIEW_QUOTE.get(chat_id)
        if isinstance(preview_data, dict):
            clean_title = preview_data.get("title", "የዕለቱ የስነ-ልቦና ማስታወሻ")
            clean_quote = preview_data.get("quote", clean_content)
        else:
            clean_title = "የዕለቱ የስነ-ልቦና ማስታወሻ"
            clean_quote = clean_content

        # Check if we already have the photo file_id from the preview message
        broadcast_file_id = None
        if call.message.photo:
            broadcast_file_id = call.message.photo[-1].file_id

        # Generate quote card bytes if not already available
        card_bytes = None
        if not broadcast_file_id:
            try:
                import quote_card
                card_bytes = quote_card.generate_quote_card(clean_quote, hook_title=clean_title)
            except Exception as ce:
                logging.error(f"Failed to generate quote card for broadcast: {ce}")

        all_users = database.get_all_user_ids()
        bot_uname = getattr(config, "BOT_USERNAME", "bayabooks_bot")

        # 1. Post Visual Quote Card to Telegram Channel
        channel_name = getattr(config, "CHANNEL_USERNAME", "BAYABOOKS1").lstrip('@')
        channel_target = f"@{channel_name}"
        channel_caption = (
            f"✨ <b>{clean_title}</b>\n\n"
            f"{clean_quote}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🧠 <b>የራስዎን የስነ-ልቦና እና የህይወት መመሪያ በነጻ በ AI ለመመርመር ቦቱን ይቀላቀሉ፦</b>\n"
            f"👉 @{bot_uname}"
        )
        channel_markup = InlineKeyboardMarkup()
        channel_markup.add(
            InlineKeyboardButton("🧠 ወደ AI ማማከሪያው ግባ (Start Bot)", url=f"https://t.me/{bot_uname}?start=channel_post")
        )

        try:
            if broadcast_file_id:
                bot.send_photo(channel_target, broadcast_file_id, caption=channel_caption, parse_mode="HTML", reply_markup=channel_markup)
            elif card_bytes:
                import io
                bio = io.BytesIO(card_bytes)
                bio.name = "baya_channel_card.png"
                sent_ch = bot.send_photo(channel_target, bio, caption=channel_caption, parse_mode="HTML", reply_markup=channel_markup)
                if sent_ch and sent_ch.photo:
                    broadcast_file_id = sent_ch.photo[-1].file_id
            else:
                bot.send_message(channel_target, channel_caption, parse_mode="HTML", reply_markup=channel_markup)
        except Exception as e:
            logging.error(f"Failed to post photo card to channel: {e}")
            try:
                bot.send_message(channel_target, channel_caption, parse_mode="HTML", reply_markup=channel_markup)
            except Exception:
                pass

        # 2. Post to Facebook Page (with Visual Photo Card)
        try:
            fb_token = os.environ.get("FB_PAGE_ACCESS_TOKEN")
            fb_page_id = os.environ.get("FB_PAGE_ID")
            
            if fb_token and fb_page_id:
                import requests
                fb_msg = (
                    f"✨ {clean_title}\n\n"
                    f"{clean_quote}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📚 ሙሉ የስነ-ልቦና መመሪያዎችን እና ምክሮችን ለማግኘት ቦቱን በነጻ ይቀላቀሉ፦\n"
                    f"👉 https://t.me/{bot_uname}\n\n"
                    f"#bayabooks #ሳይኮሎጂ #ስነልቦና #ህይወት #fyp"
                )
                
                fb_bytes = card_bytes
                if not fb_bytes and broadcast_file_id:
                    try:
                        finfo = bot.get_file(broadcast_file_id)
                        fb_bytes = bot.download_file(finfo.file_path)
                    except Exception:
                        pass

                if fb_bytes:
                    fb_photo_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/photos"
                    files = {
                        "source": ("baya_quote_card.png", fb_bytes, "image/png")
                    }
                    payload = {
                        "caption": fb_msg,
                        "access_token": fb_token
                    }
                    res = requests.post(fb_photo_url, files=files, data=payload, timeout=25)
                else:
                    fb_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
                    payload = {
                        "message": fb_msg,
                        "access_token": fb_token
                    }
                    res = requests.post(fb_url, data=payload, timeout=15)

                if res.status_code != 200:
                    bot.send_message(chat_id, f"⚠️ <b>Facebook Post Failed:</b>\n<code>{res.text}</code>", parse_mode="HTML")
                else:
                    bot.send_message(chat_id, "✅ <b>Successfully posted Photo Card to Facebook Page!</b> 📸", parse_mode="HTML")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ <b>Facebook Error:</b> {str(e)}")
            logging.error(f"Failed to post to Facebook: {e}")

        # 3. Broadcast to All Bot Users (Using Visual Photo Card file_id!)
        user_caption = f"✨ <b>{clean_title}</b>\n\n{clean_quote}"
        
        def background_broadcast():
            success = 0
            failed = 0
            for u in all_users:
                try:
                    u_lang = database.get_bot_language(u) or 'am'
                    u_markup = get_bottom_markup(u_lang, u)
                    
                    if broadcast_file_id:
                        bot.send_photo(u, broadcast_file_id, caption=user_caption, parse_mode="HTML", reply_markup=u_markup)
                    else:
                        bot.send_message(u, user_caption, parse_mode="HTML")
                        bot.send_message(u, "​", reply_markup=u_markup)
                    broadcast_entry = f"✨ {clean_title}\n\n{clean_quote}"
                    database.append_bot_message_to_history(u, broadcast_entry, is_broadcast=True)
                    database.mark_user_blocked(u, 0)
                    success += 1
                except Exception:
                    database.mark_user_blocked(u, 1)
                    failed += 1
                time.sleep(0.05)
                
            try:
                bot.send_message(chat_id, f"✅ <b>Visual Quote Card Broadcast Complete!</b>\n✔️ {success} Delivered (Photo Card)\n❌ {failed} Failed (Marked as Blocked/Left)", parse_mode="HTML")
            except Exception:
                pass
            
        threading.Thread(target=background_broadcast, daemon=True).start()
        
        confirm_msg = f"🚀 <b>Photo Card Broadcast Launched!</b>\nSending to {len(all_users)} bot users, the Telegram Channel, and Facebook in background..."
        done_markup = InlineKeyboardMarkup()
        done_markup.add(InlineKeyboardButton("🔙 Admin Panel", callback_data="adm_back"))
        if call.message.photo:
            bot.edit_message_caption(caption=confirm_msg, chat_id=chat_id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=done_markup)
        else:
            bot.edit_message_text(text=confirm_msg, chat_id=chat_id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=done_markup)
        return

    # ── Admin: Dedicated TikTok Card Creator (4:5) ──
    if data in ["adm_tiktok_init", "adm_tiktok_refresh", "adm_get_tiktok_card"]:
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "📱 Generating TikTok 4:5 Card...", show_alert=False)
        bot.send_chat_action(chat_id, 'upload_photo')
        
        psych_obj = ai_engine.generate_psych_broadcast()
        hook_title = getattr(psych_obj, "title", "የዕለቱ የስነ-ልቦና ማስታወሻ")
        quote_text = getattr(psych_obj, "quote", str(psych_obj))
        tiktok_desc = getattr(psych_obj, "tiktok_desc", "")

        clean_title = re.sub(r'<[^<]+>', '', hook_title).strip()
        clean_quote = re.sub(r'<[^<]+>', '', quote_text).strip()
        clean_tiktok_desc = re.sub(r'<[^<]+>', '', tiktok_desc).strip()

        if not clean_tiktok_desc:
            clean_tiktok_desc = "ብዙዎቻችን በየቀኑ የምንወድቅበት ግን የማንመለከተው የስነ-ልቦና ወጥመድ። በካርዱ ላይ ያለውን በጥሞና አንብበው፤ አንተስ ምን ይሰማሃል? አስተያየትህን በኮሜንት አጋራን።"

        try:
            import quote_card
            tiktok_bytes = quote_card.generate_tiktok_card(clean_quote, hook_title=clean_title)
        except Exception as e:
            logging.error(f"Failed to generate TikTok card: {e}")
            bot.send_message(chat_id, f"⚠️ <b>Failed to generate TikTok card:</b> {e}", parse_mode="HTML")
            return

        bot_uname = getattr(config, "BOT_USERNAME", "bayabooks_bot")
        
        # 5 hashtags in small letters ONLY
        hashtags = "#bayabooks #ሳይኮሎጂ #ስነልቦና #ህይወት #fyp"
        
        # Clean text Title and description ONLY — pure text to copy directly
        clean_caption = (
            f"{clean_title}\n\n"
            f"{clean_tiktok_desc}\n\n"
            f"ሙሉውን በነጻ በ AI ለመመርመር ሊንኩ በፕሮፋይላችን (Bio) ላይ ይገኛል! 👉 @{bot_uname}\n\n"
            f"{hashtags}"
        )
        
        tiktok_markup = InlineKeyboardMarkup()
        tiktok_markup.add(InlineKeyboardButton("🔄 Generate Another (4:5)", callback_data="adm_tiktok_refresh"))
        tiktok_markup.add(InlineKeyboardButton("🔙 Admin Panel", callback_data="adm_back"))
        
        if data == "adm_tiktok_refresh":
            safe_delete_message(chat_id, call.message.message_id)

        import io
        bio = io.BytesIO(tiktok_bytes)
        bio.name = "baya_tiktok_4_5.jpg"
        bot.send_photo(chat_id, bio, caption=clean_caption, reply_markup=tiktok_markup)
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
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    uid = message.from_user.id
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        if data.get('action') == 'select_book':
            book_key = data.get('book')
            mode = data.get('mode', 'buy')
            send_book_checkout_prompt(uid, book_key, mode)
    except Exception as e:
        logging.error(f"Error handling web_app_data for {uid}: {e}")

@bot.message_handler(content_types=["text", "photo", "document"])
def handle_messages(message):
    uid = message.from_user.id
    session = get_session(uid)
    state = session["state"]
    chat_id = message.chat.id
    database.sync_user_profile(uid, message.from_user.username, get_full_name(message.from_user))

    # Ban check
    if database.is_banned(uid):
        bot.reply_to(message, S(get_lang(uid), 'banned'))
        return

    if message.text == "/debug_carts" and is_admin(message.from_user):
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT status, count(*) FROM payments WHERE receipt_file_id = 'PENDING_CHECKOUT' GROUP BY status")
        rows = c.fetchall()
        c.execute("SELECT payment_date FROM payments WHERE receipt_file_id = 'PENDING_CHECKOUT' ORDER BY id DESC LIMIT 1")
        last = c.fetchone()
        conn.close()
        msg = "<b>Cart Diagnostics:</b>\n"
        for r in rows:
            msg += f"- {r[0]}: {r[1]}\n"
        if last:
            msg += f"\nLast recorded time: {last[0]}"
            from datetime import datetime
            msg += f"\nServer time now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bot.send_message(chat_id, msg or "No checkouts found.", parse_mode="HTML")
        return

    # ── Admin States ─────────────────────────
    # ── Admin: Search User (text or forwarded message) ──────
    if state == "ADMIN_SEARCH_USER" and is_admin(message.from_user):
        if message.text and message.text.strip() == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        is_forwarded = bool(
            getattr(message, "forward_from", None)
            or getattr(message, "forward_sender_name", None)
            or getattr(message, "forward_origin", None)
        )
        found = perform_admin_user_lookup(
            chat_id,
            message.from_user,
            query_text=(message.text or message.caption or ""),
            forwarded_msg=message if is_forwarded else None,
        )
        if found:
            clear_state(uid)
        return
    
    # ── Admin: Grant Book User ID Prompt ─────
    if state == "ADMIN_RENT_GRANT_UID" and is_admin(message.from_user):
        if message.text and message.text.strip() == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ Cancelled."); return
        try:
            target_uid = int(message.text.strip())
            target = database.get_user(target_uid)
            target_name = target['first_name'] if target else f"User {target_uid}"
            
            markup = InlineKeyboardMarkup(row_width=1)
            for bkey, btitle in BOOK_TITLES.items():
                markup.add(InlineKeyboardButton(f"📚 {btitle}", callback_data=f"adm_rent_gbook_{target_uid}_{bkey}"))
            markup.add(InlineKeyboardButton("❌ Cancel", callback_data="adm_rentals_menu"))
            
            bot.send_message(
                chat_id,
                f"👤 Reader: <b>{html.escape(target_name)}</b> (<code>{target_uid}</code>)\n\n"
                f"Select the book to grant:",
                parse_mode="HTML",
                reply_markup=markup
            )
            clear_state(uid)
        except ValueError:
            bot.send_message(chat_id, "❌ Please enter a valid numeric User ID (or /cancel).")
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
        raw_input = message.text.strip()
        target_id = database.add_sub_admin_by_identifier(raw_input)
        if not target_id:
            bot.send_message(chat_id, "❌ User not found! Make sure they have messaged or started the bot, then enter their @username or User ID.")
            return
        target = database.get_user(target_id)
        name = target['first_name'] if target else raw_input
        bot.send_message(chat_id, f"👮 <b>{name}</b> (<code>{target_id}</code>) is now a <b>Sub-Admin</b>.", parse_mode="HTML")
        try:
            bot.send_message(
                target_id,
                "👑 <b>Congratulations!</b>\n\nYou have been granted Sub-Admin privileges!\nUse the new bottom menu buttons (⚙️ Dashboard & 📚 Library) or type /bayacontrol.",
                parse_mode="HTML",
                reply_markup=get_bottom_markup(get_lang(target_id), target_id)
            )
        except: pass
        clear_state(uid)
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
        all_admins = get_all_admin_ids()
        feedback_text = message.text or ""
        # Forward to all admins
        if all_admins:
            gender_str = "👨 Male" if database.get_onboarding_status(uid)[1] == "male" else "👩 Female"
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("↩️ Reply", callback_data=f"adm_reply_{uid}"),
                InlineKeyboardButton("🔍 View User", callback_data=f"adm_view_user_{uid}")
            )
            markup.add(
                InlineKeyboardButton("📚 Push Book (Free / 10d Rent)", callback_data=f"adm_push_book_menu_{uid}")
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
            
            for adm_id in all_admins:
                try:
                    if message.text:
                        bot.send_message(
                            adm_id,
                            f"{header}\n\n<i>{message.text}</i>",
                            parse_mode="HTML",
                            reply_markup=markup
                        )
                    else:
                        # Send header with buttons, then copy the user's media (photo, etc.)
                        bot.send_message(adm_id, header, parse_mode="HTML", reply_markup=markup)
                        bot.copy_message(adm_id, chat_id, message.message_id)
                except Exception as e:
                    logging.error(f"Failed to forward feedback to admin {adm_id}: {e}")
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
                            database.append_bot_message_to_history(u, broadcast_text, is_broadcast=True)
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
            
        # 1. First check dedicated last_mentor_message (only written by 1-on-1 advice chat, never by broadcasts)
        last_ai_msg = database.get_last_mentor_message(uid)
        
        # 2. Fallback to scanning advice_history if not yet recorded in the dedicated column
        if not last_ai_msg:
            history_str = database.get_advice_history(uid)
            if history_str:
                try:
                    history = json.loads(history_str)
                    for idx in range(len(history) - 1, -1, -1):
                        item = history[idx]
                        if item.get("role") == "model":
                            if item.get("is_broadcast"):
                                continue
                            prev_item = history[idx - 1] if idx > 0 else None
                            if not prev_item or prev_item.get("role") != "user":
                                continue
                            
                            part_text = item.get("parts", [""])[0]
                            if database.is_broadcast_or_nudge_text(part_text):
                                continue
                                
                            last_ai_msg = part_text
                            try:
                                database.set_last_mentor_message(uid, last_ai_msg)
                            except Exception:
                                pass
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
        is_adm = is_admin(message.from_user) or is_admin_uid(uid)
        is_vip = database.is_vip(uid)
        lang = get_lang(uid)
        if is_adm:
            msgs_display = "♾️ Unlimited (👑 Admin)"
        elif is_vip:
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
        if is_adm:
            ubooks = get_all_book_keys()
            urentals = {}
            uexpired = []
        else:
            ubooks, urentals, uexpired = database.get_user_books_state(uid)
        books_section = ""
        if ubooks or uexpired:
            blines = []
            for bk in ubooks:
                bt = BOOK_TITLES.get(bk, bk)
                if bk in urentals:
                    blines.append(f"  ⏳ <b>{bt}</b> (ቀሪ {urentals[bk]} ቀናት)")
                else:
                    blines.append(f"  ✅ <b>{bt}</b> (ሙሉ መጽሐፍ)")
            for bk in uexpired:
                bt = BOOK_TITLES.get(bk, bk)
                blines.append(f"  ⏰ <b>{bt}</b> (የኪራይ ጊዜው ያለፈ)")
            books_section = "📚 <b>የእርስዎ መጻሕፍት:</b>\n" + "\n".join(blines) + "\n\n"

        markup = InlineKeyboardMarkup()
        if ubooks or uexpired:
            markup.add(
                InlineKeyboardButton(
                    "📚 የኔ መጻሕፍት (Open Library)",
                    web_app=WebAppInfo(url=f"{config.BASE_URL}/app?uid={uid}")
                )
            )
        if count >= 10:
            markup.add(InlineKeyboardButton(S(lang, 'btn_claim'), callback_data="claim_referrals"))
        if not is_adm:
            markup.add(InlineKeyboardButton(S(lang, 'btn_topup'), callback_data="show_topup"))
        markup.add(InlineKeyboardButton(S(lang, 'btn_reset'), callback_data="confirm_reset"))
            
        topup_hint = "" if is_adm else ("\n\n" + S(lang, 'mypage_topup_hint'))
        bot.send_message(
            chat_id,
            S(lang, 'mypage_title') + "\n━━━━━━━━━━━━━━━━━━━━\n" +
            S(lang, 'mypage_msgs_left', msgs=msgs_display) + "\n\n" +
            books_section +
            S(lang, 'mypage_referrals', count=count) + "\n" +
            S(lang, 'mypage_referral_hint') + "\n\n" +
            S(lang, 'mypage_reset_info') + "\n" +
            S(lang, 'mypage_reset_warn') +
            topup_hint,
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
                if not is_adm:
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
                    database.set_last_mentor_message(uid, ai_response)
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
                    bot.send_message(chat_id, S(user_lang, 'ai_error'))
                except:
                    pass
                
        try:
            threading.Thread(target=process_advice_chat, daemon=True).start()
        except Exception as e:
            logging.error(f"Failed to start thread: {e}")
            bot.send_message(chat_id, S(get_lang(uid), 'tech_error', err=str(e)))
        return

    # ── Receipt Photo or Document Handling ──────────
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif message.document:
        doc = message.document
        mime = (doc.mime_type or "").lower()
        fname = (doc.file_name or "").lower()
        if mime.startswith("image/") or any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            photo_file_id = doc.file_id
        else:
            bot.reply_to(message, S(get_lang(uid), 'text_only'))
            return

    if photo_file_id:
        lang = get_lang(uid)
        
        # Check if they have a pending checkout
        pending = database.get_latest_pending_payment(uid)
        if not pending:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_starter'), callback_data="buy_advice_25"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_pro'), callback_data="buy_advice_75"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_heavy'), callback_data="buy_advice_225"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited'), callback_data="buy_advice_unlimited"))
            markup.add(InlineKeyboardButton(S(lang, 'topup_btn_unlimited_month'), callback_data="buy_advice_unlimited_month"))
            
            prompt_text = (
                "⚠️ <b>የክፍያ ፓኬጅ አልመረጡም!</b>\n\n"
                "ደረሰኝዎን ከመላክዎ በፊት የትኛውን ፓኬጅ እንደከፈሉ እባክዎ ከታች ይምረጡ፦\n"
                "<i>(ፓኬጁን እንደመረጡ ደረሰኙን እንደገና ይላኩት።)</i>"
            ) if lang == 'am' else (
                "⚠️ <b>No Package Selected!</b>\n\n"
                "Please select the package you transferred for below, then re-send your receipt screenshot:"
            )
            bot.reply_to(message, prompt_text, parse_mode="HTML", reply_markup=markup)
            
            uname = f"@{message.from_user.username}" if message.from_user.username else "N/A"
            full_name = html.escape(get_full_name(message.from_user))
            for adm_id in get_all_admin_ids():
                try:
                    bot.send_photo(
                        adm_id,
                        photo_file_id,
                        caption=(
                            f"⚠️ <b>Unsolicited Receipt Upload</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👤 User: <b>{full_name}</b> ({uname})\n"
                            f"🆔 User ID: <code>{uid}</code>\n"
                            f"ℹ️ User uploaded a receipt before selecting a package."
                        ),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            return
            
        pending_id, amount, tx_ref, order_id = pending
        item_summary = get_payment_item_summary(tx_ref)
        
        msg = bot.reply_to(message, S(lang, 'receipt_verifying'))
        
        try:
            file_id = photo_file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Verify with ShegerPay OCR (optimized image + retry)
            import shegerpay
            success, ref_id, err = shegerpay.verify_receipt_image(downloaded_file, amount)
            
            if success:
                if database.is_receipt_ref_used(ref_id):
                    bot.edit_message_text(
                        S(lang, 'receipt_used'),
                        chat_id, msg.message_id
                    )
                    return

                fulfill_payment(uid, tx_ref, order_id=order_id, receipt_ref=ref_id)
                safe_delete_message(chat_id, msg.message_id)

                uname = f"@{message.from_user.username}" if message.from_user.username else "N/A"
                full_name = html.escape(get_full_name(message.from_user))
                notify_admin(
                    f"💰 <b>New Verified Payment (ShegerPay)!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 User: <b>{full_name}</b> ({uname})\n"
                    f"🆔 ID: <code>{uid}</code>\n"
                    f"📦 Item: <b>{item_summary}</b>\n"
                    f"💵 Amount: <b>{amount:,} ETB</b>\n"
                    f"🧾 Ref: <code>{ref_id}</code>"
                )
            else:
                # ShegerPay could not verify or timed out -> Forward to Admin for 1-tap approval
                bot.edit_message_text(
                    S(lang, 'receipt_forwarded_to_admin'),
                    chat_id, msg.message_id,
                    parse_mode="HTML"
                )
                
                uname = f"@{message.from_user.username}" if message.from_user.username else "N/A"
                full_name = html.escape(get_full_name(message.from_user))
                sheger_note = html.escape(str(err or "Verification failed"))
                admin_caption = (
                    f"⚠️ <b>Manual Receipt Review Required</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 User: <b>{full_name}</b> ({uname})\n"
                    f"🆔 User ID: <code>{uid}</code>\n"
                    f"📦 Item: <b>{item_summary}</b>\n"
                    f"💵 Expected: <b>{amount:,} ETB</b>\n"
                    f"ℹ️ ShegerPay Note: <i>{sheger_note}</i>\n"
                    f"🔖 Pending ID: <code>{pending_id}</code>"
                )
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("✅ Approve", callback_data=f"adm_rec_appr_{uid}_{pending_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"adm_rec_rej_{uid}_{pending_id}"),
                )
                markup.add(
                    InlineKeyboardButton("🔍 View User", callback_data=f"adm_view_user_{uid}")
                )
                for adm_id in get_all_admin_ids():
                    try:
                        bot.send_photo(adm_id, file_id, caption=admin_caption, parse_mode="HTML", reply_markup=markup)
                    except Exception as e:
                        logging.error(f"Failed to forward receipt to admin {adm_id}: {e}")
                
        except Exception as e:
            logging.error(f"Receipt processing exception for {uid}: {e}")
            try:
                bot.edit_message_text(S(lang, 'receipt_forwarded_to_admin'), chat_id, msg.message_id, parse_mode="HTML")
            except Exception:
                pass
            for adm_id in get_all_admin_ids():
                try:
                    bot.send_message(adm_id, f"⚠️ Error processing receipt photo for user {uid}: {e}")
                except Exception:
                    pass
        return

    # ── Catch-all: Forward to admin ──────────
    if not is_admin(message.from_user) and not message.text:
        bot.reply_to(message, '✅ መልዕክትዎ ደርሶናል!')
        return
# ══════════════════════════════════════════
#  WEBHOOK HTTP SERVER (Render & Chapa)
# ══════════════════════════════════════════
import io
_QUOTE_CARD_CACHE = {}

def process_payment_success(tx_ref):
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
    
    if purpose.startswith("BOOKRENT_"):
        book_key = purpose.replace("BOOKRENT_", "")
        database.approve_payment(tx_ref, order_id)
        database.unlock_book(uid, book_key, days=10)
        notify_user_book_unlocked(uid, book_key, days=10)
    elif purpose.startswith("BOOKEXT_"):
        book_key = purpose.replace("BOOKEXT_", "")
        database.approve_payment(tx_ref, order_id)
        database.unlock_book(uid, book_key, days=5)
        notify_user_book_unlocked(uid, book_key, days=5)
    elif purpose.startswith("BOOK_"):
        book_key = purpose.replace("BOOK_", "")
        database.approve_payment(tx_ref, order_id)
        database.unlock_book(uid, book_key, days=None)
        notify_user_book_unlocked(uid, book_key, days=None)
    elif purpose.startswith("ADVICE_"):
        pkg = purpose.split("_")[1]
        lang = get_lang(uid)
        if pkg == "unlimited":
            database.approve_payment(tx_ref, order_id)
            database.set_vip(uid, days=7)
            bot.send_message(chat_id, S(lang, 'payment_success_unlimited'), parse_mode="HTML")
        elif pkg == "unlimited_month":
            database.approve_payment(tx_ref, order_id)
            database.set_vip(uid, days=30)
            bot.send_message(chat_id, S(lang, 'payment_success_unlimited_month'), parse_mode="HTML")
        else:
            msgs = int(pkg)
            database.approve_payment(tx_ref, order_id)
            database.add_advice_messages(uid, msgs)
            bot.send_message(chat_id, S(lang, 'payment_success_msgs', msgs=msgs), parse_mode="HTML")
    elif purpose == "TIP":
        lang = get_lang(uid)
        database.approve_payment(tx_ref, order_id)
        bot.send_message(chat_id, S(lang, 'tip_received'), parse_mode="HTML")

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/admin_dashboard'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"403 Forbidden: Invalid or missing Admin credentials.")
                return
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

        if self.path.startswith('/author_dashboard'):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            try:
                with open('author_dashboard.html', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(b"Author Dashboard not found.")
            return

        if self.path.startswith('/api/author/data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            author = database.get_author_by_token(token)
            if not author:
                self.send_response(403); self.end_headers(); self.wfile.write(json.dumps({"ok": False, "error": "Invalid or missing Author Token"}).encode('utf-8')); return
            stats = database.get_author_dashboard_stats(author['author_id'])
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "data": stats}).encode('utf-8'))
            return

        if self.path.startswith('/admin/authors_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            adata = database.get_all_authors_admin_data()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(adata).encode('utf-8'))
            return

        if self.path.startswith('/admin/data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
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

        if self.path.startswith('/admin/rentals_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
                return
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            rentals_data = database.get_all_rentals_management_data()
            self.wfile.write(json.dumps(rentals_data).encode('utf-8'))
            return

        if self.path.startswith('/admin/users_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            limit = int(qs.get('limit', [100])[0])
            page = int(qs.get('page', [0])[0])
            query = qs.get('query', [''])[0]
            flt = qs.get('filter', ['all'])[0]
            data = database.get_all_users_admin_data(limit=limit, offset=page * limit, query=query, filter_status=flt)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        if self.path.startswith('/admin/user_profile_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            target_uid = int(qs.get('uid', [0])[0])
            details = database.get_user_details(target_uid) or {}
            ubooks, urentals, uexp = database.get_user_books_state(target_uid)
            hist_str = database.get_advice_history(target_uid)
            hist = []
            if hist_str:
                try: hist = json.loads(hist_str)
                except: pass
            res = {
                "details": details,
                "books": {"owned": ubooks, "rentals": urentals, "expired": uexp},
                "advice_history": hist
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        if self.path.startswith('/admin/payments_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            limit = int(qs.get('limit', [100])[0])
            page = int(qs.get('page', [0])[0])
            query = qs.get('query', [''])[0]
            st = qs.get('status', ['all'])[0]
            ptype = qs.get('type', ['all'])[0]
            data = database.get_all_payments_admin_data(limit=limit, offset=page * limit, query=query, status=st, ptype=ptype)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        if self.path.startswith('/admin/carts_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            carts = database.get_abandoned_carts_admin_data()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(carts).encode('utf-8'))
            return

        if self.path.startswith('/admin/logs_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            lines_n = int(qs.get('lines', [150])[0])
            logs = []
            if os.path.exists('app.log'):
                try:
                    with open('app.log', 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        logs = [l.strip() for l in lines[-lines_n:]]
                except Exception as e:
                    logs = [f"Error reading app.log: {e}"]
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(logs).encode('utf-8'))
            return

        if self.path.startswith('/admin/subadmins_data'):
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
            subs = database.get_all_sub_admins()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(subs).encode('utf-8'))
            return

        if self.path.startswith('/admin/advice_history'):
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            token = qs.get('token', [''])[0]
            if not is_valid_admin_token(token):
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"403 Forbidden")
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                uid = int(qs.get('uid', [0])[0])
                history_str = database.get_advice_history(uid)
                if not history_str or history_str == '[]':
                    self.wfile.write(b"No psychology readings found for this user.")
                    return
                history = json.loads(history_str)
                html_out = "<ul>"
                for msg in history:
                    raw_role = str(msg.get("role", "user")).lower()
                    role_safe = html.escape(raw_role)
                    text = msg.get("parts", [""])[0]
                    color = "blue" if raw_role == "user" else "green"
                    html_out += f"<li class='mb-2'><strong class='text-{color}-600'>{role_safe.upper()}:</strong> {html.escape(text)}</li>"
                html_out += "</ul>"
                self.wfile.write(html_out.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"Error: {html.escape(str(e))}".encode('utf-8'))
            return

        if self.path.startswith('/static/'):
            clean_path = self.path.split('?')[0].lstrip('/')
            base_dir = os.path.abspath('static')
            target_path = os.path.abspath(clean_path)
            if not target_path.startswith(base_dir) or not os.path.exists(target_path) or not os.path.isfile(target_path):
                self.send_response(404)
                self.end_headers()
                return

            ext = target_path.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg']:
                mime = 'image/jpeg'
            elif ext == 'png':
                mime = 'image/png'
            elif ext == 'json':
                mime = 'application/json; charset=utf-8'
            elif ext in ['ttf', 'woff', 'woff2']:
                mime = 'font/ttf'
            else:
                mime = 'application/octet-stream'
            with open(target_path, 'rb') as f:
                raw_bytes = f.read()
            accept_enc = self.headers.get('Accept-Encoding', '')
            self.send_response(200)
            self.send_header("Content-type", mime)
            self.send_header("Cache-Control", "public, max-age=3600")
            if ext == 'json' and 'gzip' in accept_enc:
                raw_bytes = gzip.compress(raw_bytes)
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(raw_bytes)))
            self.end_headers()
            self.wfile.write(raw_bytes)
            return

        if self.path.startswith('/api/user_books'):
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            uid = qs.get('uid', [''])[0]
            if uid and is_admin_uid(uid):
                books = get_all_book_keys()
                rentals = {}
                expired = []
            else:
                books, rentals, expired = database.get_user_books_state(uid)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps({"books": books, "rentals": rentals, "expired": expired}).encode('utf-8'))
            return

        if self.path.startswith('/api/finish_rental'):
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            uid = qs.get('uid', [''])[0]
            book_key = qs.get('book', [''])[0]
            if uid and book_key:
                try:
                    database.clear_expired_rental(int(uid), book_key)
                except Exception as e:
                    logging.error(f"Failed to finish rental: {e}")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode('utf-8'))
            return

        if self.path.startswith('/api/select_book'):
            parsed_url = urlparse(self.path)
            qs = parse_qs(parsed_url.query)
            uid = qs.get('uid', [''])[0]
            book_key = qs.get('book', [''])[0]
            mode = qs.get('mode', ['buy'])[0]
            notify = qs.get('notify', ['0'])[0] == '1'
            if uid and book_key:
                try:
                    uid_int = int(uid)
                    if notify:
                        send_book_checkout_prompt(uid_int, book_key, mode)
                    else:
                        rand_suffix = uuid.uuid4().hex[:6].upper()
                        if mode == 'rent':
                            amount = 149
                            tx_ref = f"BAYA-{uid_int}-BOOKRENT_{book_key}-MANUAL-{rand_suffix}"
                        elif mode == 'extend':
                            amount = 49
                            tx_ref = f"BAYA-{uid_int}-BOOKEXT_{book_key}-MANUAL-{rand_suffix}"
                        else:
                            amount = 399
                            tx_ref = f"BAYA-{uid_int}-BOOK_{book_key}-MANUAL-{rand_suffix}"
                        database.record_payment(uid_int, 0, amount, tx_ref, "PENDING_CHECKOUT", status="pending")
                except Exception as e:
                    logging.error(f"Failed to record book checkout: {e}")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode('utf-8'))
            return

        if self.path == '/app' or self.path.startswith('/app?'):
            try:
                with open('webapp.html', 'rb') as f:
                    raw_bytes = f.read()
                accept_enc = self.headers.get('Accept-Encoding', '')
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                if 'gzip' in accept_enc:
                    raw_bytes = gzip.compress(raw_bytes)
                    self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Length", str(len(raw_bytes)))
                self.end_headers()
                self.wfile.write(raw_bytes)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"App UI not found.")
            return


        if self.path.startswith('/api/quote_card_dl/'):
            img_id = self.path.split('/')[-1].split('?')[0].replace('.png', '')
            png_bytes = _QUOTE_CARD_CACHE.get(img_id)
            if png_bytes:
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Disposition", 'attachment; filename="baya-quote.png"')
                self.send_header("Content-Length", str(len(png_bytes)))
                self.end_headers()
                self.wfile.write(png_bytes)
            else:
                self.send_response(404)
                self.end_headers()
            return

        if self.path.startswith('/auto-verify-shegerpay/'):
            tx_ref = self.path.split('/')[-1]
            import shegerpay
            success, _ = shegerpay.verify_shegerpay_payment(tx_ref)
            if success:
                process_payment_success(tx_ref) # We reuse the same success processor since it just reads tx_ref
                
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
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (ValueError, TypeError):
            content_length = 0
        if content_length > 10 * 1024 * 1024:
            self.send_response(413)
            self.end_headers()
            self.wfile.write(b"413 Payload Too Large")
            return

        if self.path == '/api/quote_card':
            post_data = self.rfile.read(content_length)
            try:
                import base64
                data = json.loads(post_data.decode('utf-8'))
                uid = str(data.get('uid') or '').strip()
                img_b64 = data.get('image') or ''
                caption = data.get('caption') or ''
                action = data.get('action') or 'send'
                if ',' in img_b64:
                    img_b64 = img_b64.split(',', 1)[1]
                png_bytes = base64.b64decode(img_b64)
                img_id = uuid.uuid4().hex[:12]
                if len(_QUOTE_CARD_CACHE) > 60:
                    _QUOTE_CARD_CACHE.clear()
                _QUOTE_CARD_CACHE[img_id] = png_bytes
                sent_to_tg = False
                if uid and uid.isdigit() and action == 'send':
                    try:
                        bio = io.BytesIO(png_bytes)
                        bio.name = 'baya-quote.png'
                        bot.send_photo(int(uid), bio, caption=caption)
                        sent_to_tg = True
                    except Exception as tg_err:
                        logging.error(f"Failed to send quote photo to {uid}: {tg_err}")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "sent": sent_to_tg,
                    "download_url": f"/api/quote_card_dl/{img_id}.png"
                }).encode('utf-8'))
            except Exception as e:
                logging.error(f"/api/quote_card error: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/author/save_book':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                token = data.get('token')
                author = database.get_author_by_token(token)
                if not author:
                    self.send_response(403); self.end_headers(); self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode('utf-8')); return
                bkey = database.save_author_book(author['author_id'], data)
                if data.get('status') == 'pending_review':
                    for adm_id in get_all_admin_ids():
                        try:
                            a_name = author.get('pen_name') or author.get('name') or 'Author'
                            a_user = f"(@{author['telegram_username']})" if author.get('telegram_username') else ""
                            bot.send_message(
                                adm_id,
                                f"📖 <b>NEW BOOK SUBMITTED FOR REVIEW</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"✍️ <b>Author:</b> {a_name} {a_user}\n"
                                f"📚 <b>Title:</b> {data.get('title')}\n"
                                f"🏷️ <b>Category:</b> {data.get('category')}\n"
                                f"💰 <b>Purchase Price:</b> {data.get('price_buy')} ETB\n"
                                f"⏳ <b>Rental Price:</b> 5d: {data.get('price_rent_5d')} ETB | 10d: {data.get('price_rent_10d')} ETB\n\n"
                                f"<i>Review & approve in the Admin Dashboard under Authors.</i>",
                                parse_mode="HTML"
                            )
                        except Exception as ex:
                            logging.error(f"Failed to notify admin {adm_id} of book submission: {ex}")
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "book_key": bkey}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/author/request_payout':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                token = data.get('token')
                author = database.get_author_by_token(token)
                if not author:
                    self.send_response(403); self.end_headers(); self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode('utf-8')); return
                pid = database.request_author_payout(
                    author['author_id'],
                    data.get('amount'),
                    data.get('bank_name'),
                    data.get('bank_account'),
                    data.get('account_holder')
                )
                for adm_id in get_all_admin_ids():
                    try:
                        a_name = author.get('pen_name') or author.get('name') or 'Author'
                        a_user = f"(@{author['telegram_username']})" if author.get('telegram_username') else ""
                        bot.send_message(
                            adm_id,
                            f"💸 <b>AUTHOR PAYOUT REQUEST</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"✍️ <b>Author:</b> {a_name} {a_user}\n"
                            f"💰 <b>Amount:</b> <b>{data.get('amount')} ETB</b>\n"
                            f"🏦 <b>Bank:</b> {data.get('bank_name')}\n"
                            f"🔢 <b>Account:</b> <code>{data.get('bank_account')}</code>\n"
                            f"👤 <b>Holder:</b> {data.get('account_holder')}\n\n"
                            f"<i>Process this transfer in your Admin Dashboard under Authors.</i>",
                            parse_mode="HTML"
                        )
                    except Exception as ex:
                        logging.error(f"Failed to notify admin {adm_id} of payout request: {ex}")
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "payout_id": pid}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/author/update_profile':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                token = data.get('token')
                author = database.get_author_by_token(token)
                if not author:
                    self.send_response(403); self.end_headers(); self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode('utf-8')); return
                database.update_author_profile(author['author_id'], data)
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/author_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                token = data.get('token')
                if not is_valid_admin_token(token):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action')
                msg = ""
                if act == 'create_author':
                    name = data.get('name', '').strip()
                    phone = data.get('phone', '').strip()
                    tg_user = data.get('telegram_username', '').strip()
                    royalty = float(data.get('royalty', 70.0))
                    author_rec = database.create_or_get_author(name, phone=phone, telegram_username=tg_user, royalty=royalty)
                    msg = f"Author registered: {author_rec['name']} (Key: {author_rec['access_token']})"
                elif act == 'update_royalty':
                    aid = data.get('author_id')
                    royalty = float(data.get('royalty', 70.0))
                    conn = database.get_connection()
                    c = conn.cursor()
                    c.execute("UPDATE authors SET royalty_percentage = ? WHERE author_id = ?", (royalty, aid))
                    conn.commit()
                    conn.close()
                    msg = f"Royalty updated to {royalty}%"
                elif act == 'review_book':
                    bkey = data.get('book_key')
                    sub_act = data.get('sub_action')
                    feedback = data.get('feedback', '')
                    b_rec = database.admin_process_book_submission(bkey, sub_act, feedback)
                    msg = f"Book '{b_rec['title']}' {'approved & published' if sub_act == 'approve' else 'rejected'}."
                    author = database.get_author_by_token(b_rec['author_id'])
                    if author and author.get('telegram_id'):
                        try:
                            if sub_act == 'approve':
                                bot.send_message(
                                    author['telegram_id'],
                                    f"🎉 <b>Congratulations!</b>\n\n"
                                    f"Your book <b>{b_rec['title']}</b> has been approved and is now LIVE in the Baya Books Library!\n"
                                    f"Readers can now purchase and rent it.",
                                    parse_mode="HTML"
                                )
                            else:
                                bot.send_message(
                                    author['telegram_id'],
                                    f"ℹ️ <b>Book Review Update</b>\n\n"
                                    f"Your book <b>{b_rec['title']}</b> requires updates before publishing:\n"
                                    f"<i>{feedback or 'Please check your author dashboard for details.'}</i>",
                                    parse_mode="HTML"
                                )
                        except Exception:
                            pass
                elif act == 'process_payout':
                    pid = int(data.get('payout_id'))
                    sub_act = data.get('sub_action')
                    tx_ref = data.get('tx_ref', '').strip()
                    notes = data.get('notes', '').strip()
                    p_rec = database.admin_process_payout_request(pid, sub_act, tx_ref, notes)
                    msg = f"Payout #{pid} marked as {'PAID' if sub_act == 'approve' else 'REJECTED'}."
                    author = database.get_author_by_token(p_rec['author_id'])
                    if author and author.get('telegram_id') and sub_act == 'approve':
                        try:
                            bot.send_message(
                                author['telegram_id'],
                                f"✅ <b>Payout Transferred!</b>\n\n"
                                f"We have transferred <b>{p_rec['amount']} ETB</b> to your {p_rec['bank_name']} account (<code>{p_rec['bank_account']}</code>).\n"
                                f"Reference: <code>{tx_ref or 'Direct Transfer'}</code>\n\n"
                                f"Thank you for being a valued author on Baya Books! 💙",
                                parse_mode="HTML"
                            )
                        except Exception:
                            pass
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/rentals/action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                token = data.get('token')
                if not is_valid_admin_token(token):
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(b'Forbidden')
                    return
                
                action = data.get('action')
                uid = int(data.get('user_id'))
                bkey = data.get('book_key')
                b_title = BOOK_TITLES.get(bkey, bkey)
                notify = data.get('notify', True)
                
                result_msg = ""
                if action == 'extend':
                    days = int(data.get('days', 5))
                    new_exp = database.extend_rental_days(uid, bkey, additional_days=days)
                    result_msg = f"Extended {b_title} by {days} days (Expires: {new_exp[:10] if new_exp else 'N/A'})"
                    if notify:
                        try:
                            bot.send_message(
                                uid,
                                f"🎉 <b>የንባብ ጊዜ ተራዝሟል!</b>\n\n"
                                f"📖 የ <b>«{b_title}»</b> የኪራይ ጊዜዎ በ <b>+{days} ቀናት</b> ተራዝሟል!\n"
                                f"መልካም ንባብ! 📚✨",
                                parse_mode="HTML"
                            )
                        except Exception: pass
                elif action == 'lifetime':
                    database.convert_book_to_lifetime(uid, bkey)
                    result_msg = f"Converted {b_title} to Lifetime access!"
                    if notify:
                        try:
                            bot.send_message(
                                uid,
                                f"👑 <b>የቋሚ ባለቤትነት ስጦታ!</b>\n\n"
                                f"📖 የ <b>«{b_title}»</b> መጽሐፍ <b>ለዘላለም በቋሚነት (Lifetime)</b> ተከፍቶልዎታል!\n"
                                f"በማንኛውም ጊዜ ገብተው ሙሉውን መጽሐፍ ማንበብ ይችላሉ! 📚✨",
                                parse_mode="HTML"
                            )
                        except Exception: pass
                elif action == 'expire':
                    database.expire_book_rental_now(uid, bkey)
                    result_msg = f"Expired {b_title} rental now."
                elif action == 'revoke':
                    database.remove_user_book(uid, bkey)
                    result_msg = f"Revoked {b_title} from user {uid}."
                elif action == 'grant':
                    days = data.get('days')
                    rent_days = int(days) if days is not None and int(days) > 0 else None
                    database.unlock_book(uid, bkey, days=rent_days)
                    mode_label = f"{days}-Day Rental" if rent_days else "Full Permanent (Lifetime)"
                    result_msg = f"Granted {b_title} ({mode_label}) to user {uid}."
                    if notify:
                        notify_user_book_unlocked(uid, bkey, days=rent_days)
                elif action == 'nudge':
                    days_left = data.get('days_left')
                    days_msg = f"በ {days_left} ቀናት ውስጥ ያበቃል" if days_left else "በቅርቡ ያበቃል"
                    nudge_txt = (
                        f"⏳ <b>የመጽሐፍ ኪራይ ማሳሰቢያ</b>\n\n"
                        f"ውድ አንባቢ፣ የ <b>«{b_title}»</b> መጽሐፍ የኪራይ ጊዜዎ <b>{days_msg}</b>!\n\n"
                        f"ንባብዎን ሳይቋረጥ ለመቀጠል ወይም በቋሚነት ለመግዛት ቦቱን ይጠቀሙ ወይም አስተዳዳሪውን ያነጋግሩ። 📚"
                    )
                    try:
                        bot.send_message(uid, nudge_txt, parse_mode="HTML")
                        result_msg = f"Reminder sent to user {uid}."
                    except Exception as e:
                        result_msg = f"Could not send reminder (user may have blocked bot): {e}"
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": result_msg}).encode('utf-8'))
            except Exception as e:
                logging.error(f"/admin/rentals/action error: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/user_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if not is_valid_admin_token(data.get('token')):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action')
                uid = int(data.get('user_id'))
                msg = ""
                if act == 'add_msgs':
                    count = int(data.get('count', 5))
                    database.add_advice_messages(uid, count)
                    msg = f"Added {count} advice messages."
                    if data.get('notify'):
                        try: bot.send_message(uid, S(get_lang(uid), 'gift_notification', amount=count), parse_mode="HTML")
                        except: pass
                elif act == 'add_credits':
                    amt = int(data.get('amount', 5))
                    database.add_credits(uid, amt)
                    msg = f"Added {amt} credits."
                elif act == 'set_vip':
                    days = int(data.get('days', 30))
                    database.set_vip(uid, days=days)
                    msg = f"Granted VIP for {days} days."
                    if data.get('notify'):
                        try: bot.send_message(uid, f"🎉 <b>እንኳን ደስ አለዎት!</b>\nለ {days} ቀናት VIP ሆነዋል!", parse_mode="HTML")
                        except: pass
                elif act == 'ban':
                    database.ban_user(uid)
                    msg = f"User {uid} banned."
                elif act == 'unban':
                    database.unban_user(uid)
                    msg = f"User {uid} unbanned."
                elif act == 'send_dm':
                    text_to_send = data.get('message_text', '').strip()
                    if text_to_send:
                        bot.send_message(uid, text_to_send, parse_mode="HTML")
                        msg = f"Direct message sent to user {uid}."
                    else:
                        raise ValueError("Message text cannot be empty.")
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/payment_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if not is_valid_admin_token(data.get('token')):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action')
                msg = ""
                if act == 'record_manual':
                    target_uid = int(data.get('user_id'))
                    amt = float(data.get('amount', 0))
                    ptype = data.get('type', 'ADVICE')
                    ref = f"MANUAL_{ptype}_{uuid.uuid4().hex[:6]}"
                    database.record_payment(target_uid, None, amt, ref, "MANUAL_WEB_ADMIN", status="approved")
                    if ptype == 'ADVICE':
                        database.add_advice_messages(target_uid, 10)
                    elif ptype == 'VIP':
                        database.set_vip(target_uid, 30)
                    msg = f"Recorded manual payment of {amt:,.0f} ETB."
                elif act == 'delete_last':
                    row = database.delete_last_approved_payment()
                    msg = f"Deleted last payment ({row['amount'] if row else 'None'})."
                elif act == 'delete_id':
                    pid = int(data.get('payment_id'))
                    database.delete_payment_record_by_id(pid)
                    msg = f"Deleted payment ID {pid}."
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/cart_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if not is_valid_admin_token(data.get('token')):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action')
                target_uid = int(data.get('user_id'))
                cart_id = int(data.get('cart_id', 0))
                msg = ""
                if act == 'nudge':
                    u_lang = database.get_bot_language(target_uid) or 'am'
                    nudge_msgs = {
                        'am': (
                            "👋 <b>ሰላም!</b>\n\n"
                            "የጀመሩት ክፍያ እንዳልተጠናቀቀ አስተውለናል። ማንኛውም የክፍያ ወይም የቦት ችግር ካጋጠመዎት "
                            "እርዳታ ለመስጠት ዝግጁ ነን!\n\n"
                            "እንደገና ለመሞከር ከታች <b>«💎 ጥቅል ግዛ (Top Up)»</b> የሚለውን ይጫኑ ወይም በድጋፍ መስመር ያነጋግሩን። 💙"
                        ),
                        'en': (
                            "👋 <b>Hello!</b>\n\n"
                            "We noticed your payment checkout was not completed. If you experienced any issue or need assistance, "
                            "we are here to help!\n\n"
                            "Feel free to try again or reach out to our support anytime. 💙"
                        )
                    }
                    bot.send_message(target_uid, nudge_msgs.get(u_lang, nudge_msgs['am']), parse_mode="HTML")
                    database.mark_checkout_nudged(cart_id)
                    msg = f"Recovery reminder sent to user {target_uid}."
                elif act == 'dismiss':
                    database.delete_payment_record_by_id(cart_id)
                    msg = f"Cart {cart_id} dismissed."
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/broadcast_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if not is_valid_admin_token(data.get('token')):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action') # 'test' or 'blast'
                b_text = data.get('text', '').strip()
                has_app = data.get('has_app_btn', False)
                target_group = data.get('target', 'all')
                lang_filter = data.get('lang', 'all')
                
                if not b_text:
                    raise ValueError("Broadcast text cannot be empty.")
                    
                markup = None
                if has_app:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("📚 መጻሕፍት ቤት (Library)", web_app=WebAppInfo(url=f"{config.BASE_URL}/app")))
                    
                if act == 'test':
                    admins_to_test = get_all_admin_ids()
                    if admins_to_test:
                        for adm_id in admins_to_test:
                            try:
                                bot.send_message(adm_id, f"🧪 <b>[TEST BROADCAST PREVIEW]</b>\n\n{b_text}", parse_mode="HTML", reply_markup=markup)
                            except Exception:
                                pass
                        msg = "Test broadcast preview sent to all admins!"
                    else:
                        raise ValueError("No admin Telegram IDs configured.")
                elif act == 'blast':
                    def blast_worker():
                        uids = database.get_all_user_ids()
                        for u in uids:
                            try:
                                if lang_filter != 'all' and database.get_bot_language(u) != lang_filter:
                                    continue
                                if target_group == 'active' and database.is_banned(u):
                                    continue
                                bot.send_message(u, b_text, parse_mode="HTML", reply_markup=markup)
                            except Exception:
                                pass
                            time.sleep(0.05)
                    threading.Thread(target=blast_worker, daemon=True).start()
                    msg = "Mass broadcast launched in background safe mode."
                    
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/admin/maintenance_action'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                if not is_valid_admin_token(data.get('token')):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'Forbidden'); return
                act = data.get('action')
                msg = ""
                if act == 'clean_ghosts':
                    def run_clean():
                        conn = database.get_connection()
                        c = conn.cursor()
                        c.execute("SELECT user_id FROM users WHERE bot_blocked = 0 AND (gender IS NULL OR gender = '')")
                        stuck = [r[0] for r in c.fetchall()]
                        conn.close()
                        cleaned = 0
                        for u in stuck:
                            try:
                                bot.send_chat_action(u, "typing")
                            except:
                                database.mark_user_blocked(u, 1)
                                cleaned += 1
                            time.sleep(0.05)
                    threading.Thread(target=run_clean, daemon=True).start()
                    msg = "Ghost cleanup routine running in background."
                elif act == 'refresh_keyboards':
                    admin_id = get_admin_id()
                    if admin_id:
                        run_refresh_all_menus(admin_id)
                    msg = "Silent keyboard refresh initiated for all users."
                elif act == 'add_subadmin':
                    ident = data.get('identifier', '').strip()
                    uid_res = database.add_sub_admin_by_identifier(ident)
                    if uid_res:
                        setup_admin_menu(uid_res)
                        msg = f"Sub-Admin added: {ident} (ID: {uid_res})"
                    else:
                        raise ValueError(f"User {ident} not found in database.")
                elif act == 'remove_subadmin':
                    target_id = int(data.get('user_id'))
                    database.remove_sub_admin(target_id)
                    msg = f"Sub-Admin {target_id} removed."
                    
                self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": msg}).encode('utf-8'))
            except Exception as e:
                self.send_response(500); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode('utf-8'))
            return

        if self.path == '/shegerpay-webhook':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            try:
                data = json.loads(post_data.decode('utf-8'))
                tx_ref = data.get('reference_id')
                if not tx_ref and 'metadata' in data:
                    tx_ref = data['metadata'].get('tx_ref')
                if tx_ref:
                    import shegerpay
                    success, _ = shegerpay.verify_shegerpay_payment(tx_ref)
                    if success:
                        process_payment_success(tx_ref)
            except Exception as e:
                logging.error(f"ShegerPay Webhook error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = ThreadingHTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
def main():
    threading.Thread(target=run_dummy_server, daemon=True).start()
    threading.Thread(target=auto_nudge_daemon, daemon=True).start()
    try:
        setup_global_commands()
    except Exception as e:
        logging.error(f"Failed to setup commands at startup: {e}")
    print("=" * 50)
    print("  Baya Books Bot is LIVE!")
    print("=" * 50)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

def auto_nudge_daemon():
    import time
    while True:
        try:
            if True:
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
                        'am': f"👋 ሰላም <b>{name}</b>፣ የክፍያ ፓኬጅ መርጠው ደረሰኝ እስካሁን አልላኩም።\n\nክፍያዎን ሲያጠናቅቁ፣ በቀጥታ <b>እዚሁ ቻት ላይ</b> የከፈሉበትን ደረሰኝ (Screenshot) ይላኩልን። ሲስተማችን ወዲያውኑ አረጋግጦ አካውንትዎን ይከፍትልዎታል!\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'en': f"👋 Hi <b>{name}</b>, we noticed you selected a package but haven't uploaded your receipt yet.\n\nWhenever you're ready, simply upload a screenshot of your receipt <b>directly in this chat</b>. Our system will automatically verify it and unlock your account!\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'ti': f"👋 ሰላም <b>{name}</b>፡ ናይ ክፍሊት ፓኬጅ መሪጽኩም ቅዳሕ (ደረሰኝ) ክሳብ ሕጂ ኣይለኣኽኩምን።\n\nክፍሊትኩም ምስ ፈጸምኩም፡ ብቐጥታ <b>ኣብዚ ቻት</b> ናይ ዝኸፈልኩምሉ ቅዳሕ ስደዱልና። ሲስተምና ብቕጽበት ኣረጋጊጹ ኣካውንትኩም ክኸፍተልኩም እዩ!\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'om': f"👋 Akkam <b>{name}</b>, Paakeejii kaffaltii filattanii nagahee (receipt) ammallee hin ergine.\n\nYeroo kaffaltii raawwattan, nagahee keessan (Screenshot) <b>kallattiin asuma chat irratti</b> nuuf ergaa. Sirnichi yeruma sana mirkaneessee akkawuntii keessan ni bana!\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                    }.get(u_lang, "")
                    
                    try:
                        bot.send_message(uid, text, parse_mode="HTML")
                        database.mark_checkout_nudged(payment_id)
                    except:
                        # If blocked, we still mark it so we don't try again
                        database.mark_checkout_nudged(payment_id)
                    time.sleep(0.1)

                # 3. Paywall / Zero Quota Daily Nudge
                paywall_users = database.get_paywall_users()
                for p in paywall_users:
                    uid, name, u_lang = p['user_id'], p['first_name'] or 'there', p.get('bot_language') or 'am'
                    
                    text = {
                        'am': f"👋 ሰላም <b>{name}</b>፣ የነጻ መልዕክቶችዎ እንዳለቁ አስተውለናል።\n\nምክክራችንን ለመቀጠል እና ለውጥ ለማምጣት እባክዎ አካውንትዎን ይሙሉ (Top up ያድርጉ)።\nክፍያዎን ሲያጠናቅቁ ደረሰኙን <b>እዚሁ ቻት ላይ</b> ይላኩልን።\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'en': f"👋 Hi <b>{name}</b>, we noticed you've run out of messages.\n\nTo continue our conversation and keep making progress, please top up your account.\nWhenever you're ready, simply transfer and upload a screenshot of your receipt <b>directly in this chat</b>.\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'ti': f"👋 ሰላም <b>{name}</b>፡ ናጻ መልእኽትኹም ከምዝወድአ ኣስተውዒልና።\n\nምይይጥና ንምቕጻል በጃኹም ኣካውንትኩም ምልኡ።\nክፍሊትኩም ምስ ፈጸምኩም፡ ቅዳሕ <b>ኣብዚ ቻት</b> ስደዱልና።\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                        'om': f"👋 Akkam <b>{name}</b>, ergaawwan bilisaa keessan akka xumuraman hubanneerra.\n\nMarii keenya itti fufuuf maaloo akkawuntii keessan guutaa (Top up).\nYeroo kaffaltii raawwattan, nagahee keessan <b>kallattiin asuma chat irratti</b> nuuf ergaa.\n\n🏦 CBE: <code>1000073164765</code>\n🏦 CBE Birr: <code>0912689900</code>\n📱 Telebirr: <code>0912689900</code>",
                    }.get(u_lang, "")

                    try:
                        bot.send_message(uid, text, parse_mode="HTML")
                        database.mark_paywall_nudged(uid)
                    except:
                        database.mark_paywall_nudged(uid)
                    time.sleep(0.1)

        except Exception as e:
            print("Auto-nudge daemon error:", e)
        time.sleep(60)  # Sleep 1 minute to check for carts faster

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\\nBot stopped.")
