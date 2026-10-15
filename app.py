from flask import Flask, request
from datetime import datetime
import sqlite3

app = Flask(__name__)

DB_PATH = "lots.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 製程路線
STATIONS = ["Start", "Litho", "Etch", "Deposition", "CMP", "Done"]

@app.route("/")
def home():
    return {"message": "Lot Tracker is running"}

# 查詢所有批次
@app.route("/lots")
def get_lots():
    conn = get_db()
    rows = conn.execute("SELECT * FROM lots").fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 查詢單一批次
@app.route("/lots/<lot_id>")
def get_lot(lot_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM lots WHERE lot_id = ?", (lot_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return {"error": "Lot not found"}, 404
    return dict(row)

# 新增批次
@app.route("/lots", methods=["POST"])
def create_lot():
    data = request.get_json(silent=True)

    if not data:
        data = {}

    conn = get_db()

    # 沒給 lot_id 就自動產生：找出資料庫裡最大號 + 1
    if "lot_id" not in data:
        rows = conn.execute("SELECT lot_id FROM lots").fetchall()
        max_num = max((int(r["lot_id"][3:]) for r in rows), default=0)
        data["lot_id"] = f"LOT{max_num + 1:03d}"

    # 檢查是否重複
    existing = conn.execute(
        "SELECT 1 FROM lots WHERE lot_id = ?", (data["lot_id"],)
    ).fetchone()
    if existing:
        conn.close()
        return {"error": "Lot already exists"}, 400

    new_lot = {
        "lot_id": data["lot_id"],
        "product": data.get("product", "UNKNOWN"),
        "station": "Start",
        "status": "waiting",
    }
    conn.execute(
        "INSERT INTO lots (lot_id, product, station, status) VALUES (?, ?, ?, ?)",
        (new_lot["lot_id"], new_lot["product"], new_lot["station"], new_lot["status"]),
    )
    conn.commit()
    conn.close()
    return new_lot, 201

# 移到下一站
@app.route("/lots/<lot_id>/move", methods=["POST"])
def move_lot(lot_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM lots WHERE lot_id = ?", (lot_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return {"error": "Lot not found"}, 404

    lot = dict(row)

    if lot["station"] == "Done":
        conn.close()
        return {"error": "Lot already completed"}, 400

    old_station = lot["station"]
    current_index = STATIONS.index(old_station)
    new_station = STATIONS[current_index + 1]
    new_status = "completed" if new_station == "Done" else "running"

    # 更新批次位置
    conn.execute(
        "UPDATE lots SET station = ?, status = ? WHERE lot_id = ?",
        (new_station, new_status, lot_id),
    )

    # 寫入移動紀錄
    conn.execute(
        "INSERT INTO history (lot_id, from_station, to_station, time) VALUES (?, ?, ?, ?)",
        (lot_id, old_station, new_station, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )

    conn.commit()
    conn.close()

    lot["station"] = new_station
    lot["status"] = new_status
    return lot

# 查詢批次移動歷史
@app.route("/lots/<lot_id>/history")
def get_history(lot_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT lot_id, from_station, to_station, time FROM history "
        "WHERE lot_id = ? ORDER BY id",
        (lot_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)