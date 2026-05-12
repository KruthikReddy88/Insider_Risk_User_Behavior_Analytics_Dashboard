@echo off

echo Starting Insider Risk & User Behavior Analytics Dashboard...

REM ---------------------------------------------------
REM ACTIVATE PROJECT ROOT
REM ---------------------------------------------------

cd /d %~dp0

REM ---------------------------------------------------
REM START LOG STREAMER
REM ---------------------------------------------------

start cmd /k "call .venv\Scripts\activate && python -m backend.ingestion.log_streamer"

REM ---------------------------------------------------
REM START FLASK BACKEND
REM ---------------------------------------------------

start cmd /k "call .venv\Scripts\activate && python -m backend.app"

REM ---------------------------------------------------
REM START STREAMLIT DASHBOARD
REM ---------------------------------------------------

start cmd /k "call .venv\Scripts\activate && streamlit run src/dashboard/insider_risk_dashboard.py"

REM ---------------------------------------------------
REM START REACT DASHBOARD
REM ---------------------------------------------------

start cmd /k "cd frontend\soc-dashboard && npm start"

echo.
echo All services started successfully!
echo.
pause