import feedparser
import json
from datetime import datetime
from feeds import RSS_FEEDS
import os

# GitHub Pages에서 접근 가능하도록 docs/data 경로 사용
output_dir = 'docs/data'
os.makedirs(output_dir, exist_ok=True)

articles = []

for source, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:  # 각 피드당 최대 10개
        articles.append({
            "id": entry.id if "id" in entry else entry.link,
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary if "summary" in entry else "",
            "published": entry.published if "published" in entry else "",
            "source": source
        })

# JSON 파일 저장 위치 변경됨
output_path = os.path.join(output_dir, 'articles.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Saved {len(articles)} articles to {output_path}")
