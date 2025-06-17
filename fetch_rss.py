import feedparser
import json
import os
from datetime import datetime, timedelta
from feeds import RSS_FEEDS

SAVE_PATH = 'docs/data/articles.json'

# Load existing articles
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, 'r', encoding='utf-8') as f:
        existing_articles = json.load(f)
else:
    existing_articles = []

# Use article.link as the unique ID
existing_ids = {item['id'] for item in existing_articles}

# Fetch new articles
new_articles = []
for source, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        article_id = entry.get('link')  # ✅ Use link as unique ID

        if article_id not in existing_ids:
            published = entry.get('published', datetime.utcnow().isoformat())
            try:
                published_dt = datetime.strptime(published[:19], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    published_dt = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                    published = published_dt.isoformat()
                except Exception:
                    published_dt = datetime.utcnow()
                    published = published_dt.isoformat()

            new_articles.append({
                'id': article_id,  # ✅ ID is the link
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', ''),
                'published': published,
                'source': source
            })

# Merge and keep only the most recent 7 days
merged_articles = existing_articles + new_articles
seven_days_ago = datetime.utcnow() - timedelta(days=7)

filtered_articles = []
for article in merged_articles:
    try:
        pub_dt = datetime.strptime(article['published'][:19], '%Y-%m-%dT%H:%M:%S')
        if pub_dt > seven_days_ago:
            filtered_articles.append(article)
    except Exception:
        continue  # skip if date parsing fails

# Save updated article list
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
with open(SAVE_PATH, 'w', encoding='utf-8') as f:
    json.dump(filtered_articles, f, ensure_ascii=False, indent=2)

print(f"✔ {len(new_articles)} new articles added. Total stored: {len(filtered_articles)}")
