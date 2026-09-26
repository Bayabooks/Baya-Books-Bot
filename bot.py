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

def send_join_channel_msg(chat_id):
    """Tell user to join channel first."""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 ቻናሉን ተቀላቀል", url=f"https://t.me/{config.CHANNEL_USERNAME}"))
    markup.add(InlineKeyboardButton("✅ ተቀላቅያለሁ", callback_data="check_joined"))
    bot.send_message(
        chat_id,
        "📢 <b>ቦቱን ለመጠቀም በመጀመሪያ ቻናላችንን ይቀላቀሉ!</b>\n\n"
        "👇 ከታች ያለውን ይጫኑ",
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
            bot.reply_to(message, f"<pre>{logs[-3500:]}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, str(e))

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
        send_join_channel_msg(message.chat.id)
        return

    send_welcome(message.chat.id, user.first_name)

def send_welcome(chat_id, first_name):
    bottom_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, is_persistent=True)

    bottom_markup.add(
        KeyboardButton("➕ አዲስ መመሪያ"),
        KeyboardButton("📚 የኔ መመሪያዎች")
    )
    bottom_markup.add(
        KeyboardButton("🎁 ጓደኛ ይጋብዙ"),
        KeyboardButton("☕ ቡድኑን ያበረታቱ")
    )
    bottom_markup.add(KeyboardButton("💬 አስተያየት ይስጡን"), KeyboardButton("🌐 ቋንቋ / Language"))
    
    intro_text = (
        f"👋 <b>ሰላም {html.escape(first_name)}!</b> ወደ Baya Books በደህና መጡ።\n"
        f"🆔 የእርስዎ ID: <code>{chat_id}</code>\n\n"
        f"📚 ከዓለም ምርጥ መጽሐፍት ጥበብ በመውሰድ ለእርስዎ ህይወት ብቻ "
        f"የተዘጋጀ <b>ግላዊ የህይወት መመሪያ</b> እንሰራልዎታለን።\n\n"
        f"✨ መጽሐፉን ይምረጡ፣ ጥቂት ጥያቄዎችን ይመልሱ፣ "
        f"ህይወትዎን የሚቀይር መመሪያ ይቀበሉ!"
    )

    bot.send_message(
        chat_id, 
        intro_text, 
        parse_mode="HTML", 
        reply_markup=bottom_markup
    )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📖 መጽሐፉን እኔው ራሴ እመርጣለሁ", callback_data="has_book"),
        InlineKeyboardButton("🧭 መጽሐፎቹን እናንተ አማርጡኝ", callback_data="choose_for_me"),
        InlineKeyboardButton("💡 ጥልቅ የስነ-ልቦና ምክር ፈልጋለሁ", callback_data="get_advice"),
    )

    credits = database.get_credits(chat_id)
    credit_line = f"\n🎫 የእርስዎ ክሬዲት: <b>{credits} መመሪያ</b>\n" if credits > 0 else ""

    has_free_full = database.has_free_protocol(chat_id)
    previews_left, _ = database.get_preview_quota(chat_id)
    
    gifts = []
    if previews_left > 0:
        gifts.append(f"{previews_left} ነጻ የሙከራ መመሪያዎች")
    if has_free_full:
        gifts.append("1 ሙሉ ነጻ መመሪያ")
        
    if gifts:
        gifts_text = " እና ".join(gifts)
        preview_line = f"🎁 <b>ያልዎት ስጦታ፡ {gifts_text}</b>\n"
    else:
        preview_line = ""

    bot.send_message(
        chat_id,
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{preview_line}{credit_line}\n"
        f"👇 ከታች ያለውን በመጫን ይጀምሩ",
        parse_mode="HTML", reply_markup=markup,
    )

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
        send_join_channel_msg(message.chat.id); return

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
        send_join_channel_msg(message.chat.id); return
    clear_state(message.from_user.id)
    send_welcome(message.chat.id, message.from_user.first_name)

@bot.message_handler(commands=["reset_advice"])
def cmd_reset_advice(message):
    if is_admin(message.from_user):
        database.save_advice_history(message.from_user.id, '[]')
        bot.reply_to(message, "🔄 <b>Advice Chat History Reset successfully.</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ Admin only command.")

# ══════════════════════════════════════════
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
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("📤 Push PDF", callback_data="admin_push_pdf"),
    )
    markup.add(
        InlineKeyboardButton("💳 Add Credit", callback_data="admin_credit"),
        InlineKeyboardButton("🚫 Ban/Unban", callback_data="adm_ban_menu"),
    )
    markup.add(
        InlineKeyboardButton("👑 Sub-Admins", callback_data="adm_subadmin_menu"),
        InlineKeyboardButton("📋 Recent Orders", callback_data="adm_recent_orders"),
    )
    markup.add(
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
        bot.answer_callback_query(call.id, "🚫 ይህ አካውንት ታግዷል።", show_alert=True)
        return

    # ── Channel Join Check ───────────────────

    if data.startswith("setlang_"):
        lang_code = data.split("_")[1]
        database.set_bot_language(uid, lang_code)
        
        msg = "✅ Language saved!"
        if lang_code == "am": msg = "✅ ቋንቋው ወደ አማርኛ ተቀይሯል!"
        elif lang_code == "om": msg = "✅ Afaan Oromoo filatameera!"
        elif lang_code == "ti": msg = "✅ ናብ ትግርኛ ተቐይሩ እዩ!"
        
        bot.answer_callback_query(call.id, msg)
        bot.edit_message_text(msg, chat_id, call.message.message_id)
        return

    if data == "check_joined":
        if check_channel_member(uid):
            bot.answer_callback_query(call.id, "✅ ተቀላቅለዋል!")
            safe_delete_message(chat_id, call.message.message_id)
            send_welcome(chat_id, call.from_user.first_name)
        else:
            bot.answer_callback_query(call.id, "❌ ገና አልተቀላቀሉም!", show_alert=True)
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

    # ── Start: "I have a book" ───────────────
    if data == "has_book":
        if not enforce_preview_quota(uid, chat_id, call.id): return
        bot.answer_callback_query(call.id)
        get_session(uid)["data"] = {}  # Clear previous choices
        set_state(uid, "AWAITING_BOOK_INPUT")
        bot.send_message(
            chat_id,
            "📖 <b>ድንቅ!</b>\n\nየመጽሐፉን ስም ይፃፉ ወይም\nየመጽሐፉን ፎቶ ያንሱና ይላኩልን።",
            parse_mode="HTML",
        )
        return

    # ── Start: "Get Advice" ──────────────────
    if data == "get_advice":
        bot.answer_callback_query(call.id)
        set_state(uid, "ADVICE_CHAT_MODE")
        
        markup = InlineKeyboardMarkup()
        if is_admin(call.from_user):
            markup.add(InlineKeyboardButton("🔄 Reset Chat (Admin)", callback_data="admin_reset_chat"))
            
        bot.send_message(
            chat_id,
            "💡 <b>ጥልቅ የስነ-ልቦና ምክር</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "እኔ ላዩን የማይዳስስ፣ ጥልቅ እና እውነተኛ የስነ-ልቦና አማካሪዎ ነኝ።\n"
            "ስለሚያስጨንቅዎት ነገር፣ ውስጣዊ ትግልዎ፣ ወይም ስለተሰማዎት ስሜት በነፃነት ያካፍሉኝ።\n\n"
            "<i>(ወደ ዋናው ማውጫ ለመመለስ /new ይጫኑ)</i>\n\n"
            "<b>እስኪ እንነጋገር... አሁን ላይ ምን እያስቸገረዎት ነው?</b>",
            parse_mode="HTML", reply_markup=markup if is_admin(call.from_user) else None
        )
        return


    # ── Start: "Choose for me" ───────────────
    if data == "choose_for_me":
        if not enforce_preview_quota(uid, chat_id, call.id): return
        bot.answer_callback_query(call.id)
        get_session(uid)["data"] = {}  # Clear previous choices
        set_state(uid, "AWAITING_CATEGORY")
        markup = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(f"{emoji} {am}", callback_data=cid) for cid, emoji, am, en in CATEGORIES]
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                markup.row(buttons[i], buttons[i+1])
            else:
                markup.row(buttons[i])
        bot.send_message(
            chat_id,
            "🧭 <b>በጣም ጥሩ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "ዛሬ በየትኛው የህይወት ክፍል ትልቅ ለውጥ ማምጣት ይፈልጋሉ?\n\n"
            "👇 ከታች ይምረጡ",
            parse_mode="HTML", reply_markup=markup,
        )
        return

    # ── Buy Previews Top-Up ──────────────────
    if data == "buy_previews":
        bot.answer_callback_query(call.id)
        show_payment_instructions(chat_id, 100, uid, "TOPUP")
        return

    # ── Buy Advice Packages ──────────────────
    if data.startswith("buy_advice_"):
        bot.answer_callback_query(call.id)
        msgs = int(data.split("_")[2])
        amount = {120: 200, 300: 400, 600: 700}.get(msgs, 200)
        show_payment_instructions(chat_id, amount, uid, f"ADVICE_{msgs}")
        return

    # ── Admin Reset Chat ─────────────────────
    if data == "admin_reset_chat":
        if is_admin(call.from_user):
            database.save_advice_history(uid, '[]')
            bot.answer_callback_query(call.id, "✅ Chat History Wiped!", show_alert=True)
            bot.send_message(chat_id, "🔄 <b>Chat reset successfully.</b>", parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "❌ Not allowed", show_alert=True)
        return

    # ── Show Drafts ──────────────────────────
    if data == "show_drafts":
        bot.answer_callback_query(call.id)
        drafts = database.get_user_drafts(uid)
        if not drafts:
            bot.send_message(chat_id, "ምንም የተጀመረ መመሪያ የለዎትም።")
            return
        markup = InlineKeyboardMarkup(row_width=1)
        for d in drafts:
            markup.add(InlineKeyboardButton(f"📖 {d['book_title'][:30]}", callback_data=f"buy_draft_{d['id']}"))
        bot.send_message(chat_id, "💳 <b>ለመግዛት የሚፈልጉትን መመሪያ ይምረጡ:</b>", parse_mode="HTML", reply_markup=markup)
        return

    # ── Buy Draft ────────────────────────────
    if data.startswith("buy_draft_"):
        order_id = int(data.split("_")[2])
        bot.answer_callback_query(call.id)
        session = get_session(uid)
        session["data"] = {"order_id": order_id}
        
        if database.has_free_protocol(uid):
            bot.send_message(chat_id, "🎁 <b>እንኳን ደስ አለዎት!</b>\n\nይህ የመጀመሪያዎ ሙሉ መመሪያ ስለሆነ፣ በ <b>Baya Books</b> ስፖንሰርነት <b>በነጻ</b> ተዘጋጅቶልዎታል!", parse_mode="HTML")
            database.mark_free_protocol_used(uid)
            # Reconstruct data from order
            order = database.get_order(order_id)
            if order:
                session["data"] = {
                    "book_title": order["book_title"],
                    "gender": order["gender"],
                    "age_range": order["age_range"],
                    "goal": order.get("goal", ""),
                    "location": order.get("location", ""),
                    "living_situation": order.get("living_situation", ""),
                    "employment": order.get("employment", "Working"),
                    "specific_change": order.get("specific_change", ""),
                    "language": order["language"],
                    "order_id": order_id,
                }
                generate_and_deliver_pdf(chat_id, uid, session["data"])
            return
            
        show_pricing(chat_id, uid)
        return

    # ── Category Selected ────────────────────
    if data.startswith("cat_"):
        bot.answer_callback_query(call.id)
        cat = next((c for c in CATEGORIES if c[0] == data), None)
        if not cat:
            return
            
        emoji = cat[1]
        cat_name_am = cat[2]
        
        subs = SUBCATEGORIES.get(data, [])
        if not subs:
            return
            
        set_state(uid, "AWAITING_SUBCATEGORY")
        markup = InlineKeyboardMarkup(row_width=1)
        for sub_id, sub_am, sub_en in subs:
            markup.add(InlineKeyboardButton(sub_am, callback_data=sub_id))
            
        bot.send_message(
            chat_id,
            f"{emoji} <b>{cat_name_am}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "በዚህ ክፍል ውስጥ በተለይ የትኛው ላይ ትኩረት ማድረግ ይፈልጋሉ?\n\n👇 ከታች ይምረጡ",
            parse_mode="HTML", reply_markup=markup
        )
        return

    # ── Subcategory Selected ─────────────────
    if data.startswith("sub_"):
        bot.answer_callback_query(call.id)
        loading_msg = bot.send_message(chat_id, "⏳ <b>መጽሐፍት በመፈለግ ላይ...</b>", parse_mode="HTML")
        set_state(uid, "AWAITING_BOOK_PICK")
        
        sub_name_en = ""
        sub_name_am = ""
        for cat_id, cat_subs in SUBCATEGORIES.items():
            for sid, sam, sen in cat_subs:
                if sid == data:
                    sub_name_en = sen
                    sub_name_am = sam
                    break
            if sub_name_en:
                break
                
        if not sub_name_en:
            safe_delete_message(chat_id, loading_msg.message_id)
            return

        # Pass subcategory name directly as the "category" topic to the AI, and request 5 books
        books = ai_engine.recommend_books(sub_name_en, count=5)
        safe_delete_message(chat_id, loading_msg.message_id)
        
        if isinstance(books, dict) and "error" in books:
            bot.send_message(chat_id, f"⚠️ ይቅርታ፣ ችግር ተፈጥሯል። እባክዎ እንደገና ይሞክሩ።")
            return
            
        if not books or len(books) < 3:
            bot.send_message(chat_id, "⚠️ ችግር ተፈጥሯል። እባክዎ እንደገና ይሞክሩ። /new")
            return

        session = get_session(uid)
        session["data"]["recommended_books"] = books

        text = f"📚 <b>ለ {sub_name_am} ምርጥ 5 መጽሐፍት</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        markup = InlineKeyboardMarkup()
        for i, b in enumerate(books):
            text += f"{i+1}️⃣ 📕 <b>{b['title']}</b>\n   ↳ <i>{b['description']}</i>\n\n"
            markup.add(InlineKeyboardButton(f"{i+1}️⃣ {b['title']}", callback_data=f"pick_{i}"))

        text += "👇 <b>የትኛውን ይመርጣሉ?</b>"
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return

    # ── Book Picked from Recommendations ─────
    if data.startswith("pick_"):
        idx = int(data.replace("pick_", ""))
        session = get_session(uid)
        books = session["data"].get("recommended_books", [])
        if idx < len(books):
            book_title = books[idx]["title"]
            set_state(uid, "AWAITING_GENDER", book_title=book_title)
            bot.answer_callback_query(call.id)
            ask_gender(chat_id, book_title)
        return

    # ── Book Cover Confirmed ─────────────────
    if data == "confirm_book":
        session = get_session(uid)
        book_title = session["data"].get("book_title", "")
        set_state(uid, "AWAITING_GENDER", book_title=book_title)
        bot.answer_callback_query(call.id)
        ask_gender(chat_id, book_title)
        return

    if data == "retry_book":
        set_state(uid, "AWAITING_BOOK_INPUT")
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📖 የመጽሐፉን ስም ይፃፉ ወይም ፎቶ ይላኩ።")
        return

    # ── Gender ───────────────────────────────
    if data in ("gen_m", "gen_f"):
        gender = "male" if data == "gen_m" else "female"
        
        # Check if admin is in push flow
        session = get_session(uid)
        if session["state"] == "ADMIN_PUSH_GENDER" and is_admin(call.from_user):
            target_id = session["data"].get("target_id")
            push_book = session["data"].get("push_book", "")
            set_state(uid, "IDLE")
            bot.answer_callback_query(call.id, "⏳ Generating...")
            d = {
                "book_title": push_book,
                "gender": gender,
                "age_range": "25-29",
                "goal": "",
                "location": "Ethiopia",
                "living_situation": "Alone",
                "employment": "Working",
                "specific_change": "",
                "language": "am",
            }
            generate_and_deliver_pdf(target_id, target_id, d)
            bot.send_message(chat_id, f"✅ PDF ለ {target_id} ተልኳል!")
            clear_state(uid)
            return
        
        set_state(uid, "AWAITING_AGE", gender=gender)
        bot.answer_callback_query(call.id)
        ask_age(chat_id)
        return

    # ── Age Range ────────────────────────────
    if data.startswith("age_"):
        age_item = next((a for a in AGE_RANGES if a[0] == data), None)
        if age_item:
            set_state(uid, "AWAITING_LIVING", age_range=age_item[2])
            bot.answer_callback_query(call.id)
            ask_living_situation(chat_id)
        return

    # ── Living Situation ─────────────────────
    if data.startswith("liv_"):
        liv = "Alone" if data == "liv_alone" else "With Family"
        set_state(uid, "AWAITING_LOCATION", living_situation=liv)
        bot.answer_callback_query(call.id)
        ask_location(chat_id)
        return

    # ── Location ─────────────────────────────
    if data.startswith("loc_"):
        loc = "Ethiopia" if data == "loc_ethiopia" else "Abroad"
        set_state(uid, "AWAITING_SPECIFIC_CHANGE", location=loc)
        bot.answer_callback_query(call.id)
        ask_specific_change(chat_id)
        return

    # ── Language ──────────────────────────────
    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        session = get_session(uid)
        d = session["data"]
        set_state(uid, "GENERATING_PREVIEW", language=lang)
        bot.answer_callback_query(call.id)
        generate_and_show_preview(chat_id, uid, d)
        return

    # ── Buy / Pricing ────────────────────────
    if data == "buy_now":
        bot.answer_callback_query(call.id)
        if is_admin(call.from_user):
            bot.send_message(chat_id, "👑 <b>የአድሚን መብት!</b> ክፍያ አያስፈልግም።", parse_mode="HTML")
            session = get_session(uid)
            generate_and_deliver_pdf(chat_id, uid, session["data"])
            return
            
        if database.has_free_protocol(uid):
            bot.send_message(chat_id, "🎁 <b>እንኳን ደስ አለዎት!</b>\n\nይህ የመጀመሪያዎ ሙሉ መመሪያ ስለሆነ፣ በ <b>Baya Books</b> ስፖንሰርነት <b>በነጻ</b> ተዘጋጅቶልዎታል!", parse_mode="HTML")
            database.mark_free_protocol_used(uid)
            session = get_session(uid)
            generate_and_deliver_pdf(chat_id, uid, session["data"])
            return
            
        if database.is_vip(uid):
            bot.send_message(chat_id, "👑 <b>VIP አባል!</b>\nበVIP አባልነትዎ ምክንያት ክፍያ አያስፈልግም።", parse_mode="HTML")
            session = get_session(uid)
            generate_and_deliver_pdf(chat_id, uid, session["data"])
            return
            
        show_pricing(chat_id, uid)
        return

    if data == "pay_single":
        bot.answer_callback_query(call.id)
        show_payment_instructions(chat_id, config.PRICE_SINGLE, uid)
        return

    if data == "use_credit":
        session = get_session(uid)
        d = session["data"]
        if database.use_credit(uid):
            bot.answer_callback_query(call.id, "✅ ክሬዲት ተቀንሷል!")
            generate_and_deliver_pdf(chat_id, uid, d)
        else:
            bot.answer_callback_query(call.id, "❌ ክሬዲት የለዎትም!", show_alert=True)
        return

    if data.startswith("tip_"):
        amount = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "እየተዘጋጀ ነው...")
        
        checkout_url, tx_ref, err = chapa.generate_chapa_link(amount, uid, "TIP")
        if not checkout_url:
            bot.send_message(chat_id, f"❌ የክፍያ ሊንክ ማመንጨት አልተቻለም።\n<b>ምክንያት:</b> {err}", parse_mode="HTML")
            return
            
        markup = InlineKeyboardMarkup()
        from telebot.types import WebAppInfo
        markup.add(InlineKeyboardButton(f"💳 {amount} ብር ይሸልሙ", web_app=WebAppInfo(url=checkout_url)))
        
        bot.send_message(
            chat_id,
            f"☕ <b>{amount} ብር ስጦታ</b>\nእባክዎ ከታች ያለውን ቁልፍ ተጭነው ስጦታዎን ይላኩ። ከልብ እናመሰግናለን!",
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
        top_books = "\n".join([f"  {i+1}. 📕 {b[0]} ({b[1]}x)" for i, b in enumerate(stats["top_books"])]) or "  — None"
        top_goals = "\n".join([f"  {i+1}. 🎯 {g[0]} ({g[1]}x)" for i, g in enumerate(stats["top_goals"])]) or "  — None"
        total = stats["male_count"] + stats["female_count"]
        m_pct = f"{stats['male_count']/total*100:.0f}%" if total > 0 else "0%"
        f_pct = f"{stats['female_count']/total*100:.0f}%" if total > 0 else "0%"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        
        bot.send_message(chat_id,
            f"📊 <b>DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Total Users: <b>{stats['total_users']}</b>\n"
            f"🟢 New Today: <b>{stats['new_today']}</b>\n"
            f"📄 Total PDFs: <b>{stats['total_pdfs']}</b>\n\n"
            f"━━ 📈 Today's Activity ━━━━━━━\n"
            f"  🎁 Trials Given: <b>{stats['today_trials']}</b>\n"
            f"  ✅ Full Packages: <b>{stats['today_full']}</b>\n\n"
            f"━━ 💰 Revenue ━━━━━━━━━━━━\n"
            f"  📅 Today: <b>{stats['today_revenue']:,} ETB</b>\n"
            f"  📆 Weekly: <b>{stats['weekly_revenue']:,} ETB</b>\n"
            f"  💵 Total: <b>{stats['total_revenue']:,} ETB</b>\n\n"
            f"━━ 🔥 Top 5 Books ━━━━━━━━━\n{top_books}\n\n"
            f"━━ 👥 Gender Split ━━━━━━━━━\n"
            f"  👨 Male: {m_pct} | 👩 Female: {f_pct}",
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
            InlineKeyboardButton("💳 Add Credit", callback_data=f"adm_credit_{target_id}"),
            InlineKeyboardButton("📤 Push PDF", callback_data=f"adm_push_{target_id}"),
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
    
    # ── Admin: Quick Push from profile ────────
    if data.startswith("adm_push_") and not data.startswith("adm_push_pdf"):
        if not is_admin(call.from_user): return
        target_id = int(data.replace("adm_push_", ""))
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_PUSH_BOOK", target_id=target_id)
        bot.send_message(chat_id, f"📤 <b>Push PDF</b>\n\nBook title for user <code>{target_id}</code>?\n(/cancel to exit)", parse_mode="HTML")
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
    
    # ── Admin: Recent Orders ─────────────────
    if data == "adm_recent_orders":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "📋 Loading...")
        orders = database.get_recent_orders(10)
        text = "📋 <b>Recent 10 Orders</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for o in orders:
            status_icon = {"draft": "📝", "preview_sent": "👁️", "delivered": "✅", "paid": "💰"}.get(o["status"], "❓")
            text += f"{status_icon} <b>{o['book_title'][:25]}</b>\n"
            text += f"   👤 {o['first_name'] or 'N/A'} — <code>{o['user_id']}</code>\n"
            text += f"   📅 {o['created_date'][:10] if o['created_date'] else 'N/A'}\n\n"
        if not orders:
            text += "No orders yet.\n"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin Menu", callback_data="adm_back"))
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return
    

    # ── Admin: VIP Manager ───────────────────
    if data == "adm_vip_menu":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_VIP_USER")
        bot.send_message(chat_id, "👑 <b>VIP Manager</b>\n\nEnter User ID to grant VIP:\n(/cancel to exit)", parse_mode="HTML")
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

    # ── Admin: Push PDF ──────────────────────
    if data == "admin_push_pdf":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id)
        set_state(uid, "ADMIN_PUSH_USER")
        bot.send_message(chat_id, "📤 <b>PDF ላክ</b>\n\nየደንበኛውን User ID ያስገቡ:", parse_mode="HTML")
        return



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
def generate_and_show_preview(chat_id, uid, data):
    """Generate Part 1 (free hook) and show it."""
    if not data.get("book_title") or not data.get("age_range"):
        bot.send_message(chat_id, "⚠️ የሲስተም እድሳት ስለተደረገ መረጃዎ ጠፍቷል። እባክዎ /start በመጫን እንደገና ይጀምሩ። (Session expired)")
        return
        
    # Enforce quota one last time just in case
    if uid != get_admin_id():
        previews_left, _ = database.get_preview_quota(uid)
        if previews_left <= 0:
            enforce_preview_quota(uid, chat_id)
            return

    loading = bot.send_message(chat_id, "⏳ <b>ግላዊ ምርመራዎ በመዘጋጀት ላይ...</b>", parse_mode="HTML")

    preview = ai_engine.generate_preview(
        data.get("book_title", ""),
        data.get("gender", "male"),
        data.get("age_range", "20-24"),
        data.get("goal", ""),
        data.get("location", "Ethiopia"),
        data.get("living_situation", "Alone"),
        data.get("employment", "Working"),
        data.get("specific_change", ""),
        data.get("language", "am"),
    )

    safe_delete_message(chat_id, loading.message_id)

    if not preview:
        bot.send_message(chat_id, "⚠️ ችግር ተፈጥሯል። እባክዎ /new ይጫኑ እንደገና ለመሞከር።")
        return

    # Consume a preview quota
    if uid != get_admin_id():
        database.consume_preview(uid)

    # Save order
    order_id = database.create_order(
        uid, 
        data.get("book_title"), 
        data.get("gender"),
        data.get("age_range"), 
        data.get("goal"), 
        data.get("location"),
        data.get("living_situation"),
        data.get("employment"),
        data.get("specific_change"),
        data.get("language", "am"),
    )
    database.update_order_preview(order_id, preview)
    set_state(uid, "PREVIEW_SHOWN", order_id=order_id)

    # Send preview
    header = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 <b>{html.escape(data.get('book_title', ''))}</b> መመሪያ\n"
        f"👤 {data.get('age_range', '')} | {GENDER_DISPLAY.get(data.get('gender', ''), data.get('gender', ''))}\n"
        f"🏠 {LIVING_DISPLAY.get(data.get('living_situation', ''), data.get('living_situation', ''))} | 📍 {LOCATION_DISPLAY.get(data.get('location', ''), data.get('location', ''))}\n"
        f"🎯 {html.escape(data.get('specific_change', ''))}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    # Truncate preview if too long for Telegram (4096 chars max)
    max_len = 4096 - len(header) - 200
    display_preview = preview[:max_len] if len(preview) > max_len else preview

    try:
        bot.send_message(chat_id, header + display_preview, parse_mode="HTML")
    except Exception:
        # If Telegram rejects the HTML (due to unclosed tags or invalid characters),
        # strip the <b> tags and send as plain text
        clean_preview = display_preview.replace("<b>", "").replace("</b>", "")
        clean_header = header.replace("<b>", "").replace("</b>", "")
        bot.send_message(chat_id, clean_header + clean_preview)

    # CTA
    strikethrough_300 = "3\u03360\u03360\u0336 ብ\u0336ር\u0336"
    btn_text = f"🎁 የመጀመሪያዎን ሙሉ መመሪያ በነጻ ያግኙ ({strikethrough_300})" if database.has_free_protocol(uid) else f"💳 ሙሉ መመሪያ {config.PRICE_SINGLE} ብር ({strikethrough_300})"
    
    bot.send_message(
        chat_id,
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⬆️ <b>ይህ የመነሻ ምርመራ ብቻ ነው!</b>\n\n"
        "ሙሉው የ90-ቀን ስትራቴጂ፣ ዕለታዊ ልምምድ፣\n"
        "የሳምንታዊ ግምገማ፣ እና ሙሉ ግላዊ መመሪያ\n"
        "ለማግኘት ከታች ይዘዙ 👇\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(btn_text, callback_data="buy_now")
        ),
    )


def show_pricing(chat_id, uid):
    credits = database.get_credits(uid)
    
    if credits > 0:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(f"🎫 ክሬዲት ተጠቀም ({credits} ቀሪ)", callback_data="use_credit"))
        strikethrough_300 = "3\u03360\u03360\u0336 ብ\u0336ር\u0336"
        markup.add(InlineKeyboardButton(f"1️⃣ 1 መመሪያ — {config.PRICE_SINGLE} ብር ({strikethrough_300})", callback_data="pay_single"))
        bot.send_message(
            chat_id,
            "💳 <b>ክፍያ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "ከታች የሚስማማዎትን ይምረጡ 👇",
            parse_mode="HTML", reply_markup=markup,
        )
    else:
        # Bypass directly to payment instructions
        set_state(uid, "AWAITING_RECEIPT", payment_amount=config.PRICE_SINGLE)
        show_payment_instructions(chat_id, config.PRICE_SINGLE, uid)

def show_payment_instructions(chat_id, amount, uid, purpose="PROTOCOL"):
    checkout_url, tx_ref, err = chapa.generate_chapa_link(amount, uid, purpose)
    if not checkout_url:
        bot.send_message(chat_id, f"❌ የክፍያ ሊንክ ማመንጨት አልተቻለም።\n<b>ምክንያት:</b> {err}", parse_mode="HTML")
        return
        
    markup = InlineKeyboardMarkup()
    from telebot.types import WebAppInfo
    markup.add(InlineKeyboardButton("💳 Pay Now / አሁን ይክፈሉ", web_app=WebAppInfo(url=checkout_url)))
    
    bot.send_message(
        chat_id,
        f"📱 <b>ክፍያ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"እባክዎ ከታች ያለውን <b>Pay Now</b> ቁልፍ በመጫን <b>{amount} ብር</b> ይክፈሉ።\n"
        f"ክፍያዎ እንደተጠናቀቀ መመሪያዎ በራስ-ሰር ይላክልዎታል!",
        parse_mode="HTML",
        reply_markup=markup
    )


def generate_and_deliver_pdf(chat_id, uid, data):
    """Generate full protocol and deliver it."""
    if not data.get("book_title") or not data.get("age_range"):
        bot.send_message(chat_id, "⚠️ የሲስተም እድሳት ስለተደረገ መረጃዎ ጠፍቷል። እባክዎ /start በመጫን እንደገና ይጀምሩ። (Session expired)")
        return
        
    loading = bot.send_message(chat_id, "⏳ <b>ግላዊ መመሪያዎ በመዘጋጀት ላይ...</b>\nይህ ከ30-60 ሰከንድ ሊወስድ ይችላል።", parse_mode="HTML")

    full_text = ai_engine.generate_full_protocol(
        data.get("book_title", ""),
        data.get("gender", "male"),
        data.get("age_range", "20-24"),
        data.get("goal", ""),
        data.get("location", "Ethiopia"),
        data.get("living_situation", "Alone"),
        data.get("employment", "Working"),
        data.get("specific_change", ""),
        data.get("language", "am"),
    )

    if not full_text:
        safe_delete_message(chat_id, loading.message_id)
        bot.send_message(chat_id, "⚠️ ይቅርታ፣ ችግር ተፈጥሯል። እባክዎ እንደገና ይሞክሩ ወይም @Bayabooks ያናግሩን።")
        return

    # Generate Telegraph URL
    page_url = telegraph_generator.create_protocol_page(
        data.get("book_title", "Baya Books Protocol"), 
        full_text
    )

    safe_delete_message(chat_id, loading.message_id)

    if not page_url or page_url.startswith("ERROR:"):
        bot.send_message(chat_id, f"⚠️ የቴክኒክ ችግር ተፈጥሯል: {page_url}")
        return

    # Send Link
    msg_text = (
        f"🎉 <b>ግላዊ መመሪያዎ ዝግጁ ነው!</b>\n\n"
        f"📖 <b>{html.escape(data.get('book_title', ''))}</b>\n"
        f"👤 {data.get('age_range', '')} | {GENDER_DISPLAY.get(data.get('gender', ''), data.get('gender', ''))}\n"
        f"🏠 {LIVING_DISPLAY.get(data.get('living_situation', ''), data.get('living_situation', ''))} | 📍 {LOCATION_DISPLAY.get(data.get('location', ''), data.get('location', ''))}\n"
        f"🎯 {html.escape(data.get('specific_change', ''))}\n\n"
        f"👇 <b>ከታች ያለውን ሊንክ ተጭነው ያንብቡ:</b>\n"
        f"{page_url}"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📖 መመሪያዎን ያንብቡ", url=page_url))
    
    try:
        sent_msg = bot.send_message(chat_id, msg_text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to send Telegraph link: {e}")
        sent_msg = bot.send_message(chat_id, f"ግላዊ መመሪያዎ ዝግጁ ነው!\n{page_url}")

    # Save to database
    order_id = data.get("order_id")
    if order_id:
        # Save the URL instead of file_id
        database.update_order_full(order_id, full_text, page_url)



    # Show tip CTA instead of referral
    show_tip_cta(chat_id)
    
    clear_state(uid)


def show_tip_cta(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("☕ 100 ብር", callback_data="tip_100"),
        InlineKeyboardButton("🎁 1,000 ብር", callback_data="tip_1000")
    )
    markup.add(
        InlineKeyboardButton("🏅 5,000 ብር", callback_data="tip_5000"),
        InlineKeyboardButton("💎 10,000 ብር", callback_data="tip_10000")
    )
    bot.send_message(
        chat_id,
        "💎 <b>የ Baya Books ራዕይን ይደግፉ!</b>\n\n"
        "ይህን መመሪያ ጠቃሚ ሆኖ ካገኙት እና የ Baya Books ቴክኖሎጂ ለብዙዎች እንዲደርስ ከተመኙ፣ ከታች ካሉት አማራጮች በመምረጥ የፕሮጀክታችን ደጋፊ መሆን ይችላሉ።\n\n"
        "🙏 ከልብ እናመሰግናለን!",
        parse_mode="HTML",
        reply_markup=markup
    )

# ══════════════════════════════════════════
#  PAYMENT HANDLING
# ══════════════════════════════════════════
def handle_payment_approved(payment_id):
    """Process an approved payment — generate and deliver PDF."""
    payment = database.get_payment(payment_id)
    if not payment:
        return

    database.approve_payment(payment_id)
    uid = payment["user_id"]
    order_id = payment["order_id"]
    if order_id == -1:
        database.reset_previews(uid, 5)
        bot.send_message(uid, "✅ <b>ክፍያዎ ተረጋግጧል!</b>\n\n5 ተጨማሪ ነጻ ምርመራዎች ተጨምሮልዎታል!\n/new ይጫኑ", parse_mode="HTML")
        return

    order = database.get_order(order_id)
    if not order:
        return

    # User bought a full protocol, reset their preview quota too!
    database.reset_previews(uid, 5)

    data = {
        "book_title": order["book_title"],
        "gender": order["gender"],
        "age_range": order["age_range"],
        "goal": order["goal"],
        "location": order.get("location", ""),
        "living_situation": order.get("living_situation", ""),
        "employment": order.get("employment", ""),
        "specific_change": order.get("specific_change", ""),
        "language": order["language"],
        "order_id": order_id,
    }
    generate_and_deliver_pdf(uid, uid, data)


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
        bot.reply_to(message, "🚫 ይህ አካውንት ታግዷል።")
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
        success, failed = 0, 0
        for u in users:
            try:
                bot.copy_message(u, chat_id, message.message_id); success += 1
            except Exception:
                failed += 1
        bot.send_message(chat_id, f"✅ Broadcast complete!\n✔️ {success} delivered | ❌ {failed} failed")
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

    if state == "ADMIN_PUSH_USER" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ ተሰርዧል."); return
        try:
            target_id = int(message.text.strip())
            target = database.get_user(target_id)
            if not target:
                bot.send_message(chat_id, "❌ ተጠቃሚ አልተገኘም!"); return
            set_state(uid, "ADMIN_PUSH_BOOK", target_id=target_id)
            bot.send_message(chat_id, f"👤 {target['first_name']}\n\n📖 የመጽሐፉ ስም?")
        except ValueError:
            bot.send_message(chat_id, "❌ User ID ቁጥር ብቻ!")
        return

    if state == "ADMIN_PUSH_BOOK" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ ተሰርዧል."); return
        set_state(uid, "ADMIN_PUSH_GENDER", push_book=message.text.strip())
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👨 ወንድ", callback_data="gen_m"), InlineKeyboardButton("👩 ሴት", callback_data="gen_f"))
        bot.send_message(chat_id, "👤 ጾታ?", reply_markup=markup)
        # Override the gender callback to continue admin push flow
        return

    # ── Channel check for non-admin ──────────
    if not is_admin(message.from_user) and not check_channel_member(uid):
        send_join_channel_msg(chat_id); return

    # ── Bottom Menu Handlers ─────────────────
    if message.text == "➕ አዲስ መመሪያ":
        send_welcome(chat_id, message.from_user.first_name)
        return

    
    if message.text == "🌐 ቋንቋ / Language":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="setlang_am"),
            InlineKeyboardButton("🇪🇹 Oromiffa", callback_data="setlang_om"),
            InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data="setlang_ti")
        )
        markup.add(InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"))
        bot.send_message(chat_id, "የቦቱን ቋንቋ ይምረጡ / Choose Bot Language:", reply_markup=markup)
        return

    if message.text == "📚 የኔ መመሪያዎች":
        orders = database.get_user_orders(uid)
        if not orders:
            bot.send_message(chat_id, "በአሁኑ ሰዓት የተዘጋጀ መመሪያ የለዎትም። አዲስ ለመጀመር '➕ አዲስ መመሪያ' ይጫኑ።")
        else:
            bot.send_message(chat_id, "📚 <b>የእርስዎ መመሪያዎች</b>\n━━━━━━━━━━━━━━━━━━━━", parse_mode="HTML")
            for order in orders:
                bot.send_message(
                    chat_id,
                    f"📖 <b>{html.escape(order['book_title'])}</b>\n"
                    f"📅 {order['delivered_date'][:10]}\n\n"
                    f"🔗 {order['pdf_file_id']}",
                    parse_mode="HTML"
                )
        return

    if message.text == "🎁 ጓደኛ ይጋብዙ":
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start=ref_{uid}"
        count = database.get_uncredited_referral_count(uid)
        bot.send_message(
            chat_id,
            f"🎁 <b>ጓደኛዎን ይጋብዙ፣ ነጻ መመሪያ ያግኙ!</b>\n\n"
            f"5 ጓደኞችዎን ሲጋብዙ 1 ነጻ መመሪያ ያገኛሉ!\n\n"
            f"📊 ያጋበዙት: <b>{count}</b>/5\n\n"
            f"🔗 የእርስዎ መጋበዣ ሊንክ:\n<code>{link}</code>",
            parse_mode="HTML"
        )
        return

    if message.text == "☕ ቡድኑን ያበረታቱ":
        show_tip_cta(chat_id)
        return

    if message.text == "💬 አስተያየት ይስጡን":
        bot.send_message(chat_id, "💡 አስተያየትዎን፣ ጥያቄዎን ወይም ያጋጠመዎትን ችግር እዚህ ይጻፉልን። (ወደ አድሚን ይላካል)")
        set_state(uid, "AWAITING_FEEDBACK")
        return

    if state == "AWAITING_FEEDBACK" and message.text:
        admin_id = get_admin_id()
        if admin_id:
            bot.send_message(admin_id, f"💬 <b>አዲስ አስተያየት:</b>\n👤 {message.from_user.first_name} (@{message.from_user.username})\n\n{html.escape(message.text)}", parse_mode="HTML")
        bot.send_message(chat_id, "✅ አስተያየትዎ ደርሶናል! ከልብ እናመሰግናለን።")
        clear_state(uid)
        return

    # ── Advice Chat Mode ─────────────────────
    if state == "ADVICE_CHAT_MODE" and message.text:
        # Ignore commands
        if message.text.startswith("/"):
            return
            
        # Check quota
        msgs_left = database.get_advice_messages_left(uid)
        is_vip = database.is_vip(uid)
        is_adm = is_admin(message.from_user)
        
        if msgs_left <= 0 and not is_vip and not is_adm:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔹 Starter: 200 ብር (120 መልዕክቶች)", callback_data="buy_advice_120"))
            markup.add(InlineKeyboardButton("🔹 Pro: 400 ብር (300 መልዕክቶች)", callback_data="buy_advice_300"))
            markup.add(InlineKeyboardButton("🔹 Heavy: 700 ብር (600 መልዕክቶች)", callback_data="buy_advice_600"))
            
            cta_text = (
                "⚠️ <b>ነፃ የሙከራ ጊዜዎ አልቋል።</b>\n\n"
                "እስካሁን ጥሩ ቆይታ አድርገናል፤ ነገር ግን ትክክለኛው ለውጥ አሁን ነው የሚጀምረው። የጀመርነውን ጥልቅ ውይይት ለመቀጠል እና ወደ ተግባር የሚቀየሩ መፍትሄዎችን ለማግኘት እባክዎ አካውንትዎን ይሙሉ (Top up ያድርጉ)።\n\n"
                "ከታች ካሉት አማራጮች አንዱን ይምረጡ፦\n\n"
                "🔹 <b>Starter: 200 ብር</b> (120 መልዕክቶች) - ለአንድ ሳምንት ጥልቅ ውይይት የሚበቃ።\n"
                "🔹 <b>Pro: 400 ብር</b> (300 መልዕክቶች) - [ተመራጭ] በእጥፍ ዋጋ 2.5x መልዕክቶች።\n"
                "🔹 <b>Heavy: 700 ብር</b> (600 መልዕክቶች) - ለረጅም ጊዜ አገልግሎት ፈላጊዎች።\n\n"
                "ወዲያውኑ ክፍያ ፈፅመው የጀመርነውን ውይይት ለመቀጠል ከታች ያለውን የክፍያ አማራጭ ይጫኑ። 👇"
            )
            bot.send_message(chat_id, cta_text, parse_mode="HTML", reply_markup=markup)
            return

        try:
            bot.send_chat_action(chat_id, 'typing')
            bot.send_message(chat_id, "<i>(ውይይትዎን እያዘጋጀሁ ነው...)</i>", parse_mode="HTML")
        except Exception:
            pass
            
        user_text = message.text.strip()
        
        def process_advice_chat():
            try:
                # Load history from DB for persistent conversations
                try:
                    history_str = database.get_advice_history(uid)
                    history = json.loads(history_str) if history_str else []
                except Exception:
                    history = []
                
                # Get AI response
                ai_response = ai_engine.chat_with_mentor(user_text, history)
                
                if not ai_response:
                    bot.send_message(chat_id, "⚠️ ይቅርታ፣ ምላሽ ማግኘት አልተቻለም። እባክዎ እንደገና ይሞክሩ።")
                    return
                
                # Deduct quota (unless VIP or Admin)
                if not is_vip and not is_adm:
                    database.consume_advice_message(uid)
                    
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
            bot.send_message(chat_id, f"⚠️ የቴክኒክ ችግር: {e}")
        return

    # ── Book Input (title or photo) ──────────
    if state == "AWAITING_BOOK_INPUT":
        if message.photo:
            bot.send_message(chat_id, "📷 <b>ፎቶውን በማንበብ ላይ...</b>", parse_mode="HTML")
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_bytes = bot.download_file(file_info.file_path)
            result = ai_engine.identify_book_cover(file_bytes)
            if result.get("found"):
                title = result.get("title", "")
                author = result.get("author", "")
                full_title = f"{title} by {author}" if author else title
                set_state(uid, "AWAITING_BOOK_CONFIRM", book_title=full_title)
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("✅ አዎ", callback_data="confirm_book"),
                    InlineKeyboardButton("✏️ ልቀይር", callback_data="retry_book"),
                )
                bot.send_message(
                    chat_id,
                    f"📷 <b>መጽሐፉን አውቄዋለሁ!</b>\n\n"
                    f"📖 መጽሐፍ: <b>{title}</b>\n"
                    f"✍️ ደራሲ: <b>{author if author else 'ያልታወቀ'}</b>\n\n"
                    f"ያሰቡት ይህንን መጽሐፍ ነው?",
                    parse_mode="HTML", reply_markup=markup,
                )
            else:
                bot.send_message(chat_id, "⚠️ መጽሐፉን ለይቶ ማወቅ አልቻልኩም። እባክዎ ስሙን ይፃፉ:")
            return

        if message.text:
            try:
                book_title = message.text.strip()
                loading = bot.send_message(chat_id, "⏳ <b>መጽሐፉን በማረጋገጥ ላይ...</b>", parse_mode="HTML")
                
                result = ai_engine.verify_book_title(book_title)
                try:
                    safe_delete_message(chat_id, loading.message_id)
                except:
                    pass
                
                if result and result.get("found"):
                    title = str(result.get("title") or book_title)
                    author = str(result.get("author") or "")
                    
                    full_title = f"{title} by {author}" if author else title
                    set_state(uid, "AWAITING_BOOK_CONFIRM", book_title=full_title)
                    markup = InlineKeyboardMarkup()
                    markup.add(
                        InlineKeyboardButton("✅ አዎ", callback_data="confirm_book"),
                        InlineKeyboardButton("✏️ ልቀይር", callback_data="retry_book"),
                    )
                    bot.send_message(
                        chat_id,
                        f"📖 መጽሐፍ: <b>{html.escape(title)}</b>\n"
                        f"✍️ ደራሲ: <b>{html.escape(author) if author else 'ያልታወቀ'}</b>\n\n"
                        f"ያሰቡት ይህንን መጽሐፍ ነው?",
                        parse_mode="HTML", reply_markup=markup,
                    )
                else:
                    bot.send_message(chat_id, "⚠️ ይቅርታ፣ ይህን መጽሐፍ ማግኘት አልቻልኩም። እባክዎ የመጽሐፉን ትክክለኛ ስም ይፃፉ።")
                return
            except Exception as e:
                import traceback
                logging.error(f"CRITICAL ERROR in book verify: {e}\n{traceback.format_exc()}")
                bot.send_message(chat_id, "⚠️ ይቅርታ፣ ችግር ተፈጥሯል። እባክዎ እንደገና ይሞክሩ ወይም /start ይጫኑ።")
                return

    # ── Specific Change Input ────────────────
    if state == "AWAITING_SPECIFIC_CHANGE":
        if message.text:
            set_state(uid, "AWAITING_LANGUAGE", specific_change=message.text.strip())
            ask_language(chat_id)
        return

    # ── Receipt Photo or Text ────────────────────────
    if state in ["AWAITING_RECEIPT", "AWAITING_RECEIPT_TOPUP"]:
        bot.send_message(chat_id, "❌ የክፍያ ስርአታችን ተቀይሯል። እባክዎ እንደገና ይሞክሩ።", reply_markup=ReplyKeyboardRemove())
        clear_state(uid)
        send_welcome(chat_id, message.from_user.first_name)
        return

    # ── Inline-button states: nudge user ─────
    BUTTON_STATES = {"AWAITING_GENDER", "AWAITING_AGE", "AWAITING_LIVING", "AWAITING_LOCATION", "AWAITING_LANGUAGE", "AWAITING_CATEGORY", "AWAITING_SUBCATEGORY", "AWAITING_BOOK_PICK", "PREVIEW_SHOWN", "GENERATING_PREVIEW"}
    if state in BUTTON_STATES:
        bot.reply_to(message, "👆 እባክዎ ከላይ ካሉት አማራጮች ውስጥ ይምረጡ።")
        return

    # ── Catch-all: Forward to admin ──────────
    if not is_admin(message.from_user) and message.text:
        bot.reply_to(message, "✅ መልዕክትዎ ደርሶናል! በቅርቡ ምላሽ እንሰጥዎታለን።")
        admin_id = get_admin_id()
        if admin_id:
            bot.forward_message(admin_id, chat_id, message.message_id)
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🔍 Lookup", callback_data=f"adm_lookup_{uid}"),
                InlineKeyboardButton("🚫 Ban", callback_data=f"adm_ban_{uid}")
            )
            bot.send_message(admin_id, f"👤 {message.from_user.first_name} (@{message.from_user.username or 'N/A'})\n💬 ID: <code>{uid}</code>", parse_mode="HTML", reply_markup=markup)

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
    
    if purpose == "PROTOCOL":
        payment_amount = config.PRICE_SINGLE
        session = get_session(uid)
        d = session.get("data", {})
        database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK")
        bot.send_message(chat_id, f"✅ <b>ክፍያዎ በተሳካ ሁኔታ ተረጋግጧል!</b>\n\n📄 መመሪያዎን በማዘጋጀት ላይ ነን...", parse_mode="HTML")
        generate_and_deliver_pdf(chat_id, uid, d)
    elif purpose == "TOPUP":
        payment_amount = 100
        database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK")
        database.add_credit(uid, 5)
        bot.send_message(chat_id, "✅ <b>ክፍያዎ ተረጋግጧል!</b>\n5 ነጻ ምርመራዎች ወደ አካውንትዎ ገብተዋል።", parse_mode="HTML")
    elif purpose.startswith("ADVICE_"):
        msgs = int(purpose.split("_")[1])
        payment_amount = {120: 200, 300: 400, 600: 700}.get(msgs, 200)
        database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK")
        database.add_advice_messages(uid, msgs)
        bot.send_message(chat_id, f"✅ <b>ክፍያዎ ተረጋግጧል!</b>\n{msgs} መልዕክቶች ወደ አካውንትዎ ገብተዋል።\nውይይታችንን መቀጠል እንችላለን...", parse_mode="HTML")
    elif purpose == "TIP":
        database.record_payment(uid, order_id, 0, tx_ref, "CHAPA_WEBHOOK_TIP")
        bot.send_message(chat_id, "💖 <b>ስጦታዎ ደርሶናል!</b>\nከልብ እናመሰግናለን! ቡድናችንን በጣም አበረታተውታል።", parse_mode="HTML")
    elif purpose == "VIP":
        payment_amount = 500
        database.record_payment(uid, order_id, payment_amount, tx_ref, "CHAPA_WEBHOOK_VIP")
        database.set_vip(uid, days=30)
        bot.send_message(chat_id, "👑 <b>እንኳን ደስ አሎት!</b>\nየVIP አባልነትዎ ነቅቷል! አሁን ያለምንም ክፍያ ያልተገደበ መመሪያ ማዘጋጀት ይችላሉ!", parse_mode="HTML")

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/admin_dashboard':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                with open('admin_dashboard.html', 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self.wfile.write(b"Admin Dashboard not found.")
            return

        if self.path == '/admin/data':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            stats = database.get_analytics()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
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
