import pandas as pd

# Assuming 'data' folder is at the project root
df_file = pd.read_csv('../../data/baseline_file_summary.csv')
df_login = pd.read_csv('../../data/baseline_login_summary.csv')
df_usb = pd.read_csv('../../data/baseline_usb_summary.csv')

hourly_file = pd.read_csv('../../data/hourly_file.csv')
hourly_login = pd.read_csv('../../data/hourly_login.csv')
hourly_usb = pd.read_csv('../../data/hourly_usb.csv')

# Print columns
print("Baseline File Summary Columns:", df_file.columns.tolist())
print("Baseline Login Summary Columns:", df_login.columns.tolist())
print("Baseline USB Summary Columns:", df_usb.columns.tolist())
print("Hourly File Columns:", hourly_file.columns.tolist())
print("Hourly Login Columns:", hourly_login.columns.tolist())
print("Hourly USB Columns:", hourly_usb.columns.tolist())
