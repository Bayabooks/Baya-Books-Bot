import os
# SSL fix for local Windows development only (not needed on Render)
if os.environ.get("DEV_MODE"):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

import logging
import uuid
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

logging.basicConfig(level=logging.INFO)

if not config.BOT_TOKEN:
    print("ERROR: BOT_TOKEN missing in .env!"); exit(1)
if not config.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY missing in .env!"); exit(1)

bot = TeleBot(config.BOT_TOKEN)

# ══════════════════════════════════════════
#  CONVERSATION STATE MANAGER
# ══════════════════════════════════════════
user_sessions = {}  # {user_id: {state, data...}}

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "IDLE", "data": {}}
    return user_sessions[user_id]

def set_state(user_id, state, **kwargs):
    s = get_session(user_id)
    s["state"] = state
    s["data"].update(kwargs)

def clear_state(user_id):
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

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def is_admin(user):
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
                bot.send_message(referred_by, "🎉 <b>እንኳን ደስ አሎት!</b>\n\n5 ጓደኞችዎ ስለተቀላቀሉ 1 ነጻ የፕሮቶኮል ክሬዲት አግኝተዋል!\n\n/new ይጫኑ እና ፕሮቶኮልዎን ያዘጋጁ!", parse_mode="HTML")
            except Exception:
                pass

    # Channel check
    if not is_admin(user) and not check_channel_member(user.id):
        send_join_channel_msg(message.chat.id)
        return

    send_welcome(message.chat.id, user.first_name)

def send_welcome(chat_id, first_name):
    bottom_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    bottom_markup.add(
        KeyboardButton("➕ አዲስ ፕሮቶኮል"),
        KeyboardButton("📚 የኔ ፕሮቶኮሎች")
    )
    bottom_markup.add(
        KeyboardButton("🎁 ጓደኛ ይጋብዙ"),
        KeyboardButton("☕ ቡድኑን ያበረታቱ")
    )
    bottom_markup.add(KeyboardButton("💬 አስተያየት ይስጡን"))
    
    bot.send_message(
        chat_id, 
        f"👋 <b>ሰላም {html.escape(first_name)}!</b>\nእንኳን ወደ Baya Books በደህና መጡ።", 
        parse_mode="HTML", 
        reply_markup=bottom_markup
    )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📖 መጽሐፉን እኔው ራሴ እመርጣለሁ", callback_data="has_book"),
        InlineKeyboardButton("🧭 መጽሐፎቹን እናንተ አማርጡኝ", callback_data="choose_for_me"),
    )

    credits = database.get_credits(chat_id)
    credit_line = f"\n🎫 የእርስዎ ክሬዲት: <b>{credits} ፕሮቶኮል</b>\n" if credits > 0 else ""

    previews_left, _ = database.get_preview_quota(chat_id)
    preview_line = f"🎁 <b>{previews_left} ነጻ የሙከራ ምርመራዎች (Free Trials) አልዎት!</b>\n" if previews_left > 0 else "🚫 <b>የነጻ ምርመራ ኮታዎ አልቋል!</b>\n"

    bot.send_message(
        chat_id,
        f"🕊️ <b>እንኳን ወደ Baya Books በደህና መጡ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{preview_line}{credit_line}\n"
        f"የአለማችን ምርጥ መጽሐፍት ጥበብ ለእርስዎ\n"
        f"ህይወት ብቻ የተዘጋጀ ግላዊ የለውጥ መመሪያ\n"
        f"እናዘጋጃለን።\n\n"
        f"📖 መጽሐፍ ይምረጡ → ጥያቄዎችን ይመልሱ →\n"
        f"🔥 ህይወትዎን የሚቀይር መመሪያ ያግኙ!\n\n"
        f"👇 ከታች ያለውን በመጫን ይጀምሩ:",
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ መጽሐፍ ይምረጡ ወይም እኛ እንምረጥልዎ\n"
        "2️⃣ ጥቂት ጥያቄዎችን ይመልሱ\n"
        "3️⃣ ነጻ ማሳያ ያንብቡ\n"
        "4️⃣ ሙሉ PDF ይዘዙ (200 ብር)\n"
        "5️⃣ ግላዊ ፕሮቶኮልዎን ያውርዱ!\n\n"
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
        f"🎉 <b>ጓደኛዎን ይጋብዙ፣ ነጻ ፕሮቶኮል ያግኙ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 5 ጓደኞችዎን ይህን ሊንክ ተጠቅመው\n"
        f"ቦቱን ሲቀላቀሉ — እርስዎ ነጻ 1 ፕሮቶኮል ያገኛሉ!\n\n"
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

# ══════════════════════════════════════════
#  /admin COMMAND
# ══════════════════════════════════════════
@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "❌ የ Admin መብት የለዎትም!"); return
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Analytics", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
    )
    markup.add(
        InlineKeyboardButton("💳 ክሬዲት ጨምር", callback_data="admin_credit"),
        InlineKeyboardButton("📤 PDF ላክ", callback_data="admin_push_pdf"),
    )
    bot.send_message(
        message.chat.id,
        f"👑 <b>Baya Books Admin</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 {message.from_user.first_name}!\nምን ማድረግ ይፈልጋሉ?",
        reply_markup=markup, parse_mode="HTML",
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
        InlineKeyboardButton("📖 የጀመሩትን ፕሮቶኮል ይግዙ", callback_data="show_drafts")
    )
    
    bot.send_message(
        chat_id,
        f"🚫 <b>የነጻ ምርመራ ኮታዎ አልቋል! (5/5)</b>\n\n"
        f"⏳ በድጋሚ 5 ነጻ ምርመራ ለማግኘት: <b>{hours} ሰዓት ከ {minutes} ደቂቃ</b> ይጠብቁ።\n\n"
        f"<b>ወይም አሁኑኑ ይክፈቱ፡</b>\n"
        f"1️⃣ 100 ብር በመክፈል 5 ተጨማሪ ምርመራዎችን ያግኙ\n"
        f"2️⃣ <b>የጀመሩትን ሙሉ ፕሮቶኮል ይግዙ!</b>\n(ሙሉውን ሲገዙ ተጨማሪ 5 ምርመራ በቦነስ ያገኛሉ!)\n",
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

    # ── Channel Join Check ───────────────────
    if data == "check_joined":
        if check_channel_member(uid):
            bot.answer_callback_query(call.id, "✅ ተቀላቅለዋል!")
            bot.delete_message(chat_id, call.message.message_id)
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
        set_state(uid, "AWAITING_BOOK_INPUT")
        bot.send_message(
            chat_id,
            "📖 <b>ድንቅ!</b>\n\nየመጽሐፉን ስም ይፃፉ ወይም\nየመጽሐፉን ፎቶ ያንሱና ይላኩልን።",
            parse_mode="HTML",
        )
        return

    # ── Start: "Choose for me" ───────────────
    if data == "choose_for_me":
        if not enforce_preview_quota(uid, chat_id, call.id): return
        bot.answer_callback_query(call.id)
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
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ዛሬ በየትኛው የህይወት ክፍል ትልቅ ለውጥ ማምጣት ይፈልጋሉ?\n\n"
            "👇 ከታች ይምረጡ",
            parse_mode="HTML", reply_markup=markup,
        )
        return

    # ── Buy Previews Top-Up ──────────────────
    if data == "buy_previews":
        bot.answer_callback_query(call.id)
        show_payment_instructions(chat_id, 100)
        set_state(uid, "AWAITING_RECEIPT_TOPUP")
        return

    # ── Show Drafts ──────────────────────────
    if data == "show_drafts":
        bot.answer_callback_query(call.id)
        drafts = database.get_user_drafts(uid)
        if not drafts:
            bot.send_message(chat_id, "ምንም የተጀመረ ፕሮቶኮል የለዎትም።")
            return
        markup = InlineKeyboardMarkup(row_width=1)
        for d in drafts:
            markup.add(InlineKeyboardButton(f"📖 {d['book_title'][:30]}", callback_data=f"buy_draft_{d['id']}"))
        bot.send_message(chat_id, "💳 <b>ለመግዛት የሚፈልጉትን ፕሮቶኮል ይምረጡ:</b>", parse_mode="HTML", reply_markup=markup)
        return

    # ── Buy Draft ────────────────────────────
    if data.startswith("buy_draft_"):
        order_id = int(data.split("_")[2])
        bot.answer_callback_query(call.id)
        session = get_session(uid)
        session["data"] = {"order_id": order_id}
        
        if database.has_free_protocol(uid):
            bot.send_message(chat_id, "🎁 <b>እንኳን ደስ አለዎት!</b>\n\nይህ የመጀመሪያዎ ሙሉ ፕሮቶኮል ስለሆነ፣ በ <b>Baya Books</b> ስፖንሰርነት <b>በነጻ</b> ተዘጋጅቶልዎታል!", parse_mode="HTML")
            database.mark_free_protocol_used(uid)
            # Reconstruct data from order
            order = database.get_order(order_id)
            if order:
                session["data"] = {
                    "book_title": order["book_title"],
                    "gender": order["gender"],
                    "age_range": order["age_range"],
                    "location": order.get("location", ""),
                    "living_situation": order.get("living_situation", ""),
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
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
            bot.delete_message(chat_id, loading_msg.message_id)
            return

        # Pass subcategory name directly as the "category" topic to the AI, and request 5 books
        books = ai_engine.recommend_books(sub_name_en, count=5)
        bot.delete_message(chat_id, loading_msg.message_id)
        
        if isinstance(books, dict) and "error" in books:
            bot.send_message(chat_id, f"⚠️ የቴክኒክ ችግር: {html.escape(books['error'])}")
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
        set_state(uid, "AWAITING_GENDER")
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
            bot.send_message(chat_id, "🎁 <b>እንኳን ደስ አለዎት!</b>\n\nይህ የመጀመሪያዎ ሙሉ ፕሮቶኮል ስለሆነ፣ በ <b>Baya Books</b> ስፖንሰርነት <b>በነጻ</b> ተዘጋጅቶልዎታል!", parse_mode="HTML")
            database.mark_free_protocol_used(uid)
            session = get_session(uid)
            generate_and_deliver_pdf(chat_id, uid, session["data"])
            return
            
        show_pricing(chat_id, uid)
        return

    if data == "pay_single":
        bot.answer_callback_query(call.id)
        set_state(uid, "AWAITING_RECEIPT", payment_amount=config.PRICE_SINGLE, bundle_credits=0)
        show_payment_instructions(chat_id, config.PRICE_SINGLE)
        return

    if data == "pay_bundle":
        bot.answer_callback_query(call.id)
        set_state(uid, "AWAITING_RECEIPT", payment_amount=config.PRICE_BUNDLE, bundle_credits=2)
        show_payment_instructions(chat_id, config.PRICE_BUNDLE)
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

    # ── Admin: Stats ─────────────────────────
    if data == "admin_stats":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "📊 Loading...")
        stats = database.get_analytics()
        top_books = "\n".join([f"  {i+1}. 📕 {b[0]} ({b[1]}x)" for i, b in enumerate(stats["top_books"])]) or "  — ምንም"
        top_goals = "\n".join([f"  {i+1}. 🎯 {g[0]} ({g[1]}x)" for i, g in enumerate(stats["top_goals"])]) or "  — ምንም"
        total = stats["male_count"] + stats["female_count"]
        m_pct = f"{stats['male_count']/total*100:.0f}%" if total > 0 else "0%"
        f_pct = f"{stats['female_count']/total*100:.0f}%" if total > 0 else "0%"

        bot.send_message(chat_id,
            f"👑 <b>BAYA BOOKS ADMIN DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 ጠቅላላ ተጠቃሚዎች: <b>{stats['total_users']}</b>\n"
            f"🟢 ዛሬ የተጨመሩ: <b>{stats['new_today']}</b>\n"
            f"📄 የተዘጋጁ PDFs: <b>{stats['total_pdfs']}</b>\n\n"
            f"━━ 💰 ገቢ ━━━━━━━━━━━━━━━━━━━━\n"
            f"  📅 ዛሬ: <b>{stats['today_revenue']:,} ብር</b>\n"
            f"  📆 ሳምንታዊ: <b>{stats['weekly_revenue']:,} ብር</b>\n"
            f"  💵 ጠቅላላ: <b>{stats['total_revenue']:,} ብር</b>\n\n"
            f"━━ 🔥 ተወዳጅ 5 መጽሐፍት ━━━━━━━━━\n{top_books}\n\n"
            f"━━ 🎯 ተወዳጅ 5 ግቦች ━━━━━━━━━━━━\n{top_goals}\n\n"
            f"━━ 👥 ስብጥር ━━━━━━━━━━━━━━━━━━\n"
            f"  👨 ወንድ: {m_pct} | 👩 ሴት: {f_pct}\n\n"
            f"⏳ በመጠባበቅ: <b>{stats['pending_payments']}</b> ክፍያዎች",
            parse_mode="HTML",
        )
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

    # ── Admin: Approve/Reject Payment ────────
    if data.startswith("approve_"):
        if not is_admin(call.from_user): return
        payment_id = int(data.replace("approve_", ""))
        bot.answer_callback_query(call.id, "✅ Approved!")
        handle_payment_approved(payment_id)
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        bot.send_message(chat_id, f"✅ Payment #{payment_id} approved. PDF being generated...")
        return

    if data.startswith("reject_"):
        if not is_admin(call.from_user): return
        payment_id = int(data.replace("reject_", ""))
        database.reject_payment(payment_id)
        payment = database.get_payment(payment_id)
        if payment:
            bot.send_message(payment["user_id"], "❌ ክፍያዎ አልተረጋገጠም። እባክዎ እንደገና ይሞክሩ ወይም @Bayabooks ያናግሩን።")
        bot.answer_callback_query(call.id, "❌ Rejected")
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
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
        f"📖 <i>{book_title}</i> — ለእርስዎ ህይወት ብቻ\n"
        f"ልዩ አድርጌ ላዘጋጅልዎ ጥቂት ጥያቄዎችን ልጠይቅዎት።\n\n"
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
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

    bot.delete_message(chat_id, loading.message_id)

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
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 <b>{html.escape(data.get('book_title', ''))}</b> ፕሮቶኮል\n"
        f"👤 {html.escape(data.get('age_range', ''))} | {html.escape(data.get('gender', ''))}\n"
        f"🏠 {html.escape(data.get('living_situation', ''))} | 📍 {html.escape(data.get('location', ''))}\n"
        f"🎯 {html.escape(data.get('specific_change', ''))}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
    btn_text = f"🎁 የመጀመሪያዎን ሙሉ ፕሮቶኮል በነጻ ያግኙ ({strikethrough_300})" if database.has_free_protocol(uid) else f"💳 ሙሉ ፕሮቶኮል 200 ብር ({strikethrough_300})"
    
    bot.send_message(
        chat_id,
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⬆️ <b>ይህ የመነሻ ምርመራ ብቻ ነው!</b>\n\n"
        "ሙሉው የ90-ቀን ስትራቴጂ፣ ዕለታዊ ልምምድ፣\n"
        "የሳምንታዊ ግምገማ፣ እና ሙሉ ግላዊ ፕሮቶኮል\n"
        "ለማግኘት ከታች ይዘዙ 👇\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(btn_text, callback_data="buy_now")
        ),
    )


def show_pricing(chat_id, uid):
    credits = database.get_credits(uid)
    markup = InlineKeyboardMarkup(row_width=1)

    if credits > 0:
        markup.add(InlineKeyboardButton(f"🎫 ክሬዲት ተጠቀም ({credits} ቀሪ)", callback_data="use_credit"))

    strikethrough_300 = "3\u03360\u03360\u0336 ብ\u0336ር\u0336"
    markup.add(InlineKeyboardButton(f"1️⃣ 1 ፕሮቶኮል — {config.PRICE_SINGLE} ብር ({strikethrough_300})", callback_data="pay_single"))
    markup.add(InlineKeyboardButton(f"3️⃣ 3 ፕሮቶኮሎች — {config.PRICE_BUNDLE} ብር (17% ቅናሽ!)", callback_data="pay_bundle"))

    bot.send_message(
        chat_id,
        "💳 <b>የዋጋ አማራጮች</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "ከታች የሚስማማዎትን ይምረጡ 👇",
        parse_mode="HTML", reply_markup=markup,
    )


def show_payment_instructions(chat_id, amount):
    bot.send_message(
        chat_id,
        f"📱 <b>Telebirr ክፍያ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ከታች ወዳለው ቁጥር <b>{amount} ብር</b> ይላኩ፦\n\n"
        f"📱 Telebirr: <code>{config.TELEBIRR_PHONE}</code>\n"
        f"👤 ስም: <b>{config.TELEBIRR_NAME}</b>\n\n"
        f"✅ ከላኩ በኋላ የክፍያ ማረጋገጫ\n"
        f"<b>ስክሪን ሾት ፎቶ</b> አንስተው ወደዚህ ቻት ይላኩ።",
        parse_mode="HTML",
    )


def generate_and_deliver_pdf(chat_id, uid, data):
    """Generate full protocol and deliver it."""
    loading = bot.send_message(chat_id, "⏳ <b>ግላዊ ፕሮቶኮልዎ በመዘጋጀት ላይ...</b>\nይህ ከ30-60 ሰከንድ ሊወስድ ይችላል።", parse_mode="HTML")

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
        bot.delete_message(chat_id, loading.message_id)
        bot.send_message(chat_id, "⚠️ ችግር ተፈጥሯል። @Bayabooks ያናግሩን።")
        return

    # Generate Telegraph URL
    page_url = telegraph_generator.create_protocol_page(
        data.get("book_title", "Baya Books Protocol"), 
        full_text
    )

    bot.delete_message(chat_id, loading.message_id)

    if not page_url or page_url.startswith("ERROR:"):
        bot.send_message(chat_id, f"⚠️ የቴክኒክ ችግር ተፈጥሯል: {page_url}")
        return

    # Send Link
    msg_text = (
        f"🎉 <b>ግላዊ ፕሮቶኮልዎ ዝግጁ ነው!</b>\n\n"
        f"📖 <b>{html.escape(data.get('book_title', ''))}</b>\n"
        f"👤 {html.escape(data.get('age_range', ''))} | {html.escape(data.get('gender', ''))}\n"
        f"🏠 {html.escape(data.get('living_situation', ''))} | 📍 {html.escape(data.get('location', ''))}\n"
        f"🎯 {html.escape(data.get('specific_change', ''))}\n\n"
        f"👇 <b>ከታች ያለውን ሊንክ ተጭነው ያንብቡ:</b>\n"
        f"{page_url}"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📖 ፕሮቶኮልዎን ያንብቡ", url=page_url))
    
    try:
        sent_msg = bot.send_message(chat_id, msg_text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to send Telegraph link: {e}")
        sent_msg = bot.send_message(chat_id, f"ግላዊ ፕሮቶኮልዎ ዝግጁ ነው!\n{page_url}")

    # Save to database
    order_id = data.get("order_id")
    if order_id:
        # Save the URL instead of file_id
        database.update_order_full(order_id, full_text, page_url)



    # Show tip CTA instead of referral
    show_tip_cta(chat_id)
    
    clear_state(uid)


def show_tip_cta(chat_id):
    bot.send_message(
        chat_id,
        "☕ <b>ስራችንን ከወደዱት ሊደግፉን ይችላሉ!</b>\n\n"
        "ይህን ፕሮቶኮል ጠቃሚ ሆኖ ካገኙት፣ ከታች ባለው አካውንት የፈለጉትን ያህል ስጦታ በመላክ ቡድናችንን ማበረታታት ይችላሉ፦\n\n"
        f"📱 Telebirr: <code>{config.TELEBIRR_PHONE}</code>\n"
        f"👤 ስም: <b>{config.TELEBIRR_NAME}</b>\n\n"
        "🙏 ከልብ እናመሰግናለን!",
        parse_mode="HTML",
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

    # Add bundle credits if applicable
    session = get_session(uid)
    bundle_credits = session.get("data", {}).get("bundle_credits", 0)
    if bundle_credits > 0:
        database.add_credits(uid, bundle_credits)
        bot.send_message(uid, f"🎫 <b>{bundle_credits} ተጨማሪ PDF ክሬዲት ተጨምሯል!</b>\n📊 ቀሪ: {database.get_credits(uid)}", parse_mode="HTML")

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

    # ── Admin States ─────────────────────────
    if state == "ADMIN_BROADCAST" and is_admin(message.from_user):
        if message.text == "/cancel":
            clear_state(uid); bot.send_message(chat_id, "❌ ተሰርዟል።"); return
        users = database.get_all_user_ids()
        success, failed = 0, 0
        for u in users:
            try:
                bot.copy_message(u, chat_id, message.message_id); success += 1
            except Exception:
                failed += 1
        bot.send_message(chat_id, f"✅ Broadcast ተጠናቋል!\n✔️ {success} | ❌ {failed}")
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
    if message.text == "➕ አዲስ ፕሮቶኮል":
        send_welcome(chat_id, message.from_user.first_name)
        return

    if message.text == "📚 የኔ ፕሮቶኮሎች":
        orders = database.get_user_orders(uid)
        if not orders:
            bot.send_message(chat_id, "በአሁኑ ሰዓት የተዘጋጀ ፕሮቶኮል የለዎትም። አዲስ ለመጀመር '➕ አዲስ ፕሮቶኮል' ይጫኑ።")
        else:
            bot.send_message(chat_id, "📚 <b>የእርስዎ ፕሮቶኮሎች</b>\n━━━━━━━━━━━━━━━━━━━━", parse_mode="HTML")
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
            f"🎁 <b>ጓደኛዎን ይጋብዙ፣ ነጻ ፕሮቶኮል ያግኙ!</b>\n\n"
            f"5 ጓደኞችዎን ሲጋብዙ 1 ነጻ ፕሮቶኮል ያገኛሉ!\n\n"
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

    # ── Book Input (title or photo) ──────────
    if state == "AWAITING_BOOK_INPUT":
        if message.photo:
            bot.send_message(chat_id, "📷 <b>ፎቶውን በማንበብ ላይ...</b>", parse_mode="HTML")
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_bytes = bot.download_file(file_info.file_path)
            result = ai_engine.identify_book_cover(file_bytes)
            if result.get("found"):
                title = result["title"]
                author = result.get("author", "")
                set_state(uid, "AWAITING_BOOK_CONFIRM", book_title=title)
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("✅ አዎ", callback_data="confirm_book"),
                    InlineKeyboardButton("✏️ ልቀይር", callback_data="retry_book"),
                )
                bot.send_message(
                    chat_id,
                    f"📷 <b>መጽሐፉን አውቄዋለሁ!</b>\n\n"
                    f"📖 <b>{title}</b>{' — ' + author if author else ''}\n\n"
                    f"ይህ ትክክል ነው?",
                    parse_mode="HTML", reply_markup=markup,
                )
            else:
                bot.send_message(chat_id, "⚠️ መጽሐፉን ለይቶ ማወቅ አልቻልኩም። እባክዎ ስሙን ይፃፉ:")
            return

        if message.text:
            book_title = message.text.strip()
            loading = bot.send_message(chat_id, "⏳ <b>መጽሐፉን በማረጋገጥ ላይ...</b>", parse_mode="HTML")
            
            result = ai_engine.verify_book_title(book_title)
            bot.delete_message(chat_id, loading.message_id)
            
            if result and result.get("found"):
                title = result.get("title", book_title)
                author = result.get("author", "")
                
                set_state(uid, "AWAITING_BOOK_CONFIRM", book_title=title)
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("✅ አዎ", callback_data="confirm_book"),
                    InlineKeyboardButton("✏️ ልቀይር", callback_data="retry_book"),
                )
                bot.send_message(
                    chat_id,
                    f"📖 <b>{html.escape(title)}</b>{' (' + html.escape(author) + ')' if author else ''}\n\n"
                    f"ያሰቡት ይህንን መጽሐፍ ነው?",
                    parse_mode="HTML", reply_markup=markup,
                )
            else:
                bot.send_message(chat_id, "⚠️ እንዲህ ዓይነት መጽሐፍ ማግኘት አልቻልኩም። እባክዎ የመጽሐፉን ትክክለኛ ስም እና የጸሐፊውን ስም አብረው ይጻፉ።")
            return

    # ── Specific Change Input ────────────────
    if state == "AWAITING_SPECIFIC_CHANGE":
        if message.text:
            set_state(uid, "AWAITING_LANGUAGE", specific_change=message.text.strip())
            ask_language(chat_id)
        return

    # ── Receipt Photo ────────────────────────
    if state in ["AWAITING_RECEIPT", "AWAITING_RECEIPT_TOPUP"]:
        if message.photo:
            bot.send_message(chat_id, "⏳ <b>ክፍያዎን በማረጋገጥ ላይ...</b>", parse_mode="HTML")
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_bytes = bot.download_file(file_info.file_path)

            expected_amount = session["data"].get("payment_amount", config.PRICE_SINGLE)
            if state == "AWAITING_RECEIPT_TOPUP":
                expected_amount = 100

            result = ai_engine.verify_receipt(
                file_bytes, expected_amount,
                config.TELEBIRR_NAME, config.TELEBIRR_PHONE,
            )

            tx_id = result.get("transaction_id", uuid.uuid4().hex[:12])
            if tx_id and database.is_tx_ref_used(tx_id):
                bot.send_message(chat_id, "❌ ይህ ደረሰኝ ከዚህ ቀደም ጥቅም ላይ ውሏል!")
                return

            order_id = session["data"].get("order_id", -1) if state == "AWAITING_RECEIPT" else -1
            payment_id = database.record_payment(uid, order_id, expected_amount, tx_id or uuid.uuid4().hex, file_id)

            if result.get("auto_approved"):
                bot.send_message(chat_id, "✅ <b>ክፍያዎ ተረጋግጧል!</b>", parse_mode="HTML")
                if payment_id:
                    handle_payment_approved(payment_id)
            else:
                bot.send_message(chat_id, "⏳ <b>ክፍያዎ ለማረጋገጥ ወደ ቡድናችን ተልኳል።</b>\nበጥቂት ደቂቃዎች ውስጥ ይረጋገጣል!", parse_mode="HTML")
                # Forward to admin
                admin_id = get_admin_id()
                if admin_id:
                    bot.forward_message(admin_id, chat_id, message.message_id)
                    markup = InlineKeyboardMarkup()
                    markup.add(
                        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{payment_id}"),
                        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{payment_id}"),
                    )
                    confidence = result.get("confidence", "low")
                    amount_found = result.get("amount", "?")
                    bot.send_message(
                        admin_id,
                        f"💳 <b>Payment Verification</b>\n"
                        f"👤 User: {message.from_user.first_name} (ID: {uid})\n"
                        f"💰 Expected: {expected_amount} ብር\n"
                        f"📊 AI Found: {amount_found} ብር\n"
                        f"🔍 Confidence: {confidence}\n"
                        f"📝 TX ID: {tx_id}",
                        parse_mode="HTML", reply_markup=markup,
                    )
            return

        bot.send_message(chat_id, "📸 እባክዎ የክፍያ ስክሪን ሾት <b>ፎቶ</b> ይላኩ።", parse_mode="HTML")
        return

    # ── Catch-all: Forward to admin ──────────
    if not is_admin(message.from_user) and message.text:
        bot.reply_to(message, "✅ መልዕክትዎ ደርሶናል! በቅርቡ ምላሽ እንሰጥዎታለን።")
        admin_id = get_admin_id()
        if admin_id:
            bot.forward_message(admin_id, chat_id, message.message_id)
            bot.send_message(admin_id, f"👤 {message.from_user.first_name} (@{message.from_user.username or 'N/A'})\n💬 ID: <code>{uid}</code>", parse_mode="HTML")

# ══════════════════════════════════════════
#  DUMMY HTTP SERVER (Render)
# ══════════════════════════════════════════
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Baya Books Bot is running!")
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
