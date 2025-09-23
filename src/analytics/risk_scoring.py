# -------------------------------
# Rule-based anomaly flags (robust)
# -------------------------------

TOP_N_SPIKES = 3  # fallback: flag top N users if thresholds are too strict

def compute_spike_flag(series, multiplier=1.0, top_n=TOP_N_SPIKES):
    mean = series.mean()
    std = series.std()
    threshold = mean + multiplier * std
    flags = (series > threshold).astype(int)

    # If all zeros (no spikes detected), flag top N values
    if flags.sum() == 0:
        top_indices = series.nlargest(top_n).index
        flags = pd.Series(0, index=series.index)
        flags.loc[top_indices] = 1
    return flags

# Login anomalies
LOGIN_SPIKE_MULTIPLIER = 1.0
df['login_spike_flag'] = compute_spike_flag(df[login_col], LOGIN_SPIKE_MULTIPLIER)

# File access anomalies
FILE_SPIKE_MULTIPLIER = 1.0
df['file_spike_flag'] = compute_spike_flag(df[file_col], FILE_SPIKE_MULTIPLIER)

# USB anomalies
USB_SPIKE_MULTIPLIER = 1.0
df['usb_spike_flag'] = compute_spike_flag(df[usb_col], USB_SPIKE_MULTIPLIER)

# -------------------------------
# Risk Score Calculation
# -------------------------------
# Weighted sum of anomaly flags
df['risk_score'] = df['login_spike_flag'] * 0.4 + \
                   df['file_spike_flag'] * 0.4 + \
                   df['usb_spike_flag'] * 0.2

# Normalize risk score to 0-100
if df['risk_score'].max() > 0:
    df['risk_score'] = df['risk_score'] / df['risk_score'].max() * 100
else:
    df['risk_score'] = 0

# -------------------------------
# Save risk scores
# -------------------------------
df.to_csv('data/user_risk_scores.csv', index=False)
print("Risk scoring completed. Results saved to user_risk_scores.csv")
