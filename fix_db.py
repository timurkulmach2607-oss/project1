import sqlite3

def fix_barcodes():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, serial_number FROM assets")
    rows = cursor.fetchall()
    
    prefixes = {
        "Ноутбук": "LAP",
        "ПК": "PC",
        "Принтер": "PRN",
        "Монітор": "MON",
        "Мережеве обладнання": "NET",
        "Інше": "OTH"
    }
    
    for row in rows:
        asset_id, category, serial_number = row
        prefix = prefixes.get(category, "AST")
        new_barcode = f"{prefix}-{serial_number}"
        cursor.execute("UPDATE assets SET barcode_data = ? WHERE id = ?", (new_barcode, asset_id))
        
    conn.commit()
    conn.close()
    print("Barcodes updated successfully.")

if __name__ == '__main__':
    fix_barcodes()
