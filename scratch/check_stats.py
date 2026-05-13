import sqlite3
import pandas as pd

def check_stats():
    conn = sqlite3.connect("inventory.db")
    df = pd.read_sql_query("SELECT category, status, quantity FROM assets WHERE status != 'Списано (Scrapped)'", conn)
    
    print("--- Status Stats ---")
    status_stats = df.groupby('status')['quantity'].sum()
    print(status_stats)
    
    total = status_stats.sum()
    print(f"\nTotal Active Assets: {total}")
    for status, qty in status_stats.items():
        print(f"{status}: {qty/total*100:.1f}%")
        
    print("\n--- Category Stats ---")
    category_stats = df.groupby('category')['quantity'].sum()
    print(category_stats)
    
    conn.close()

if __name__ == "__main__":
    check_stats()
