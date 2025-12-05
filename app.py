from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DB_FILE = "bills.db"


# ------------------------- Database Setup --------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consumer_name TEXT,
            industry_name TEXT,
            contact_detail TEXT,
            bill_month TEXT,
            net_consumption REAL,
            total_amount REAL,
            savings REAL
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ----------------------------- UI Page ------------------------------
@app.route("/", methods=["GET"])
def home_page():
    return render_template("index.html")


# ------------------------ Manual Save API ----------------------------
@app.route("/manual-save", methods=["POST"])
def manual_save():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON received"}), 400

    consumer_name = data.get("consumer_name")
    industry_name = data.get("Industry_name")
    contact_detail = data.get("contact_detail")
    bill_month = data.get("bill_month")
    net_consumption = data.get("net_consumption")
    total_amount = data.get("total_amount")

    if not all([consumer_name, industry_name, contact_detail, bill_month, net_consumption, total_amount]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        total_amount = float(total_amount)
        net_consumption = float(net_consumption)
    except:
        return jsonify({"error": "Numeric fields must contain numbers"}), 400

    savings = round(total_amount * 0.03, 2)

    # Save in Database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bill_records 
        (consumer_name, industry_name, contact_detail, bill_month, net_consumption, total_amount, savings) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (consumer_name, industry_name, contact_detail, bill_month, net_consumption, total_amount, savings))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "saved",
        "preview": {
            "consumer_name": consumer_name,
            "Industry_name": industry_name,
            "contact_detail": contact_detail,
            "bill_month": bill_month,
            "net_consumption": net_consumption,
            "total_amount": total_amount
        },
        "savings": savings
    })


# --------------------- Return DB Data in JSON ---------------------------
@app.route("/download-data", methods=["GET"])
def download_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT * FROM bill_records")
    rows = cur.fetchall()

    conn.close()

    if not rows:
        return jsonify({"error": "No data available"}), 400

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "consumer_name": r[1],
            "industry_name": r[2],
            "contact_detail": r[3],
            "bill_month": r[4],
            "net_consumption": r[5],
            "total_amount": r[6],
            "savings": r[7]
        })

    return jsonify({"records": result})


# ------------------------------ Run App -----------------------------
if __name__ == "__main__":
    app.run
