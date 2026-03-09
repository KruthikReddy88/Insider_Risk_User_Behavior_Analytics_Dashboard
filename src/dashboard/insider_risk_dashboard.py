import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# ------------------------------
# Page Setup
# ------------------------------
st.set_page_config(page_title="Insider Risk Dashboard", layout="wide")

st.title("🔐 Insider Risk & User Behavior Analytics Dashboard")

DB_PATH = "src/DB/insider_risk.db"

# ------------------------------
# Refresh Button
# ------------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data(ttl=5)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM risk_data_final", conn)

    conn.close()

    return df


df = load_data()

st.write("Total Records Loaded:", len(df))

# ------------------------------
# Handle Missing Columns
# ------------------------------
expected_columns = [
    "usb_spike_flag",
    "file_spike_flag",
    "login_spike_flag",
    "file_name",
    "device_id",
    "department"
]

for col in expected_columns:
    if col not in df.columns:
        df[col] = None

df.fillna({
    "usb_spike_flag":0,
    "file_spike_flag":0,
    "login_spike_flag":0
}, inplace=True)

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("Filters")

users = sorted(df["user_id"].unique())

selected_users = st.sidebar.multiselect(
    "Select User(s)",
    users,
    default=users
)

if "department" in df.columns:

    departments = sorted(df["department"].dropna().unique())

    selected_dept = st.sidebar.multiselect(
        "Select Department(s)",
        departments,
        default=departments
    )

    df = df[df["department"].isin(selected_dept)]

df = df[df["user_id"].isin(selected_users)]

# ------------------------------
# Key Metrics
# ------------------------------
st.subheader("📊 Key Metrics")

col1,col2,col3 = st.columns(3)

col1.metric(
    "Total Users",
    df["user_id"].nunique()
)

col2.metric(
    "Average Risk Score",
    round(df["final_risk_score"].mean(),2)
)

col3.metric(
    "Total Anomalies Detected",
    int(
        df["usb_spike_flag"].sum()
        + df["file_spike_flag"].sum()
        + df["login_spike_flag"].sum()
    )
)

# ------------------------------
# Top Risk Users
# ------------------------------
st.subheader("🔥 Top Risk Users")

top_users = (
    df.groupby("user_id")["final_risk_score"]
    .max()
    .sort_values(ascending=False)
    .reset_index()
)

st.dataframe(top_users.head(10))

# ------------------------------
# High Risk Alerts
# ------------------------------
st.subheader("🚨 High-Risk Alerts (Score > 80)")

high_risk = df[df["final_risk_score"] > 80]

if "department" not in high_risk.columns:
    high_risk["department"] = "Unknown"

st.dataframe(
    high_risk[["user_id","department","final_risk_score"]]
)

# ------------------------------
# Top Risk Files
# ------------------------------
st.subheader("📂 Top Risk Files")

if df["file_name"].notnull().sum() > 0:

    top_files = (
        df.groupby("file_name")["final_risk_score"]
        .max()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(top_files.head(10))

else:

    st.info("No file data available yet.")

# ------------------------------
# Top Risk USB Devices
# ------------------------------
st.subheader("💽 Top Risk USB Devices")

if df["device_id"].notnull().sum() > 0:

    top_usb = (
        df.groupby("device_id")["final_risk_score"]
        .max()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(top_usb.head(10))

else:

    st.info("No USB device data available yet.")

# ------------------------------
# Risk Distribution
# ------------------------------
st.subheader("📈 Risk Distribution")

risk_chart = alt.Chart(df).mark_bar().encode(

    x=alt.X(
        "final_risk_score",
        bin=alt.Bin(maxbins=20),
        title="Risk Score"
    ),

    y="count()",

    tooltip=["count()"]

).properties(height=400)

st.altair_chart(risk_chart, use_container_width=True)

# ------------------------------
# Risk by Department
# ------------------------------
if "department" in df.columns:

    st.subheader("🏢 Risk by Department")

    dept_chart = alt.Chart(df).mark_bar().encode(

        x="department",

        y="mean(final_risk_score)",

        color="department",

        tooltip=["department","mean(final_risk_score)"]

    ).properties(height=400)

    st.altair_chart(dept_chart, use_container_width=True)

# ------------------------------
# Time-of-Day Risk Trends
# ------------------------------
if "hour" in df.columns:

    st.subheader("🕒 Time-of-Day Risk Trends")

    time_chart = alt.Chart(df).mark_line(point=True).encode(

        x="hour:O",

        y="mean(final_risk_score)",

        tooltip=["hour","mean(final_risk_score)"]

    ).properties(height=400)

    st.altair_chart(time_chart, use_container_width=True)

# ------------------------------
# Anomaly Breakdown
# ------------------------------
st.subheader("🛑 Anomaly Categories Breakdown")

anomaly_counts = {

    "USB Spikes": int(df["usb_spike_flag"].sum()),
    "File Spikes": int(df["file_spike_flag"].sum()),
    "Login Spikes": int(df["login_spike_flag"].sum())

}

st.bar_chart(anomaly_counts)

# ------------------------------
# User Drilldown
# ------------------------------
st.subheader("👤 User Risk Profile Drilldown")

selected_user = st.selectbox(
    "Select a User",
    df["user_id"].unique()
)

user_data = df[df["user_id"] == selected_user]

dept = (
    user_data["department"].iloc[0]
    if "department" in user_data
    else "Unknown"
)

st.write("Department:", dept)

st.write(
    "Average Risk Score:",
    round(user_data["final_risk_score"].mean(),2)
)

if "hour" in user_data.columns:

    profile_chart = alt.Chart(user_data).mark_line(point=True).encode(

        x="hour:O",

        y="final_risk_score",

        tooltip=["hour","final_risk_score"]

    )

    st.altair_chart(profile_chart, use_container_width=True)

# ------------------------------
# Risk Trends per Department
# ------------------------------
if "department" in df.columns and "hour" in df.columns:

    st.subheader("📊 Risk Trends per Department (Hour-wise)")

    trend_chart = alt.Chart(df).mark_line(point=True).encode(

        x="hour:O",

        y="mean(final_risk_score)",

        color="department",

        tooltip=["department","hour","mean(final_risk_score)"]

    ).properties(height=400)

    st.altair_chart(trend_chart, use_container_width=True)

# ------------------------------
# Anomalies per User
# ------------------------------
st.subheader("📊 Anomalies per User")

anomaly_user_df = (
    df.groupby("user_id")[
        ["usb_spike_flag","file_spike_flag","login_spike_flag"]
    ]
    .sum()
    .reset_index()
)

anomaly_user_df = anomaly_user_df.melt(

    id_vars="user_id",
    var_name="Anomaly_Type",
    value_name="Count"
)

chart = alt.Chart(anomaly_user_df).mark_bar().encode(

    x="user_id",

    y="Count",

    color="Anomaly_Type",

    tooltip=["user_id","Anomaly_Type","Count"]

).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# ------------------------------
# Anomalies Table
# ------------------------------
st.subheader("📋 Anomalies Detected")

anomaly_df = df[
    (df["usb_spike_flag"] == 1)
    | (df["file_spike_flag"] == 1)
    | (df["login_spike_flag"] == 1)
]

st.dataframe(

    anomaly_df[
        [
            "user_id",
            "hour",
            "usb_spike_flag",
            "file_spike_flag",
            "login_spike_flag",
            "final_risk_score"
        ]
    ]
)

# ------------------------------
# Download Data
# ------------------------------
st.download_button(

    label="⬇️ Download Risk Data",

    data=df.to_csv(index=False),

    file_name="insider_risk_data.csv",

    mime="text/csv"
)