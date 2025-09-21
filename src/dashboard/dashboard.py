import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Load data
# -------------------------------
risk_df = pd.read_csv('../../data/user_risk_scores.csv')
login_df = pd.read_csv('../../data/anomaly_login_summary.csv')
file_df = pd.read_csv('../../data/anomaly_file_summary.csv')
usb_df = pd.read_csv('../../data/anomaly_usb_summary.csv')

# -------------------------------
# Sidebar filters
# -------------------------------
st.sidebar.title("Filters")
min_risk = st.sidebar.slider("Minimum Risk Score", 0, 100, 0)
max_risk = st.sidebar.slider("Maximum Risk Score", 0, 100, 100)

# Filter users by risk score
filtered_df = risk_df[(risk_df['risk_score'] >= min_risk) & (risk_df['risk_score'] <= max_risk)]

# -------------------------------
# Top risky users
# -------------------------------
st.title("Insider Risk Dashboard")
st.header("Top Risky Users")
top_users = filtered_df.sort_values('risk_score', ascending=False).head(10)
st.dataframe(top_users[['user_id', 'risk_score', 'login_spike_flag', 'file_spike_flag', 'usb_spike_flag']])

# -------------------------------
# Risk Score Distribution
# -------------------------------
st.header("Risk Score Distribution")
fig_dist = px.histogram(filtered_df, x='risk_score', nbins=20, title="Distribution of User Risk Scores")
st.plotly_chart(fig_dist)

# -------------------------------
# Activity Trends (Example: File Access)
# -------------------------------
st.header("Activity Trends")
activity_option = st.selectbox("Select Activity Type", ["Login", "File Access", "USB"])

if activity_option == "Login":
    df_plot = login_df.groupby('user_id')['total_logins'].sum().reset_index()
    fig = px.bar(df_plot.sort_values('total_logins', ascending=False).head(20),
                 x='user_id', y='total_logins', title="Top Users by Login Count")
elif activity_option == "File Access":
    df_plot = file_df.groupby('user_id')['total_file_access'].sum().reset_index()
    fig = px.bar(df_plot.sort_values('total_file_access', ascending=False).head(20),
                 x='user_id', y='total_file_access', title="Top Users by File Access Count")
else:
    df_plot = usb_df.groupby('user_id')['total_usb_events'].sum().reset_index()
    fig = px.bar(df_plot.sort_values('total_usb_events', ascending=False).head(20),
                 x='user_id', y='total_usb_events', title="Top Users by USB Events")

st.plotly_chart(fig)

# -------------------------------
# Download Risk Scores
# -------------------------------
st.header("Download User Risk Scores")
st.download_button("Download CSV", filtered_df.to_csv(index=False), "user_risk_scores_filtered.csv")
