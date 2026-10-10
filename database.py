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
        credits INTEGER DEFAULT 0,
        previews_left INTEGER DEFAULT 5,
        preview_timer_start TEXT,
        free_protocol_used INTEGER DEFAULT 0,
        vip_expiry TEXT,
        bot_language TEXT DEFAULT 'am',
        is_banned INTEGER DEFAULT 0,
        is_sub_admin INTEGER DEFAULT 0
    )''')
    # Migrations for existing databases
    for col_sql in [
        "ALTER TABLE users ADD COLUMN previews_left INTEGER DEFAULT 5",
        "ALTER TABLE users ADD COLUMN preview_timer_start TEXT",
        "ALTER TABLE users ADD COLUMN free_protocol_used INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN vip_expiry TEXT",
        "ALTER TABLE users ADD COLUMN bot_language TEXT DEFAULT 'am'",
        "ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN is_sub_admin INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN advice_messages_left INTEGER DEFAULT 5",
        "ALTER TABLE users ADD COLUMN advice_history TEXT DEFAULT '[]'",
        "ALTER TABLE users ADD COLUMN gender TEXT",
        "ALTER TABLE users ADD COLUMN age_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN bot_blocked INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN last_paywall_nudge TEXT",
    ]:
        try: c.execute(col_sql)
        except: pass

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
    c.execute('''INSERT INTO users (user_id, username, first_name, joined_date, referred_by, credits, advice_messages_left)
        VALUES (?, ?, ?, ?, ?, 0, 5)
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
    return dict(row) if row else None

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

def record_payment(user_id, order_id, amount, tx_ref, receipt_file_id, status='pending'):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO payments (user_id, order_id, amount, tx_ref, receipt_file_id, status, payment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, order_id, amount, tx_ref, receipt_file_id, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        payment_id = c.lastrowid
        conn.commit()
    except Exception:
        payment_id = None
    conn.close()
    return payment_id

def get_latest_pending_payment(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, amount, tx_ref, order_id 
        FROM payments 
        WHERE user_id = ? AND status = 'pending' 
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_abandoned_checkouts():
    """Get pending payments older than 1 hour that haven't been nudged yet."""
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime, timedelta
    threshold = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        SELECT payments.id, payments.user_id, payments.amount, payments.tx_ref, users.bot_language, users.first_name
        FROM payments
        JOIN users ON payments.user_id = users.user_id
        WHERE payments.status = 'pending' 
        AND payments.receipt_file_id = 'PENDING_CHECKOUT'
        AND payment_date <= ?
    ''', (threshold,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_checkout_nudged(payment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE payments SET status = 'abandoned_nudged' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

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

def approve_payment(tx_ref, order_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE payments 
                 SET status = 'approved', order_id = ?, receipt_file_id = 'CHAPA_WEBHOOK'
                 WHERE tx_ref = ?''', (order_id, tx_ref))
    updated = c.rowcount
    conn.commit()
    conn.close()
    return updated > 0

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
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # User counts
    c.execute("SELECT COUNT(*) FROM users WHERE bot_blocked = 0")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE bot_blocked = 1")
    blocked_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE joined_date LIKE ? AND bot_blocked = 0", (today + "%",))
    new_today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE joined_date >= ? AND bot_blocked = 0", (week_ago,))
    new_this_week = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE advice_history != '[]' AND advice_history IS NOT NULL")
    active_advice_users = c.fetchone()[0]

    # Revenue — count ALL payments that are approved OR have WEBHOOK in receipt_file_id or tx_ref
    c.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%'""")
    total_revenue = c.fetchone()[0]

    c.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%') 
        AND payment_date LIKE ?""", (today + "%",))
    today_revenue = c.fetchone()[0]

    c.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%') 
        AND payment_date >= ?""", (week_ago,))
    weekly_revenue = c.fetchone()[0]

    c.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%') 
        AND payment_date >= ?""", (month_ago,))
    monthly_revenue = c.fetchone()[0]

    c.execute("""SELECT COUNT(*) FROM payments 
        WHERE status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%'""")
    total_transactions = c.fetchone()[0]

    # Gender stats
    c.execute("SELECT COUNT(*) FROM users WHERE gender = 'male' AND bot_blocked = 0")
    male_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE gender = 'female' AND bot_blocked = 0")
    female_count = c.fetchone()[0]

    # Recent payments (include all successful)
    c.execute('''
        SELECT u.first_name, p.amount, p.payment_date, p.tx_ref
        FROM payments p 
        LEFT JOIN users u ON p.user_id = u.user_id 
        WHERE p.status = 'approved' OR p.receipt_file_id LIKE '%WEBHOOK%' OR p.tx_ref LIKE '%WEBHOOK%'
        ORDER BY p.id DESC LIMIT 15
    ''')
    recent_payments = []
    for r in c.fetchall():
        tx = r['tx_ref'] or ''
        ptype = 'Tip' if 'TIP' in tx else 'Advice' if 'ADVICE' in tx else 'Other'
        recent_payments.append({
            "name": r['first_name'] or 'Unknown', 
            "amount": r['amount'], 
            "date": r['payment_date'],
            "type": ptype
        })

    # Recent users (only active, not blocked)
    c.execute("SELECT first_name, username, joined_date FROM users WHERE bot_blocked = 0 ORDER BY user_id DESC LIMIT 15")
    recent_users = [{"name": r['first_name'], "username": r['username'] or '', "date": r['joined_date']} for r in c.fetchall()]

    conn.close()
    return {
        "total_users": total_users,
        "blocked_users": blocked_users,
        "new_today": new_today,
        "new_this_week": new_this_week,
        "active_advice_users": active_advice_users,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "weekly_revenue": weekly_revenue,
        "monthly_revenue": monthly_revenue,
        "total_transactions": total_transactions,
        "male_count": male_count,
        "female_count": female_count,
        "recent_payments": recent_payments,
        "recent_users": recent_users
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

# ─── Ban Functions ─────────────────────────

def ban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def mark_user_blocked(user_id, is_blocked=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET bot_blocked = ? WHERE user_id = ?", (is_blocked, user_id))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(is_banned, 0) as is_banned FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row['is_banned'])

# ─── Sub-Admin Functions ──────────────────

def add_sub_admin(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_sub_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def remove_sub_admin(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_sub_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_sub_admin(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(is_sub_admin, 0) as is_sub_admin FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row['is_sub_admin'])

def get_all_sub_admins():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name FROM users WHERE is_sub_admin = 1")
    rows = c.fetchall()
    conn.close()
    return rows

# ─── User Lookup & Search ─────────────────

def search_users(query):
    """Search users by ID, username, or first_name."""
    conn = get_connection()
    c = conn.cursor()
    try:
        uid = int(query)
        c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    except ValueError:
        c.execute("SELECT * FROM users WHERE username LIKE ? OR first_name LIKE ? LIMIT 10", (f"%{query}%", f"%{query}%"))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_details(user_id):
    """Get comprehensive user info for the psychology bot."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return None
    
    # Total paid (approved + webhook confirmed)
    c.execute("""SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE user_id = ? AND (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%')""", (user_id,))
    total_paid = c.fetchone()[0]

    # Payment count
    c.execute("""SELECT COUNT(*) FROM payments 
        WHERE user_id = ? AND (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%')""", (user_id,))
    payment_count = c.fetchone()[0]
    
    # Referral count
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    referral_count = c.fetchone()[0]

    # Recent payments
    c.execute("""SELECT amount, payment_date, tx_ref FROM payments 
        WHERE user_id = ? AND (status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%')
        ORDER BY id DESC LIMIT 5""", (user_id,))
    recent_payments = c.fetchall()
    
    conn.close()
    return {
        "user": dict(user),
        "total_paid": total_paid,
        "payment_count": payment_count,
        "referral_count": referral_count,
        "recent_payments": [dict(p) for p in recent_payments],
    }

def get_recent_orders(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT o.id, o.user_id, o.book_title, o.status, o.created_date, u.first_name, u.username
        FROM orders o LEFT JOIN users u ON o.user_id = u.user_id
        ORDER BY o.id DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_user_count():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_banned_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name FROM users WHERE is_banned = 1")
    rows = c.fetchall()
    conn.close()
    return rows

def get_advice_messages_left(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(advice_messages_left, 5) as advice_messages_left FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['advice_messages_left'] if row else 5

def consume_advice_message(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET advice_messages_left = advice_messages_left - 1 WHERE user_id = ? AND advice_messages_left > 0", (user_id,))
    conn.commit()
    conn.close()

def add_advice_messages(user_id, count):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET advice_messages_left = IFNULL(advice_messages_left, 5) + ? WHERE user_id = ?", (count, user_id))
    conn.commit()
    conn.close()

def get_advice_history(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT advice_history FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['advice_history'] if row and row['advice_history'] else '[]'

def save_advice_history(user_id, history_json):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET advice_history = ? WHERE user_id = ?", (history_json, user_id))
    conn.commit()
    conn.close()

def set_user_gender(user_id, gender):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
    conn.commit()
    conn.close()

def set_user_age_verified(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET age_verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_onboarding_status(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT age_verified, gender FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, None
    return bool(row['age_verified']), row['gender']

def reset_user_onboarding(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET age_verified = 0, gender = NULL, advice_history = '[]' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def factory_reset():
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users')
    c.execute('DELETE FROM orders')
    c.execute('DELETE FROM payments')
    conn.commit()
    conn.close()

def get_user_stage_stats():
    """Return counts of users at each stage of the funnel."""
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    paid_sql = """
        SELECT DISTINCT user_id FROM payments
        WHERE status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%'
    """

    # 1. VIP (Highest priority)
    c.execute("SELECT COUNT(*) FROM users WHERE vip_expiry IS NOT NULL AND vip_expiry > ? AND bot_blocked = 0", (now_str,))
    vip_users = c.fetchone()[0]

    # 2. Paid Users (Not VIP)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE user_id IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    paid_users = c.fetchone()[0]

    # 3. Stuck Onboarding (Not Paid, Not VIP, No Gender)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE (gender IS NULL OR gender = '') 
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    stuck_onboarding = c.fetchone()[0]

    # 4. Onboarded, No Chat (Not Paid, Not VIP, Has Gender, No History)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
        AND (advice_history IS NULL OR advice_history = '[]') 
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    onboarded_no_chat = c.fetchone()[0]

    # 5. In Trial (Not Paid, Not VIP, Has Gender, Has History, msgs > 0)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
        AND advice_history IS NOT NULL AND advice_history != '[]' 
        AND IFNULL(advice_messages_left, 5) > 0 
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    in_trial = c.fetchone()[0]

    # 6. Trial Ended (Not Paid, Not VIP, Has Gender, Has History, msgs <= 0)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
        AND advice_history IS NOT NULL AND advice_history != '[]' 
        AND IFNULL(advice_messages_left, 5) <= 0 
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    trial_ended = c.fetchone()[0]

    conn.close()
    return {
        "stuck_onboarding": stuck_onboarding,
        "onboarded_no_chat": onboarded_no_chat,
        "in_trial": in_trial,
        "trial_ended": trial_ended,
        "paid_users": paid_users,
        "vip_users": vip_users
    }

def get_stuck_users():
    """Get users who haven't completed onboarding (no age_verified or no gender)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, first_name, bot_language, joined_date, IFNULL(nudge_onboard_sent, 0) as nudge_count
        FROM users
        WHERE (IFNULL(age_verified, 0) = 0 OR gender IS NULL OR gender = '')
        AND bot_blocked = 0
        AND IFNULL(nudge_onboard_sent, 0) < 5
    """)
    rows = c.fetchall()
    conn.close()
    
    valid_users = []
    from datetime import datetime
    for r in rows:
        try:
            joined_dt = datetime.strptime(r['joined_date'], "%Y-%m-%d %H:%M:%S") if r['joined_date'] else datetime.now()
        except:
            joined_dt = datetime.now()
        
        days_since_joined = (datetime.now() - joined_dt).days
        # For nudge 0, days >= 0 (immediate)
        # For nudge 1, days >= 1 (after 24h)
        # For nudge 2, days >= 2 (after 48h)
        if days_since_joined >= r['nudge_count']:
            valid_users.append(dict(r))
            
    return valid_users

def get_silent_users():
    """Get users who completed onboarding but never sent a message."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, first_name, bot_language
        FROM users
        WHERE IFNULL(age_verified, 0) = 1 
        AND gender IS NOT NULL AND gender != '' 
        AND (advice_history IS NULL OR advice_history = '[]') 
        AND bot_blocked = 0
        AND IFNULL(nudge_silent_sent, 0) = 0
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_trial_ended_users():
    """Get users who exhausted their trial but haven't paid."""
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        SELECT user_id, first_name, bot_language
        FROM users
        WHERE advice_history IS NOT NULL AND advice_history != '[]'
        AND IFNULL(advice_messages_left, 5) <= 0
        AND (vip_expiry IS NULL OR vip_expiry < ?)
        AND bot_blocked = 0
        AND IFNULL(nudge_revive_sent, 0) = 0
        AND user_id NOT IN (
            SELECT DISTINCT user_id FROM payments
            WHERE status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%'
        )
    """, (now_str,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

import json
import re

def append_bot_message_to_history(user_id, text):
    """Appends a message sent by the bot to the user's AI history so the AI has context."""
    try:
        history_str = get_advice_history(user_id)
        history = json.loads(history_str) if history_str else []
    except:
        history = []
    
    # Strip HTML tags so the AI sees clean text
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Avoid appending duplicate consecutive bot messages
    if history and history[-1].get("role") == "model" and history[-1].get("parts") == [clean_text]:
        return
        
    history.append({"role": "model", "parts": [clean_text]})
    
    # Keep only the last 20 messages to prevent blob from growing too large
    if len(history) > 20:
        history = history[-20:]
        
    save_advice_history(user_id, json.dumps(history, ensure_ascii=False))

def get_setting(key, default=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row['setting_value'] if row else default

def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def mark_nudge_sent(user_id, nudge_type):
    """Marks a user as having received a specific nudge (nudge_onboard_sent, nudge_silent_sent, nudge_revive_sent)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE users SET {nudge_type} = IFNULL({nudge_type}, 0) + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def auto_migrate_nudge_columns():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT
    )''')
    for col in ["nudge_onboard_sent", "nudge_silent_sent", "nudge_revive_sent"]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT 0")
        except: pass
    conn.commit()
    conn.close()

auto_migrate_nudge_columns()


def get_paywall_users():
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime, timedelta
    threshold = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        SELECT users.user_id, users.first_name, users.bot_language
        FROM users
        JOIN payments ON users.user_id = payments.user_id
        WHERE users.advice_messages_left <= 0 
        AND payments.status = 'pending'
        AND users.age_verified = 1
        AND users.bot_blocked = 0
        AND (users.vip_expiry IS NULL OR users.vip_expiry < ?)
        AND (users.last_paywall_nudge IS NULL OR users.last_paywall_nudge <= ?)
        GROUP BY users.user_id
    ''', (now, threshold))
    rows = c.fetchall()
    conn.close()
    return rows

def mark_paywall_nudged(user_id):
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    c.execute('UPDATE users SET last_paywall_nudge = ? WHERE user_id = ?', 
             (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()
    conn.close()
