from flask import Flask, request

app = Flask(__name__)


# 製程路線
STATIONS = ["Start", "Litho", "Etch", "Deposition", "CMP", "Done"]
# 暫存的批次資料（之後會換成資料庫）
lots = [
    {"lot_id": "LOT001", "product": "A100", "station": "Litho", "status": "running"},
    {"lot_id": "LOT002", "product": "B200", "station": "Etch", "status": "waiting"},
]

@app.route("/")
def home():
    return {"message": "Lot Tracker is running"}

# 查詢所有批次
@app.route("/lots")
def get_lots():
    return lots

# 查詢單一批次
@app.route("/lots/<lot_id>")
def get_lot(lot_id):
    for lot in lots:
        if lot["lot_id"] == lot_id:
            return lot
    return {"error": "Lot not found"}, 404

@app.route("/lots", methods=["POST"])
def create_lot():
    data = request.get_json(silent=True)

    if not data:
        data = {}

    if "lot_id" not in data:
        max_num = max((int(lot["lot_id"][3:]) for lot in lots), default=0)
        data["lot_id"] = f"LOT{max_num + 1:03d}"

    for lot in lots:
        if lot["lot_id"] == data["lot_id"]:
            return {"error": "Lot already exists"}, 400

    new_lot = {
        "lot_id": data["lot_id"],
        "product": data.get("product", "UNKNOWN"),
        "station": "Start",
        "status": "waiting",
    }
    lots.append(new_lot)
    return new_lot, 201
# 移到下一站
@app.route("/lots/<lot_id>/move", methods=["POST"])
def move_lot(lot_id):
    for lot in lots:
        if lot["lot_id"] == lot_id:
            current_index = STATIONS.index(lot["station"])

            if lot["station"] == "Done":
                return {"error": "Lot already completed"}, 400

            lot["station"] = STATIONS[current_index + 1]

            if lot["station"] == "Done":
                lot["status"] = "completed"
            else:
                lot["status"] = "running"

            return lot

    return {"error": "Lot not found"}, 404

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)


