import pandas as pd

# ----------------- Preprocess Login Events -----------------
df_login = pd.read_csv('data/raw_login.csv')
df_login['timestamp'] = pd.to_datetime(df_login['timestamp'])
df_login['user_id'].fillna('unknown', inplace=True)
df_login.to_csv('data/preprocessed_login.csv', index=False)

# ----------------- Preprocess File-access Events -----------------
df_file = pd.read_csv('data/raw_file_access.csv')
df_file['timestamp'] = pd.to_datetime(df_file['timestamp'])
df_file['user_id'].fillna('unknown', inplace=True)
df_file['file_name'].fillna('unknown', inplace=True)
df_file['action'].fillna('unknown', inplace=True)
df_file.to_csv('data/preprocessed_file_access.csv', index=False)

# ----------------- Preprocess USB Events -----------------
df_usb = pd.read_csv('data/raw_usb.csv')
df_usb['timestamp'] = pd.to_datetime(df_usb['timestamp'])
df_usb['user_id'].fillna('unknown', inplace=True)
df_usb['device_id'].fillna('unknown', inplace=True)
df_usb['action'].fillna('unknown', inplace=True)
df_usb.to_csv('data/preprocessed_usb.csv', index=False)

print("Preprocessing completed. Preprocessed files saved in 'data/' folder.")
