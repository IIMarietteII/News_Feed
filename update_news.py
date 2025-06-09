import feedparser
import google.generativeai as genai
import os, json
from datetime import datetime

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

RSS_FEEDS = {
    "Global": "https://rss.nytimes.com/services/xml/rss/nyt/MediaandAdvertising.xml",
    "Korea": "https://www.zdnet.co.kr/news/news.xml",
    "A+E": "https://www.prnewswire.com/rss/all-a-e-networks-news.rss"
}

news_data = {}

def summarize(text):
    prompt = f"다음 기사 내용을 한국어로 3줄로 요약해줘:\n{text}"
    response = model.generate_content(prompt)
    return response.text.strip()

for topic, url in RSS_FEEDS.items():
    news_data[topic] = []
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]:
        summary = summarize(entry.description)
        news_data[topic].append({
            "title": entry.title,
            "summary": summary,
            "link": entry.link,
            "published": entry.get("published", datetime.now().isoformat())
        })

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, indent=2, ensure_ascii=False)
