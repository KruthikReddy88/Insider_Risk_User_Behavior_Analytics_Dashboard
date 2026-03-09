from flask import Blueprint, jsonify
import sqlite3
import pandas as pd

threat_feed = Blueprint("threat_feed", __name__)

DB_PATH = "src/DB/insider_risk.db"

@threat_feed.route("/api/threat-feed")
def get_threat_feed():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT user_id as user,
               final_risk_score as risk_score
        FROM risk_data_final
        WHERE final_risk_score >= 65
        ORDER BY final_risk_score DESC
        LIMIT 10
    """, conn)

    conn.close()

    alerts = []

    for _, row in df.iterrows():

        alerts.append({
            "user": row["user"],
            "risk_score": row["risk_score"],
            "event": "Suspicious activity detected"
        })

    return jsonify(alerts)