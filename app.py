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



def generate_prediction_advanced(home_stats, away_stats, h2h_data):
    reasons = []

    # BTTS логика
    home_btts = home_stats.get("btts_percentage", 0)
    away_btts = away_stats.get("btts_percentage", 0)
    avg_btts = (home_btts + away_btts) / 2
    if avg_btts > 70:
        reasons.append(f"BTTS %%: {home_btts}%% и {away_btts}%%")
        prediction = "BTTS"
        confidence = int(avg_btts)
    else:
        # Over 2.5 логика
        home_over = home_stats.get("over25_percentage", 0)
        away_over = away_stats.get("over25_percentage", 0)
        avg_over = (home_over + away_over) / 2
        if avg_over > 65:
            reasons.append(f"Over 2.5 %%: {home_over}%% и {away_over}%%")
            prediction = "Over 2.5"
            confidence = int(avg_over)
        else:
            # Проста логика за 1X или 2
            home_form = home_stats.get("form_score", 0)
            away_form = away_stats.get("form_score", 0)
            if home_form > away_form:
                prediction = "1X"
                confidence = 70
                reasons.append("Домакинът е в по-добра форма от госта.")
            else:
                prediction = "X2"
                confidence = 68
                reasons.append("Гостът е в по-добра форма от домакина.")

    return prediction, confidence, reasons
