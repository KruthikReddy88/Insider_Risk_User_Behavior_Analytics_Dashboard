"""
pipeline_api.py

Run:
    python pipeline_api.py

This script:
 - Loads CSV (insider_risk_data_with_scores.csv)
 - Cleans and preprocesses
 - Stores base table risk_data in SQLite
 - Produces baseline profiling (baseline table)
 - Runs IsolationForest -> iso_anomaly + iso_score
 - Computes final_risk_score (weighted combo)
 - Stores risk_data_final in SQLite
 - Starts a Flask API to serve results for dashboards
"""

import os
import sqlite3
from flask import Flask, jsonify, request
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime

# ====== CONFIG ======
CSV_PATH = os.path.join("data", "insider_risk_data_with_scores.csv")  # update if needed
DB_PATH = os.path.join("src", "DB", "insider_risk.db")                     # update if needed
ISOLATION_CONTAMINATION = 0.05   # fraction of points assumed anomalies
RISK_WEIGHT_RULE = 0.7
RISK_WEIGHT_ML = 0.3
ACTIVITY_COLS = ['login_spike_flag', 'file_spike_flag', 'usb_spike_flag']   # features for anomaly detection

# ====== PIPELINE FUNCTIONS ======
def load_csv(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    return df

def clean_and_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure required columns present; create if missing
    for col in ACTIVITY_COLS:
        if col not in df.columns:
            df[col] = 0

    # Fill numeric missing values with 0
    num_cols = [c for c in df.columns if df[c].dtype.kind in 'biufc']  # numeric types
    df[num_cols] = df[num_cols].fillna(0)

    # Convert timestamp columns if they exist
    # detect columns that look like timestamp names
    for ts_col in ['timestamp', 'first_login', 'last_login', 'login_time']:
        if ts_col in df.columns:
            try:
                df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
            except Exception:
                pass

    # Normalize user_id to string
    if 'user_id' in df.columns:
        df['user_id'] = df['user_id'].astype(str)
    else:
        raise KeyError("CSV must contain 'user_id' column")

    # Ensure risk_score column exists and numeric
    if 'risk_score' not in df.columns:
        df['risk_score'] = 0.0
    df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce').fillna(0.0)

    # Ensure hour column if present numeric
    if 'hour' in df.columns:
        df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(-1).astype(int)
    return df

def store_to_sqlite(df: pd.DataFrame, db_path=DB_PATH, table_name='risk_data'):
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def compute_baseline(df: pd.DataFrame) -> pd.DataFrame:
    # baseline per user: mean & std for the activity columns
    baseline = df.groupby('user_id')[ACTIVITY_COLS].agg(['mean', 'std'])
    baseline.columns = ['_'.join(col).strip() for col in baseline.columns.values]
    baseline = baseline.reset_index()
    # fill NaNs in std with 0
    for c in baseline.columns:
        if baseline[c].dtype.kind in 'f' :
            baseline[c] = baseline[c].fillna(0)
    return baseline

def run_isolation_forest(df: pd.DataFrame, contamination=ISOLATION_CONTAMINATION) -> pd.DataFrame:
    # Use activity cols. If data has very low variance use robust handling.
    X = df[ACTIVITY_COLS].copy().astype(float).fillna(0.0).values

    # If all zeros (or nearly constant), IsolationForest can't learn well; return zeros
    if np.all(np.isclose(X, 0)):
        df['iso_score_raw'] = 0.0
        df['iso_anomaly'] = 0
        return df

    iso = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    iso.fit(X)
    # decision_function: higher = normal, lower = anomalous
    df['iso_score_raw'] = iso.decision_function(X)   # continuous score (higher = more normal)
    iso_pred = iso.predict(X)                        # -1 anomaly, 1 normal
    df['iso_anomaly'] = np.where(iso_pred == -1, 1, 0)
    return df

def compute_final_risk(df: pd.DataFrame, w_rule=RISK_WEIGHT_RULE, w_ml=RISK_WEIGHT_ML) -> pd.DataFrame:
    # Normalize iso_anomaly contribution to same scale as risk_score (assuming risk_score in 0-1 or 0-100).
    # We check typical scale: if risk_score mostly <= 1, scale iso_anomaly to 1; if risk_score >1, scale iso_anomaly*100.
    risk_median = df['risk_score'].median() if 'risk_score' in df.columns else 0
    if risk_median <= 1:
        ml_contrib = df['iso_anomaly']  # 0 or 1
    else:
        ml_contrib = df['iso_anomaly'] * 100

    df['final_risk_score'] = w_rule * df['risk_score'] + w_ml * ml_contrib
    # Clip to reasonable range (0, 100)
    df['final_risk_score'] = df['final_risk_score'].clip(lower=0)
    return df

def pipeline_run(csv_path=CSV_PATH, db_path=DB_PATH):
    print(f"[{datetime.now()}] Starting pipeline...")
    df_raw = load_csv(csv_path)
    df = clean_and_preprocess(df_raw)
    store_to_sqlite(df, db_path, table_name='risk_data')

    baseline = compute_baseline(df)
    store_to_sqlite(baseline, db_path, table_name='baseline')

    df = run_isolation_forest(df, contamination=ISOLATION_CONTAMINATION)
    df = compute_final_risk(df, w_rule=RISK_WEIGHT_RULE, w_ml=RISK_WEIGHT_ML)

    # Save final table
    store_to_sqlite(df, db_path, table_name='risk_data_final')
    print(f"[{datetime.now()}] Pipeline finished. Tables written to {db_path}: risk_data, baseline, risk_data_final")
    return True

# ====== API ======
app = Flask(__name__)

def get_connection(db_path=DB_PATH):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Please run the pipeline first.")
    conn = sqlite3.connect(db_path)
    return conn

@app.route("/health", methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

@app.route("/run_pipeline", methods=['POST', 'GET'])
def run_pipeline_endpoint():
    """
    Trigger a re-run of the pipeline.
    GET allowed for convenience. This runs synchronously and returns status when finished.
    """
    try:
        pipeline_run()
        return jsonify({"status": "ok", "msg": "Pipeline run completed", "timestamp": datetime.utcnow().isoformat()})
    except Exception as e:
        return jsonify({"status":"error", "error": str(e)}), 500

@app.route("/top_risks", methods=['GET'])
def top_risks():
    """
    Query params:
      n (optional) : number of top users to return (default 10)
    Returns top users by max final_risk_score
    """
    n = int(request.args.get('n', 10))
    conn = get_connection()
    df = pd.read_sql_query("SELECT user_id, final_risk_score FROM risk_data_final", conn)
    conn.close()
    if df.empty:
        return jsonify({"status":"empty", "msg":"No data in risk_data_final"}), 404
    top = df.groupby('user_id')['final_risk_score'].max().sort_values(ascending=False).head(n).reset_index()
    return jsonify(top.to_dict(orient='records'))

@app.route("/anomalies", methods=['GET'])
def anomalies():
    """
    Returns rows flagged as iso_anomaly == 1. Optional param limit.
    """
    limit = int(request.args.get('limit', 100))
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM risk_data_final WHERE iso_anomaly = 1 ORDER BY final_risk_score DESC LIMIT ?", conn, params=(limit,))
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route("/user/<user_id>", methods=['GET'])
def user_details(user_id):
    """
    Returns all records for a user_id
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM risk_data_final WHERE user_id = ? ORDER BY final_risk_score DESC", conn, params=(user_id,))
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route("/summary", methods=['GET'])
def summary():
    """
    High-level summary metrics useful for dashboard KPI cards.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM risk_data_final", conn)
    conn.close()
    if df.empty:
        return jsonify({"status":"empty"})
    total_users = int(df['user_id'].nunique())
    avg_risk = float(df['final_risk_score'].mean())
    total_anomalies = int(df['iso_anomaly'].sum())
    return jsonify({
        "total_users": total_users,
        "avg_risk": avg_risk,
        "total_anomalies": total_anomalies
    })

# ====== MAIN ======
if __name__ == "__main__":
    # Run pipeline once at startup (comment out if not desired)
    try:
        pipeline_run()
    except Exception as e:
        print("Pipeline initial run produced error:", e)
        print("You can call /run_pipeline after fixing issues.")

    # Start Flask app
    app.run(host="0.0.0.0", port=5001, debug=True)
