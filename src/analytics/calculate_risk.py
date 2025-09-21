import pandas as pd

# Load your CSV
df = pd.read_csv("data/user_risk_scores.csv")

# Define weights
weights = {
    "login_spike_flag": 0.4,
    "file_spike_flag": 0.3,
    "usb_spike_flag": 0.3,
    "anomaly_x": 0.2,
    "anomaly_y": 0.2,
    "anomaly": 0.2
}

# Function to calculate risk score
def calculate_risk(row):
    score = 0
    # Add spike flags
    score += row["login_spike_flag"] * weights["login_spike_flag"]
    score += row["file_spike_flag"] * weights["file_spike_flag"]
    score += row["usb_spike_flag"] * weights["usb_spike_flag"]
    
    # Add anomaly weights
    score += row["anomaly_x"] * weights["anomaly_x"]
    if str(row["anomaly_y"]).lower() == "anomaly":
        score += weights["anomaly_y"]
    if str(row["anomaly"]).lower() == "anomaly":
        score += weights["anomaly"]
        
    return score

# Apply function
df["risk_score"] = df.apply(calculate_risk, axis=1)

# Save updated CSV
df.to_csv("data/insider_risk_data_with_scores.csv", index=False)

print("Risk scores calculated and saved successfully!")
