import sqlite3
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from backend.api.threat_feed import threat_feed

app = Flask(__name__)
CORS(app)

DB_PATH = "src/DB/insider_risk.db"

# Register blueprint
app.register_blueprint(threat_feed)

# -----------------------------
# API: Full Risk Data
# -----------------------------
@app.route("/api/risk-data")
def risk_data():

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM risk_data_final", conn)

    return jsonify(df.to_dict(orient="records"))


# -----------------------------
# API: Dashboard Metrics
# -----------------------------
@app.route("/api/dashboard")
def dashboard_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM risk_data_final", conn)

    conn.close()

    total_users = df["user_id"].nunique()

    high_risk = len(df[df["final_risk_score"] > 70])

    avg_risk = df["final_risk_score"].mean()

    top_users = df.sort_values(
        "final_risk_score",
        ascending=False
    ).head(5)

    return jsonify({
        "total_users": int(total_users),
        "high_risk_users": int(high_risk),
        "avg_risk_score": round(avg_risk,2),
        "top_users": top_users[["user_id","final_risk_score"]].to_dict("records")
    })

@app.route("/api/top-users")
def top_users():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT user_id, department, MAX(final_risk_score) as risk
        FROM risk_data_final
        GROUP BY user_id
        ORDER BY risk DESC
        LIMIT 10
    """, conn)

    conn.close()

    return jsonify(df.to_dict(orient="records"))

@app.route("/api/threat-feed")
def threat_feed_api():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT user_id, department, final_risk_score
        FROM risk_data_final
        WHERE final_risk_score > 80
        ORDER BY final_risk_score DESC
        LIMIT 10
    """, conn)

    conn.close()

    return jsonify(df.to_dict(orient="records"))

@app.route("/api/anomaly-summary")
def anomaly_summary():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT
        SUM(usb_spike_flag) as usb_spikes,
        SUM(file_spike_flag) as file_spikes,
        SUM(login_spike_flag) as login_spikes
        FROM risk_data_final
    """, conn)

    conn.close()

    return jsonify(df.to_dict(orient="records")[0])

if __name__ == "__main__":
    app.run(debug=True, port=5000)