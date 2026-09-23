import sqlite3
import os
from datetime import datetime, timedelta
import config

def get_connection():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def setup_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_date TEXT,
        referred_by INTEGER,
        credits INTEGER DEFAULT 0
    )''')
    try:
        c.execute("ALTER TABLE users ADD COLUMN previews_left INTEGER DEFAULT 5")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN preview_timer_start TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN free_protocol_used INTEGER DEFAULT 0")
    except:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_title TEXT,
        gender TEXT,
        age_range TEXT,
        goal TEXT,
        language TEXT,
        free_preview TEXT,
        full_content TEXT,
        pdf_file_id TEXT,
        status TEXT DEFAULT 'draft',
        created_date TEXT,
        delivered_date TEXT
    )''')
    try: c.execute("ALTER TABLE orders ADD COLUMN location TEXT")
    except: pass
    try: c.execute("ALTER TABLE orders ADD COLUMN living_situation TEXT")
    except: pass
    try: c.execute("ALTER TABLE orders ADD COLUMN employment TEXT")
    except: pass
    try: c.execute("ALTER TABLE orders ADD COLUMN specific_change TEXT")
    except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id INTEGER,
        amount INTEGER,
        tx_ref TEXT UNIQUE,
        receipt_file_id TEXT,
        status TEXT DEFAULT 'pending',
        payment_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        credit_given INTEGER DEFAULT 0,
        created_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_content TEXT,
        date_added TEXT
    )''')

    conn.commit()
    conn.close()

# ─── User Functions ────────────────────────

def add_user(user_id, username, first_name, referred_by=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO users (user_id, username, first_name, joined_date, referred_by, credits)
        VALUES (?, ?, ?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name
    ''', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), referred_by))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def is_new_user(user_id):
    return get_user(user_id) is None

def get_all_user_ids():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r['user_id'] for r in rows]

def get_credits(user_id):
    user = get_user(user_id)
    return user['credits'] if user else 0

def add_credits(user_id, amount):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def use_credit(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits - 1 WHERE user_id = ? AND credits > 0", (user_id,))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

# ─── Referral Functions ────────────────────

def record_referral(referrer_id, referred_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT OR IGNORE INTO referrals (referrer_id, referred_id, credit_given, created_date)
            VALUES (?, ?, 0, ?)
        ''', (referrer_id, referred_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception:
        pass
    conn.close()

def get_referrer(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT referrer_id FROM referrals WHERE referred_id = ? AND credit_given = 0", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['referrer_id'] if row else None

def mark_referral_credited(referred_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE referrals SET credit_given = 1 WHERE referred_id = ?", (referred_id,))
    conn.commit()
    conn.close()

def mark_n_referrals_credited(referrer_id, n=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE referrals 
        SET credit_given = 1 
        WHERE id IN (
            SELECT id FROM referrals 
            WHERE referrer_id = ? AND credit_given = 0 
            LIMIT ?
        )
    ''', (referrer_id, n))
    conn.commit()
    conn.close()

def get_referral_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND credit_given = 1", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_uncredited_referral_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND credit_given = 0", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def has_free_protocol(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(free_protocol_used, 0) as free_protocol_used FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return True # Default to true if user not found, though should exist
    return row['free_protocol_used'] == 0

def mark_free_protocol_used(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET free_protocol_used = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ─── Order Functions ───────────────────────

def create_order(user_id, book_title, gender, age_range, goal, location, living_situation, employment, specific_change, language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO orders (user_id, book_title, gender, age_range, goal, location, living_situation, employment, specific_change, language, status, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?)
    ''', (user_id, book_title, gender, age_range, goal, location, living_situation, employment, specific_change, language, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_preview(order_id, preview_text):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET free_preview = ?, status = 'preview_sent' WHERE id = ?", (preview_text, order_id))
    conn.commit()
    conn.close()

def update_order_full(order_id, full_content, pdf_file_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE orders SET full_content = ?, pdf_file_id = ?, status = 'delivered',
        delivered_date = ? WHERE id = ?
    ''', (full_content, pdf_file_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id))
    conn.commit()
    conn.close()

def update_order_status(order_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_order(order_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_orders(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id = ? AND status = 'delivered' ORDER BY delivered_date DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ─── Payment Functions ─────────────────────

def record_payment(user_id, order_id, amount, tx_ref, receipt_file_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO payments (user_id, order_id, amount, tx_ref, receipt_file_id, status, payment_date)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        ''', (user_id, order_id, amount, tx_ref, receipt_file_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        payment_id = c.lastrowid
        conn.commit()
    except Exception:
        payment_id = None
    conn.close()
    return payment_id

def approve_payment(payment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE payments SET status = 'approved' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

def reject_payment(payment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE payments SET status = 'rejected' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

def get_payment(payment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = c.fetchone()
    conn.close()
    return row

def is_tx_ref_used(tx_ref):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM payments WHERE tx_ref = ? AND status = 'approved'", (tx_ref,))
    row = c.fetchone()
    conn.close()
    return row is not None

# ─── Analytics Functions ───────────────────

def get_analytics():
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE joined_date LIKE ?", (today + "%",))
    new_today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered'")
    total_pdfs = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved'")
    total_revenue = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved' AND payment_date LIKE ?", (today + "%",))
    today_revenue = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved' AND payment_date >= ?", (week_ago,))
    weekly_revenue = c.fetchone()[0]

    c.execute('''SELECT book_title, COUNT(*) as cnt FROM orders WHERE status = 'delivered'
        GROUP BY book_title ORDER BY cnt DESC LIMIT 5''')
    top_books = [(r['book_title'], r['cnt']) for r in c.fetchall()]

    c.execute('''SELECT goal, COUNT(*) as cnt FROM orders WHERE status = 'delivered'
        GROUP BY goal ORDER BY cnt DESC LIMIT 5''')
    top_goals = [(r['goal'], r['cnt']) for r in c.fetchall()]

    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered' AND gender = 'male'")
    male_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'delivered' AND gender = 'female'")
    female_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM payments WHERE status = 'pending'")
    pending_payments = c.fetchone()[0]

    conn.close()
    return {
        "total_users": total_users,
        "new_today": new_today,
        "total_pdfs": total_pdfs,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "weekly_revenue": weekly_revenue,
        "top_books": top_books,
        "top_goals": top_goals,
        "male_count": male_count,
        "female_count": female_count,
        "pending_payments": pending_payments,
    }

# Run setup
setup_database()


def get_preview_quota(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 5) as previews_left, preview_timer_start FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 5, None

    previews_left = row['previews_left']
    timer_start = row['preview_timer_start']

    if previews_left <= 0 and timer_start:
        from datetime import datetime, timedelta
        try:
            start_dt = datetime.fromisoformat(timer_start)
            if datetime.now() >= start_dt + timedelta(hours=24):
                c.execute("UPDATE users SET previews_left = 5, preview_timer_start = NULL WHERE user_id = ?", (user_id,))
                conn.commit()
                previews_left = 5
                timer_start = None
        except ValueError:
            pass

    conn.close()
    return previews_left, timer_start

def consume_preview(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 5) as previews_left FROM users WHERE user_id = ?", (user_id,))
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

def reset_previews(user_id, amount=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(previews_left, 5) as previews_left FROM users WHERE user_id = ?", (user_id,))
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


def is_vip(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT vip_expiry FROM users WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
    except Exception as e:
        row = None
    finally:
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
        UPDATE users SET vip_expiry = ? WHERE user_id = ?
    ''', (expiry, user_id))
    conn.commit()
    conn.close()


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
