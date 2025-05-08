import requests
import pandas as pd
import joblib
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

# Зареждаме моделите
model_1x2 = joblib.load("model_1x2.pkl")
model_btts = joblib.load("model_btts.pkl")
model_ou25 = joblib.load("model_over25.pkl")

def get_today_fixtures():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures"
    params = {"date": today}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json().get("response", [])

# Събиране и предсказване
fixtures = get_today_fixtures()
predictions = []

for fixture in fixtures:
    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    home_id = fixture["teams"]["home"]["id"]
    away_id = fixture["teams"]["away"]["id"]

    goals = fixture.get("goals", {})
    home_goals = goals.get("home", 0) or 0
    away_goals = goals.get("away", 0) or 0

    goal_diff = home_goals - away_goals
    total_goals = home_goals + away_goals

    X = pd.DataFrame([{
        "home_goals": home_goals,
        "away_goals": away_goals,
        "goal_diff": goal_diff,
        "total_goals": total_goals
    }])

    try:
        pred_1x2 = model_1x2.predict(X)[0]
        pred_btts = "Yes" if model_btts.predict(X)[0] == 1 else "No"
        pred_ou = "Over 2.5" if model_ou25.predict(X)[0] == 1 else "Under 2.5"

        predictions.append({
            "match": f"{home} vs {away}",
            "1X2": pred_1x2,
            "BTTS": pred_btts,
            "Over/Under": pred_ou
        })
    except Exception as e:
        print("⚠️ Пропуснат мач поради грешка:", e)

# Запис в CSV
df = pd.DataFrame(predictions)
df.to_csv("predictions_today.csv", index=False)
print("✅ Прогнозите са записани в predictions_today.csv")
