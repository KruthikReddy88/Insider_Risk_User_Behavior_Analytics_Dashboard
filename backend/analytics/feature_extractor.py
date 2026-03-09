import pandas as pd

def extract_features(df):

    features = pd.DataFrame()

    features["total_logins"] = df["total_logins"]
    features["total_file_access"] = df["total_file_access"]
    features["total_usb_events"] = df["total_usb_events"]

    return features