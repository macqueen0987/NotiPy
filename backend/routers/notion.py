import requests
from fastapi import APIRouter, HTTPException
from var import NOTION_DB_ID, NOTION_TOKEN

router = APIRouter(prefix="/notion", tags=["Notion"])


@router.get("/projects")
def fetch_projects():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers)
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    results = []

    for page in data.get("results", []):
        props = page.get("properties", {})

        name = (
            props.get(
                "프로젝트 이름", {}).get(
                "title", [
                    {}])[0].get(
                    "plain_text", "") if props.get(
                        "프로젝트 이름", {}).get("title") else "")

        status = props.get("상태", {}).get("status", {}).get("name", "")

        people = props.get("담당자", {}).get("people", [])
        assignee = people[0].get("name", "") if people else ""

        part = [
            tag.get(
                "name",
                "") for tag in props.get(
                "파트",
                {}).get(
                "multi_select",
                [])]

        priority = props.get("우선순위", {}).get("select", {}).get("name", "")

        rich_text = props.get("PR", {}).get("rich_text", [])
        pr = rich_text[0].get("plain_text", "") if rich_text else ""

        start_block = props.get("시작일", {}).get("date") or {}
        start = start_block.get("start", "")

        end_block = props.get("종료일", {}).get("date") or {}
        end = end_block.get("end", "")

        results.append(
            {
                "name": name,
                "status": status,
                "assignee": assignee,
                "part": part,
                "priority": priority,
                "pr": pr,
                "start": start,
                "end": end,
            }
        )

    return {"projects": results}
