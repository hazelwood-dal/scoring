from flask import Flask, render_template, jsonify
from threading import Thread
import time
from scoring import grade_all_teams

app = Flask(__name__)
results = []

def background_scoring():
    global results
    while True:
        results = grade_all_teams()
        time.sleep(120)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/results")
def api_results():
    return jsonify(results)

if __name__ == "__main__":
    results = grade_all_teams()  # populate immediately on start
    Thread(target=background_scoring, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5000)
