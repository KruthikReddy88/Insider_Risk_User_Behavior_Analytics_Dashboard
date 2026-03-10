import random
import time
import json
import sqlite3
from datetime import datetime

from backend.analytics.anomaly_model import AnomalyDetector


DB_PATH = "src/DB/insider_risk.db"


users = [f"user{i}" for i in range(1,51)]

departments = ["HR","Finance","IT","Legal"]

devices = ["Laptop","Workstation"]

files = [
    "payroll.xlsx",
    "customer_data.csv",
    "financial_report.pdf",
    "employee_records.docx",
    "source_code.zip"
]

restricted_files = [
    "restricted_financials.xlsx",
    "executive_salary.xlsx"
]

usb_devices = ["USB-A1","USB-B2","USB-C3"]


# ------------------------------------------------
# USER BASELINES
# ------------------------------------------------

user_department = {u: random.choice(departments) for u in users}

user_baseline = {}

for u in users:

    user_baseline[u] = {

        "login_hour": random.randint(9,11),
        "file_access": random.randint(2,6)

    }


# ------------------------------------------------
# USER HISTORY (FOR ADAPTIVE BASELINE)
# ------------------------------------------------

user_activity_history = {u: [] for u in users}


# ------------------------------------------------
# DYNAMIC RISK SCORES
# ------------------------------------------------

user_risk = {u:0 for u in users}


# ------------------------------------------------
# TRAIN ISOLATION FOREST MODEL
# ------------------------------------------------

detector = AnomalyDetector()

training_data = []

for _ in range(500):

    training_data.append({

        "login_hour": random.randint(8,18),
        "files_accessed": random.randint(1,6),
        "usb_size_mb": random.randint(0,20)

    })

detector.train(training_data)


# ------------------------------------------------
# UPDATE BASELINE
# ------------------------------------------------

def update_baseline(user, files_accessed):

    history = user_activity_history[user]

    history.append(files_accessed)

    if len(history) > 20:
        history.pop(0)

    avg = sum(history) / len(history)

    user_baseline[user]["file_access"] = avg


# ------------------------------------------------
# EVENT GENERATION
# ------------------------------------------------

def generate_event():

    user = random.choice(users)

    baseline = user_baseline[user]

    login_hour = int(random.gauss(baseline["login_hour"],2))

    files_accessed = max(1,int(random.gauss(baseline["file_access"],2)))

    usb_connected = 0
    usb_size_mb = 0
    device_id = None

    file_name = random.choice(files)

    scenario = random.random()


    # abnormal login
    if scenario < 0.02:
        login_hour = random.randint(0,4)


    # mass file download
    elif scenario < 0.04:
        files_accessed = random.randint(50,100)


    # restricted file access
    elif scenario < 0.06:
        file_name = random.choice(restricted_files)


    # USB data theft
    elif scenario < 0.08:

        usb_connected = 1
        device_id = random.choice(usb_devices)
        usb_size_mb = random.randint(80,200)


    return {

        "user": user,
        "department": user_department[user],
        "timestamp": datetime.now().isoformat(),
        "login_hour": login_hour,
        "files_accessed": files_accessed,
        "usb_connected": usb_connected,
        "usb_size_mb": usb_size_mb,
        "file_name": file_name,
        "device_id": device_id

    }


# ------------------------------------------------
# RISK ENGINE
# ------------------------------------------------

def compute_risk(event):

    user = event["user"]

    baseline = user_baseline[user]


    # ---------------- TIME DECAY ----------------

    user_risk[user] = user_risk[user] * 0.95


    risk_change = 0

    file_spike = 0
    usb_spike = 0
    login_spike = 0


    # ---------------- RULE BASED DETECTION ----------------

    # abnormal login
    if abs(event["login_hour"] - baseline["login_hour"]) > 6:

        risk_change += 10
        login_spike = 1


    # mass download relative to baseline
    if event["files_accessed"] > baseline["file_access"] * 5:

        risk_change += 35
        file_spike = 1


    # restricted file
    if event["file_name"] in restricted_files:

        risk_change += 25
        file_spike = 1


    # USB large transfer
    if event["usb_connected"] == 1 and event["usb_size_mb"] > 50:

        risk_change += 20
        usb_spike = 1


    # ---------------- ML ANOMALY DETECTION ----------------

    prediction, score = detector.predict({

        "login_hour": event["login_hour"],
        "files_accessed": event["files_accessed"],
        "usb_size_mb": event["usb_size_mb"]

    })

    if prediction == -1 and score < -0.2:

        risk_change += 10


    # ---------------- EVENT DECAY ----------------

    if risk_change == 0:

        user_risk[user] -= 3

    else:

        user_risk[user] += risk_change


    # ---------------- CLAMP RISK ----------------

    user_risk[user] = max(0, min(100, user_risk[user]))

    iso_flag = 1 if user_risk[user] >= 70 else 0


    # update adaptive baseline
    update_baseline(user, event["files_accessed"])


    return user_risk[user], file_spike, usb_spike, login_spike, iso_flag


# ------------------------------------------------
# DATABASE STORAGE
# ------------------------------------------------

def save_event_to_db(event, risk, file_spike, usb_spike, login_spike, iso_flag):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO risk_data_final

    (

        user_id,
        department,
        hour,
        login_count,
        total_logins,
        usb_spike_flag,
        file_spike_flag,
        login_spike_flag,
        file_name,
        device_id,
        iso_anomaly,
        final_risk_score

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """,(

        event["user"],
        event["department"],
        event["login_hour"],
        random.randint(1,10),
        random.randint(50,300),

        usb_spike,
        file_spike,
        login_spike,

        event["file_name"],
        event["device_id"],

        iso_flag,
        risk

    ))

    conn.commit()

    conn.close()


# ------------------------------------------------
# STREAM SIMULATION
# ------------------------------------------------

def stream_logs():

    while True:

        event = generate_event()

        risk, file_spike, usb_spike, login_spike, iso_flag = compute_risk(event)

        save_event_to_db(event, risk, file_spike, usb_spike, login_spike, iso_flag)

        if iso_flag == 1:

            print("⚠ THREAT DETECTED")

            print({

                "user": event["user"],
                "department": event["department"],
                "risk_score": risk

            })

        else:

            print(json.dumps(event))

        time.sleep(2)


if __name__ == "__main__":

    stream_logs()