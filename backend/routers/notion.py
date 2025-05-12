from fastapi import APIRouter, HTTPException
import requests
from var import NOTION_TOKEN, NOTION_DB_ID

router = APIRouter(prefix="/notion", tags=["Notion"])

@router.get("/users")
def fetch_notion_users():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    users = []
    for page in response.json().get("results", []):
        props = page.get("properties", {})
        name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "")
        github = props.get("GitHub ID", {}).get("rich_text", [{}])[0].get("plain_text", "")
        discord = props.get("Discord Tag", {}).get("rich_text", [{}])[0].get("plain_text", "")
        users.append({
            "name": name,
            "github": github,
            "discord": discord
        })

    return {"users": users}
