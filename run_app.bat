@echo off
cd /d %USERPROFILE%\Desktop\SoccerPredictionApp\app

echo Starting Soccer Prediction App...

start http://localhost:8501

streamlit run app.py

pause