import sqlite3

def migrate():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    # Shift existing timestamps by +3 hours
    cursor.execute("UPDATE audit_log SET timestamp = datetime(timestamp, '+3 hours')")
    conn.commit()
    print(f"Updated {cursor.rowcount} records.")
    conn.close()

if __name__ == "__main__":
    migrate()
