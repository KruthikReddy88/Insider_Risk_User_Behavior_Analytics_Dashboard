import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

MODEL_PATH = "./models/anomaly_model.pkl"

def train():

    data = []

    # simulate normal user behaviour
    for _ in range(300):

        login_count = np.random.randint(3,8)
        downloads = np.random.randint(0,4)
        privilege_actions = np.random.randint(0,1)
        risk_score = np.random.randint(0,30)

        data.append([
            login_count,
            downloads,
            privilege_actions,
            risk_score
        ])

    data = np.array(data)

    model = IsolationForest(contamination=0.05)

    model.fit(data)

    joblib.dump(model,MODEL_PATH)

    print("Behavior anomaly model trained")


def predict(features):

    model = joblib.load(MODEL_PATH)

    result = model.predict([features])

    return result[0] == -1


if __name__ == "__main__":
    train()