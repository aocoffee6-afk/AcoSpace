import sqlite3

conn = sqlite3.connect("app.db")
conn.execute("PRAGMA foreign_keys = ON")
try:
    conn.execute(
        "INSERT INTO logs (goal_id, log_date, amount) VALUES (?, ?, ?)",
        (99999, "2026-11-12", 1.0)
    )
    conn.commit()
    print("插入成功（说明外键没生效）")
except sqlite3.IntegrityError as e:
    print("外键拦住了:", e)
finally:
    conn.close()