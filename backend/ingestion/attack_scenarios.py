import sqlite3
import random
import time
from datetime import datetime


DB_PATH = "src/DB/insider_risk.db"


users = [f"user{i}" for i in range(1,51)]

departments = ["HR","Finance","IT","Legal"]

restricted_files = [
    "restricted_financials.xlsx",
    "executive_salary.xlsx"
]

usb_devices = ["USB-A1","USB-B","USB-C3","USB-C$","USB-A2"]


# ------------------------------------------------
# DATABASE INSERT
# ------------------------------------------------

def save_attack_event(user, department, hour, file_spike, usb_spike, login_spike, file_name, device_id, risk):

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

        user,
        department,
        hour,
        random.randint(5,15),
        random.randint(100,300),

        usb_spike,
        file_spike,
        login_spike,

        file_name,
        device_id,

        1,
        risk

    ))

    conn.commit()

    conn.close()


# ------------------------------------------------
# ATTACK SCENARIOS
# ------------------------------------------------

def abnormal_login(user, dept):

    print("⚠ Scenario: Abnormal Login")

    save_attack_event(
        user,
        dept,
        random.randint(0,3),
        0,
        0,
        1,
        None,
        None,
        40
    )


def restricted_file_access(user, dept):

    print("⚠ Scenario: Privilege Abuse")

    save_attack_event(
        user,
        dept,
        random.randint(9,18),
        1,
        0,
        0,
        random.choice(restricted_files),
        None,
        70
    )


def mass_file_download(user, dept):

    print("⚠ Scenario: Data Exfiltration")

    save_attack_event(
        user,
        dept,
        random.randint(9,18),
        1,
        0,
        0,
        "financial_report.pdf",
        None,
        90
    )


def usb_data_theft(user, dept):

    print("⚠ Scenario: USB Data Theft")

    save_attack_event(
        user,
        dept,
        random.randint(9,18),
        0,
        1,
        0,
        "customer_data.csv",
        random.choice(usb_devices),
        80
    )


# ------------------------------------------------
# ATTACK ENGINE
# ------------------------------------------------

def run_attack_engine():

    scenarios = [

        abnormal_login,
        restricted_file_access,
        mass_file_download,
        usb_data_theft

    ]

    while True:

        time.sleep(random.randint(25,60))

        user = random.choice(users)

        dept = random.choice(departments)

        scenario = random.choice(scenarios)

        scenario(user, dept)


if __name__ == "__main__":

    run_attack_engine()