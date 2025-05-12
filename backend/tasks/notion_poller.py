import requests
import time
from var import NOTION_TOKEN, NOTION_DB_ID

# 전역 캐시
last_known_ids = set()

def poll_notion_projects(interval: int = 30):
    """
    주기적으로 Notion DB를 폴링하여 새로운 프로젝트를 감지합니다.
    :param interval: 폴링 주기(초)
    """
    global last_known_ids

    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    while True:
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 현재 페이지 ID 집합 추출
            current_ids = {page.get("id") for page in data.get("results", [])}

            # 새로 추가된 ID 감지
            new_ids = current_ids - last_known_ids
            if new_ids:
                print(f"[🔔] New projects detected: {new_ids}")
                # TODO: Discord 전송 기능 호출 가능

            # 캐시 업데이트
            last_known_ids = current_ids

        except Exception as e:
            print(f"[⚠️] Error while polling Notion: {e}")

        # 다음 폴링까지 대기
        time.sleep(interval)
