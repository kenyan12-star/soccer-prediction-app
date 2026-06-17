from flask import Flask, render_template, request
import random
import pandas as pd

app = Flask(__name__)

def ai_model(team1, team2):
    outcomes = ["Home Win", "Draw", "Away Win"]
    prediction = random.choices(outcomes, weights=[50, 25, 25])[0]
    confidence = random.randint(70, 95)
    return prediction, confidence


def stats_model(team1, team2):
    g1 = random.randint(0, 4)
    g2 = random.randint(0, 4)

    if g1 > g2:
        result = "Home Win"
    elif g2 > g1:
        result = "Away Win"
    else:
        result = "Draw"

    confidence = random.randint(60, 90)

    return result, confidence, g1, g2


def save_to_excel(data):
    file = "results.xlsx"

    try:
        old = pd.read_excel(file)
        df = pd.concat([old, pd.DataFrame([data])], ignore_index=True)
    except:
        df = pd.DataFrame([data])

    df.to_excel(file, index=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    team1 = request.form["team1"]
    team2 = request.form["team2"]

    ai_pred, ai_conf = ai_model(team1, team2)
    stats_pred, stats_conf, g1, g2 = stats_model(team1, team2)

    # combine AI + stats
    if ai_pred == stats_pred:
        final = ai_pred
        confidence = (ai_conf + stats_conf) // 2 + 5
    else:
        final = ai_pred if ai_conf > stats_conf else stats_pred
        confidence = (ai_conf + stats_conf) // 2

    score = f"{g1}-{g2}"

    save_to_excel({
        "Home Team": team1,
        "Away Team": team2,
        "AI": ai_pred,
        "Stats": stats_pred,
        "Final": final,
        "Score": score,
        "Confidence": confidence
    })

    return render_template(
        "index.html",
        team1=team1,
        team2=team2,
        ai=ai_pred,
        stats=stats_pred,
        final=final,
        confidence=confidence,
        score=score
    )


if __name__ == "__main__":
    app.run(debug=True)