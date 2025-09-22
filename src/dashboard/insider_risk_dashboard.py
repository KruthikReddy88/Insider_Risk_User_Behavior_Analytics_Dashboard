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

# Departments
if 'department' in df.columns:
    departments = df['department'].unique()
    selected_dept = st.sidebar.multiselect("Select Department(s)", departments, default=departments)
    df = df[df['department'].isin(selected_dept)]

# Apply filters
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

profile_chart = alt.Chart(user_data).mark_line(point=True).encode(
    x='hour:O',
    y='final_risk_score',
    tooltip=['hour', 'final_risk_score']
)
st.altair_chart(profile_chart, use_container_width=True)

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
