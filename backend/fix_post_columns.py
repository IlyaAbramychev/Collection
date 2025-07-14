import sqlite3

DB_PATH = 'backend/app.db'

columns = [
    ("image_path", "VARCHAR(256)"),
    ("latitude", "FLOAT"),
    ("longitude", "FLOAT")
]

def add_column_if_not_exists(cursor, table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        print(f"Добавлен столбец: {column}")
    else:
        print(f"Столбец уже существует: {column}")

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    for col, coltype in columns:
        add_column_if_not_exists(cur, "post", col, coltype)
    conn.commit()
print("Готово!") 