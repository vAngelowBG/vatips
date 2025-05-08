import os
import requests
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
HEADERS = {"X-Auth-Token": API_TOKEN}
BASE_URL = "https://api.football-data.org/v4"

def get_today_matches():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"{BASE_URL}/matches?dateFrom={today}&dateTo={today}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("matches", [])

def get_last_matches(team_id):
    url = f"{BASE_URL}/teams/{team_id}/matches?status=FINISHED&limit=5"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("matches", [])

def analyze_match(match):
    home_id = match["homeTeam"]["id"]
    away_id = match["awayTeam"]["id"]
    home_name = match["homeTeam"]["name"]
    away_name = match["awayTeam"]["name"]

    home_matches = get_last_matches(home_id)
    away_matches = get_last_matches(away_id)

    def calc_form(matches, team_id):
        wins = 0
        goals = 0
        for m in matches:
            if m["score"]["winner"] == "HOME_TEAM" and m["homeTeam"]["id"] == team_id:
                wins += 1
            elif m["score"]["winner"] == "AWAY_TEAM" and m["awayTeam"]["id"] == team_id:
                wins += 1
            goals += m["score"]["fullTime"]["home"] + m["score"]["fullTime"]["away"]
        avg_goals = goals / len(matches) if matches else 0
        return wins, avg_goals

    home_wins, home_avg_goals = calc_form(home_matches, home_id)
    away_wins, away_avg_goals = calc_form(away_matches, away_id)

    # Определяне на прогноза
    if home_wins >= 3 and away_wins <= 1:
        prediction = "1"
        reason = "Домакинът е във форма с поне 3 победи, гостът слаба форма."
    elif home_avg_goals > 2.5 or away_avg_goals > 2.5:
        prediction = "Over 2.5"
        reason = "Средно над 2.5 гола в последните 5 мача."
    elif home_wins == 0 and away_wins >= 2:
        prediction = "2"
        reason = "Гостът е в по-добра форма, домакинът няма победа."
    else:
        prediction = "X2"
        reason = "Гостът има стабилна форма, домакинът не доминира."
    
    return {
        "match": f"{home_name} vs {away_name}",
        "prediction": prediction,
        "reason": reason
    }

@app.route("/today")
def today():
    matches = get_today_matches()
    analyzed = [analyze_match(m) for m in matches if m["status"] == "SCHEDULED"]
    return render_template("today.html", matches=analyzed)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return render_template("history.html")

def get_today_matches():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"{BASE_URL}/matches?dateFrom={today}&dateTo={today}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    print("MATCHES DATA:", data)  # ← Добави това
    return data.get("matches", [])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
