import random
import time
import json
from datetime import datetime

users = ["emp101","emp102","emp103","emp104","emp105","emp106","emp107","emp108","emp109","emp110","emp111","emp112","emp113","emp114","emp115","emp116","emp117","emp118","emp119","emp120","emp121","emp122","emp123","emp124","emp125","emp126","emp127","emp128","emp129","emp130","emp131","emp132","emp133","emp134","emp135","emp136","emp137","emp138","emp139","emp140","emp141","emp142","emp143","emp144","emp145","emp146","emp147","emp148","emp149","emp150"]

actions = [
    "login",
    "logout",
    "file_access",
    "file_download",
    "usb_insert",
    "privilege_escalation"
]

files = [
    "finance.xlsx",
    "hr_records.pdf",
    "client_data.csv",
    "source_code.zip"
]


def generate_log():

    log = {
        "user": random.choice(users),
        "action": random.choice(actions),
        "file": random.choice(files),
        "timestamp": datetime.now().isoformat()
    }

    return log


while True:

    log = generate_log()

    with open("./logs/user_logs.json","a") as f:
        f.write(json.dumps(log) + "\n")

    print(log)

    time.sleep(2)