import pandas as pd
import sqlite3

# ---------------------------
# File Paths
# ---------------------------
CSV_FILE_ACCESS = "data/raw_file_access.csv"
CSV_LOGIN = "data/raw_login.csv"
CSV_USB = "data/raw_usb.csv"

DB_PATH = "src/DB/insider_risk.db"

# ---------------------------
# Load CSVs
# ---------------------------
df_file = pd.read_csv(CSV_FILE_ACCESS)
df_login = pd.read_csv(CSV_LOGIN)
df_usb = pd.read_csv(CSV_USB)

# ---------------------------
# Convert timestamps
# ---------------------------
for df in [df_file, df_login, df_usb]:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# ---------------------------
# Add Event Type Column
# ---------------------------
df_file['event_type'] = 'file'
df_login['event_type'] = 'login'
df_usb['event_type'] = 'usb'

# ---------------------------
# Normalize Columns
# ---------------------------
# File Access
df_file = df_file[['user_id', 'timestamp', 'event_type', 'file_name', 'action']]
df_file['device_id'] = None
df_file['success'] = None

# Login
df_login = df_login[['user_id', 'timestamp', 'event_type', 'success']]
df_login['file_name'] = None
df_login['action'] = None
df_login['device_id'] = None

# USB
df_usb = df_usb[['user_id', 'timestamp', 'event_type', 'device_id', 'action']]
df_usb['file_name'] = None
df_usb['success'] = None

# ---------------------------
# Combine All DataFrames
# ---------------------------
df_all = pd.concat([df_file, df_login, df_usb], ignore_index=True)

# ---------------------------
# Clean Data
# ---------------------------
df_all['user_id'] = df_all['user_id'].fillna('Unknown')
df_all = df_all.dropna(subset=['timestamp'])

# ---------------------------
# Write to SQLite
# ---------------------------
conn = sqlite3.connect(DB_PATH)
df_all.to_sql('risk_data', conn, if_exists='replace', index=False)
conn.close()

print("✅ All raw CSVs cleaned and merged into SQLite DB as 'risk_data'.")
