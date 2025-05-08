import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Четене на CSV
df = pd.read_csv("storage/ai_dataset.csv")
df = df.dropna()
df = df[df["result"].isin(["1", "X", "2"])]
df["goal_diff"] = df["home_goals"] - df["away_goals"]
df["total_goals"] = df["home_goals"] + df["away_goals"]
X = df[["home_goals", "away_goals", "goal_diff", "total_goals"]]

# 1X2 модел
y_1x2 = df["result"]
X_train, X_test, y_train, y_test = train_test_split(X, y_1x2, test_size=0.2, random_state=42)
model_1x2 = RandomForestClassifier()
model_1x2.fit(X_train, y_train)
print("1X2 accuracy:", accuracy_score(y_test, model_1x2.predict(X_test)))
joblib.dump(model_1x2, "storage/model_1x2.pkl")

# BTTS
y_btts = df["btts"].map({"Yes": 1, "No": 0})
model_btts = RandomForestClassifier()
model_btts.fit(X, y_btts)
joblib.dump(model_btts, "storage/model_btts.pkl")

# Over 2.5
y_ou = df["over_2_5"].map({"Yes": 1, "No": 0})
model_ou = RandomForestClassifier()
model_ou.fit(X, y_ou)
joblib.dump(model_ou, "storage/model_over25.pkl")

print("✅ Моделите са обучени и записани локално.")

# === Качване в GitHub ===
token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPO")

g = Github(token)
repo = g.get_repo(repo_name)

def upload_to_github(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        content = f.read()
    try:
        existing = repo.get_contents(f"storage/{filename}")
        repo.update_file(existing.path, f"Update {filename}", content, existing.sha)
        print(f"🔁 Обновено: {filename}")
    except:
        repo.create_file(f"storage/{filename}", f"Add {filename}", content)
        print(f"🆕 Качено: {filename}")

# Качи и трите модела
for f in ["model_1x2.pkl", "model_btts.pkl", "model_over25.pkl"]:
    upload_to_github(f"storage/{f}")
