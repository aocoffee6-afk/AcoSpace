import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# SQLite 默认不强制外键，必须手动打开，否则 goal_id 可以填不存在的目标
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target_amount REAL,
    unit TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE RESTRICT
)
""")

conn.commit()
conn.close()
print("app.db 建表完成")