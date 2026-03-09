def calculate_risk_score(row):

    risk = 0

    if row["login_spike_flag"] == 1:
        risk += 30

    if row["file_spike_flag"] == 1:
        risk += 40

    if row["usb_spike_flag"] == 1:
        risk += 30

    return risk