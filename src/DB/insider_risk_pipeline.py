import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest

# ------------------------------
# Step 1: Load CSV
# ------------------------------
csv_file = "data/insider_risk_data_with_scores.csv"  # replace with your CSV name
df = pd.read_csv(csv_file)
print("CSV Loaded:")
print(df.head())

# ------------------------------
# Step 2: Data Cleaning
# ------------------------------
numeric_cols = ['login_spike_flag', 'file_spike_flag', 'usb_spike_flag', 'risk_score']
df[numeric_cols] = df[numeric_cols].fillna(0)

if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

print("Data cleaned:")
print(df.head())

# ------------------------------
# Step 3: Store to SQLite
# ------------------------------
conn = sqlite3.connect('insider_risk.db')
df.to_sql('risk_data', conn, if_exists='replace', index=False)
print("Data stored in SQLite!")

# ------------------------------
# Step 4: Baseline Profiling
# ------------------------------
baseline = df.groupby('user_id')[['login_spike_flag', 'file_spike_flag', 'usb_spike_flag']].agg(['mean','std'])
baseline.columns = ['_'.join(col) for col in baseline.columns]
baseline.reset_index(inplace=True)
print("Baseline profiling done:")
print(baseline.head())

# ------------------------------
# Step 5: Isolation Forest
# ------------------------------
activity_cols = ['login_spike_flag', 'file_spike_flag', 'usb_spike_flag']
iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
df['iso_score'] = iso.fit_predict(df[activity_cols])
df['iso_anomaly'] = df['iso_score'].apply(lambda x: 1 if x == -1 else 0)
print("Isolation Forest anomalies detected:")
print(df[['user_id', 'iso_anomaly']].head())

# ------------------------------
# Step 6: Final Risk Score
# ------------------------------
df['final_risk_score'] = 0.7 * df['risk_score'] + 0.3 * df['iso_anomaly']*100
print("Final risk score calculated:")
print(df[['user_id', 'risk_score', 'iso_anomaly', 'final_risk_score']].head())

# Optional: Update final results back to DB
df.to_sql('risk_data_final', conn, if_exists='replace', index=False)
print("Final data with risk scores stored in SQLite!")
conn.close()
