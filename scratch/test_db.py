import sqlite3

def test_duplicates():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # Try to insert two assets with same barcode_data
    asset1 = ("Test", "HP", "Model1", "SN1", "PN1", "Desc", "In Stock", "BAR1", "None", None, 1, "UPC1")
    asset2 = ("Test", "HP", "Model2", "SN2", "PN2", "Desc", "In Stock", "BAR1", "None", None, 1, "UPC2")
    
    try:
        cursor.execute("INSERT INTO assets (category, brand, model, serial_number, part_number, description, status, barcode_data, assigned_to, photo_path, quantity, upc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", asset1)
        conn.commit()
        print("Asset 1 inserted.")
        
        cursor.execute("INSERT INTO assets (category, brand, model, serial_number, part_number, description, status, barcode_data, assigned_to, photo_path, quantity, upc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", asset2)
        conn.commit()
        print("Asset 2 inserted (EXPECTED FAILURE).")
    except sqlite3.IntegrityError as e:
        print(f"Caught expected IntegrityError: {e}")
    finally:
        # Cleanup
        cursor.execute("DELETE FROM assets WHERE barcode_data = 'BAR1'")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_duplicates()
