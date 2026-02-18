from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd
from collections import Counter
import re

def simple_keyword_fallback(records: list[dict]):
    """Fallback if clustering fails or not enough data."""
    # Simple word frequency (primitive version)
    text = " ".join([r["text"].lower() for r in records])
    words = re.findall(r'\w+', text)
    # Filter common stopwords (hardcoded for MVP)
    stopwords = {"the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at", "from", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "of", "in", "on", "it", "is", "was", "be", "this", "that", "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their", "not", "no", "yes", "so", "up", "down", "out", "in", "off", "on", "over", "under", "again", "further", "then", "once"}
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
    common = Counter(filtered_words).most_common(5)
    
    return [{
        "topic_id": -1,
        "label": f"Keyword Frequency: {word}",
        "keywords": [word],
        "count": count,
        "examples": records[:3] # Just show some examples
    } for word, count in common]

def analyze(records: list[dict]):
    if len(records) < 20:
        return simple_keyword_fallback(records)

    texts = [r["text"] for r in records]

    try:
        # Use a small, fast embedding model
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic(
            embedding_model=embedding_model,
            min_topic_size=min(5, len(records) // 4),
            nr_topics="auto",
            calculate_probabilities=False
        )

        topics, _ = topic_model.fit_transform(texts)
        topic_info = topic_model.get_topic_info()
        
        # Check if we only got outliers (-1)
        if len(topic_info) <= 1 and topic_info.iloc[0]["Topic"] == -1:
             return simple_keyword_fallback(records)

        results = []
        for _, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:
                continue  # skip outliers

            keywords = [word for word, _ in topic_model.get_topic(topic_id)]
            # Get top 3 representative texts for this topic
            topic_docs = [
                records[i] for i, t in enumerate(topics)
                if t == topic_id
            ]
            top_docs = sorted(topic_docs, key=lambda x: x["score"], reverse=True)[:3]

            results.append({
                "topic_id": int(topic_id),
                "label": ", ".join(keywords[:4]),
                "keywords": keywords[:10],
                "count": int(row["Count"]),
                "examples": [
                    {"text": d["text"][:300], "score": d["score"], "url": d["url"]}
                    for d in top_docs
                ]
            })

        # Sort by frequency
        results.sort(key=lambda x: x["count"], reverse=True)
        
        if not results:
            return simple_keyword_fallback(records)
            
        return results

    except Exception as e:
        print(f"Error in BERTopic analysis: {e}")
        return simple_keyword_fallback(records)

if __name__ == "__main__":
    print("Analyzer module loaded.")
