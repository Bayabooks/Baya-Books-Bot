import sys

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

handler_code = """
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    try:
        import json
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        
        if action == 'request_book':
            title = data.get('title')
            author = data.get('author')
            # Trigger standard generation pipeline directly
            set_state(uid, "AWAITING_LANGUAGE", specific_change="")
            session = get_session(uid)
            session["data"] = {"book_title": f"{title} by {author}"}
            ask_language(chat_id)
            
        elif action == 'buy_vip':
            checkout_url, tx_ref, err = chapa.generate_chapa_link(500, uid, "VIP")
            if checkout_url:
                from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("💳 Pay VIP / ክፈሉ", web_app=WebAppInfo(url=checkout_url)))
                bot.send_message(chat_id, "👑 <b>VIP Subscription (500 ETB)</b>\\nእባክዎ ከታች ያለውን ቁልፍ ተጭነው ይክፈሉ።", parse_mode="HTML", reply_markup=markup)
            else:
                bot.send_message(chat_id, "❌ Error generating VIP link.")
    except Exception as e:
        logging.error(f"WebApp Data Error: {e}")
"""

if "@bot.message_handler(content_types=['web_app_data'])" not in content:
    # Insert it right before @bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
    content = content.replace(
        "@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])",
        handler_code + "\n@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])"
    )
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
print("done")
