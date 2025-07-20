
import requests
import feedparser
import os
import json

def get_top_news():
    # Naver 뉴스 RSS (정치면 기준. 다른 섹션도 가능)
    rss_url = "https://rss.etoday.co.kr/newssection.xml?section=1"  # 이투데이 정치 섹션 RSS 예시

    feed = feedparser.parse(rss_url)
    news_list = []

    for entry in feed.entries[:10]:
        title = entry.title
        summary = entry.summary if hasattr(entry, "summary") else "(요약 없음)"
        link = entry.link

        news_list.append({
            "title": title,
            "summary": summary,
            "link": link
        })

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
        "receiver_id": os.environ['KAKAO_WORK_USER_ID'],  # 환경변수 사용
        "receiver_type": "user",
        "text": text
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.status_code, response.text)

if __name__ == "__main__":
    news = get_top_news()
    message = format_news_message(news)
    send_message(message)
