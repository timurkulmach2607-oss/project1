import sqlite3

def find_duplicates():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    print("Checking for duplicate Serial Numbers...")
    cursor.execute("SELECT serial_number, COUNT(*) FROM assets GROUP BY serial_number HAVING COUNT(*) > 1")
    dupes_sn = cursor.fetchall()
    for d in dupes_sn:
        print(f"Duplicate SN: {d[0]} (found {d[1]} times)")
        
    print("\nChecking for duplicate Barcode Data...")
    cursor.execute("SELECT barcode_data, COUNT(*) FROM assets GROUP BY barcode_data HAVING COUNT(*) > 1")
    dupes_bar = cursor.fetchall()
    for d in dupes_bar:
        print(f"Duplicate Barcode: {d[0]} (found {d[1]} times)")
        
    conn.close()

if __name__ == "__main__":
    find_duplicates()
