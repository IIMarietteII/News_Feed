
import feedparser
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from feeds import RSS_FEEDS

SAVE_PATH = 'docs/data/articles.json'

def extract_real_url(google_url):
    try:
        parsed = urlparse(google_url)
        query = parse_qs(parsed.query)
        return query.get("url", [google_url])[0]
    except Exception:
        return google_url

# Load existing articles
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, 'r', encoding='utf-8') as f:
        existing_articles = json.load(f)
else:
    existing_articles = []

existing_ids = {item['id'] for item in existing_articles}

# Fetch new articles
new_articles = []
for source, urls in RSS_FEEDS.items():
    if not isinstance(urls, list):
        urls = [urls]

    for url in urls:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            continue

        for entry in feed.entries:
            raw_link = entry.get('link', '')
            real_link = extract_real_url(raw_link)
            article_id = real_link  # use cleaned real URL

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
                    'link': real_link,
                    'summary': entry.get('summary', '').strip(),
                    'published': published,
                    'source': source
                })

# ✅ KCTA 기사 추가
from kcta_scraper import fetch_kcta_articles
new_articles += fetch_kcta_articles() 

# Merge and filter to past 7 days
merged_articles = existing_articles + new_articles
seven_days_ago = datetime.utcnow() - timedelta(days=7)

filtered_articles = []
for article in merged_articles:
    try:
        pub_dt = datetime.strptime(article['published'][:19], '%Y-%m-%dT%H:%M:%S')
        if pub_dt > seven_days_ago:
            filtered_articles.append(article)
    except Exception:
        continue

# Save
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
with open(SAVE_PATH, 'w', encoding='utf-8') as f:
    json.dump(filtered_articles, f, ensure_ascii=False, indent=2)

print(f"✔ {len(new_articles)} new articles added. Total stored: {len(filtered_articles)}")
