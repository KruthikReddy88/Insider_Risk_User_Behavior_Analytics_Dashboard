import pandas as pd
from sklearn.ensemble import IsolationForest


class AnomalyDetector:

    def __init__(self):

        self.model = IsolationForest(
            contamination=0.02,
            random_state=42
        )

        self.trained = False


    def train(self, data):

        df = pd.DataFrame(data)

        features = df[[
            "login_hour",
            "files_accessed",
            "usb_size_mb"
        ]]

        self.model.fit(features)

        self.trained = True


    def predict(self, event):

        if not self.trained:
            return 1, 0

        df = pd.DataFrame([event])

        features = df[[
            "login_hour",
            "files_accessed",
            "usb_size_mb"
        ]]

        prediction = self.model.predict(features)[0]

        score = self.model.decision_function(features)[0]

        return prediction, score