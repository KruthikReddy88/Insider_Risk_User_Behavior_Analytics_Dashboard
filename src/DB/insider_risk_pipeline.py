# File: src/DB/insider_risk_pipeline.py

import os
import sqlite3
import pandas as pd

# ------------------------------
# Paths
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
DB_PATH = os.path.join(BASE_DIR, "insider_risk.db")

RAW_FILES = {
    "login": os.path.join(DATA_DIR, "raw_login.csv"),
    "file_access": os.path.join(DATA_DIR, "raw_file_access.csv"),
    "usb": os.path.join(DATA_DIR, "raw_usb.csv")
}

PREPROCESSED_FILES = {
    "login": os.path.join(DATA_DIR, "preprocessed_login.csv"),
    "file_access": os.path.join(DATA_DIR, "preprocessed_file_access.csv"),
    "usb": os.path.join(DATA_DIR, "preprocessed_usb.csv")
}

BASELINE_FILES = {
    "login": os.path.join(DATA_DIR, "baseline_login_summary.csv"),
    "file_access": os.path.join(DATA_DIR, "baseline_file_summary.csv"),
    "usb": os.path.join(DATA_DIR, "baseline_usb_summary.csv")
}

ANOMALY_FILES = {
    "login": os.path.join(DATA_DIR, "anomaly_login_summary.csv"),
    "file_access": os.path.join(DATA_DIR, "anomaly_file_summary.csv"),
    "usb": os.path.join(DATA_DIR, "anomaly_usb_summary.csv")
}

RISK_OUTPUT_CSV = os.path.join(DATA_DIR, "user_risk_scores.csv")

# ------------------------------
# Step 1: Preprocess Raw Logs
# ------------------------------
def preprocess_logs():
    # Login
    df_login = pd.read_csv(RAW_FILES['login'])
    df_login['timestamp'] = pd.to_datetime(df_login['timestamp'])
    df_login.to_csv(PREPROCESSED_FILES['login'], index=False)

    # File Access
    df_file = pd.read_csv(RAW_FILES['file_access'])
    df_file['timestamp'] = pd.to_datetime(df_file['timestamp'])
    df_file.to_csv(PREPROCESSED_FILES['file_access'], index=False)

    # USB
    df_usb = pd.read_csv(RAW_FILES['usb'])
    df_usb['timestamp'] = pd.to_datetime(df_usb['timestamp'])
    df_usb.to_csv(PREPROCESSED_FILES['usb'], index=False)

    print("✅ Preprocessed CSVs saved.")

# ------------------------------
# Step 2: Load preprocessed CSVs
# ------------------------------
def load_preprocessed():
    df_login = pd.read_csv(PREPROCESSED_FILES['login'])
    df_file = pd.read_csv(PREPROCESSED_FILES['file_access'])
    df_usb = pd.read_csv(PREPROCESSED_FILES['usb'])
    return df_login, df_file, df_usb

# ------------------------------
# Step 3: Store preprocessed data in SQLite
# ------------------------------
def save_to_db(df_login, df_file, df_usb):
    conn = sqlite3.connect(DB_PATH)
    df_login.to_sql("login", conn, if_exists="replace", index=False)
    df_file.to_sql("file_access", conn, if_exists="replace", index=False)
    df_usb.to_sql("usb", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ Preprocessed data stored in SQLite DB at {DB_PATH}")

# ------------------------------
# Step 4: Baseline profiling
# ------------------------------
def baseline_profiling(df_login, df_file, df_usb):
    # Simple per-user aggregation
    df_login_summary = df_login.groupby("user_id").agg(
        total_logins=('success', lambda x: x.notna().sum()),
        first_login=('timestamp', 'min'),
        last_login=('timestamp', 'max')
    ).reset_index()

    df_file_summary = df_file.groupby("user_id").agg(
        total_file_access=('file_name', 'count'),
        first_file_access=('timestamp', 'min'),
        last_file_access=('timestamp', 'max')
    ).reset_index()

    df_usb_summary = df_usb.groupby("user_id").agg(
        total_usb_events=('device_id', 'count'),
        first_usb_event=('timestamp', 'min'),
        last_usb_event=('timestamp', 'max')
    ).reset_index()

    # Save baseline summaries
    df_login_summary.to_csv(BASELINE_FILES['login'], index=False)
    df_file_summary.to_csv(BASELINE_FILES['file_access'], index=False)
    df_usb_summary.to_csv(BASELINE_FILES['usb'], index=False)

    print("✅ Baseline summaries saved.")
    return df_login_summary, df_file_summary, df_usb_summary

# ------------------------------
# Step 5: Anomaly Detection (Isolation Forest)
# ------------------------------
from sklearn.ensemble import IsolationForest

def detect_anomalies(df_login_summary, df_file_summary, df_usb_summary):
    # File Access
    clf_file = IsolationForest(contamination=0.05, random_state=42)
    df_file_summary['iso_anomaly'] = clf_file.fit_predict(df_file_summary[['total_file_access']])
    df_file_summary['iso_anomaly'] = df_file_summary['iso_anomaly'].map({1: 0, -1: 1})
    df_file_summary.to_csv(ANOMALY_FILES['file_access'], index=False)

    # Login
    clf_login = IsolationForest(contamination=0.05, random_state=42)
    df_login_summary['iso_anomaly'] = clf_login.fit_predict(df_login_summary[['total_logins']])
    df_login_summary['iso_anomaly'] = df_login_summary['iso_anomaly'].map({1: 0, -1: 1})
    df_login_summary.to_csv(ANOMALY_FILES['login'], index=False)

    # USB
    clf_usb = IsolationForest(contamination=0.05, random_state=42)
    df_usb_summary['iso_anomaly'] = clf_usb.fit_predict(df_usb_summary[['total_usb_events']])
    df_usb_summary['iso_anomaly'] = df_usb_summary['iso_anomaly'].map({1: 0, -1: 1})
    df_usb_summary.to_csv(ANOMALY_FILES['usb'], index=False)

    print("✅ Anomaly detection completed.")
    return df_login_summary, df_file_summary, df_usb_summary

# ------------------------------
# Step 6: Risk Scoring (combine ML + rule-based)
# ------------------------------
def calculate_risk(df_login_summary, df_file_summary, df_usb_summary):
    # Merge all
    df_risk = pd.merge(df_login_summary, df_file_summary, on='user_id', how='outer')
    df_risk = pd.merge(df_risk, df_usb_summary, on='user_id', how='outer')

    # Rule-based flags placeholders (already exist in your current dashboard)
    df_risk['login_spike_flag'] = 0
    df_risk['file_spike_flag'] = 0
    df_risk['usb_spike_flag'] = 0

    # Final risk score = weighted sum of rule-based + ML anomaly
    df_risk['final_risk_score'] = (
        0.4 * df_risk['login_spike_flag'] +
        0.3 * df_risk['file_spike_flag'] +
        0.2 * df_risk['usb_spike_flag'] +
        0.1 * df_risk['iso_anomaly']  # simple weight for ML anomaly
    ) * 100

    # Save final risk scores
    df_risk.to_csv(RISK_OUTPUT_CSV, index=False)

    # Update SQLite DB table
    conn = sqlite3.connect(DB_PATH)
    df_risk.to_sql("risk_data_final", conn, if_exists="replace", index=False)
    conn.close()

    print(f"✅ Final risk scores calculated and saved to CSV + DB ({RISK_OUTPUT_CSV})")
    return df_risk

# ------------------------------
# Main pipeline execution
# ------------------------------
if __name__ == "__main__":
    print("🚀 Starting Insider Risk Pipeline...")

    preprocess_logs()
    df_login, df_file, df_usb = load_preprocessed()
    save_to_db(df_login, df_file, df_usb)
    df_login_summary, df_file_summary, df_usb_summary = baseline_profiling(df_login, df_file, df_usb)
    df_login_anom, df_file_anom, df_usb_anom = detect_anomalies(df_login_summary, df_file_summary, df_usb_summary)
    df_final_risk = calculate_risk(df_login_anom, df_file_anom, df_usb_anom)

    print("✅ Insider Risk Pipeline completed successfully.")
