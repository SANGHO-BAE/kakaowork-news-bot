import requests
from bs4 import BeautifulSoup
import json
import os

# ✅ 1. 주요 뉴스 가져오기
def get_top_news():
    url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100'  # 정치 섹션
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = soup.select('div.cluster_body ul li a')

    top_news = []
    seen = set()

    for item in news_items:
        title = item.get_text(strip=True)
        link = item['href']

        if link not in seen and link.startswith("https://"):
            seen.add(link)

            # 기사 본문 크롤링
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.text, 'html.parser')

            content_div = article_soup.select_one('#dic_area')
            if content_div:
                summary = content_div.get_text(strip=True)[:100] + "..."
            else:
                summary = "(내용 불러오기 실패)"

            top_news.append({
                "title": title,
                "link": link,
                "summary": summary
            })

        if len(top_news) >= 10:
            break

    return top_news

# ✅ 2. 카카오워크로 보낼 메시지 포맷
def format_news_message(news_items):
    message = "📰 오늘의 주요 뉴스 TOP 10\n\n"
    for i, item in enumerate(news_items, 1):
        message += f"{i}. [{item['title']}]({item['link']})\n{item['summary']}\n\n"
    return message

# ✅ 3. 카카오워크 메시지 전송
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

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.status_code, response.text)

# ✅ 4. 전체 실행
if __name__ == "__main__":
    news = get_top_news()
    message = format_news_message(news)
    send_message(message)
