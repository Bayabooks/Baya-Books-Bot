import sys

with open('database.py', 'r', encoding='utf-8') as f:
    content = f.read()

vip_functions = """
def is_vip(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT vip_expiry FROM users WHERE id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        from datetime import datetime
        try:
            expiry = datetime.fromisoformat(row[0])
            return datetime.now() < expiry
        except:
            pass
    return False

def set_vip(user_id, days=30):
    from datetime import datetime, timedelta
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET vip_expiry = ? WHERE id = ?
    ''', (expiry, user_id))
    conn.commit()
    conn.close()
"""

if "def is_vip" not in content:
    content += "\n" + vip_functions
    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(content)
print("done")
