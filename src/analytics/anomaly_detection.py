import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# ------------------------------
# Config
# ------------------------------
DB_PATH = "../../src/DB/insider_risk.db"
CONTAMINATION = 0.05
RANDOM_STATE = 42

# ------------------------------
# Load merged risk_data from SQLite
# ------------------------------
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM risk_data", conn)
conn.close()

# ------------------------------
# Feature Engineering
# ------------------------------
# File access features
df['file_access_count'] = 1
df_file = df.groupby('user_id').agg(
    total_reads=('action', lambda x: (x=='read').sum()),
    total_writes=('action', lambda x: (x=='write').sum()),
    total_deletes=('action', lambda x: (x=='delete').sum()),
    total_file_access=('file_access_count', 'sum')
).reset_index()

# Login features
df_login = df.groupby('user_id').agg(
    total_logins=('success', lambda x: x.notna().sum()),
    failed_logins=('success', lambda x: (~x).sum())
).reset_index()

# USB features
df_usb = df.groupby('user_id').agg(
    usb_inserts=('action', lambda x: (x=='insert').sum()),
    usb_removes=('action', lambda x: (x=='remove').sum()),
    total_usb_events=('action', 'count')
).reset_index()

# Merge all features
df_features = df_file.merge(df_login, on='user_id', how='outer')
df_features = df_features.merge(df_usb, on='user_id', how='outer')
df_features.fillna(0, inplace=True)

# ------------------------------
# Isolation Forest Anomaly Detection
# ------------------------------
features = ['total_file_access', 'total_logins', 'failed_logins', 'total_usb_events']

clf = IsolationForest(contamination=CONTAMINATION, random_state=RANDOM_STATE)
df_features['ml_anomaly'] = clf.fit_predict(df_features[features])
# Map to 0 = normal, 1 = anomaly
df_features['ml_anomaly_flag'] = df_features['ml_anomaly'].map({1: 0, -1: 1})

# ------------------------------
# Normalize ML anomaly score to 0-100
# ------------------------------
scaler = MinMaxScaler(feature_range=(0, 100))
df_features['ml_risk_score'] = scaler.fit_transform(df_features[['total_file_access', 'total_logins', 'failed_logins', 'total_usb_events']].values.mean(axis=1).reshape(-1, 1))
df_features['ml_risk_score'] = (df_features['ml_risk_score'] * df_features['ml_anomaly_flag'])

# ------------------------------
# Combine with rule-based flags
# ------------------------------
# Ensure rule flags exist
for col in ['login_spike_flag', 'file_spike_flag', 'usb_spike_flag']:
    if col not in df.columns:
        df[col] = 0

df_final = df.merge(df_features[['user_id', 'ml_risk_score']], on='user_id', how='left')
df_final['rule_flags_sum'] = df_final['login_spike_flag'] + df_final['file_spike_flag'] + df_final['usb_spike_flag']
df_final['final_risk_score'] = 0.6 * df_final['ml_risk_score'] + 0.4 * (df_final['rule_flags_sum'] / 3 * 100)

# ------------------------------
# Save final risk table to SQLite
# ------------------------------
conn = sqlite3.connect(DB_PATH)
df_final.to_sql('risk_data_final', conn, if_exists='replace', index=False)
conn.close()

print("✅ Final risk scores computed and saved as 'risk_data_final'.")
