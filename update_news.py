import feedparser
import json
from datetime import datetime
import os

# 뉴스 RSS 피드 목록
RSS_FEEDS = {
    "Global": "https://www.adweek.com/feed/",
    "Korea": "https://www.zdnet.co.kr/news/news.xml",
    "A+E": "https://cdn.feedcontrol.net/10476/18830-Gn9fHlEmknBGj.xml",
}

news_data = {}

def fake_summarize(text, length=180):
    """요약 대신 앞부분만 잘라서 보여줍니다."""
    return text.strip().replace("\n", " ")[:length] + "..."

for topic, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    news_data[topic] = []
    for entry in feed.entries[:10]:  # 카테고리당 3개 기사
        summary = fake_summarize(entry.get("summary", entry.get("description", "")))
        news_data[topic].append({
            "title": entry.title,
            "summary": summary,
            "link": entry.link,
            "published": entry.get("published", datetime.now().isoformat())
        })

# news.json 파일 저장
os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, indent=2, ensure_ascii=False)
