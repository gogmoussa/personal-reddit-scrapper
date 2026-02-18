from apify_client import ApifyClient
import os
import re
from dotenv import load_dotenv

load_dotenv()

PAIN_SIGNALS = [
    "hate", "wish", "frustrated", "annoying", "broken", "bug",
    "why can't", "anyone else", "please fix", "can't believe",
    "disappointed", "useless", "slow", "crashes", "missing feature"
]

def clean_text(text: str) -> str:
    """Strip Reddit markdown and normalize whitespace."""
    if not text:
        return ""
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove bold/italic markers
    text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape(topic: str, subreddits: list[str], limit: int = 200):
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        raise ValueError("APIFY_API_TOKEN missing in .env file.")
        
    client = ApifyClient(apify_token)

    # Prepare search query
    query = f"{topic} " + " OR ".join([f'"{s}"' for s in PAIN_SIGNALS[:6]])
    
    # Configure the actor
    # We use apify/reddit-scraper which is highly reliable
    run_input = {
        "searchTerms": [query],
        "searchType": "comments", # We can search for comments directly as they contain more pain points
        "subreddits": subreddits,
        "maxItems": limit,
        "sort": "relevance",
        "time": "month"
    }

    print(f"Calling Apify Reddit Scraper for query: {query}")
    
    try:
        # Run the actor and wait for it to finish
        run = client.actor("apify/reddit-scraper").call(run_input=run_input)
        
        results = []
        # Fetch and process items from the run's dataset
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            # Apify format varies slightly by actor version, but usually:
            # comments: body, upvotes, url, createdAt, subreddit
            # posts: title, selfText, upvotes, url, createdAt, subreddit
            
            text = ""
            if "body" in item: # Comment
                text = item["body"]
                item_type = "comment"
            elif "selfText" in item: # Post
                text = f"{item.get('title', '')}. {item.get('selfText', '')}"
                item_type = "post"
            else:
                continue

            cleaned = clean_text(text)
            if len(cleaned) > 40:
                results.append({
                    "text": cleaned,
                    "score": item.get("upvotes", 0),
                    "url": item.get("url", ""),
                    "source": item.get("subreddit", "unknown"),
                    "type": item_type,
                    "timestamp": item.get("createdAt", "")
                })

        # Also try to get some posts if we specifically want them, 
        # but searching comments is often enough for pain points.
        # For simplicity in MVP, we stick to the primary search.

        return results

    except Exception as e:
        print(f"Error calling Apify: {e}")
        return []

if __name__ == "__main__":
    print("Apify Scraper module loaded.")
