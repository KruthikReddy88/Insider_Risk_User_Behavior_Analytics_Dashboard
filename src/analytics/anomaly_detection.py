import pandas as pd
from sklearn.ensemble import IsolationForest

# Load baseline summaries
df_file = pd.read_csv('../../data/baseline_file_summary.csv')
df_login = pd.read_csv('../../data/baseline_login_summary.csv')
df_usb = pd.read_csv('../../data/baseline_usb_summary.csv')

# Anomaly detection models
clf_file = IsolationForest(contamination=0.05, random_state=42)
clf_login = IsolationForest(contamination=0.05, random_state=42)
clf_usb = IsolationForest(contamination=0.05, random_state=42)

# Detect anomalies in file access
df_file['anomaly'] = clf_file.fit_predict(df_file[['total_file_access']])
df_file['anomaly'] = df_file['anomaly'].map({1: 'normal', -1: 'anomaly'})

# Detect anomalies in login
df_login['anomaly'] = clf_login.fit_predict(df_login[['total_logins']])
df_login['anomaly'] = df_login['anomaly'].map({1: 'normal', -1: 'anomaly'})

# Detect anomalies in USB events
df_usb['anomaly'] = clf_usb.fit_predict(df_usb[['total_usb_events']])
df_usb['anomaly'] = df_usb['anomaly'].map({1: 'normal', -1: 'anomaly'})

# Save results
df_file.to_csv('../../data/anomaly_file_summary.csv', index=False)
df_login.to_csv('../../data/anomaly_login_summary.csv', index=False)
df_usb.to_csv('../../data/anomaly_usb_summary.csv', index=False)

print("Anomaly detection completed. Files saved in '../../data/'")
