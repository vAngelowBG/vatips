import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
HEADERS = {"X-Auth-Token": API_TOKEN}
BASE_URL = "https://api.football-data.org/v4"

def get_matches():
    response = requests.get(f"{BASE_URL}/matches", headers=HEADERS)
    return response.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/today")
def today():
    data = get_matches()
    return render_template("today.html", matches=data.get("matches", []))

@app.route("/history")
def history():
    try:
        with open("storage/history.json", "r") as file:
            history_data = file.read()
        return jsonify(history_data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
