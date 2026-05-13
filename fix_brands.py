import sqlite3

conn = sqlite3.connect('inventory.db')
cur = conn.cursor()

# Знайдемо всі варіанти написання HP у ноутбуках
cur.execute("SELECT id, brand FROM assets WHERE category='Ноутбук'")
rows = cur.fetchall()
print("До виправлення:")
for r in rows:
    print(f"  id={r[0]}, brand='{r[1]}'")

# Нормалізуємо всі варіанти 'hp', 'Hp', 'hP' тощо -> 'HP'
cur.execute("UPDATE assets SET brand='HP' WHERE category='Ноутбук' AND LOWER(brand)='hp'")
conn.commit()
print(f"\nОновлено рядків: {cur.rowcount}")

cur.execute("SELECT id, brand FROM assets WHERE category='Ноутбук'")
rows = cur.fetchall()
print("\nПісля виправлення:")
for r in rows:
    print(f"  id={r[0]}, brand='{r[1]}'")

conn.close()
