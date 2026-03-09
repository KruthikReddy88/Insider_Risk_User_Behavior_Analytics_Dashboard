import random
import time
import json
import sqlite3

DB_PATH = "src/DB/insider_risk.db"

users = [f"user{i}" for i in range(1,51)]

departments = ["HR","Finance","IT","Legal"]

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

devices = ["USB-A1","USB-B2","USB-C3","USB-D4"]


# ------------------------------------------------
# USER BASELINES
# ------------------------------------------------

user_department = {u: random.choice(departments) for u in users}

user_baseline = {}

for u in users:

    user_baseline[u] = {

        "login_hour": random.randint(9,11),
        "file_access": random.randint(2,6),
        "usb_usage": random.choice([0,1])

    }


# dynamic risk score per user
user_risk = {u:0 for u in users}


# ------------------------------------------------
# EVENT GENERATION
# ------------------------------------------------

def generate_event():

    user = random.choice(users)

    base = user_baseline[user]

    login_hour = int(random.gauss(base["login_hour"],2))

    files_accessed = max(1,int(random.gauss(base["file_access"],2)))

    usb_connected = 0
    usb_size_mb = 0
    device_id = None

    file_name = random.choice(files)

    # small chance anomalies

    if random.random() < 0.02:
        login_hour = random.randint(0,4)

    if random.random() < 0.008:
        file_name = random.choice(restricted_files)

    if random.random() < 0.005:
        files_accessed = random.randint(60,120)

    if random.random() < 0.05:

        usb_connected = 1
        device_id = random.choice(devices)

        usb_size_mb = random.randint(5,50)

        if random.random() < 0.02:
            usb_size_mb = random.randint(60,200)

    return {

        "user": user,
        "department": user_department[user],
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

    risk_change = 0

    file_spike = 0
    usb_spike = 0
    login_spike = 0


    # abnormal login
    if abs(event["login_hour"] - baseline["login_hour"]) > 6:

        risk_change += 15
        login_spike = 1


    # mass file download
    if event["files_accessed"] > baseline["file_access"] * 10:

        risk_change += 40
        file_spike = 1


    # restricted file access
    if event["file_name"] in restricted_files:

        risk_change += 25
        file_spike = 1


    # USB large transfer
    if event["usb_connected"] == 1 and event["usb_size_mb"] > 50:

        risk_change += 30
        usb_spike = 1


    # risk decay (normal behavior)
    if risk_change == 0:

        user_risk[user] -= 2

    else:

        user_risk[user] += risk_change


    # clamp risk
    user_risk[user] = max(0,min(100,user_risk[user]))

    iso_flag = 1 if user_risk[user] >= 70 else 0

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

            print("⚠️ THREAT DETECTED")

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