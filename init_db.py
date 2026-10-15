import sqlite3

conn = sqlite3.connect("lots.db")

# 如果資料表已存在就先刪掉，方便重新初始化
conn.execute("DROP TABLE IF EXISTS history")
conn.execute("DROP TABLE IF EXISTS lots")

# 建立 lots 資料表
conn.execute("""
    CREATE TABLE lots (
        lot_id  TEXT PRIMARY KEY,
        product TEXT,
        station TEXT,
        status  TEXT
    )
""")


conn.execute("""
    CREATE TABLE history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        lot_id       TEXT,
        from_station TEXT,
        to_station   TEXT,
        time         TEXT,
        FOREIGN KEY (lot_id) REFERENCES lots(lot_id)
    )
""")

# dataset
conn.execute(
    "INSERT INTO lots (lot_id, product, station, status) VALUES (?, ?, ?, ?)",
    ("LOT001", "A100", "Litho", "running"),
)
conn.execute(
    "INSERT INTO lots (lot_id, product, station, status) VALUES (?, ?, ?, ?)",
    ("LOT002", "B200", "Etch", "waiting"),
)

conn.commit()
conn.close()

print("Database initialized.")