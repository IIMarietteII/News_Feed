import feedparser
import json
from datetime import datetime
from feeds import RSS_FEEDS
import os

output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

articles = []

for source, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:  # Limit per feed
        articles.append({
            "id": entry.id if "id" in entry else entry.link,
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary if "summary" in entry else "",
            "published": entry.published if "published" in entry else "",
            "source": source
        })

with open(os.path.join(output_dir, 'articles.json'), 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Saved {len(articles)} articles.")
