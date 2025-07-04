
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time

def fetch_kcta_articles():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    today = datetime.now(timezone.utc)
    year, month, day = today.year, today.month, today.day

    url = f"http://kcta.or.kr:/kcta_new/mediaclipping/sharePreview.do?SEARCH_TIME=getDay&NOW_YEAR={year}&NOW_MONTH={month}&NOW_DAY={day}"

    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    news_links = soup.select('div.clippingContent01 a[href]')
    articles = []

    for a in news_links:
        href = a.get("href", "").strip()
        title = a.get_text(strip=True)
        if href and title:
            article = {
                "id": href,
                "title": title,
                "link": href,
                "summary": "",
                "published": today.isoformat(),
                "source": "News_KCTA"
            }
            articles.append(article)

    return articles
