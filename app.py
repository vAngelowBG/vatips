from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/today")
def today():
    try:
        df = pd.read_csv("predictions_today.csv")
        return render_template("today.html", predictions=df.to_dict(orient="records"))
    except Exception as e:
        return f"<h2>⚠️ Прогнозите не са налични:</h2><p>{str(e)}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
