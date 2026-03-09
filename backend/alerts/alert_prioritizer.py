def get_alert_level(score):

    if score >= 85:
        return "CRITICAL"

    elif score >= 70:
        return "HIGH"

    elif score >= 50:
        return "MEDIUM"

    else:
        return "LOW"