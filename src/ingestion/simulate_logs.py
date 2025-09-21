import pandas as pd
import random
from datetime import datetime, timedelta

# Number of records to simulate
n_records = 1000
users = ['user1', 'user2', 'user3', 'user4']

# ----------------- Login events -----------------
login_data = []
for _ in range(n_records):
    login_data.append({
        'user_id': random.choice(users),
        'timestamp': datetime.now() - timedelta(minutes=random.randint(0, 10000)),
        'success': random.choice([True, False])
    })
df_login = pd.DataFrame(login_data)
df_login.to_csv('../../data/raw_login.csv', index=False)

# ----------------- File-access events -----------------
file_data = []
files = ['fileA.txt', 'fileB.txt', 'fileC.doc']
actions = ['read', 'write', 'delete']

for _ in range(n_records):
    file_data.append({
        'user_id': random.choice(users),
        'timestamp': datetime.now() - timedelta(minutes=random.randint(0, 10000)),
        'file_name': random.choice(files),
        'action': random.choice(actions)
    })
df_file = pd.DataFrame(file_data)
df_file.to_csv('../../data/raw_file_access.csv', index=False)

# ----------------- USB usage events -----------------
usb_data = []
devices = ['USB1', 'USB2', 'USB3']
usb_actions = ['insert', 'remove']

for _ in range(n_records):
    usb_data.append({
        'user_id': random.choice(users),
        'timestamp': datetime.now() - timedelta(minutes=random.randint(0, 10000)),
        'device_id': random.choice(devices),
        'action': random.choice(usb_actions)
    })
df_usb = pd.DataFrame(usb_data)
df_usb.to_csv('../../data/raw_usb.csv', index=False)

print("Simulated raw datasets created in 'data/' folder.")
