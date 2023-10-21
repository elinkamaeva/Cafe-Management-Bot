import sqlite3

conn = sqlite3.connect("cafe.db")
cur = conn.cursor()

items = [(1, 'Американо', '200 мл', 80), 
         (2, 'Американо', '300 мл', 100), 
         (3, 'Капучино', '200 мл', 120), 
         (4, 'Капучино', '300 мл', 170), 
         (5, 'Капучино', '400 мл', 200), 
         (6, 'Латте', '300 мл', 120), 
         (7, 'Латте', '400 мл', 170), 
         (8, 'БейбиЧино', '100 мл', 50), 
         (9, 'Чёрный чай с лемонграссом, мятой и цедрой лимона', '300 мл', 50), 
         (10, 'Зелёный чай с кусочками клубники, вишни, красной и чёрной смородины', '300 мл', 50), 
         (11, 'Иван-чай со смородиной', '300 мл', 50), 
         (12, 'Сок яблочный', '200 мл', 50), 
         (13, 'Пряник', '190 гр', 120), 
         (14, 'Шоколад', '5 гр', 10)]

cur.execute("""
CREATE TABLE IF NOT EXISTS items
(id INTEGER PRIMARY KEY AUTOINCREMENT, item text, volume text, price int)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders
(id INTEGER PRIMARY KEY AUTOINCREMENT, sum int, created datetime)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS items_orders
(item_id int, amount int, order_id int)
""")
            
cur.execute("SELECT COUNT(*) FROM items")
result = cur.fetchall()
if result[0][0] == 0:
    cur.executemany("INSERT INTO items (id, item, volume, price) VALUES (?, ?, ?, ?)", items)

conn.commit()
conn.close()
