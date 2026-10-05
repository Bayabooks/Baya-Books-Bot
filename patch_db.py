import sys

with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

funcs = """
def get_bot_language(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT bot_language FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row["bot_language"]:
        return row["bot_language"]
    return "am"

def set_bot_language(user_id, lang_code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET bot_language = ? WHERE user_id = ?", (lang_code, user_id))
    conn.commit()
    conn.close()
"""

if "def get_bot_language" not in content:
    content += "\n" + funcs
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(content)
print("Updated database.py")
