import requests
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from github import Github

# Зареждаме променливите от .env
load_dotenv()

RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # <-- Добави този токен в .env
REPO_NAME = "vAngelowBG/vatips"
CSV_PATH = "storage/ai_dataset.csv"

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

# Запис във файл локално
os.makedirs("storage", exist_ok=True)
df = pd.DataFrame(match_data)
df.to_csv(CSV_PATH, index=False)
print(f"✅ Данните са записани в {CSV_PATH}")

# Качване в GitHub
if GITHUB_TOKEN:
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        commit_msg = f"Обновяване на ai_dataset.csv ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        
        with open(CSV_PATH, "r", encoding="utf-8") as file:
            content = file.read()
        
        try:
            existing = repo.get_contents(CSV_PATH)
            repo.update_file(existing.path, commit_msg, content, existing.sha)
        except:
            repo.create_file(CSV_PATH, commit_msg, content)

        print("🚀 ai_dataset.csv е успешно качен в GitHub.")
    except Exception as e:
        print("❌ Неуспешно качване в GitHub:", e)
else:
    print("⚠️ GITHUB_TOKEN липсва или не е зададен.")
