import streamlit as st
import requests

st.title("API Test")

try:
    API_KEY = st.secrets["API_KEY"]

    headers = {
        "x-apisports-key": API_KEY
    }

    url = "https://v3.football.api-sports.io/status"

    response = requests.get(url, headers=headers)
    data = response.json()

    st.write("API Response:")
    st.json(data)

except Exception as e:
    st.error(str(e))