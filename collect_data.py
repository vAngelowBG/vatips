import requests
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

start_date = datetime(datetime.now().year, 1, 1)
end_date = datetime.now()

match_data = []

current = start_date
while current <= end_date:
    try:
        url = f"{BASE_URL}/fixtures"
        params = {"date": current.strftime("%Y-%m-%d")}
        response = requests.get(url, headers=HEADERS, params=params)
        fixtures = response.json().get("response", [])

        for fixture in fixtures:
            home = fixture["teams"]["home"]["name"]
            away = fixture["teams"]["away"]["name"]
            home_goals = fixture["goals"]["home"]
            away_goals = fixture["goals"]["away"]
            if home_goals is None or away_goals is None:
                continue

            full_time_result = "1" if home_goals > away_goals else "2" if away_goals > home_goals else "X"
            btts = "Yes" if home_goals > 0 and away_goals > 0 else "No"
            over_2_5 = "Yes" if (home_goals + away_goals) > 2.5 else "No"
            half_time_result = fixture["score"]["halftime"]
            correct_score = f"{home_goals}:{away_goals}"

            match_data.append({
                "date": current.strftime("%Y-%m-%d"),
                "home_team": home,
                "away_team": away,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": full_time_result,
                "btts": btts,
                "over_2_5": over_2_5,
                "half_time_result": f"{half_time_result['home']}:{half_time_result['away']}",
                "correct_score": correct_score
            })
    except Exception as e:
        print(f"⚠️ Error on {current.strftime('%Y-%m-%d')}: {e}")
    current += timedelta(days=1)

# Запис в устойчивата директория
os.makedirs("storage", exist_ok=True)
output_path = "storage/ai_dataset.csv"
df = pd.DataFrame(match_data)
df.to_csv(output_path, index=False)
print(f"✅ Данните са записани в {output_path}")
