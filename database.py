import sqlite3
import os
import logging
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
        "ALTER TABLE users ADD COLUMN last_nudge_at TEXT",
        "ALTER TABLE users ADD COLUMN last_mentor_message TEXT",
        "ALTER TABLE users ADD COLUMN commission_balance REAL DEFAULT 0.0",
        "ALTER TABLE users ADD COLUMN total_earned_commission REAL DEFAULT 0.0",
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
        has_chatted INTEGER DEFAULT 0,
        chatted_date TEXT,
        created_date TEXT
    )''')
    try: c.execute("ALTER TABLE referrals ADD COLUMN has_chatted INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE referrals ADD COLUMN chatted_date TEXT")
    except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS referral_commissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        buyer_id INTEGER,
        tx_ref TEXT UNIQUE,
        package_name TEXT,
        purchase_amount REAL,
        commission_amount REAL,
        created_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS referral_payouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        payment_method TEXT,
        account_holder TEXT,
        account_number TEXT,
        phone_number TEXT,
        status TEXT DEFAULT 'pending',
        admin_notes TEXT DEFAULT '',
        created_at TEXT,
        processed_at TEXT DEFAULT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_content TEXT,
        date_added TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_gift_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        cycle_date TEXT,
        chosen_word TEXT,
        is_correct INTEGER DEFAULT 0,
        attempt_time TEXT,
        UNIQUE(user_id, cycle_date)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_gift_winners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        cycle_date TEXT,
        rank INTEGER,
        book_chosen TEXT,
        awarded_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_books (
        user_id INTEGER,
        book_key TEXT,
        purchased_at TEXT,
        expires_at TEXT DEFAULT NULL,
        PRIMARY KEY (user_id, book_key)
    )''')
    try:
        c.execute("ALTER TABLE user_books ADD COLUMN expires_at TEXT DEFAULT NULL")
    except:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id TEXT UNIQUE,
        access_token TEXT UNIQUE,
        name TEXT,
        pen_name TEXT,
        email TEXT,
        phone TEXT,
        telegram_id INTEGER,
        telegram_username TEXT,
        royalty_percentage REAL DEFAULT 70.0,
        bank_name TEXT DEFAULT 'CBE',
        bank_account TEXT DEFAULT '',
        account_holder TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS author_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_key TEXT UNIQUE,
        author_id TEXT,
        title TEXT,
        subtitle TEXT,
        category TEXT DEFAULT 'psychology',
        pages INTEGER DEFAULT 120,
        price_buy REAL DEFAULT 399.0,
        allow_rent INTEGER DEFAULT 1,
        price_rent_5d REAL DEFAULT 99.0,
        price_rent_10d REAL DEFAULT 149.0,
        cover_url TEXT DEFAULT '',
        description TEXT DEFAULT '',
        sample_chapter_title TEXT DEFAULT 'መግቢያ (Introduction)',
        sample_chapter_text TEXT DEFAULT '',
        full_manuscript_url TEXT DEFAULT '',
        status TEXT DEFAULT 'draft',
        admin_feedback TEXT DEFAULT '',
        created_at TEXT,
        updated_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS author_payouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id TEXT,
        amount REAL,
        bank_name TEXT,
        bank_account TEXT,
        account_holder TEXT,
        status TEXT DEFAULT 'pending',
        tx_ref TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        requested_at TEXT,
        processed_at TEXT
    )''')

    try:
        c.execute("CREATE TABLE IF NOT EXISTS settings (setting_key TEXT PRIMARY KEY, setting_value TEXT)")
        c.execute("SELECT setting_value FROM settings WHERE setting_key = 'giveaway_reset_request'")
        row = c.fetchone()
        if not row or row[0] != "done_v2":
            c.execute("DELETE FROM daily_gift_attempts")
            c.execute("DELETE FROM daily_gift_winners")
            c.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES ('giveaway_reset_request', 'done_v2')")
            c.execute("DELETE FROM settings WHERE setting_key IN ('daily_gift_secret_word', 'daily_gift_secret_word_date')")
    except Exception as e:
        logging.warning(f"Giveaway reset notice: {e}")

    conn.commit()
    conn.close()

def unlock_book(user_id, book_key, days=None):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    expires_str = None
    if days is not None:
        days_int = int(days)
        if days_int < 0:
            expires_str = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            base_dt = now_dt
            if days_int == 5:
                try:
                    c.execute("SELECT expires_at FROM user_books WHERE user_id = ? AND book_key = ?", (user_id, book_key))
                    row = c.fetchone()
                    if row and row['expires_at']:
                        prev_dt = datetime.strptime(row['expires_at'][:19], "%Y-%m-%d %H:%M:%S")
                        if prev_dt > now_dt:
                            base_dt = prev_dt
                except:
                    pass
            expires_str = (base_dt + timedelta(days=days_int)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT OR REPLACE INTO user_books (user_id, book_key, purchased_at, expires_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, book_key, now_str, expires_str))
    conn.commit()
    conn.close()

def remove_user_book(user_id, book_key):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_books WHERE user_id = ? AND book_key = ?", (user_id, book_key))
    conn.commit()
    conn.close()

def clear_expired_rental(user_id, book_key):
    """Safely removes a book rental ONLY if expires_at is set and in the past. Never deletes permanent purchases."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "DELETE FROM user_books WHERE user_id = ? AND book_key = ? AND expires_at IS NOT NULL AND (expires_at <= ? OR expires_at <= datetime('now'))",
        (user_id, book_key, now_str)
    )
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_user_books_state(user_id):
    if not user_id:
        return [], {}, []
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return [], {}, []
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT book_key, expires_at FROM user_books WHERE user_id = ?", (user_id,))
    except:
        try:
            c.execute("ALTER TABLE user_books ADD COLUMN expires_at TEXT DEFAULT NULL")
            conn.commit()
        except:
            pass
        c.execute("SELECT book_key, NULL as expires_at FROM user_books WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()

    now_dt = datetime.now()
    books = []
    rentals = {}
    expired = []
    for r in rows:
        bkey = r['book_key']
        exp = r['expires_at']
        if exp:
            try:
                exp_dt = datetime.strptime(exp[:19].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                if exp_dt <= now_dt:
                    expired.append(bkey)
                    continue
                rem_days = max(1, (exp_dt - now_dt).days + (1 if (exp_dt - now_dt).seconds > 0 else 0))
                books.append(bkey)
                rentals[bkey] = rem_days
            except:
                books.append(bkey)
        else:
            books.append(bkey)
    return books, rentals, expired

def get_user_books_with_meta(user_id):
    books, rentals, _ = get_user_books_state(user_id)
    return books, rentals

def get_user_books(user_id):
    return get_user_books_state(user_id)[0]

def get_all_rentals_management_data():
    """
    Returns structured data for the Rented Books Management Dashboard:
    - Summary metrics (total rentals, active rentals, expiring soon <= 48h, expired, lifetime purchases)
    - Full list of all records with user details, book info, time remaining, and status.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT book_key, expires_at FROM user_books LIMIT 1")
    except Exception:
        try:
            c.execute("ALTER TABLE user_books ADD COLUMN expires_at TEXT DEFAULT NULL")
            conn.commit()
        except Exception:
            pass

    query = """
        SELECT 
            ub.user_id,
            ub.book_key,
            ub.purchased_at,
            ub.expires_at,
            u.username,
            u.first_name,
            u.bot_blocked
        FROM user_books ub
        LEFT JOIN users u ON ub.user_id = u.user_id
        ORDER BY 
            CASE 
                WHEN ub.expires_at IS NOT NULL AND ub.expires_at > datetime('now') THEN 1
                WHEN ub.expires_at IS NULL THEN 2
                ELSE 3
            END,
            ub.expires_at DESC,
            ub.purchased_at DESC
    """
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    now_dt = datetime.now()
    rentals_list = []
    
    active_count = 0
    expiring_soon_count = 0
    expired_count = 0
    lifetime_count = 0

    BOOK_NAMES = {
        "narcissist": "የናርስሲስቶች ወጥመድ",
        "boundaries": "ድንበርህን አብጅ",
        "buyback": "ጊዜህን አስመልስ (Buy Back Your Time)",
        "meaning": "የህይወት ትርጉም"
    }

    for r in rows:
        uid = r['user_id']
        bkey = r['book_key']
        p_at = r['purchased_at'] or ''
        e_at = r['expires_at']
        uname = r['username'] or ''
        fname = r['first_name'] or 'User'
        blocked = bool(r['bot_blocked'])
        
        btitle = BOOK_NAMES.get(bkey, bkey)

        is_rental = bool(e_at)
        status = 'lifetime'
        days_left = None
        hours_left = None
        status_label = 'Permanent (Lifetime)'
        
        if is_rental:
            try:
                exp_dt = datetime.strptime(e_at[:19], "%Y-%m-%d %H:%M:%S")
                diff = exp_dt - now_dt
                total_seconds = int(diff.total_seconds())
                
                if total_seconds > 0:
                    hours_left = total_seconds // 3600
                    days_left = max(1, diff.days + (1 if diff.seconds > 0 else 0))
                    if total_seconds <= 48 * 3600:
                        status = 'expiring_soon'
                        expiring_soon_count += 1
                        status_label = f"Expiring Soon ({hours_left}h left)"
                    else:
                        status = 'active'
                        active_count += 1
                        status_label = f"Active ({days_left}d left)"
                else:
                    status = 'expired'
                    expired_count += 1
                    ago_days = abs(diff.days)
                    status_label = f"Expired ({ago_days}d ago)"
            except Exception:
                status = 'active'
                active_count += 1
                status_label = 'Active Rental'
        else:
            lifetime_count += 1

        rentals_list.append({
            "user_id": uid,
            "username": uname,
            "first_name": fname,
            "bot_blocked": blocked,
            "book_key": bkey,
            "book_title": btitle,
            "purchased_at": p_at,
            "expires_at": e_at,
            "is_rental": is_rental,
            "status": status,
            "status_label": status_label,
            "days_left": days_left,
            "hours_left": hours_left
        })

    return {
        "summary": {
            "total_records": len(rentals_list),
            "total_rentals": active_count + expiring_soon_count + expired_count,
            "active_rentals": active_count,
            "expiring_soon_rentals": expiring_soon_count,
            "expired_rentals": expired_count,
            "lifetime_purchases": lifetime_count
        },
        "rentals": rentals_list
    }

def extend_rental_days(user_id, book_key, additional_days=5):
    """Extends a user's book rental by additional_days. Returns the new expiration string."""
    try:
        user_id = int(user_id)
        additional_days = int(additional_days)
    except (ValueError, TypeError):
        return None
        
    now_dt = datetime.now()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT expires_at FROM user_books WHERE user_id = ? AND book_key = ?", (user_id, book_key))
    row = c.fetchone()
    
    base_dt = now_dt
    if row and row['expires_at']:
        try:
            curr_exp = datetime.strptime(row['expires_at'][:19], "%Y-%m-%d %H:%M:%S")
            if curr_exp > now_dt:
                base_dt = curr_exp
        except Exception:
            pass
            
    new_exp_dt = base_dt + timedelta(days=additional_days)
    new_exp_str = new_exp_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('''INSERT OR REPLACE INTO user_books (user_id, book_key, purchased_at, expires_at)
        VALUES (?, ?, COALESCE((SELECT purchased_at FROM user_books WHERE user_id = ? AND book_key = ?), ?), ?)
    ''', (user_id, book_key, user_id, book_key, now_str, new_exp_str))
    conn.commit()
    conn.close()
    return new_exp_str

def convert_book_to_lifetime(user_id, book_key):
    """Converts a rental into permanent lifetime ownership."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_books (user_id, book_key, purchased_at, expires_at)
        VALUES (?, ?, COALESCE((SELECT purchased_at FROM user_books WHERE user_id = ? AND book_key = ?), ?), NULL)
    ''', (user_id, book_key, user_id, book_key, now_str))
    conn.commit()
    conn.close()
    return True

def expire_book_rental_now(user_id, book_key):
    """Immediately expires a rental."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return False
    exp_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE user_books SET expires_at = ? WHERE user_id = ? AND book_key = ?", (exp_str, user_id, book_key))
    conn.commit()
    conn.close()
    return True

def get_all_users_admin_data(limit=150, offset=0, query='', filter_status='all'):
    """Fetch users for the admin user directory with aggregated stats."""
    conn = get_connection()
    c = conn.cursor()
    
    where_clauses = []
    params = []
    
    if query:
        q = f"%{query.strip().lower()}%"
        where_clauses.append("(LOWER(u.first_name) LIKE ? OR LOWER(u.username) LIKE ? OR CAST(u.user_id AS TEXT) LIKE ?)")
        params.extend([q, q, q])
        
    if filter_status == 'active':
        where_clauses.append("u.bot_blocked = 0")
    elif filter_status == 'blocked':
        where_clauses.append("u.bot_blocked = 1")
    elif filter_status == 'vip':
        where_clauses.append("u.vip_expiry IS NOT NULL AND u.vip_expiry > datetime('now')")
    elif filter_status == 'exhausted':
        where_clauses.append("u.advice_messages_left <= 0 AND (u.vip_expiry IS NULL OR u.vip_expiry <= datetime('now'))")
    elif filter_status == 'male':
        where_clauses.append("u.gender = 'male'")
    elif filter_status == 'female':
        where_clauses.append("u.gender = 'female'")

    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    c.execute(f"SELECT COUNT(*) FROM users u {where_str}", params)
    total_count = c.fetchone()[0]
    
    sql = f"""
        SELECT 
            u.user_id,
            u.username,
            u.first_name,
            u.joined_date,
            u.credits,
            u.advice_messages_left,
            u.vip_expiry,
            u.bot_language,
            u.gender,
            u.bot_blocked,
            (SELECT COUNT(*) FROM user_books ub WHERE ub.user_id = u.user_id) as books_count,
            (SELECT COALESCE(SUM(amount), 0) FROM payments p WHERE p.user_id = u.user_id AND (p.status = 'approved' OR p.receipt_file_id LIKE '%WEBHOOK%' OR p.tx_ref LIKE '%WEBHOOK%')) as total_spent
        FROM users u
        {where_str}
        ORDER BY u.user_id DESC
        LIMIT ? OFFSET ?
    """
    c.execute(sql, params + [limit, offset])
    rows = c.fetchall()
    conn.close()
    
    now_dt = datetime.now()
    user_list = []
    for r in rows:
        d = dict(r)
        vip_exp = d.get('vip_expiry')
        is_vip_active = False
        if vip_exp:
            try:
                is_vip_active = datetime.strptime(vip_exp[:19], "%Y-%m-%d %H:%M:%S") > now_dt
            except Exception:
                pass
        d['is_vip'] = is_vip_active
        user_list.append(d)
        
    return {
        "total": total_count,
        "users": user_list
    }

def get_all_payments_admin_data(limit=100, offset=0, query='', status='all', ptype='all'):
    """Fetch payments records for the transactions table."""
    conn = get_connection()
    c = conn.cursor()
    
    where_clauses = []
    params = []
    
    if query:
        q = f"%{query.strip().lower()}%"
        where_clauses.append("(LOWER(u.first_name) LIKE ? OR LOWER(u.username) LIKE ? OR CAST(p.user_id AS TEXT) LIKE ? OR LOWER(p.tx_ref) LIKE ?)")
        params.extend([q, q, q, q])
        
    if status != 'all':
        if status == 'approved':
            where_clauses.append("(p.status = 'approved' OR p.receipt_file_id LIKE '%WEBHOOK%' OR p.tx_ref LIKE '%WEBHOOK%')")
        else:
            where_clauses.append("p.status = ?")
            params.append(status)
            
    if ptype != 'all':
        if ptype == 'book':
            where_clauses.append("p.tx_ref LIKE '%BOOK%'")
        elif ptype == 'advice':
            where_clauses.append("p.tx_ref LIKE '%ADVICE%'")
        elif ptype == 'tip':
            where_clauses.append("p.tx_ref LIKE '%TIP%'")

    where_str = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    c.execute(f"SELECT COUNT(*) FROM payments p LEFT JOIN users u ON p.user_id = u.user_id {where_str}", params)
    total_count = c.fetchone()[0]
    
    sql = f"""
        SELECT 
            p.id,
            p.user_id,
            p.amount,
            p.payment_date,
            p.tx_ref,
            p.receipt_file_id,
            p.status,
            u.first_name,
            u.username
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id
        {where_str}
        ORDER BY p.id DESC
        LIMIT ? OFFSET ?
    """
    c.execute(sql, params + [limit, offset])
    rows = c.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        tx = r['tx_ref'] or ''
        rf = r['receipt_file_id'] or ''
        st = r['status']
        if rf.startswith('PENDING_CHECKOUT'):
            st = 'abandoned_cart'
        elif st == 'approved' or 'WEBHOOK' in rf or 'WEBHOOK' in tx:
            st = 'approved'
            
        t_type = 'Book' if 'BOOK' in tx else 'Advice' if 'ADVICE' in tx else 'Tip' if 'TIP' in tx else 'VIP' if 'VIP' in tx else 'Other'
        provider = 'Chapa' if 'CHAPA' in tx or 'WEBHOOK' in rf else 'ShegerPay' if 'SHEGER' in tx else 'Manual/CBE'
        
        items.append({
            "id": r['id'],
            "user_id": r['user_id'],
            "name": r['first_name'] or 'Unknown',
            "username": r['username'] or '',
            "amount": r['amount'],
            "date": r['payment_date'],
            "tx_ref": tx,
            "type": t_type,
            "provider": provider,
            "status": st
        })
        
    return {
        "total": total_count,
        "payments": items
    }

def get_abandoned_carts_admin_data():
    """Fetch pending checkout sessions for recovery."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT 
            p.id,
            p.user_id,
            p.amount,
            p.payment_date,
            p.tx_ref,
            u.first_name,
            u.username,
            u.bot_language,
            u.bot_blocked
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.user_id
        WHERE p.receipt_file_id = 'PENDING_CHECKOUT' AND p.status = 'pending'
        ORDER BY p.id DESC LIMIT 100
    ''')
    rows = c.fetchall()
    conn.close()
    
    now_dt = datetime.now()
    carts = []
    for r in rows:
        tx = r['tx_ref'] or ''
        item_title = "Book Checkout" if "BOOK" in tx else "Advice Package" if "ADVICE" in tx else "Checkout Order"
        pdate = r['payment_date']
        time_ago = ""
        if pdate:
            try:
                dt = datetime.strptime(pdate[:19], "%Y-%m-%d %H:%M:%S")
                diff = now_dt - dt
                if diff.days > 0:
                    time_ago = f"{diff.days}d ago"
                elif diff.seconds >= 3600:
                    time_ago = f"{diff.seconds // 3600}h ago"
                else:
                    time_ago = f"{diff.seconds // 60}m ago"
            except Exception:
                time_ago = pdate[:16]
                
        carts.append({
            "id": r['id'],
            "user_id": r['user_id'],
            "name": r['first_name'] or 'User',
            "username": r['username'] or '',
            "language": r['bot_language'] or 'am',
            "blocked": bool(r['bot_blocked']),
            "amount": r['amount'],
            "date": pdate,
            "time_ago": time_ago,
            "item_title": item_title,
            "tx_ref": tx
        })
    return carts

def delete_payment_record_by_id(pid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM payments WHERE id = ?", (pid,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_last_approved_payment():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, amount FROM payments WHERE status = 'approved' ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row:
        c.execute("DELETE FROM payments WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        return dict(row)
    conn.close()
    return None


# ─── User Functions ────────────────────────

def add_user(user_id, username, first_name, referred_by=None):
    conn = get_connection()
    c = conn.cursor()
    clean_uname = (username or "").lstrip('@').strip() or "Unknown"
    clean_name = (first_name or "").strip() or "User"
    c.execute('''INSERT INTO users (user_id, username, first_name, joined_date, referred_by, credits, advice_messages_left)
        VALUES (?, ?, ?, ?, ?, 0, 5)
        ON CONFLICT(user_id) DO UPDATE SET
            username = CASE WHEN excluded.username != 'Unknown' AND excluded.username != '' THEN excluded.username ELSE users.username END,
            first_name = CASE WHEN excluded.first_name != 'User' AND excluded.first_name != '' THEN excluded.first_name ELSE users.first_name END
    ''', (user_id, clean_uname, clean_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), referred_by))
    conn.commit()
    conn.close()

def sync_user_profile(user_id, username=None, full_name=None):
    if not user_id:
        return
    clean_uname = (username or "").lstrip('@').strip()
    clean_name = (full_name or "").strip()
    if not clean_uname and not clean_name:
        return
    conn = get_connection()
    c = conn.cursor()
    try:
        if clean_uname and clean_name:
            c.execute("UPDATE users SET username = ?, first_name = ? WHERE user_id = ? AND (IFNULL(username, '') != ? OR IFNULL(first_name, '') != ?)",
                      (clean_uname, clean_name, user_id, clean_uname, clean_name))
        elif clean_name:
            c.execute("UPDATE users SET first_name = ? WHERE user_id = ? AND IFNULL(first_name, '') != ?",
                      (clean_name, user_id, clean_name))
        elif clean_uname:
            c.execute("UPDATE users SET username = ? WHERE user_id = ? AND IFNULL(username, '') != ?",
                      (clean_uname, user_id, clean_uname))
        if c.rowcount > 0:
            conn.commit()
    except Exception:
        pass
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_username(username):
    if not username:
        return None
    cleaned = str(username).strip()
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].split("?")[0].strip("/")
            break
    uname = cleaned.lstrip('@').strip().lower()
    if not uname:
        return None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(username) = ?", (uname,))
    row = c.fetchone()
    if not row:
        # Fallback: exact case-insensitive match on first_name (Telegram display name)
        c.execute("SELECT * FROM users WHERE LOWER(first_name) = ? ORDER BY user_id DESC LIMIT 1", (uname,))
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

# ─── Referral & Commission Functions ────────────────────

def record_referral(referrer_id, referred_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT OR IGNORE INTO referrals (referrer_id, referred_id, credit_given, has_chatted, created_date)
            VALUES (?, ?, 0, 0, ?)
        ''', (referrer_id, referred_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception:
        pass
    conn.close()

def get_referrer(user_id):
    """Legacy lookup for uncredited referrer."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT referrer_id FROM referrals WHERE referred_id = ? AND credit_given = 0", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['referrer_id'] if row else None

def get_user_referrer(user_id):
    """Lifetime lookup for who referred this user."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row['referred_by']:
        conn.close()
        return row['referred_by']
    c.execute("SELECT referrer_id FROM referrals WHERE referred_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['referrer_id'] if row else None

def mark_referred_user_chatted(referred_id):
    """
    Called when a user sends a chat message to the mentor AI.
    Marks has_chatted = 1 if not already marked.
    Returns (is_new_chatter, referrer_id, uncredited_chatted_count).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, referrer_id, has_chatted FROM referrals WHERE referred_id = ?", (referred_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, None, 0
    referrer_id = row['referrer_id']
    if row['has_chatted'] == 1:
        conn.close()
        return False, referrer_id, 0
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE referrals SET has_chatted = 1, chatted_date = ? WHERE referred_id = ?", (now_str, referred_id))
    conn.commit()

    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND has_chatted = 1 AND credit_given = 0", (referrer_id,))
    uncredited = c.fetchone()[0]
    conn.close()
    return True, referrer_id, uncredited

def get_user_referral_stats(user_id):
    """
    Returns referral statistics for a user:
    - total_started: count of people who joined using their referral link
    - total_chatted: count of referred people who started conversating with AI
    - uncredited_chatted: chatting friends not yet claimed for 5-friend milestones
    - can_claim: True if uncredited_chatted >= 5
    - claimable_count: uncredited_chatted // 5
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    total_started = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND has_chatted = 1", (user_id,))
    total_chatted = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND has_chatted = 1 AND credit_given = 0", (user_id,))
    uncredited_chatted = c.fetchone()[0]
    conn.close()

    return {
        "total_started": total_started,
        "total_chatted": total_chatted,
        "uncredited_chatted": uncredited_chatted,
        "can_claim": uncredited_chatted >= 5,
        "claimable_count": uncredited_chatted // 5
    }

def mark_n_chatted_referrals_credited(referrer_id, n=5):
    """
    Marks n uncredited chatting referrals as credited towards rewards.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE referrals 
        SET credit_given = 1 
        WHERE id IN (
            SELECT id FROM referrals 
            WHERE referrer_id = ? AND has_chatted = 1 AND credit_given = 0 
            ORDER BY id ASC
            LIMIT ?
        )
    ''', (referrer_id, n))
    updated = c.rowcount
    conn.commit()
    conn.close()
    return updated

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
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND has_chatted = 1 AND credit_given = 0", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

# ─── Commission & Payout Functions ────────────────────

def get_commission_balance(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(commission_balance, 0.0) as bal FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return float(row['bal']) if row and row['bal'] is not None else 0.0

def add_commission_balance(user_id, amount):
    conn = get_connection()
    c = conn.cursor()
    amt = float(amount)
    c.execute('''
        UPDATE users 
        SET commission_balance = IFNULL(commission_balance, 0.0) + ?,
            total_earned_commission = IFNULL(total_earned_commission, 0.0) + ?
        WHERE user_id = ?
    ''', (amt, amt, user_id))
    conn.commit()
    conn.close()

def deduct_commission_balance(user_id, amount):
    """
    Deducts amount from commission balance if balance is sufficient.
    Returns True if successfully deducted, False if insufficient balance.
    """
    conn = get_connection()
    c = conn.cursor()
    amt = float(amount)
    c.execute('''
        UPDATE users 
        SET commission_balance = commission_balance - ? 
        WHERE user_id = ? AND IFNULL(commission_balance, 0.0) >= ?
    ''', (amt, user_id, amt))
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    return success

def record_referral_commission(referrer_id, buyer_id, tx_ref, package_name, purchase_amount, commission_rate=0.30):
    """
    Records a 30% commission for referrer on a package purchase.
    Idempotent based on tx_ref.
    Returns (credited, commission_amount).
    """
    if not referrer_id or referrer_id == buyer_id:
        return False, 0.0
    purchase_amount = float(purchase_amount)
    if purchase_amount <= 0:
        return False, 0.0

    comm_amt = round(purchase_amount * commission_rate, 2)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO referral_commissions (
                referrer_id, buyer_id, tx_ref, package_name, purchase_amount, commission_amount, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (referrer_id, buyer_id, tx_ref, package_name, purchase_amount, comm_amt, now_str))
        conn.commit()
        credited = True
    except Exception:
        credited = False
    conn.close()

    if credited:
        add_commission_balance(referrer_id, comm_amt)
        return True, comm_amt
    return False, 0.0

def create_referral_payout(user_id, amount, payment_method, account_holder, account_number='', phone_number=''):
    """
    Creates a pending payout request for referral commission.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO referral_payouts (
            user_id, amount, payment_method, account_holder, account_number, phone_number, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (user_id, float(amount), payment_method, account_holder, account_number, phone_number, now_str))
    payout_id = c.lastrowid
    conn.commit()
    conn.close()
    return payout_id

def get_referral_payout(payout_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM referral_payouts WHERE id = ?", (payout_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def approve_referral_payout(payout_id, admin_notes=''):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM referral_payouts WHERE id = ? AND status = 'pending'", (payout_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    c.execute('''
        UPDATE referral_payouts 
        SET status = 'approved', admin_notes = ?, processed_at = ? 
        WHERE id = ?
    ''', (admin_notes, now_str, payout_id))
    conn.commit()
    conn.close()
    return dict(row)

def reject_referral_payout(payout_id, admin_notes=''):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM referral_payouts WHERE id = ? AND status = 'pending'", (payout_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    amount = float(row['amount'])
    user_id = row['user_id']
    c.execute('''
        UPDATE referral_payouts 
        SET status = 'rejected', admin_notes = ?, processed_at = ? 
        WHERE id = ?
    ''', (admin_notes, now_str, payout_id))
    conn.commit()
    conn.close()
    # Refund amount back to user's commission balance
    add_commission_balance(user_id, amount)
    return dict(row)

def get_user_referral_payouts(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM referral_payouts WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_pending_referral_payouts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM referral_payouts WHERE status = 'pending' ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

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
        if status == 'pending' and receipt_file_id == 'PENDING_CHECKOUT':
            c.execute('''DELETE FROM payments 
                         WHERE user_id = ? AND status IN ('pending', 'abandoned_nudged') 
                         AND receipt_file_id = 'PENDING_CHECKOUT' ''', (user_id,))
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
        WHERE user_id = ? AND status IN ('pending', 'abandoned_nudged') 
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_abandoned_checkouts():
    """Get pending payments older than 5 minutes that haven't been nudged yet."""
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

def approve_payment(tx_ref, order_id=None, receipt_ref=None):
    conn = get_connection()
    c = conn.cursor()
    receipt_tag = f"WEBHOOK_OCR_{str(receipt_ref).strip().upper()}" if receipt_ref else "CHAPA_WEBHOOK"
    c.execute("SELECT user_id FROM payments WHERE tx_ref = ?", (tx_ref,))
    prow = c.fetchone()
    c.execute('''UPDATE payments 
                 SET status = 'approved', order_id = ?, receipt_file_id = ?
                 WHERE tx_ref = ?''', (order_id, receipt_tag, tx_ref))
    updated = c.rowcount
    if prow and prow['user_id']:
        c.execute('''DELETE FROM payments 
                     WHERE user_id = ? AND status IN ('pending', 'abandoned_nudged') 
                     AND tx_ref != ?''', (prow['user_id'], tx_ref))
    conn.commit()
    conn.close()
    return updated > 0

def is_receipt_ref_used(receipt_ref):
    if not receipt_ref:
        return False
    clean_ref = str(receipt_ref).strip().upper()
    if len(clean_ref) < 5 or clean_ref in ("NONE", "NULL", "N/A", "UNKNOWN"):
        return False
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id FROM payments 
                 WHERE status = 'approved' 
                 AND (receipt_file_id = ? OR receipt_file_id = ?)''',
              (f"WEBHOOK_OCR_{clean_ref}", clean_ref))
    row = c.fetchone()
    conn.close()
    return row is not None

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

    c.execute("""SELECT COUNT(*) FROM users 
        WHERE (advice_history LIKE '%"role": "user"%' OR IFNULL(advice_messages_left, 5) < 5) 
        AND bot_blocked = 0""")
    active_advice_users = c.fetchone()[0]

    c.execute("""SELECT COUNT(*) FROM users 
        WHERE IFNULL(advice_messages_left, 5) <= 0 
        AND bot_blocked = 0""")
    trial_exhausted_users = c.fetchone()[0]

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

    # Book stats
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT COUNT(*) FROM user_books WHERE expires_at IS NULL OR expires_at > ?", (now_str,))
    total_books_unlocked = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM user_books WHERE expires_at IS NOT NULL AND expires_at > ?", (now_str,))
    active_book_rentals = c.fetchone()[0]

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
        ptype = 'Tip' if 'TIP' in tx else 'Advice' if 'ADVICE' in tx else 'Book' if 'BOOK' in tx else 'Other'
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
        "trial_exhausted_users": trial_exhausted_users,
        "total_books_unlocked": total_books_unlocked,
        "active_book_rentals": active_book_rentals,
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
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
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
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        pass
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_sub_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def remove_sub_admin(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        pass
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_sub_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_sub_admin(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        pass
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT IFNULL(is_sub_admin, 0) as is_sub_admin FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row['is_sub_admin'])

def add_sub_admin_by_identifier(identifier):
    conn = get_connection()
    c = conn.cursor()
    try:
        uid = int(identifier)
        c.execute("UPDATE users SET is_sub_admin = 1 WHERE user_id = ?", (uid,))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return uid if affected > 0 else None
    except (ValueError, TypeError):
        uname = str(identifier).lstrip('@').lower()
        c.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (uname,))
        row = c.fetchone()
        if row:
            uid = row['user_id']
            c.execute("UPDATE users SET is_sub_admin = 1 WHERE user_id = ?", (uid,))
            conn.commit()
            conn.close()
            return uid
        conn.close()
        return None

def get_all_sub_admins():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name FROM users WHERE is_sub_admin = 1")
    rows = c.fetchall()
    conn.close()
    return rows

# ─── User Lookup & Search ─────────────────

def search_users(query):
    """Search users by User ID, @username, t.me link, or Telegram display name (first/last/full name, Unicode-aware)."""
    if not query:
        return []
    raw = str(query).strip()
    if not raw:
        return []

    # Strip t.me links and leading @
    cleaned = raw
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].split("?")[0].strip("/")
            break
    cleaned_no_at = cleaned.lstrip("@").strip()
    if not cleaned_no_at:
        return []

    conn = get_connection()
    c = conn.cursor()

    results = []
    seen_ids = set()

    # 1. Exact User ID match if numeric
    if cleaned_no_at.isdigit():
        uid = int(cleaned_no_at)
        c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        row = c.fetchone()
        if row:
            d = dict(row)
            results.append(d)
            seen_ids.add(d["user_id"])

    # 2. Unicode case-insensitive search across first_name (full display name) & username
    q_fold = cleaned_no_at.casefold()
    q_tokens = [t for t in q_fold.split() if t]

    c.execute("SELECT * FROM users ORDER BY user_id DESC")
    all_rows = c.fetchall()
    conn.close()

    scored = []
    for r in all_rows:
        uid = r["user_id"]
        if uid in seen_ids:
            continue
        fname_raw = (r["first_name"] or "").strip()
        uname_raw = (r["username"] or "").strip().lstrip("@")
        if uname_raw.lower() == "unknown":
            uname_raw = ""

        fname = fname_raw.casefold()
        uname = uname_raw.casefold()
        combined = f"{fname} {uname}".strip()

        score = 0
        if uname and uname == q_fold:
            score = 100
        elif fname and fname == q_fold:
            score = 98
        elif uname and uname.startswith(q_fold):
            score = 88
        elif fname and fname.startswith(q_fold):
            score = 85
        elif uname and q_fold in uname:
            score = 75
        elif fname and q_fold in fname:
            score = 72
        elif len(q_tokens) > 1 and all(tok in combined for tok in q_tokens):
            score = 60
        else:
            # Check individual word/token matches for multi-word queries or partial names
            name_words = fname.split()
            matched_tokens = [tok for tok in q_tokens if len(tok) >= 2 and (tok in fname or tok in uname)]
            if matched_tokens:
                if any(any(w.startswith(tok) for w in name_words) for tok in matched_tokens):
                    score = 40 + len(matched_tokens) * 5
                else:
                    score = 25 + len(matched_tokens) * 5

        if score > 0:
            scored.append((score, uid, dict(r)))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    for _, _, user_dict in scored[:25 - len(results)]:
        results.append(user_dict)

    return results

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

def get_last_mentor_message(user_id):
    """Retrieves the last actual 1-on-1 advice message sent by the AI mentor."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_mentor_message FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row['last_mentor_message'] if row and row['last_mentor_message'] else None

def set_last_mentor_message(user_id, text):
    """Saves the last actual 1-on-1 advice message from the AI mentor (never overwritten by broadcasts)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET last_mentor_message = ? WHERE user_id = ?", (text, user_id))
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
    c.execute("UPDATE users SET age_verified = 0, gender = NULL, advice_history = '[]', last_mentor_message = NULL WHERE user_id = ?", (user_id,))
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

    # 4. Onboarded, No Chat (Not Paid, Not VIP, Has Gender, Never Sent User Message)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
        AND (advice_history IS NULL OR advice_history NOT LIKE '%"role": "user"%')
        AND IFNULL(advice_messages_left, 5) >= 5
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    onboarded_no_chat = c.fetchone()[0]

    # 5. In Trial (Not Paid, Not VIP, Has Gender, Sent User Msg, msgs > 0)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
        AND (advice_history LIKE '%"role": "user"%' OR IFNULL(advice_messages_left, 5) < 5)
        AND IFNULL(advice_messages_left, 5) > 0 
        AND user_id NOT IN ({paid_sql}) 
        AND (vip_expiry IS NULL OR vip_expiry <= ?) 
        AND bot_blocked = 0""", (now_str,))
    in_trial = c.fetchone()[0]

    # 6. Trial Ended (Not Paid, Not VIP, Has Gender, msgs <= 0)
    c.execute(f"""SELECT COUNT(*) FROM users 
        WHERE gender IS NOT NULL AND gender != '' 
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
        SELECT user_id, first_name, bot_language, joined_date, last_nudge_at, IFNULL(nudge_onboard_sent, 0) as nudge_count
        FROM users
        WHERE (IFNULL(age_verified, 0) = 0 OR gender IS NULL OR gender = '')
        AND bot_blocked = 0
        AND IFNULL(nudge_onboard_sent, 0) < 5
    """)
    rows = c.fetchall()
    conn.close()
    
    valid_users = []
    now = datetime.now()
    for r in rows:
        try:
            raw_joined = (r['joined_date'] or "")[:19].replace('T', ' ')
            joined_dt = datetime.strptime(raw_joined, "%Y-%m-%d %H:%M:%S") if raw_joined else now
        except Exception:
            joined_dt = now

        last_nudge = None
        if r['last_nudge_at']:
            try:
                raw_nudge = r['last_nudge_at'][:19].replace('T', ' ')
                last_nudge = datetime.strptime(raw_nudge, "%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        
        n_count = r['nudge_count']
        if n_count == 0:
            # Only nudge if stuck for at least 30 minutes after joining
            if (now - joined_dt).total_seconds() >= 1800:
                valid_users.append(dict(r))
        else:
            # Subsequent nudges require at least 20 hours since previous nudge
            if last_nudge:
                if (now - last_nudge).total_seconds() >= 72000:
                    valid_users.append(dict(r))
            elif (now - joined_dt).days >= n_count:
                valid_users.append(dict(r))
            
    return valid_users

def get_silent_users():
    """Get users who completed onboarding but never sent a message. Waits at least 2 hours after joining."""
    conn = get_connection()
    c = conn.cursor()
    two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        SELECT user_id, first_name, bot_language
        FROM users
        WHERE IFNULL(age_verified, 0) = 1 
        AND gender IS NOT NULL AND gender != '' 
        AND (advice_history IS NULL OR advice_history NOT LIKE '%"role": "user"%')
        AND IFNULL(advice_messages_left, 5) >= 5
        AND bot_blocked = 0
        AND IFNULL(nudge_silent_sent, 0) = 0
        AND (joined_date IS NULL OR joined_date <= ?)
    """, (two_hours_ago,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_trial_ended_users():
    """Get users who exhausted their trial but haven't paid. Waits at least 12 hours since last nudge."""
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    twelve_hours_ago = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        SELECT user_id, first_name, bot_language
        FROM users
        WHERE advice_history IS NOT NULL AND advice_history != '[]'
        AND IFNULL(advice_messages_left, 5) <= 0
        AND (vip_expiry IS NULL OR vip_expiry < ?)
        AND bot_blocked = 0
        AND IFNULL(nudge_revive_sent, 0) = 0
        AND (last_nudge_at IS NULL OR last_nudge_at <= ?)
        AND user_id NOT IN (
            SELECT DISTINCT user_id FROM payments
            WHERE status = 'approved' OR receipt_file_id LIKE '%WEBHOOK%' OR tx_ref LIKE '%WEBHOOK%'
        )
    """, (now_str, twelve_hours_ago))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

import json
import re

def append_bot_message_to_history(user_id, text, is_broadcast=True):
    """Appends a message sent by the bot to the user's AI history so the AI has context, tagged as broadcast."""
    try:
        history_str = get_advice_history(user_id)
        history = json.loads(history_str) if history_str else []
    except:
        history = []
    
    # Strip HTML tags so the AI sees clean text
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if not clean_text:
        return
    
    # Avoid appending duplicate consecutive bot messages
    if history and history[-1].get("role") == "model" and history[-1].get("parts") == [clean_text]:
        return
        
    entry = {"role": "model", "parts": [clean_text]}
    if is_broadcast:
        entry["is_broadcast"] = True
    history.append(entry)
    
    # Keep only the last 20 messages to prevent blob from growing too large
    if len(history) > 20:
        history = history[-20:]
        
    save_advice_history(user_id, json.dumps(history, ensure_ascii=False))

def is_broadcast_or_nudge_text(text):
    """Helper to detect if a message text is an automated nudge or broadcast rather than 1-on-1 mentor advice."""
    if not text:
        return True
    t = str(text).strip()
    nudge_signatures = [
        "በሩን ከፍተው ገብተዋል ግን ዝምታን መርጠዋል",
        "opened the door but stayed silent",
        "ማዕጾ ኸፊጥካ ኣቲኻ ግን ስቕታ መሪጽካ",
        "balbala banteet seente garuu cal'isuu filatte",
        "ስለተወያየንበት ጉዳይ አንድ ያልነገርኩዎት ትልቅ ነገር አለ",
        "one major thing I haven't told you",
        "ሓደ ዘይነገርኩኻ ዓቢ ነገር ኣሎ",
        "wanta guddaa tokko kanin sitti hin himin jira",
        "እባክዎ ጾታዎን ይምረጡ",
        "Please select your gender",
        "ጾታዎን ይምረጡ",
        "የዕለቱ የስነ-ልቦና ማስታወሻ",
        "የዕለቱ የሳይኮሎጂ ማስታወሻ",
        "የዕለቱ የስነልቦና ማስታወሻ",
        "[BROADCAST]",
    ]
    for sig in nudge_signatures:
        if sig in t:
            return True
    return False

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
    ALLOWED_NUDGES = {"nudge_onboard_sent", "nudge_silent_sent", "nudge_revive_sent"}
    if nudge_type not in ALLOWED_NUDGES:
        logging.error(f"Invalid nudge_type in mark_nudge_sent: {nudge_type}")
        return
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(f"UPDATE users SET {nudge_type} = IFNULL({nudge_type}, 0) + 1, last_nudge_at = ? WHERE user_id = ?", (now_str, user_id))
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
    try: c.execute("ALTER TABLE users ADD COLUMN last_nudge_at TEXT")
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
        AND payments.status IN ('pending', 'abandoned_nudged')
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


# ─── Author & Publishing Platform ────────────────────────
import uuid
import secrets

def create_or_get_author(name, phone='', telegram_username='', telegram_id=None, royalty=70.0, pen_name=''):
    """Creates a new author record or returns an existing one."""
    conn = get_connection()
    c = conn.cursor()
    
    existing = None
    if telegram_id:
        c.execute("SELECT * FROM authors WHERE telegram_id = ?", (telegram_id,))
        existing = c.fetchone()
    if not existing and telegram_username:
        clean_u = telegram_username.strip().lstrip('@').lower()
        c.execute("SELECT * FROM authors WHERE LOWER(telegram_username) = ?", (clean_u,))
        existing = c.fetchone()
        
    if existing:
        conn.close()
        return dict(existing)
        
    author_id = f"auth_{uuid.uuid4().hex[:8]}"
    access_token = f"AUTH-{secrets.token_hex(4).upper()}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_u = telegram_username.strip().lstrip('@').lower() if telegram_username else ''
    
    c.execute('''
        INSERT INTO authors (
            author_id, access_token, name, pen_name, phone, 
            telegram_id, telegram_username, royalty_percentage, 
            bank_name, bank_account, account_holder, bio, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'CBE', '', '', '', 'active', ?)
    ''', (author_id, access_token, name.strip(), pen_name.strip() or name.strip(), phone.strip(), 
          telegram_id, clean_u, float(royalty), now_str))
    
    conn.commit()
    c.execute("SELECT * FROM authors WHERE author_id = ?", (author_id,))
    row = c.fetchone()
    conn.close()
    return dict(row)

def get_author_by_token(token):
    """Retrieve author by access_token or author_id."""
    if not token:
        return None
    token = token.strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM authors WHERE access_token = ? OR author_id = ?", (token, token))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_author_by_telegram_id(telegram_id, username=None):
    """Retrieve author by telegram ID or username."""
    conn = get_connection()
    c = conn.cursor()
    row = None
    if telegram_id:
        c.execute("SELECT * FROM authors WHERE telegram_id = ?", (telegram_id,))
        row = c.fetchone()
    if not row and username:
        clean_u = username.strip().lstrip('@').lower()
        c.execute("SELECT * FROM authors WHERE LOWER(telegram_username) = ?", (clean_u,))
        row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_author_profile(author_id, data):
    """Updates author pen name, bio, phone, and bank details."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE authors SET
            pen_name = COALESCE(?, pen_name),
            bio = COALESCE(?, bio),
            phone = COALESCE(?, phone),
            bank_name = COALESCE(?, bank_name),
            bank_account = COALESCE(?, bank_account),
            account_holder = COALESCE(?, account_holder)
        WHERE author_id = ?
    ''', (
        data.get('pen_name'),
        data.get('bio'),
        data.get('phone'),
        data.get('bank_name'),
        data.get('bank_account'),
        data.get('account_holder'),
        author_id
    ))
    conn.commit()
    conn.close()
    return True

def get_author_dashboard_stats(author_id):
    """Calculates all metrics, sales, books, and payouts for an author."""
    author = get_author_by_token(author_id)
    if not author:
        return None
        
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Fetch author books
    c.execute("SELECT * FROM author_books WHERE author_id = ? ORDER BY id DESC", (author_id,))
    books_rows = c.fetchall()
    author_books = [dict(r) for r in books_rows]
    
    # 2. Calculate earnings and readers per book
    total_copies_sold = 0
    total_rentals = 0
    total_gross_revenue = 0.0
    recent_sales = []
    
    royalty_pct = float(author.get('royalty_percentage', 70.0)) / 100.0
    
    for b in author_books:
        bk = b['book_key']
        
        # Count sales from payments table
        c.execute('''
            SELECT p.id, p.user_id, p.amount, p.payment_date, p.tx_ref, u.first_name, u.username
            FROM payments p
            LEFT JOIN users u ON p.user_id = u.user_id
            WHERE (p.status = 'approved' OR p.receipt_file_id LIKE '%WEBHOOK%' OR p.tx_ref LIKE '%WEBHOOK%')
              AND (p.tx_ref LIKE ? OR p.receipt_file_id LIKE ?)
            ORDER BY p.id DESC
        ''', (f"%BOOK%{bk}%", f"%BOOK%{bk}%"))
        sales = c.fetchall()
        
        b_sold = 0
        b_rented = 0
        b_revenue = 0.0
        
        for s in sales:
            amt = float(s['amount'] or 0.0)
            tx = (s['tx_ref'] or '').upper()
            is_rent = 'RENT' in tx or 'EXT' in tx
            if is_rent:
                b_rented += 1
            else:
                b_sold += 1
            b_revenue += amt
            
            author_cut = round(amt * royalty_pct, 2)
            recent_sales.append({
                "payment_id": s['id'],
                "book_key": bk,
                "book_title": b['title'],
                "buyer_name": s['first_name'] or 'Reader',
                "buyer_username": s['username'] or '',
                "type": "Rental" if is_rent else "Lifetime Purchase",
                "gross_amount": amt,
                "author_cut": author_cut,
                "date": s['payment_date']
            })
            
        b['copies_sold'] = b_sold
        b['rentals_count'] = b_rented
        b['gross_revenue'] = b_revenue
        b['author_royalties'] = round(b_revenue * royalty_pct, 2)
        
        total_copies_sold += b_sold
        total_rentals += b_rented
        total_gross_revenue += b_revenue

    recent_sales.sort(key=lambda x: str(x['date'] or ''), reverse=True)
    recent_sales = recent_sales[:50]
    
    total_royalties = round(total_gross_revenue * royalty_pct, 2)
    
    # 3. Payouts calculation
    c.execute("SELECT * FROM author_payouts WHERE author_id = ? ORDER BY id DESC", (author_id,))
    payout_rows = c.fetchall()
    payouts = [dict(p) for p in payout_rows]
    
    paid_amount = sum(float(p['amount']) for p in payouts if p['status'] == 'paid')
    pending_amount = sum(float(p['amount']) for p in payouts if p['status'] == 'pending')
    available_balance = max(0.0, round(total_royalties - paid_amount - pending_amount, 2))
    
    conn.close()
    
    return {
        "author": author,
        "kpis": {
            "total_gross_revenue": round(total_gross_revenue, 2),
            "royalty_percentage": round(royalty_pct * 100, 1),
            "total_royalties": total_royalties,
            "paid_amount": round(paid_amount, 2),
            "pending_amount": round(pending_amount, 2),
            "available_balance": available_balance,
            "total_copies_sold": total_copies_sold,
            "total_rentals": total_rentals,
            "total_readers": total_copies_sold + total_rentals,
            "books_count": len(author_books)
        },
        "books": author_books,
        "recent_sales": recent_sales,
        "payouts": payouts
    }

def save_author_book(author_id, data):
    """Creates or updates a book for an author."""
    conn = get_connection()
    c = conn.cursor()
    
    book_key = (data.get('book_key') or '').strip().lower()
    title = data.get('title', '').strip()
    subtitle = data.get('subtitle', '').strip()
    category = data.get('category', 'psychology').strip()
    pages = int(data.get('pages', 100))
    price_buy = float(data.get('price_buy', 399.0))
    allow_rent = 1 if data.get('allow_rent', True) else 0
    price_rent_5d = float(data.get('price_rent_5d', 99.0))
    price_rent_10d = float(data.get('price_rent_10d', 149.0))
    cover_url = data.get('cover_url', '').strip()
    description = data.get('description', '').strip()
    sample_title = data.get('sample_chapter_title', 'መግቢያ (Introduction)').strip()
    sample_text = data.get('sample_chapter_text', '').strip()
    full_url = data.get('full_manuscript_url', '').strip()
    req_status = data.get('status', 'draft') # 'draft' or 'pending_review'
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not book_key:
        clean_slug = ''.join(ch for ch in title.lower() if ch.isalnum() or ch in '_-')[:16]
        if not clean_slug:
            clean_slug = f"book_{uuid.uuid4().hex[:6]}"
        book_key = f"{clean_slug}_{uuid.uuid4().hex[:4]}"
        
    c.execute("SELECT id, author_id, status FROM author_books WHERE book_key = ?", (book_key,))
    existing = c.fetchone()
    
    if existing:
        if existing['author_id'] != author_id:
            conn.close()
            raise ValueError("You do not have permission to edit this book.")
        c.execute('''
            UPDATE author_books SET
                title = ?, subtitle = ?, category = ?, pages = ?,
                price_buy = ?, allow_rent = ?, price_rent_5d = ?, price_rent_10d = ?,
                cover_url = ?, description = ?, sample_chapter_title = ?, sample_chapter_text = ?,
                full_manuscript_url = ?, status = ?, updated_at = ?
            WHERE book_key = ?
        ''', (
            title, subtitle, category, pages,
            price_buy, allow_rent, price_rent_5d, price_rent_10d,
            cover_url, description, sample_title, sample_text,
            full_url, req_status, now_str, book_key
        ))
    else:
        c.execute('''
            INSERT INTO author_books (
                book_key, author_id, title, subtitle, category, pages,
                price_buy, allow_rent, price_rent_5d, price_rent_10d,
                cover_url, description, sample_chapter_title, sample_chapter_text,
                full_manuscript_url, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book_key, author_id, title, subtitle, category, pages,
            price_buy, allow_rent, price_rent_5d, price_rent_10d,
            cover_url, description, sample_title, sample_text,
            full_url, req_status, now_str, now_str
        ))
        
    conn.commit()
    conn.close()
    return book_key

def request_author_payout(author_id, amount, bank_name, bank_account, account_holder):
    """Submits a payout request for an author."""
    stats = get_author_dashboard_stats(author_id)
    if not stats:
        raise ValueError("Author not found.")
        
    avail = stats['kpis']['available_balance']
    amount = float(amount)
    if amount < 100.0:
        raise ValueError("Minimum payout amount is 100 ETB.")
    if amount > avail:
        raise ValueError(f"Requested amount ({amount} ETB) exceeds available balance ({avail} ETB).")
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO author_payouts (
            author_id, amount, bank_name, bank_account, account_holder,
            status, tx_ref, notes, requested_at
        ) VALUES (?, ?, ?, ?, ?, 'pending', '', '', ?)
    ''', (author_id, amount, bank_name, bank_account, account_holder, now_str))
    payout_id = c.lastrowid
    
    c.execute('''
        UPDATE authors SET bank_name = ?, bank_account = ?, account_holder = ?
        WHERE author_id = ?
    ''', (bank_name, bank_account, account_holder, author_id))
    
    conn.commit()
    conn.close()
    return payout_id

def get_all_authors_admin_data():
    """Returns summary of all authors, pending book reviews, and pending payouts."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM authors ORDER BY id DESC")
    authors_rows = c.fetchall()
    
    authors_list = []
    for a in authors_rows:
        aid = a['author_id']
        stats = get_author_dashboard_stats(aid)
        k = stats['kpis'] if stats else {}
        ad = dict(a)
        ad['kpis'] = k
        authors_list.append(ad)
        
    c.execute('''
        SELECT ab.*, a.name as author_name, a.pen_name, a.telegram_username
        FROM author_books ab
        LEFT JOIN authors a ON ab.author_id = a.author_id
        WHERE ab.status = 'pending_review'
        ORDER BY ab.id DESC
    ''')
    pending_books = [dict(r) for r in c.fetchall()]
    
    c.execute('''
        SELECT ap.*, a.name as author_name, a.pen_name, a.telegram_username, a.phone
        FROM author_payouts ap
        LEFT JOIN authors a ON ap.author_id = a.author_id
        WHERE ap.status = 'pending'
        ORDER BY ap.id DESC
    ''')
    pending_payouts = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return {
        "authors": authors_list,
        "pending_books": pending_books,
        "pending_payouts": pending_payouts
    }

def admin_process_book_submission(book_key, action, feedback=''):
    """Approves or rejects a submitted book."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM author_books WHERE book_key = ?", (book_key,))
    book = c.fetchone()
    if not book:
        conn.close()
        raise ValueError(f"Book {book_key} not found.")
        
    new_status = 'published' if action == 'approve' else 'rejected'
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        UPDATE author_books 
        SET status = ?, admin_feedback = ?, updated_at = ?
        WHERE book_key = ?
    ''', (new_status, feedback, now_str, book_key))
    conn.commit()
    conn.close()
    return dict(book)

def admin_process_payout_request(payout_id, action, tx_ref='', notes=''):
    """Approves or rejects a payout request."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM author_payouts WHERE id = ?", (payout_id,))
    payout = c.fetchone()
    if not payout:
        conn.close()
        raise ValueError(f"Payout #{payout_id} not found.")
        
    new_status = 'paid' if action == 'approve' else 'rejected'
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        UPDATE author_payouts
        SET status = ?, tx_ref = ?, notes = ?, processed_at = ?
        WHERE id = ?
    ''', (new_status, tx_ref, notes, now_str, payout_id))
    conn.commit()
    conn.close()
    return dict(payout)

def get_published_author_books():
    """Returns all published author books."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT ab.*, a.name as author_real_name, a.pen_name
        FROM author_books ab
        LEFT JOIN authors a ON ab.author_id = a.author_id
        WHERE ab.status = 'published'
        ORDER BY ab.id DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ══════════════════════════════════════════════════════════════════
#  DAILY FREE BOOK GIFT (TIKTOK GIVEAWAY)
# ══════════════════════════════════════════════════════════════════

def has_user_won_daily_gift(user_id):
    """Returns True if the user has ever won a lifetime book in the daily gift game."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM daily_gift_winners WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row)

def get_user_daily_gift_attempt(user_id, cycle_date):
    """Returns the user's attempt record for the given cycle_date, or None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_gift_attempts WHERE user_id = ? AND cycle_date = ?", (user_id, cycle_date))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def record_daily_gift_attempt(user_id, cycle_date, chosen_word, is_correct):
    """Records a daily gift game attempt for the cycle date. Returns True if successfully recorded, False if already attempted."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO daily_gift_attempts (user_id, cycle_date, chosen_word, is_correct, attempt_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, cycle_date, chosen_word, 1 if is_correct else 0, now_str))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def get_today_gift_winners_count(cycle_date):
    """Returns the number of winners who claimed a book today (max 5 per day)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM daily_gift_winners WHERE cycle_date = ?", (cycle_date,))
    count = c.fetchone()[0]
    conn.close()
    return count

def record_daily_gift_winner(user_id, cycle_date, rank, book_chosen):
    """Records a winner for the daily gift game. Fails if user already won previously."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO daily_gift_winners (user_id, cycle_date, rank, book_chosen, awarded_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, cycle_date, rank, book_chosen, now_str))
    conn.commit()
    conn.close()

def get_daily_gift_winners(cycle_date):
    """Returns the list of winners for the specified cycle date."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT w.*, u.username, u.first_name
        FROM daily_gift_winners w
        LEFT JOIN users u ON w.user_id = u.user_id
        WHERE w.cycle_date = ?
        ORDER BY w.rank ASC
    ''', (cycle_date,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_total_gift_winners_count():
    """Returns the total number of lifetime gift winners."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM daily_gift_winners")
    count = c.fetchone()[0]
    conn.close()
    return count

def reset_daily_gift_game(cycle_date=None, reset_lifetime=False):
    """
    Resets the daily gift game.
    If reset_lifetime is True or cycle_date is None, clears all attempts and winners.
    Otherwise clears only for the specified cycle_date.
    """
    conn = get_connection()
    c = conn.cursor()
    if reset_lifetime or not cycle_date:
        c.execute("DELETE FROM daily_gift_attempts")
        c.execute("DELETE FROM daily_gift_winners")
    else:
        c.execute("DELETE FROM daily_gift_attempts WHERE cycle_date = ?", (cycle_date,))
        c.execute("DELETE FROM daily_gift_winners WHERE cycle_date = ?", (cycle_date,))
    conn.commit()
    conn.close()

def reset_user_daily_gift(user_id):
    """
    Removes attempt and win records for a specific user (useful for admin testing).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM daily_gift_attempts WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM daily_gift_winners WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()



