import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Зареждаме CSV файла
df = pd.read_csv("ai_dataset.csv")

# Преобразуване на категориални изходи в числа
df = df.dropna()
df = df[df["result"].isin(["1", "X", "2"])]

# Features: голове, домакин/гост
df["goal_diff"] = df["home_goals"] - df["away_goals"]
df["total_goals"] = df["home_goals"] + df["away_goals"]

X = df[["home_goals", "away_goals", "goal_diff", "total_goals"]]

# 1X2 модел
y_1x2 = df["result"]
X_train, X_test, y_train, y_test = train_test_split(X, y_1x2, test_size=0.2, random_state=42)
model_1x2 = RandomForestClassifier()
model_1x2.fit(X_train, y_train)
print("1X2 accuracy:", accuracy_score(y_test, model_1x2.predict(X_test)))
joblib.dump(model_1x2, "model_1x2.pkl")

# BTTS модел
y_btts = df["btts"].map({"Yes": 1, "No": 0})
model_btts = RandomForestClassifier()
model_btts.fit(X, y_btts)
joblib.dump(model_btts, "model_btts.pkl")

# Over/Under 2.5 модел
y_ou = df["over_2_5"].map({"Yes": 1, "No": 0})
model_ou = RandomForestClassifier()
model_ou.fit(X, y_ou)
joblib.dump(model_ou, "model_over25.pkl")

print("✅ Моделите са обучени и записани: model_1x2.pkl, model_btts.pkl, model_over25.pkl")
