import sqlite3
import os
import shutil

DB_NAME = "inventory.db"
BACKUP_NAME = "inventory.db.bak"

def migrate():
    if not os.path.exists(DB_NAME):
        print("Error: inventory.db not found.")
        return

    # 1. Create backup
    print(f"Creating backup: {BACKUP_NAME}")
    shutil.copy2(DB_NAME, BACKUP_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # 2. Get current columns from assets
        cursor.execute("PRAGMA table_info(assets)")
        columns = [c[1] for c in cursor.fetchall()]
        cols_str = ", ".join(columns)
        
        print("Migrating assets table to enforce UNIQUE constraints...")
        
        # 3. Create new table with correct schema
        # Note: serial_number and barcode_data now have UNIQUE constraint
        cursor.execute("""
            CREATE TABLE assets_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE,
                part_number TEXT,
                description TEXT,
                status TEXT NOT NULL,
                barcode_data TEXT UNIQUE NOT NULL,
                assigned_to TEXT DEFAULT 'Не призначено',
                photo_path TEXT,
                quantity INTEGER DEFAULT 1,
                upc TEXT
            )
        """)

        # 4. Copy data, discarding duplicates
        # We use INSERT OR IGNORE to automatically skip rows that violate UNIQUE constraints
        # We order by ID so we keep the OLDEST records in case of duplicates
        cursor.execute(f"INSERT OR IGNORE INTO assets_new ({cols_str}) SELECT {cols_str} FROM assets ORDER BY id ASC")
        
        # 5. Verify how many rows were dropped
        cursor.execute("SELECT COUNT(*) FROM assets")
        old_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM assets_new")
        new_count = cursor.fetchone()[0]
        
        print(f"Migration complete. Rows kept: {new_count}/{old_count}. (Dropped {old_count - new_count} duplicates)")

        # 6. Swap tables
        cursor.execute("DROP TABLE assets")
        cursor.execute("ALTER TABLE assets_new RENAME TO assets")

        conn.commit()
        print("Success! Database schema updated.")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
