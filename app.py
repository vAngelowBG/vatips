
from flask import Flask, render_template
import requests
import json
from datetime import datetime

app = Flask(__name__)

API_TOKEN = "b1c3dc94d1c94e39a54157e6c6dccfd7"
API_BASE = "https://api.football-data.org/v4"

headers = {"X-Auth-Token": API_TOKEN}

@app.route("/today")
def today():
    today_date = datetime.today().strftime('%Y-%m-%d')
    tips = [{
        "time": "21:00",
        "match": "Man United – Arsenal",
        "league": "Premier League",
        "prediction": "BTTS",
        "confidence": "78%",
        "reasoning": "И двата отбора вкарват в 4 от последните 5 мача. Висока форма на нападението."
    }]
    with open(f"storage/tips_{today_date}.json", "w", encoding="utf-8") as f:
        json.dump(tips, f, ensure_ascii=False)
    return render_template("today.html", tips=tips)

@app.route("/")
def index():
    try:
        files = sorted(os.listdir("storage"), reverse=True)
        with open(f"storage/{files[0]}", encoding="utf-8") as f:
            tips = json.load(f)
        correct = sum(1 for tip in tips if tip.get("result") == "✅")
        success = round((correct / len(tips)) * 100, 1) if tips else 0
    except:
        tips, success = [], 0
    return render_template("index.html", tips=tips, success=success)

if __name__ == "__main__":
    app.run(debug=True)
