import os
import requests
from bs4 import BeautifulSoup

def get_top_news():
    url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    news_blocks = soup.select(".cluster_body .cluster_text")[:10]
    news_list = []

    for idx, block in enumerate(news_blocks):
        title_tag = block.select_one("a")
        desc_tag = block.select_one(".cluster_text_lede")

        if title_tag:
            title = title_tag.text.strip()
            link = "https://news.naver.com" + title_tag["href"]
        else:
            continue

        desc = desc_tag.text.strip() if desc_tag else "요약 없음"
        news_list.append(f"{idx+1}. {title}\n- {desc}\n🔗 {link}\n")

    return "\n".join(news_list)

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
    app_key = os.environ.get("APP_KEY")
    email = os.environ.get("EMAIL")
    send_to_kakaowork(app_key, email)
