import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from scipy.stats import poisson
import os

# --------------------------------
# PAGE SETTINGS
# --------------------------------
st.set_page_config(
    page_title="Elite Soccer Predictor",
    layout="wide"
)

st.title("⚽ Elite Worldwide Soccer Prediction")
st.write(
    "25 strongest worldwide games • "
    "70%–100% confidence"
)

# --------------------------------
# API KEY
# --------------------------------
API_KEY = "816965adde03a5632c4bf03087cd6de3"

HEADERS = {
    "x-apisports-key": API_KEY
}

FIXTURE_URL = (
    "https://v3.football.api-sports.io/fixtures"
)

# --------------------------------
# DATE PICKER
# --------------------------------
selected_date = st.date_input(
    "Select Match Date",
    datetime.today()
)

match_date = (
    selected_date.strftime("%Y-%m-%d")
)

st.write(
    f"Games for: {match_date}"
)

# --------------------------------
# GET FIXTURES
# --------------------------------
try:
    response = requests.get(
        FIXTURE_URL,
        headers=HEADERS,
        params={
            "date": match_date
        },
        timeout=30
    )

    data = response.json()

except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

predictions = []

# --------------------------------
# TEAM FORM ANALYSIS
# --------------------------------
def get_team_form(team_id):

    try:
        response = requests.get(
            FIXTURE_URL,
            headers=HEADERS,
            params={
                "team": team_id,
                "last": 10
            },
            timeout=20
        )

        matches = (
            response.json()
            .get("response", [])
        )

        if not matches:
            return (
                1.4,
                1.1,
                0.5,
                0.5
            )

        scored = 0
        conceded = 0
        wins = 0
        clean_sheets = 0

        for m in matches:

            home_id = (
                m["teams"]["home"]["id"]
            )

            hg = (
                m["goals"]["home"]
                or 0
            )

            ag = (
                m["goals"]["away"]
                or 0
            )

            if home_id == team_id:

                scored += hg
                conceded += ag

                if hg > ag:
                    wins += 1

                if ag == 0:
                    clean_sheets += 1

            else:

                scored += ag
                conceded += hg

                if ag > hg:
                    wins += 1

                if hg == 0:
                    clean_sheets += 1

        avg_scored = (
            scored / len(matches)
        )

        avg_conceded = (
            conceded / len(matches)
        )

        win_rate = (
            wins / len(matches)
        )

        clean_sheet_rate = (
            clean_sheets
            / len(matches)
        )

        return (
            max(avg_scored, 0.9),
            max(avg_conceded, 0.8),
            win_rate,
            clean_sheet_rate
        )

    except:
        return (
            1.4,
            1.1,
            0.5,
            0.5
        )

# --------------------------------
# PREDICTION ENGINE
# --------------------------------
if "response" in data:

    for match in data["response"]:

        try:
            home_team = (
                match["teams"]["home"]["name"]
            )

            away_team = (
                match["teams"]["away"]["name"]
            )

            home_id = (
                match["teams"]["home"]["id"]
            )

            away_id = (
                match["teams"]["away"]["id"]
            )

            country = (
                match["league"]["country"]
            )

            league = (
                match["league"]["name"]
            )

            (
                home_attack,
                home_defense,
                home_form,
                home_clean
            ) = get_team_form(home_id)

            (
                away_attack,
                away_defense,
                away_form,
                away_clean
            ) = get_team_form(away_id)

            # Stronger xG logic
            home_xg = (
                (home_attack * 0.65)
                + (away_defense * 0.25)
                + (home_form * 1.0)
                + 0.45
            )

            away_xg = (
                (away_attack * 0.55)
                + (home_defense * 0.25)
                + (away_form * 0.80)
            )

            predicted_home = round(
                poisson.rvs(
                    max(home_xg, 1.0)
                )
            )

            predicted_away = round(
                poisson.rvs(
                    max(away_xg, 0.7)
                )
            )

            total_goals = (
                predicted_home
                + predicted_away
            )

            # RESULT
            if predicted_home > predicted_away:
                prediction = (
                    "HOME WIN"
                )
            elif predicted_away > predicted_home:
                prediction = (
                    "AWAY WIN"
                )
            else:
                prediction = (
                    "DRAW"
                )

            gg = (
                "YES"
                if predicted_home > 0
                and predicted_away > 0
                else "NO"
            )

            over15 = (
                "YES"
                if total_goals >= 2
                else "NO"
            )

            over25 = (
                "OVER 2.5"
                if total_goals >= 3
                else "UNDER 2.5"
            )

            # Higher confidence filter
            confidence = round(
                min(
                    100,
                    70 + (
                        abs(
                            home_form
                            - away_form
                        ) * 50
                    )
                    + (
                        abs(
                            home_attack
                            - away_attack
                        ) * 4
                    )
                )
            )

            # FINAL SCORE
            final_home = (
                match["goals"]["home"]
            )

            final_away = (
                match["goals"]["away"]
            )

            if (
                final_home is None
                or final_away is None
            ):
                final_score = (
                    "Not Played"
                )
                status = (
                    "PENDING"
                )

            else:

                final_score = (
                    f"{final_home}-"
                    f"{final_away}"
                )

                if (
                    final_home
                    > final_away
                ):
                    actual = (
                        "HOME WIN"
                    )
                elif (
                    final_away
                    > final_home
                ):
                    actual = (
                        "AWAY WIN"
                    )
                else:
                    actual = (
                        "DRAW"
                    )

                status = (
                    "WON"
                    if prediction
                    == actual
                    else "LOST"
                )

            # ONLY 70%+
            if confidence >= 70:

                predictions.append({
                    "Country":
                        country,
                    "League":
                        league,
                    "Home Team":
                        home_team,
                    "Away Team":
                        away_team,
                    "Predicted Score":
                        f"{predicted_home}-{predicted_away}",
                    "GG":
                        gg,
                    "Over 1.5":
                        over15,
                    "Over/Under":
                        over25,
                    "Prediction":
                        prediction,
                    "Final Score":
                        final_score,
                    "Prediction Won?":
                        status,
                    "Confidence %":
                        confidence
                })

        except:
            pass

# --------------------------------
# RESULTS
# --------------------------------
df = pd.DataFrame(predictions)

if len(df) > 0:

    df = df.sort_values(
        by="Confidence %",
        ascending=False
    )

    # EXACTLY 25 GAMES
    df = df.head(25)

    st.subheader(
        "Top 25 Elite Picks"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # SAVE EXCEL
    os.makedirs(
        "../output",
        exist_ok=True
    )

    excel_path = (
        "../output/"
        "elite_predictions.xlsx"
    )

    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer,
            index=False
        )

    st.success(
        "Excel saved successfully!"
    )

    with open(
        excel_path,
        "rb"
    ) as file:
        st.download_button(
            label=
            "Download Excel",
            data=file,
            file_name=
            "elite_predictions.xlsx",
            mime=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning(
        "No strong games "
        "found above 70%."
    )