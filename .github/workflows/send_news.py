import os
import requests
from bs4 import BeautifulSoup

def get_top_news():
    url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100'  # 정치면 기준
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = soup.select('div.cluster_body ul li a')

    top_news = []
    seen = set()
    for item in news_items:
        title = item.get_text(strip=True)
        link = item['href']
        if link not in seen and link.startswith("https://"):
            seen.add(link)
            # 기사 내용 크롤링
            article = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            article_soup = BeautifulSoup(article.text, 'html.parser')

            # 본문 요약 추출 (간단한 방식)
            content_div = article_soup.select_one('#dic_area')
            if content_div:
                content = content_div.get_text(strip=True)[:100] + "..."
            else:
                content = "(내용 불러오기 실패)"

            top_news.append({
                "title": title,
                "link": link,
                "summary": content
            })

        if len(top_news) >= 10:
            break

    return top_news

def format_news_message(news_items):
    message = "📰 오늘의 주요 뉴스 TOP 10\n\n"
    for idx, item in enumerate(news_items, 1):
        message += f"{idx}. [{item['title']}]({item['link']})\n"
        message += f"{item['summary']}\n\n"
    return message
    
def send_to_kakaowork(app_key, email):
    headers = {"Authorization": f"Bearer {app_key}"}

    user = requests.get(
        "https://api.kakaowork.com/v1/users.find_by_email",
        headers=headers,
        params={"email": email}
    ).json()["user"]

    conv = requests.post(
        "https://api.kakaowork.com/v1/conversations.open",
        headers=headers,
        json={"user_id": user["id"]}
    ).json()["conversation"]

    news_text = get_top_news()
    message = f"📢 오늘의 주요 뉴스 Top 10\n\n{news_text}"

    res = requests.post(
        "https://api.kakaowork.com/v1/messages.send",
        headers=headers,
        json={"conversation_id": conv["id"], "text": message}
    )

    print("✅ 뉴스 전송 완료" if res.ok else f"❌ 오류 발생: {res.text}")

if __name__ == "__main__":
    news_list = get_top_news()
    message = format_news_message(news_list)
    send_message(message)  # 이미 정의된 카카오워크 메시지 함수
