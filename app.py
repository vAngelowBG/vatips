import os
import requests
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv

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

def analyze_fixture(fixture):
    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    match_str = f"{home} vs {away}"

    # Примерна логика: ако домакинът е фаворит според коефициенти
    prediction = "1X"
    reason = "Домакинът има предимство по ранкинг/домакинство (примерна логика)."

    return {
        "match": match_str,
        "prediction": prediction,
        "reason": reason
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/today")
def today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    fixtures = get_fixtures(today_str)
    analyzed = [analyze_fixture(f) for f in fixtures]
    return render_template("today.html", matches=analyzed)

@app.route("/fixtures")
def fixtures():
    date = (datetime.now().date()).strftime("%Y-%m-%d")
    fixtures = get_fixtures(date)
    analyzed = [analyze_fixture(f) for f in fixtures]
    return render_template("fixtures.html", matches=analyzed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
