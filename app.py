import os
import requests
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def get_fixtures(date):
    url = f"{BASE_URL}/fixtures"
    params = {"date": date}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data.get("response", [])

def get_team_last_matches(team_id):
    url = f"{BASE_URL}/teams"
    params = {"id": team_id}
    response = requests.get(url, headers=HEADERS)

    url = f"{BASE_URL}/fixtures"
    params = {"team": team_id, "last": 5}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("response", [])

def analyze_fixture(fixture):
    home = fixture["teams"]["home"]
    away = fixture["teams"]["away"]
    league = fixture["league"]
    time_utc = fixture["fixture"]["date"]
    time = datetime.fromisoformat(time_utc).strftime("%H:%M")
    
    home_matches = get_team_last_matches(home["id"])
    away_matches = get_team_last_matches(away["id"])

    def calc_stats(matches, team_key):
        wins = 0
        goals = 0
        for match in matches:
            score = match["goals"]
            if match["teams"][team_key]["winner"]:
                wins += 1
            goals += score["home"] + score["away"]
        avg_goals = goals / len(matches) if matches else 0
        return wins, avg_goals

    home_wins, home_avg_goals = calc_stats(home_matches, "home")
    away_wins, away_avg_goals = calc_stats(away_matches, "away")

    # Аналитична логика
    if away_wins >= 3 and home_wins <= 1:
        prediction = "2"
        reason = "Гостът е във форма: над 3 победи. Домакинът слаба форма."
    elif home_wins >= 3 and away_wins <= 1:
        prediction = "1"
        reason = "Домакинът е във форма: над 3 победи. Гостът слаба форма."
    elif home_avg_goals + away_avg_goals > 3:
        prediction = "Over 2.5"
        reason = "Двата отбора вкарват много – средно над 3 гола."
    else:
        prediction = "X2"
        reason = "Формата е балансирана, гостът с леко предимство."

    return {
        "league": f"{league['country']} - {league['name']}",
        "match": f"{home['name']} vs {away['name']}",
        "time": time,
        "prediction": prediction,
        "reason": reason
    }

@app.route("/today")
def today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    fixtures = get_fixtures(today_str)
    analyzed = [analyze_fixture(f) for f in fixtures]
    grouped = defaultdict(list)
    for match in analyzed:
        grouped[match["league"]].append(match)
    return render_template("today.html", grouped_matches=grouped)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
