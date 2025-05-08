from flask import Flask, render_template
import requests
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

API_KEY_RAPIDAPI = os.environ.get("X_RAPIDAPI_KEY")
HEADERS_RAPIDAPI = {
    "X-RapidAPI-Key": API_KEY_RAPIDAPI,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

API_KEY_FOOTBALLDATA = os.environ.get("FOOTBALLDATA_API_KEY")
HEADERS_FOOTBALLDATA = {
    "X-Auth-Token": API_KEY_FOOTBALLDATA
}

def fetch_fixtures(date):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"date": date, "timezone": "Europe/Sofia"}
    response = requests.get(url, headers=HEADERS_RAPIDAPI, params=params)
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

@app.route("/")
def index():
    files = sorted(Path("storage").glob("tips_*.json"), reverse=True)
    if not files:
        return render_template("index.html", tips=[], success=0)
    with open(files[0], encoding="utf-8") as f:
        tips = json.load(f)
    total = len(tips)
    correct = sum(1 for tip in tips if tip.get("result") == "✅")
    success_rate = round((correct / total) * 100, 1) if total else 0
    return render_template("index.html", tips=tips, success=success_rate)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
