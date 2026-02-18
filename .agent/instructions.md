# Claude Code Agent Instructions — Reddit Pain Point Scraper

## Your Role

You are building a local web app that scrapes Reddit for user pain points around a given topic, clusters them into themes using NLP, and displays results in a browser dashboard. Follow the MVP spec in `reddit-painpoint-mvp.md` exactly. Do not add features not listed there.

---

## Ground Rules

- **Build in order.** Do not jump ahead. Each step depends on the previous one working.
- **Test each module before moving on.** Run a quick smoke test after building each file.
- **Never commit `.env`.** Add it to `.gitignore` immediately when you create the project folder.
- **Ask before deviating.** If something in the spec is unclear or seems wrong, stop and ask rather than guessing.
- **No extra dependencies.** Do not add libraries not listed in `requirements.txt` unless a listed one is unavailable, in which case ask first.
- **Keep it local.** This is a local dev app. No deployment, no auth, no database — just Flask + JSON file cache.

---

## Build Order (Follow This Exactly)

### Phase 1 — Scaffold
1. Create the project folder structure as defined in the spec
2. Create `requirements.txt` with all listed packages
3. Create `.env.example` with placeholder values
4. Create `.gitignore` that includes `.env`, `data/`, `__pycache__/`, `.venv/`
5. Initialize a virtual environment: `python -m venv .venv`

### Phase 2 — Scraper
1. Build `scraper.py` in full per the spec
2. Smoke test: add a `if __name__ == "__main__"` block that calls `scrape("notion", ["notion"], limit=20)` and prints the count and first 3 results
3. Run it: `python scraper.py`
4. Confirm you get back at least some results before proceeding
5. Remove or comment out the test block

### Phase 3 — Analyzer
1. Build `analyzer.py` in full per the spec
2. Smoke test: create 50 dummy complaint strings covering 3-4 fake themes, run `analyze()` on them, print topic labels and counts
3. Run it: `python analyzer.py`
4. Confirm BERTopic returns multiple distinct topics
5. Remove the test block

### Phase 4 — Flask Backend
1. Build `app.py` in full per the spec
2. Start the server: `python app.py`
3. Test POST `/scrape` with curl or a quick Python requests call using a small limit (20)
4. Test GET `/results` returns the cached data
5. Confirm both routes return valid JSON before building the frontend

### Phase 5 — Frontend Dashboard
1. Build `templates/index.html` per the spec
2. Reload the Flask app and open `http://localhost:5000` in a browser
3. Verify the config panel renders correctly
4. Run a full end-to-end scrape from the UI on topic "linear", subreddits "linear, projectmanagement"
5. Confirm topic cards and bar chart render with real data

### Phase 6 — README
1. Write `README.md` with setup instructions per the spec
2. Do a clean install test: follow the README from scratch in a new terminal to confirm it works

---

## Error Handling Checklist

Make sure these are all implemented before calling the build done:

- [ ] Reddit API credentials missing → clear error message pointing to `.env.example`
- [ ] Fewer than 20 comments collected → warning in UI: "Not enough data — try broader subreddits"
- [ ] BERTopic returns 1 topic or all outliers → fall back to keyword frequency mode
- [ ] Reddit API rate limit hit → catch `prawcore.exceptions.TooManyRequests`, return 429 with message
- [ ] `/results` called before any scrape → 404 with helpful message
- [ ] Subreddit doesn't exist → catch `praw.exceptions.InvalidURL` or redirect errors, surface in UI

---

## Code Style

- Python: follow PEP 8, use type hints on all function signatures
- Use f-strings, not `.format()` or `%`
- No global mutable state outside of Flask's app context
- Comments on any non-obvious logic (especially BERTopic config choices)
- HTML/CSS/JS: vanilla only, no frameworks, keep everything in the single `index.html` file
- JS: use `async/await` with `fetch()`, not `.then()` chains
- No inline styles — use a `<style>` block in `<head>`

---

## What NOT to Build

These are explicitly out of scope for this MVP. Do not implement them even if it seems easy:

- CSV export
- Side-by-side topic comparison
- Sentiment scoring
- Time-series analysis
- Auto-suggested subreddits
- User accounts or auth
- Database (SQLite, Postgres, etc.)
- Deployment config (Dockerfile, Procfile, etc.)

If you finish early, ask before adding anything.

---

## Testing the Final Build

Run this checklist end-to-end before declaring done:

1. Fresh clone → `pip install -r requirements.txt` completes without errors
2. `.env` filled in → `python app.py` starts without errors
3. Open `http://localhost:5000` → dashboard loads
4. Enter topic "figma", subreddits "figma, design", limit 100 → scrape runs
5. Results appear: bar chart with 3+ topics, topic cards with example quotes
6. Refresh page → results are still there (loaded from cache)
7. Click a "View on Reddit" link → opens valid Reddit URL
8. Enter a fake subreddit name → error is shown in UI, app does not crash

---

## If You Get Stuck

- BERTopic install issues → try `pip install bertopic --no-deps` then install deps individually
- UMAP or HDBSCAN compile errors on Windows → use `pip install umap-learn hdbscan --prefer-binary`
- Reddit returns 0 results → the subreddit may restrict search; try `subreddit.hot(limit=100)` as a fallback and filter by PAIN_SIGNALS keywords post-fetch
- BERTopic clustering all into `-1` (outliers) → lower `min_topic_size` to 3 and retry