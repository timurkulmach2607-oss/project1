import sqlite3
import bcrypt
import pandas as pd

DB_NAME = "inventory.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблиця активів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            serial_number TEXT UNIQUE,
            part_number TEXT,
            description TEXT,
            status TEXT NOT NULL,
            barcode_data TEXT UNIQUE NOT NULL
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE assets ADD COLUMN assigned_to TEXT DEFAULT 'Не призначено'")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE assets ADD COLUMN photo_path TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE assets ADD COLUMN quantity INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE assets ADD COLUMN upc TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Таблиця аудиту
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблиця користувачів
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    
    # Додаємо адміністратора за замовчуванням (admin / admin)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", hashed_pw))
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN session_token TEXT")
    except sqlite3.OperationalError:
        pass
        
    cursor.execute("UPDATE users SET full_name = 'Кульмач Т.В' WHERE username = 'admin' AND (full_name IS NULL OR full_name = '')")
        
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ? AND is_active = 1", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        stored_hash = row[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
    return False

def get_user_info(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return username

def update_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_pw, username))
    conn.commit()
    conn.close()
    return username

def add_audit_log(username, action, details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_log (username, action, details, timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))",
        (username, action, details)
    )
    conn.commit()
    conn.close()

def set_session_token(username, token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET session_token = ? WHERE username = ?", (token, username))
    conn.commit()
    conn.close()

def get_user_by_token(token):
    if not token: return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE session_token = ? AND is_active = 1", (token,))
    row = cursor.fetchone()
    conn.close()
    if row: return row[0]
    return None

def get_all_assets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assets", conn)
    conn.close()
    return df

def get_assets_by_serial_or_barcode(code):
    conn = get_connection()
    cursor = conn.cursor()
    like_code = f"{code}-%"
    cursor.execute("""
        SELECT * FROM assets 
        WHERE serial_number = ? OR serial_number LIKE ? 
        OR barcode_data = ? OR barcode_data LIKE ?
        OR upc = ?
    """, (code, like_code, code, like_code, code))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description] if cursor.description else []
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def add_asset(asset_data, username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO assets (category, brand, model, serial_number, part_number, description, status, barcode_data, assigned_to, photo_path, quantity, upc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_data['category'], asset_data['brand'], asset_data['model'],
            asset_data['serial_number'], asset_data['part_number'],
            asset_data['description'], asset_data['status'], asset_data['barcode_data'],
            asset_data.get('assigned_to', 'Не призначено'),
            asset_data.get('photo_path', None),
            asset_data.get('quantity', 1),
            asset_data.get('upc', None)
        ))
        conn.commit()
        qty_text = f" (Кількість: {asset_data.get('quantity', 1)})" if asset_data.get('quantity', 1) > 1 else ""
        add_audit_log(username, "Додавання", f"Додано актив: {asset_data['serial_number']} ({asset_data['category']} {asset_data['brand']}){qty_text}")
        return True, "Актив успішно додано"
    except sqlite3.IntegrityError:
        return False, "Помилка: Актив з таким серійним номером або штрихкодом вже існує"
    finally:
        conn.close()

def get_audit_log():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 1000", conn)
    conn.close()
    return df

def get_all_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, username, full_name FROM users WHERE is_active = 1", conn)
    conn.close()
    return df

def add_user(username, password, full_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)", (username, hashed_pw, full_name))
        conn.commit()
        return True, "Користувача успішно створено"
    except sqlite3.IntegrityError:
        return False, "Користувач з таким іменем вже існує"
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
