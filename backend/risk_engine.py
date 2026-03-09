from datetime import datetime

NORMAL_ACTIONS = [
    "login",
    "logout",
    "file_access"
]

def calculate_risk(log):

    action = log["action"]

    score = 0

    if action == "usb_insert":
        score += 40

    elif action == "file_download":
        score += 25

    elif action == "privilege_escalation":
        score += 60

    elif action in NORMAL_ACTIONS:
        score -= 5   # normal behavior reduces risk slightly

    return score


def decay_risk(current_score):

    DECAY_RATE = 2

    if current_score > 0:
        current_score -= DECAY_RATE

    return max(current_score, 0)