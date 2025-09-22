import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# ------------------------------
# Streamlit App Setup
# ------------------------------
st.set_page_config(page_title="Insider Risk Dashboard", layout="wide")
st.title("🔐 Insider Risk & User Behavior Analytics Dashboard")

# ------------------------------
# Load Data from SQLite
# ------------------------------
DB_PATH = "C:/Users/Admin/OneDrive/Desktop/Insider_Risk_User_Behavior_Analytics_Dashboard/src/DB/insider_risk.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM risk_data_final", conn)
    conn.close()
    return df

df = load_data()

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("Filters")

# Users
users = df['user_id'].unique()
selected_user = st.sidebar.multiselect("Select User(s)", users, default=users)

# Departments (if available)
if 'department' in df.columns:
    departments = df['department'].unique()
    selected_dept = st.sidebar.multiselect("Select Department(s)", departments, default=departments)
    df = df[df['department'].isin(selected_dept)]

# Apply user filter
df = df[df['user_id'].isin(selected_user)]

# ------------------------------
# Key Metrics
# ------------------------------
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", df['user_id'].nunique())
col2.metric("Average Risk Score", round(df['final_risk_score'].mean(), 2))
col3.metric("Total Anomalies Detected", df['iso_anomaly'].sum())

# ------------------------------
# Top Risk Users
# ------------------------------
st.subheader("🔥 Top Risk Users")
top_users = df.groupby('user_id')['final_risk_score'].max().sort_values(ascending=False).reset_index()
st.dataframe(top_users.head(10))

# ------------------------------
# High-Risk Alerts
# ------------------------------
st.subheader("🚨 High-Risk Alerts (Score > 80)")
high_risk_df = df[df['final_risk_score'] > 80].copy()
if 'department' not in high_risk_df.columns:
    high_risk_df['department'] = 'N/A'
st.dataframe(high_risk_df[['user_id', 'department', 'final_risk_score']])

# ------------------------------
# Top Risk Files
# ------------------------------
st.subheader("📂 Top Risk Files")
if 'file_name' in df.columns:
    top_files = df.groupby('file_name')['final_risk_score'].max().sort_values(ascending=False).reset_index()
    st.dataframe(top_files.head(10))
else:
    st.info("No file data available yet.")

# ------------------------------
# Top Risk USB Devices
# ------------------------------
st.subheader("💽 Top Risk USB Devices")
if 'device_id' in df.columns:
    top_usb = df.groupby('device_id')['final_risk_score'].max().sort_values(ascending=False).reset_index()
    st.dataframe(top_usb.head(10))
else:
    st.info("No USB device data available yet.")

# ------------------------------
# Ensure Department Column Exists
# ------------------------------
if 'department' not in df.columns:
    # Simple placeholder mapping (you can adjust)
    user_dept_map = {
        'user1': 'HR',
        'user2': 'Finance',
        'user3': 'IT',
        'user4': 'Legal'
    }
    df['department'] = df['user_id'].map(user_dept_map)

# ------------------------------
# Risk Distribution
# ------------------------------
st.subheader("📈 Risk Distribution")
risk_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('final_risk_score', bin=alt.Bin(maxbins=20), title='Risk Score'),
    y='count()',
    tooltip=['count()']
).properties(width=700, height=400)
st.altair_chart(risk_chart, use_container_width=True)

# ------------------------------
# Risk by Department
# ------------------------------
if 'department' in df.columns:
    st.subheader("🏢 Risk by Department")
    dept_chart = alt.Chart(df).mark_bar().encode(
        x='department',
        y='mean(final_risk_score)',
        color='department',
        tooltip=['department', 'mean(final_risk_score)']
    ).properties(width=700, height=400)
    st.altair_chart(dept_chart, use_container_width=True)

    dept_summary = df.groupby('department').agg(
        avg_risk=('final_risk_score', 'mean'),
        anomalies=('iso_anomaly', 'sum')
    ).reset_index()
    st.dataframe(dept_summary)

# ------------------------------
# Time-of-Day Risk Trends
# ------------------------------
if 'hour' in df.columns:
    st.subheader("🕒 Time-of-Day Risk Trends")
    time_chart = alt.Chart(df).mark_line(point=True).encode(
        x='hour:O',
        y='mean(final_risk_score)',
        tooltip=['hour', 'mean(final_risk_score)']
    ).properties(width=700, height=400)
    st.altair_chart(time_chart, use_container_width=True)

# ------------------------------
# Heatmap (Day vs Hour)
# ------------------------------
if 'day_of_week' in df.columns and 'hour' in df.columns:
    st.subheader("🌡 Risk Heatmap (Day vs Hour)")
    heatmap = alt.Chart(df).mark_rect().encode(
        x='hour:O',
        y='day_of_week:O',
        color='mean(final_risk_score):Q',
        tooltip=['hour', 'day_of_week', 'mean(final_risk_score)']
    )
    st.altair_chart(heatmap, use_container_width=True)

# ------------------------------
# Anomaly Categories Breakdown
# ------------------------------
st.subheader("🛑 Anomaly Categories Breakdown")
anomaly_counts = {
    "USB Spikes": int(df['usb_spike_flag'].sum()),
    "File Spikes": int(df['file_spike_flag'].sum()),
    "Login Spikes": int(df['login_spike_flag'].sum())
}
st.bar_chart(anomaly_counts)

# ------------------------------
# User Drilldown
# ------------------------------
st.subheader("👤 User Risk Profile Drilldown")
selected_profile = st.selectbox("Select a User", df['user_id'].unique())
user_data = df[df['user_id'] == selected_profile]

st.write(f"**Department:** {user_data['department'].iloc[0] if 'department' in user_data else 'N/A'}")
st.write(f"**Average Risk Score:** {round(user_data['final_risk_score'].mean(), 2)}")

if 'hour' in user_data.columns:
    profile_chart = alt.Chart(user_data).mark_line(point=True).encode(
        x='hour:O',
        y='final_risk_score',
        tooltip=['hour', 'final_risk_score']
    )
    st.altair_chart(profile_chart, use_container_width=True)

# ------------------------------
# Risk Trends per Department over Time
# ------------------------------
if 'hour' in df.columns and 'department' in df.columns:
    st.subheader("📊 Risk Trends per Department (Hour-wise)")
    trend_chart = alt.Chart(df).mark_line(point=True).encode(
        x='hour:O',
        y='mean(final_risk_score)',
        color='department',
        tooltip=['department', 'hour', 'mean(final_risk_score)']
    ).properties(width=700, height=400)
    st.altair_chart(trend_chart, use_container_width=True)

# ------------------------------
# Combined Anomaly Counts per User
# ------------------------------
st.subheader("📊 Anomalies per User")
anomaly_user_df = df.groupby('user_id')[['usb_spike_flag','file_spike_flag','login_spike_flag']].sum().reset_index()
anomaly_user_df = anomaly_user_df.melt(id_vars='user_id', var_name='Anomaly_Type', value_name='Count')

anomaly_user_chart = alt.Chart(anomaly_user_df).mark_bar().encode(
    x='user_id',
    y='Count',
    color='Anomaly_Type',
    tooltip=['user_id', 'Anomaly_Type', 'Count']
).properties(width=700, height=400)
st.altair_chart(anomaly_user_chart, use_container_width=True)

# ------------------------------
# Anomalies Table
# ------------------------------
st.subheader("📋 Anomalies Detected")
anomaly_df = df[df['iso_anomaly'] == 1]
st.dataframe(anomaly_df[['user_id', 'hour', 'login_spike_flag', 'file_spike_flag', 'usb_spike_flag', 'final_risk_score']])

# ------------------------------
# Download Option
# ------------------------------
st.download_button(
    label="⬇️ Download Risk Data (CSV)",
    data=df.to_csv(index=False),
    file_name="risk_dashboard_export.csv",
    mime="text/csv"
)
