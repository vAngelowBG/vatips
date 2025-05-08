from flask import Flask, render_template
import json
from pathlib import Path

app = Flask(__name__)

def load_latest_tips():
    files = sorted(Path("storage").glob("tips_*.json"), reverse=True)
    if not files:
        return []
    with open(files[0], encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")
    tips = load_latest_tips()
    total = len(tips)
    correct = sum(1 for tip in tips if tip.get("result") == "✅")
    success_rate = round((correct / total) * 100, 1) if total else 0

    return render_template("index.html", tips=tips, success=success_rate)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
