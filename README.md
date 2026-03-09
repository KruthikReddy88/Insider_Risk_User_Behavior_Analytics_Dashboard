# Insider Risk & User Behavior Analytics Dashboard

A full-stack **User Behavior Analytics (UBA) / Insider Threat Detection System** that simulates enterprise user activity, detects anomalous behavior, and visualizes security insights through **two dashboards**:

* **React SOC Dashboard** → Real-time monitoring
* **Streamlit Analytics Dashboard** → Deep behavioral analysis

This project demonstrates how modern **Security Operations Centers (SOC)** monitor insider threats in organizations.

---

# System Overview

The system simulates an organization with **50 users** across multiple departments.
User activities such as **logins, file access, and USB usage** are continuously generated and analyzed for potential insider threats.

Architecture Flow:

```
Simulated Users
      ↓
Log Streamer (Event Generator)
      ↓
Threat Detection Engine
      ↓
SQLite Database
      ↓
Flask Backend APIs
      ↓
React SOC Dashboard (Live Monitoring)
      ↓
Streamlit Analytics Dashboard (Investigation)
```

---

# Key Features

### Real-Time SOC Monitoring (React Dashboard)

* Live **Threat Feed**
* **Top Risk Users**
* **Anomaly Counters**
* **User Activity Timeline**
* **Department Activity Visualization**

Designed to mimic real SOC tools like:

* Microsoft Sentinel
* Splunk
* Exabeam

---

### Behavioral Analytics (Streamlit Dashboard)

The Streamlit dashboard provides deeper analysis:

* Risk distribution analysis
* Department risk insights
* User risk drilldown
* Anomaly category breakdown
* Risk trends over time
* Anomalies per user

This dashboard helps security analysts **investigate suspicious users**.

---

# Threat Detection Logic

Risk scoring follows policy-based rules:

| Behavior                       | Risk Score |
| ------------------------------ | ---------- |
| Normal login during work hours | 0          |
| Normal file access             | 0          |
| USB device connection          | 65         |
| Unauthorized file access       | 70         |
| Mass file download             | 95         |

Only **5–8 users out of 50** exhibit abnormal behavior to simulate realistic insider threats.

---

# Technology Stack

### Backend

* Python
* Flask (API server)
* SQLite (database)
* Pandas / NumPy (data processing)
* Scikit-learn (anomaly detection)

### Dashboards

* React.js (SOC Monitoring UI)
* Streamlit (Analytics dashboard)

### Visualization

* Recharts (React charts)
* Altair (Streamlit charts)

---

# Project Structure

```
Insider_Risk_User_Behavior_Analytics_Dashboard
│
├── backend
│   ├── api
│   ├── analytics
│   └── ingestion
│
├── frontend
│   └── soc-dashboard
│
├── src
│   ├── DB
│   └── dashboard
│
├── requirements.txt
├── README.md
└── reset_db.py
```

---

# Installation

Clone the repository:

```
git clone https://github.com/your-username/insider-risk-dashboard.git
cd insider-risk-dashboard
```

Install Python dependencies:

```
pip install -r requirements.txt
```

Install frontend dependencies:

```
cd frontend/soc-dashboard
npm install
```

---

# Running the Project

Start each component in separate terminals.

### 1. Start the backend API

```
python backend/app.py
```

### 2. Start the React SOC dashboard

```
cd frontend/soc-dashboard
npm start
```

### 3. Start the Streamlit analytics dashboard

```
streamlit run src/dashboard/insider_risk_dashboard.py
```

### 4. Start the log streamer (simulation engine)

```
python -m backend.ingestion.log_streamer
```

The dashboards will now begin showing **live simulated insider activity**.

---

# Reset Database (Optional)

To clear all events before a demo:

```
python reset_db.py
```

---

# Example SOC Alerts

```
⚠ user18 mass file download → risk 95
⚠ user7 USB device usage → risk 65
⚠ user12 abnormal login time → risk 70
```

These alerts appear in the **React SOC dashboard** in real time.

---

# Academic Use

This project was developed as a **B.Tech Capstone Project** to demonstrate:

* Insider threat detection
* User behavior analytics
* SOC monitoring dashboards
* Full-stack cybersecurity system design

---

# Future Improvements

Potential extensions include:

* Real log ingestion (SIEM integration)
* Kafka-based event streaming
* Advanced ML anomaly detection
* Role-based access control
* Alert prioritization engine

---

# Author

Kruthik Reddy
Cyber Security & Web Application Developer

Y Chaitanya Sai
Cyber Security Analyst

P Prasanth
Cyber Secuirty Enginner