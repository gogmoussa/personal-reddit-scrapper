from flask import Flask, render_template, request, jsonify
import json
import os
import traceback
from scraper import scrape
from analyzer import analyze

app = Flask(__name__)
CACHE_FILE = "data/results.json"
os.makedirs("data", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def run_scrape():
    try:
        body = request.json
        topic = body.get("topic", "")
        subreddits_str = body.get("subreddits", "")
        limit = int(body.get("limit", 150))

        if not topic or not subreddits_str:
            return jsonify({"error": "Topic and subreddits are required"}), 400

        subreddits = [s.strip() for s in subreddits_str.split(",") if s.strip()]
        
        print(f"Starting scrape for topic: {topic} in subs: {subreddits}")
        records = scrape(topic, subreddits, limit=limit)
        
        if not records:
            return jsonify({"error": "No data found for this topic/subreddit combination."}), 404

        print(f"Scraped {len(records)} records. Starting analysis...")
        topics = analyze(records)

        payload = {
            "topic": topic,
            "subreddits": subreddits,
            "total_comments": len(records),
            "topics": topics,
            "warning": "Not enough data for reliable clustering" if len(records) < 20 else None
        }

        with open(CACHE_FILE, "w") as f:
            json.dump(payload, f, indent=2)

        return jsonify(payload)
    except Exception as e:
        print(f"Error in /scrape: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/results", methods=["GET"])
def get_results():
    if not os.path.exists(CACHE_FILE):
        return jsonify({"error": "No results yet. Run a scrape first."}), 404
    try:
        with open(CACHE_FILE) as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": f"Failed to load cache: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
