import pandas as pd

# Load preprocessed data
login_df = pd.read_csv('data/preprocessed_login.csv')
usb_df = pd.read_csv('data/preprocessed_usb.csv')
file_df = pd.read_csv('data/preprocessed_file_access.csv')

# ---------------- Login Summary ----------------
# Convert timestamp to datetime
login_df['timestamp'] = pd.to_datetime(login_df['timestamp'])

# Aggregate baseline login behaviour per user
login_summary = login_df.groupby('user_id').agg(
    total_logins=('timestamp', 'count'),
    first_login=('timestamp', 'min'),
    last_login=('timestamp', 'max')
).reset_index()

# Hourly login patterns
login_df['hour'] = login_df['timestamp'].dt.hour
hourly_login = login_df.groupby(['user_id', 'hour']).size().reset_index(name='login_count')

# ---------------- USB Summary ----------------
usb_df['timestamp'] = pd.to_datetime(usb_df['timestamp'])

usb_summary = usb_df.groupby('user_id').agg(
    total_usb_events=('timestamp', 'count'),
    first_usb_event=('timestamp', 'min'),
    last_usb_event=('timestamp', 'max')
).reset_index()

usb_df['hour'] = usb_df['timestamp'].dt.hour
hourly_usb = usb_df.groupby(['user_id', 'hour']).size().reset_index(name='usb_count')

# ---------------- File Access Summary ----------------
file_df['timestamp'] = pd.to_datetime(file_df['timestamp'])

file_summary = file_df.groupby('user_id').agg(
    total_file_access=('timestamp', 'count'),
    first_file_access=('timestamp', 'min'),
    last_file_access=('timestamp', 'max')
).reset_index()

file_df['hour'] = file_df['timestamp'].dt.hour
hourly_file = file_df.groupby(['user_id', 'hour']).size().reset_index(name='file_count')

# ---------------- Save Summaries ----------------
login_summary.to_csv('data/baseline_login_summary.csv', index=False)
hourly_login.to_csv('data/hourly_login.csv', index=False)

usb_summary.to_csv('data/baseline_usb_summary.csv', index=False)
hourly_usb.to_csv('data/hourly_usb.csv', index=False)

file_summary.to_csv('data/baseline_file_summary.csv', index=False)
hourly_file.to_csv('data/hourly_file.csv', index=False)

print("Baseline profiling completed and summaries saved.")
