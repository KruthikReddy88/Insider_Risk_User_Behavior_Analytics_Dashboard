import pandas as pd
import streamlit as st
import plotly.express as px

# Load risk scores
df = pd.read_csv('data/insider_risk_data_with_scores.csv')  # Updated file

st.set_page_config(page_title="Insider Risk Dashboard", layout="wide")
st.title("Insider Risk User Behavior Analytics Dashboard")

# -------------------------------
# Assign Risk Levels
# -------------------------------
def categorize_risk(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

df['risk_level'] = df['risk_score'].apply(categorize_risk)

# -------------------------------
# Overall Risk Summary
# -------------------------------
st.header("Overall Risk Summary")
avg_risk = df['risk_score'].mean()
max_risk = df['risk_score'].max()
st.metric("Average Risk Score", f"{avg_risk:.2f}")
st.metric("Maximum Risk Score", f"{max_risk:.2f}")

# -------------------------------
# Top High-Risk Users
# -------------------------------
st.header("Top High-Risk Users")
top_users = df.sort_values(by='risk_score', ascending=False).head(10)
st.dataframe(top_users[['user_id', 'risk_score', 'risk_level', 'login_spike_flag', 'file_spike_flag', 'usb_spike_flag']])

# -------------------------------
# Risk Distribution with Colors
# -------------------------------
st.header("Risk Distribution")
fig_dist = px.histogram(df, x='risk_score', color='risk_level',
                        color_discrete_map={'Low':'green', 'Medium':'orange', 'High':'red'},
                        nbins=20, title="Distribution of User Risk Scores")
st.plotly_chart(fig_dist, use_container_width=True)

# -------------------------------
# Anomaly Breakdown
# -------------------------------
st.header("Anomaly Breakdown")
anomaly_counts = df[['login_spike_flag', 'file_spike_flag', 'usb_spike_flag']].sum().reset_index()
anomaly_counts.columns = ['Anomaly Type', 'Count']
fig_bar = px.bar(anomaly_counts, x='Anomaly Type', y='Count', title="Count of Each Anomaly Type", color='Count',
                 color_continuous_scale='Viridis')
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# Filter by Risk Score
# -------------------------------
st.header("Filter Users by Risk Score")
risk_threshold = st.slider("Minimum Risk Score", 0, 100, 50)
filtered_df = df[df['risk_score'] >= risk_threshold]
st.dataframe(filtered_df[['user_id', 'risk_score', 'risk_level']])
