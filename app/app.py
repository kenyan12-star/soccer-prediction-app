import streamlit as st
import pandas as pd

st.set_page_config(page_title="Soccer Prediction App", layout="wide")

st.title("⚽ Elite Worldwide Soccer Prediction")

data = [
    ["Arsenal vs Chelsea", "Home Win", 82],
    ["Real Madrid vs Sevilla", "Home Win", 88],
    ["Bayern vs Dortmund", "Over 2.5", 79],
]

df = pd.DataFrame(data, columns=["Match", "Prediction", "Confidence %"])

st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False)

st.download_button(
    label="📥 Download Predictions",
    data=csv,
    file_name="predictions.csv",
    mime="text/csv"
)