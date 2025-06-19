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

# Use article.id (from RSS feed, fallback to link)
existing_ids = {item['id'] for item in existing_articles}

# Fetch new articles from all feeds
new_articles = []
for source, urls in RSS_FEEDS.items():
    # Ensure urls is always a list
    if not isinstance(urls, list):
        urls = [urls]

    for url in urls:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            continue

        for entry in feed.entries:
            article_id = entry.get('id', entry.get('link'))

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
                    'id': article_id,
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', '').strip(),
                    'summary': entry.get('summary', '').strip(),
                    'published': published,
                    'source': source
                })

# Merge and keep articles from the past 7 days
merged_articles = existing_articles + new_articles
seven_days_ago = datetime.utcnow() - timedelta(days=7)

filtered_articles = []
for article in merged_articles:
    try:
        pub_dt = datetime.strptime(article['published'][:19], '%Y-%m-%dT%H:%M:%S')
        if pub_dt > seven_days_ago:
            filtered_articles.append(article)
    except Exception:
        continue  # skip if parsing fails

# Save final result
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
with open(SAVE_PATH, 'w', encoding='utf-8') as f:
    json.dump(filtered_articles, f, ensure_ascii=False, indent=2)

print(f"✔ {len(new_articles)} new articles added. Total stored: {len(filtered_articles)}")
