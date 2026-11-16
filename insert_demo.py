import sqlite3

conn = sqlite3.connect("app.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO goals (name, target_amount, unit) VALUES (?, ?, ?)",
    ("德语 A1", 60, "小时")
)
goal_id = cursor.lastrowid
conn.commit()

row = cursor.execute(
    "SELECT id, name, target_amount, unit, status FROM goals WHERE id = ?",
    (goal_id,)
).fetchone()

print("插入的 id:", goal_id)
print("查出来的行:", row)

conn.close()