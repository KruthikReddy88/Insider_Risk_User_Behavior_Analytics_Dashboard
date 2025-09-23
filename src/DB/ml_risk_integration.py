import pandas as pd
import sqlite3

# ------------------------------
# Load baseline summaries
# ------------------------------
df_file = pd.read_csv('data/baseline_file_summary.csv')
df_login = pd.read_csv('data/baseline_login_summary.csv')
df_usb = pd.read_csv('data/baseline_usb_summary.csv')

# ------------------------------
# Aggregate per user
# ------------------------------
agg_file = df_file.groupby('user_id').agg(
    total_file_access=pd.NamedAgg(column='total_file_access', aggfunc='sum')
).reset_index()

agg_login = df_login.groupby('user_id').agg(
    total_logins=pd.NamedAgg(column='total_logins', aggfunc='sum')
).reset_index()

agg_usb = df_usb.groupby('user_id').agg(
    total_usb_events=pd.NamedAgg(column='total_usb_events', aggfunc='sum')
).reset_index()

# ------------------------------
# Merge all features
# ------------------------------
df_agg = agg_file.merge(agg_login, on='user_id', how='outer')
df_agg = df_agg.merge(agg_usb, on='user_id', how='outer')

# Fill NaNs with 0
df_agg = df_agg.fillna(0)

# ------------------------------
# Calculate combined risk score (example: simple sum normalized)
# ------------------------------
df_agg['final_risk_score'] = (
    df_agg['total_file_access'] * 0.4 +
    df_agg['total_logins'] * 0.3 +
    df_agg['total_usb_events'] * 0.3
)

# Normalize to 0–1
df_agg['final_risk_score'] = df_agg['final_risk_score'] / df_agg['final_risk_score'].max()

# ------------------------------
# Save to SQLite
# ------------------------------
conn = sqlite3.connect('src/DB/insider_risk.db')
df_agg.to_sql('risk_data_final', conn, if_exists='replace', index=False)
conn.close()

print("✅ ML risk integration completed and saved to SQLite.")
