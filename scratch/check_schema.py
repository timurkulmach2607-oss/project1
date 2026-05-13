import sqlite3

def check_schema():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(assets)")
    columns = cursor.fetchall()
    print("--- Columns ---")
    for c in columns:
        print(c)
        
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='assets'")
    sql = cursor.fetchone()[0]
    print("\n--- SQL CREATE Statement ---")
    print(sql)
    conn.close()

if __name__ == "__main__":
    check_schema()
