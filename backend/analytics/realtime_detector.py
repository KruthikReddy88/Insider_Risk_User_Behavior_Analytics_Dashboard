import json

def detect_threat(event):

    risk = 0
    alerts = []

    # Suspicious login hour
    if event["login_hour"] < 6:
        risk += 20
        alerts.append("Suspicious login time")

    # File exfiltration
    if event["files_accessed"] > 150:
        risk += 40
        alerts.append("Large file access spike")

    # USB activity
    if event["usb_connected"] == 1:
        risk += 30
        alerts.append("USB device connected")

    return risk, alerts