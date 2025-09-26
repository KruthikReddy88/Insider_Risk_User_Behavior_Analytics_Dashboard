import pandas as pd
import sqlite3

DB_PATH = "src/DB/insider_risk.db"
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM risk_data", conn)
conn.close()

if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
else:
    df['timestamp'] = pd.NaT

users = df['user_id'].unique()
baseline_list = []

for user in users:
    user_df = df[df['user_id'] == user]

    # Login Metrics
    if 'success' in user_df.columns:
        total_logins = user_df['success'].notna().sum()
        failed_logins = user_df['success'].value_counts().get(False, 0)
    else:
        total_logins = 0
        failed_logins = 0

    # File Access Metrics
    if 'action' in user_df.columns and 'file_name' in user_df.columns:
        total_reads = user_df[user_df['action'] == 'read'].shape[0]
        total_writes = user_df[user_df['action'] == 'write'].shape[0]
        total_deletes = user_df[user_df['action'] == 'delete'].shape[0]
    else:
        total_reads = total_writes = total_deletes = 0

    # USB Metrics
    if 'action' in user_df.columns and 'device_id' in user_df.columns:
        usb_inserts = user_df[user_df['action'] == 'insert'].shape[0]
        usb_removes = user_df[user_df['action'] == 'remove'].shape[0]
    else:
        usb_inserts = usb_removes = 0

    if 'timestamp' in user_df.columns and not user_df['timestamp'].isna().all():
        avg_hour = user_df['timestamp'].dt.hour.mean()
    else:
        avg_hour = None

    baseline_list.append({
        'user_id': user,
        'total_logins': total_logins,
        'failed_logins': failed_logins,
        'total_reads': total_reads,
        'total_writes': total_writes,
        'total_deletes': total_deletes,
        'usb_inserts': usb_inserts,
        'usb_removes': usb_removes,
        'avg_activity_hour': avg_hour
    })

baseline_df = pd.DataFrame(baseline_list)

conn = sqlite3.connect(DB_PATH)
baseline_df.to_sql('user_baseline_profile', conn, if_exists='replace', index=False)
conn.close()

print("✅ User baseline profiling completed and saved to SQLite as 'user_baseline_profile'.")
