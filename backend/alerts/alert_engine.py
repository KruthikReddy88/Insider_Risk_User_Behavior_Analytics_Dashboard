from backend.alerts.alert_prioritizer import get_alert_level

def generate_alert(user, risk_score):

    severity = get_alert_level(risk_score)

    return {
        "user": user,
        "risk_score": risk_score,
        "severity": severity
    }