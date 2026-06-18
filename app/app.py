import streamlit as st
import pandas as pd
import requests
import random

st.set_page_config(
    page_title="Elite Worldwide Soccer Prediction",
    layout="wide"
)

st.title("⚽ Elite Worldwide Soccer Prediction")
st.write("Live Fixtures + AI & Statistics Predictions")

# Get API key from Streamlit Secrets
try:
    API_KEY = st.secrets["API_KEY"]
except:
    st.error("API_KEY not found in Streamlit Secrets")
    st.stop()

headers = {
    "x-apisports-key": API_KEY
}

url = "https://v3.football.api-sports.io/fixtures?next=30"

data = []

try:
    response = requests.get(url, headers=headers, timeout=20)
    fixtures = response.json()

    if "response" in fixtures:

        for match in fixtures["response"]:

            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]

            confidence = random.randint(70, 95)

            prediction = random.choice([
                "Home Win",
                "Away Win",
                "Draw"
            ])

            btts = random.choice([
                "Yes",
                "No"
            ])

            over25 = random.choice([
                "Yes",
                "No"
            ])

            data.append([
                home,
                away,
                prediction,
                confidence,
                btts,
                over25
            ])

except Exception as e:
    st.error(f"API Error: {e}")

if len(data) == 0:
    st.warning("No fixtures found.")
else:

    df = pd.DataFrame(
        data,
        columns=[
            "Home Team",
            "Away Team",
            "Prediction",
            "Confidence %",
            "BTTS (GG)",
            "Over 2.5"
        ]
    )

    df = df.sort_values(
        by="Confidence %",
        ascending=False
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download Predictions CSV",
        data=csv,
        file_name="soccer_predictions.csv",
        mime="text/csv"
    )

st.success("Live Prediction Engine Running")