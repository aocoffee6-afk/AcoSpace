import sqlite3

conn = sqlite3.connect("app.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# 先拿一个已存在的 goal_id，避免外键报错
row = cursor.execute("SELECT id FROM goals LIMIT 1").fetchone()
if row is None:
    print("goals 表是空的，先运行 insert_demo.py")
    conn.close()
    raise SystemExit

goal_id = row[0]

logs = [
    (goal_id, "2026-11-10", 2.0, "背单词"),
    (goal_id, "2026-11-10", 1.5, "听力"),   # 同一天第二条
    (goal_id, "2026-11-11", 3.0, "复习"),
]

cursor.executemany(
    "INSERT INTO logs (goal_id, log_date, amount, note) VALUES (?, ?, ?, ?)",
    logs
)
conn.commit()

summary = cursor.execute(
    """
    SELECT goal_id,
           SUM(amount) AS total_amount,
           COUNT(DISTINCT log_date) AS days
    FROM logs
    WHERE goal_id = ?
    GROUP BY goal_id
    """,
    (goal_id,)
).fetchone()

print("goal_id:", goal_id)
print("总工作量 / 记录天数:", summary)

conn.close()