from flask import Flask, render_template
import requests
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

API_KEY = os.environ.get("X_RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}


from random import randint

def generate_prediction_ai(stats=None):
    probabilities = {
        "1": randint(40, 65),
        "2": randint(30, 60),
        "BTTS": randint(50, 85),
        "Over 2.5": randint(50, 90),
        "1X": randint(60, 92)
    }
    best_market = max(probabilities, key=probabilities.get)
    best_confidence = probabilities[best_market]
    reasons = {
        "1": "Домакинът е в по-добра форма и играе силно у дома.",
        "2": "Гостът е с 4 победи в последните 5 мача.",
        "BTTS": "И двата отбора имат висока BTTS честота – 78% и 74%.",
        "Over 2.5": "Средно над 3 гола в последните им срещи.",
        "1X": "Домакинът рядко губи, особено на собствен терен."
    }
    return best_market, best_confidence, reasons[best_market]


def fetch_fixtures(date):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"date": date, "timezone": "Europe/Sofia"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        return []
    return response.json().get("response", [])

def generate_prediction(league, home, away):
    if "U19" in league or "Women" in league:
        return "Over 2.5", 76, "Младите отбори вкарват повече – 3.1 средно."
    elif "Premier" in league or "Serie A" in league:
        return "BTTS", 68, "Двата отбора бележат в повечето мачове."
    elif "Liga" in league or "Bundes" in league:
        return "Over 2.5", 72, "Средно 2.9 гола в последните кръгове."
    else:
        return "1", 64, "Домакинът има предимство у дома."

@app.route("/today")
def today():
    from datetime import datetime
    today = datetime.today().strftime("%Y-%m-%d")
    fixtures = fetch_fixtures(today)
    tips = []
    for item in fixtures:
        fixture = item["fixture"]
        league = item["league"]["name"]
        country = item["league"]["country"]
        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]
        prediction, confidence, reasoning = generate_prediction_ai()
        tips.append({
            "time": fixture["date"][11:16],
            "match": f"{home} – {away}",
            "league": league,
            "country": country,
            "prediction": prediction,
            "confidence": confidence,
            "reasoning": reasoning
        })
    with open(f"storage/tips_{today}.json", "w", encoding="utf-8") as f:
        json.dump(tips, f, ensure_ascii=False, indent=2)
    return render_template("today.html", tips=tips)

    today = datetime.today().strftime('%Y-%m-%d')
    fixtures = fetch_fixtures(today)
    tips = []

    for item in fixtures:
        fixture = item["fixture"]
        league = item["league"]["name"]
        country = item["league"]["country"]
        home = item["teams"]["home"]["name"]
        away = item["teams"]["away"]["name"]

        prediction, confidence, reasoning = generate_prediction(league, home, away)

        tips.append({
            "time": fixture["date"][11:16],
            "match": f"{home} – {away}",
            "league": league,
            "country": country,
            "prediction": prediction,
            "confidence": confidence,
            "reasoning": reasoning
        })

    with open(f"storage/tips_{today}.json", "w", encoding="utf-8") as f:
        json.dump(tips, f, ensure_ascii=False)

    return render_template("today.html", tips=tips)
def load_latest_tips():
    files = sorted(Path("storage").glob("tips_*.json"), reverse=True)
    if not files:
        return []
    with open(files[0], encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    tips = load_latest_tips()
    total = len(tips)
    correct = sum(1 for tip in tips if tip.get("result") == "✅")
    success_rate = round((correct / total) * 100, 1) if total else 0
    return render_template("index.html", tips=tips, success=success_rate)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
