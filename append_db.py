import sqlite3

def append_db():
    with open('database.py', 'a', encoding='utf-8') as f:
        f.write("""
def get_preview_quota(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 3) as previews_left, preview_timer_start FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 3, None

    previews_left = row['previews_left']
    timer_start = row['preview_timer_start']

    if previews_left <= 0 and timer_start:
        from datetime import datetime, timedelta
        try:
            start_dt = datetime.fromisoformat(timer_start)
            if datetime.now() >= start_dt + timedelta(hours=24):
                c.execute("UPDATE users SET previews_left = 3, preview_timer_start = NULL WHERE user_id = ?", (user_id,))
                conn.commit()
                previews_left = 3
                timer_start = None
        except ValueError:
            pass

    conn.close()
    return previews_left, timer_start

def consume_preview(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 3) as previews_left FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row['previews_left'] > 0:
        new_left = row['previews_left'] - 1
        if new_left == 0:
            from datetime import datetime
            c.execute("UPDATE users SET previews_left = 0, preview_timer_start = ? WHERE user_id = ?", (datetime.now().isoformat(), user_id))
        else:
            c.execute("UPDATE users SET previews_left = ? WHERE user_id = ?", (new_left, user_id))
        conn.commit()
    conn.close()

def reset_previews(user_id, amount=3):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 3) as previews_left FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        new_amount = row['previews_left'] + amount
        c.execute("UPDATE users SET previews_left = ?, preview_timer_start = NULL WHERE user_id = ?", (new_amount, user_id))
        conn.commit()
    conn.close()

def get_user_drafts(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id = ? AND status IN ('draft', 'preview') ORDER BY id DESC LIMIT 5", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
""")

if __name__ == '__main__':
    append_db()
