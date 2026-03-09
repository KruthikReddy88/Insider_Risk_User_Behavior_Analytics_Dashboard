from sklearn.ensemble import IsolationForest

class MLAnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )

    def train(self, X):
        self.model.fit(X)

    def predict(self, X):

        preds = self.model.predict(X)

        results = []

        for p in preds:
            if p == -1:
                results.append(1)
            else:
                results.append(0)

        return results