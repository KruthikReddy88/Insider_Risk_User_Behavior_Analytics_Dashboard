import pandas as pd

# -------------------------------
# Load anomaly detection outputs
# -------------------------------

# File access summary
file_df = pd.read_csv('../../data/anomaly_file_summary.csv')
# Login results
login_df = pd.read_csv('../../data/anomaly_login_results.csv')
# USB summary
usb_df = pd.read_csv('../../data/anomaly_usb_summary.csv')

# Make sure column names match your CSVs
# For example, file_df might have columns: ['user_id', 'total_file_access', 'first_file_access', 'last_file_access']
# Adjust below column names if needed
file_col = 'total_file_access' if 'total_file_access' in file_df.columns else file_df.columns[1]
login_col = 'total_logins' if 'total_logins' in login_df.columns else login_df.columns[3]
usb_col = 'total_usb_events' if 'total_usb_events' in usb_df.columns else usb_df.columns[1]

# -------------------------------
# Merge all anomaly outputs
# -------------------------------
df = pd.merge(login_df, file_df, on='user_id', how='outer')
df = pd.merge(df, usb_df, on='user_id', how='outer')

# Fill missing values with 0
df.fillna(0, inplace=True)

# -------------------------------
# Rule-based anomaly flags
# -------------------------------

# 1. Login anomalies
LOGIN_SPIKE_MULTIPLIER = 2
login_mean = df[login_col].mean()
login_std = df[login_col].std()
df['login_spike_flag'] = df[login_col].apply(
    lambda x: 1 if x > login_mean + LOGIN_SPIKE_MULTIPLIER * login_std else 0
)

# 2. File access anomalies
FILE_SPIKE_MULTIPLIER = 2
file_mean = df[file_col].mean()
file_std = df[file_col].std()
df['file_spike_flag'] = df[file_col].apply(
    lambda x: 1 if x > file_mean + FILE_SPIKE_MULTIPLIER * file_std else 0
)

# 3. USB anomalies
USB_SPIKE_MULTIPLIER = 2
usb_mean = df[usb_col].mean()
usb_std = df[usb_col].std()
df['usb_spike_flag'] = df[usb_col].apply(
    lambda x: 1 if x > usb_mean + USB_SPIKE_MULTIPLIER * usb_std else 0
)

# -------------------------------
# Risk Score Calculation
# -------------------------------
# Weighted sum of anomaly flags
df['risk_score'] = df['login_spike_flag'] * 0.4 + df['file_spike_flag'] * 0.4 + df['usb_spike_flag'] * 0.2

# Normalize risk score to 0-100
df['risk_score'] = df['risk_score'] / df['risk_score'].max() * 100

# -------------------------------
# Save risk scores
# -------------------------------
df.to_csv('../../data/user_risk_scores.csv', index=False)
print("Risk scoring completed. Results saved to user_risk_scores.csv")
