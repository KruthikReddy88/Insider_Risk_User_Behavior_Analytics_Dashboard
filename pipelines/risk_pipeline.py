import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from backend.analytics.feature_extractor import extract_features
from backend.analytics.ml_anomaly_detector import MLAnomalyDetector
from backend.analytics.risk_engine import calculate_risk_score
from backend.alerts.alert_engine import generate_alert


def run_pipeline():

    df = pd.read_csv("data/user_risk_scores.csv")

    features = extract_features(df)

    model = MLAnomalyDetector()

    model.train(features)

    df["ml_anomaly"] = model.predict(features)

    alerts = []

    for _, row in df.iterrows():

        risk = calculate_risk_score(row)

        if risk >= 50:

            alert = generate_alert(row["user_id"], risk)

            alerts.append(alert)

    return alerts


if __name__ == "__main__":

    alerts = run_pipeline()

    for a in alerts:
        print(a)