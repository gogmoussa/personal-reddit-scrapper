# Reddit Pain Point Scraper — MVP

A local Python app that scrapes Reddit for user complaints and pain points around a given topic or product, clusters them into themes using BERTopic, and displays them in a sleek web dashboard.

## 🚀 Features
- **Scraper**: Collects data using [Apify's Reddit Scraper](https://apify.com/apify/reddit-scraper), avoiding local rate limits and API credential complexities.
- **NLP Clustering**: Uses [BERTopic](https://github.com/MaartenGr/BERTopic) to automatically group complaints into themes.
- **Web Dashboard**: Modern Glassmorphic UI with Chart.js visualization of pain point frequency.
- **Caching**: Saves results to `data/results.json` for persistent viewing.

## 🛠️ Setup

### 1. Apify API Token
1. Sign up/Log in to [Apify](https://apify.com).
2. Go to **Settings > API Tokens**.
3. Copy your **Personal API Token**.

### 2. Environment Configuration
Create/Update the `.env` file in the root directory:
```env
APIFY_API_TOKEN=your_apify_api_token
```


### 3. Installation
Ensure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

## 📝 Troubleshooting
- **First Scrape**: The first run will download the `sentence-transformers` model (~400MB) and may take 2-4 minutes.
- **Rate Limits**: If you scrape too many subreddits quickly, Reddit may rate-limit you. The app handles this gracefully, but try to keep limits under 200 per run for best results.
- **NLTK/Models**: If you see errors about missing models, they should auto-download on first use.

## 📂 Project Structure
- `scraper.py`: Reddit scraping logic using PRAW.
- `analyzer.py`: Topic modeling logic using BERTopic.
- `app.py`: Flask backend and API routes.
- `templates/index.html`: Dashboard frontend.
- `data/`: Stores results in JSON.
