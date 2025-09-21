import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# ------------------------------
# Streamlit App Setup
# ------------------------------
st.set_page_config(page_title="Insider Risk Dashboard", layout="wide")
st.title("Insider Risk & User Behavior Analytics Dashboard")

# ------------------------------
# Load Data from SQLite
# ------------------------------
# Change this line
conn = sqlite3.connect("C:/Users/Admin/OneDrive/Desktop/Insider_Risk_User_Behavior_Analytics_Dashboard/src/DB/insider_risk.db")
df = pd.read_sql("SELECT * FROM risk_data_final", conn)
conn.close()

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("Filters")
users = df['user_id'].unique()
selected_user = st.sidebar.multiselect("Select User(s)", users, default=users)

if 'department' in df.columns:
    departments = df['department'].unique()
    selected_dept = st.sidebar.multiselect("Select Department(s)", departments, default=departments)
    df = df[df['department'].isin(selected_dept)]

df = df[df['user_id'].isin(selected_user)]

# ------------------------------
# Key Metrics
# ------------------------------
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Users", df['user_id'].nunique())
col2.metric("Average Risk Score", round(df['final_risk_score'].mean(), 2))
col3.metric("Total Anomalies Detected", df['iso_anomaly'].sum())

# ------------------------------
# Top Risk Users
# ------------------------------
st.subheader("Top Risk Users")
top_users = df.groupby('user_id')['final_risk_score'].max().sort_values(ascending=False).reset_index()
st.dataframe(top_users.head(10))

# ------------------------------
# Risk Distribution Chart
# ------------------------------
st.subheader("Risk Distribution")
risk_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('final_risk_score', bin=alt.Bin(maxbins=20), title='Risk Score'),
    y='count()',
    tooltip=['count()']
).properties(width=700, height=400)

st.altair_chart(risk_chart)

# ------------------------------
# Risk by Department (if available)
# ------------------------------
if 'department' in df.columns:
    st.subheader("Risk by Department")
    dept_chart = alt.Chart(df).mark_bar().encode(
        x='department',
        y='mean(final_risk_score)',
        color='department',
        tooltip=['department', 'mean(final_risk_score)']
    ).properties(width=700, height=400)
    st.altair_chart(dept_chart)

# ------------------------------
# Time-of-Day Risk Trends
# ------------------------------
if 'hour' in df.columns:
    st.subheader("Time-of-Day Risk Trends")
    time_chart = alt.Chart(df).mark_line(point=True).encode(
        x='hour:O',
        y='mean(final_risk_score)',
        tooltip=['hour', 'mean(final_risk_score)']
    ).properties(width=700, height=400)
    st.altair_chart(time_chart)

# ------------------------------
# Anomalies Table
# ------------------------------
st.subheader("Anomalies Detected")
anomaly_df = df[df['iso_anomaly'] == 1]
st.dataframe(anomaly_df[['user_id', 'hour', 'login_spike_flag', 'file_spike_flag', 'usb_spike_flag', 'final_risk_score']])
