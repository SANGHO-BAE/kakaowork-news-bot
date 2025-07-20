import requests
from bs4 import BeautifulSoup
import json
import os

def get_top_news():
    headers = {"User-Agent": "Mozilla/5.0"}

    url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100'  # 정치 분야 주요 뉴스
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    articles = soup.select('div.cluster_body a.cluster_text_headline')
    seen_links = set()
    news_list = []

    for article in articles:
        title = article.get_text(strip=True)
        link = article['href']

        if link in seen_links:
            continue
        seen_links.add(link)

        # 본문 가져오기
        try:
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.text, 'html.parser')
            content = article_soup.select_one('#dic_area')

            if content:
                summary = content.get_text(strip=True)[:100] + "..."
            else:
                summary = "(본문 요약 불가)"
        except Exception as e:
            summary = "(본문 불러오기 오류)"

        news_list.append({
            "title": title,
            "link": link,
            "summary": summary
        })

        if len(news_list) >= 10:
            break

    return news_list

def format_news_message(news_items):
    message = "📰 오늘의 주요 뉴스 TOP 10\n\n"
    for i, item in enumerate(news_items, 1):
        message += f"{i}. [{item['title']}]({item['link']})\n{item['summary']}\n\n"
    return message

def send_message(text):
    url = "https://api.kakaowork.com/v1/messages.send"
    headers = {
        "Authorization": f"Bearer {os.environ['KAKAO_WORK_BOT_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "receiver_id": os.environ['KAKAO_WORK_USER_ID'],
        "receiver_type": "user",
        "text": text
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    print(res.status_code, res.text)

if __name__ == "__main__":
    news = get_top_news()
    msg = format_news_message(news)
    send_message(msg)
