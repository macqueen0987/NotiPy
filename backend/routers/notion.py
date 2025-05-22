from typing import Optional, Sequence

import requests
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, HTTPException, Request, Depends, status, BackgroundTasks
from pydantic import BaseModel
from json import dumps
from common import *
from cachetools import TTLCache
from datetime import datetime, timedelta

from services import notionservice

router = APIRouter(prefix="/notion", tags=["Notion"])
from services import notionservice, discordservice

'''
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

        status = props.get("상태", {}).get("status", {}).get("name", "")yyy

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
'''

class notionItems(BaseModel):
    """
    Pydantic model for Notion items.
    don't do this. this is a very bad example of how to use pydantic
    """
    token: Optional[str] = None
    databaseid: Optional[str] = None
    serverid: Optional[int] = None
    channelid: Optional[int] = None
    threadid: Optional[int] = None
    updated: Optional[bool] = None

@router.post("/databases")
@checkInternalServer
async def fetch_databases(request: Request, token: notionItems, conn=Depends(get_db)):
    """
    get all databases the token has access to
    """
    url = NOTION_API_URL + "/search"
    headers = notionHeaders(token.token)
    data = {
        "filter": {
            "property": "object",
            "value": "database"
        },
        "query": ""
    }
    statuscode, response = await make_request(url=url, headers=headers, method="POST", json=data, internal=False)
    if statuscode != 200:
        raise HTTPException(status_code=statuscode, detail=response)
    return JSONResponse(content={"status": "success", "data": response})

@router.post("/database")
@checkInternalServer
async def fetch_database(request: Request, items:notionItems, conn=Depends(get_db)):
    """
    Fetch the database from Notion.
    """
    url = NOTION_API_URL + f"/databases/{items.databaseid}"
    status, response = await make_request(url=url, headers=notionHeaders(items.token), method="GET")
    if status != 200:
        raise HTTPException(status_code=status, detail=response)
    return JSONResponse(content={"status": "success", "data": response})


@router.post("/setnotiontoken")
@checkInternalServer
async def set_token(request: Request, items:notionItems, conn=Depends(get_db)):
    """
    Set the Notion token.
    """
    if not items.token:
        raise HTTPException(status_code=400, detail="Token is required")
    # Save the token to the database
    await notionservice.set_notion_token(conn, items.serverid, items.token)
    return JSONResponse(content={"status": "success", "message": "Token set successfully"})

@router.get("/getnotiontoken")
@checkInternalServer
async def get_token(request: Request, serverid:int, conn=Depends(get_db)):
    """
    Get the Notion token.
    """
    # Fetch the token from the database
    token = await notionservice.get_notion_token(conn, serverid)
    if not token:
        return JSONResponse(content="", status_code=status.HTTP_204_NO_CONTENT) # 204 No Content
    return JSONResponse(content={"status": "success", "token": token})

@router.get("/removenotiontoken")
@checkInternalServer
async def remove_token(request: Request, serverid:int, conn=Depends(get_db)):
    """
    Remove the Notion token.
    """
    # Remove the token from the database
    await notionservice.remove_notion_token(conn, serverid)
    return JSONResponse(content={"status": "success", "message": "Token removed successfully"})


@router.post("/linknotiondatabase")
@checkInternalServer
async def notion_database_linked(request: Request, items:notionItems, conn=Depends(get_db)):
    """
    Link the Notion database to the server.
    """
    res = await notionservice.get_linked_notion_database(conn, items.channelid)
    if res is not None:
        return JSONResponse(content={"status": "error", "message": "channel_already_linked"}, status_code=400)
    await notionservice.link_notion_database(conn, items.serverid, items.databaseid, items.channelid)
    return JSONResponse(content={"status": "success", "message": "Database linked successfully"})


@router.get("/getuser")
async def get_user(request: Request, notionuserid: str, token: str, conn=Depends(get_db)):
    """
    Get the user information from Notion.
    """
    res = await get_user_func(notionuserid, token)
    if res:
        return JSONResponse(content={"status": "success", "data": res})
    return JSONResponse(content={"status": "error", "message": "User not found"})

@router.get("/getpage")
async def get_page(request: Request, pageid: str, token: str, forcereload: bool = False, conn=Depends(get_db)):
    """
    Get the page information from Notion.
    """
    res = await get_page_func(pageid, token, forcereload)
    if res:
        return JSONResponse(content={"status": "success", "data": res})
    return JSONResponse(content={"status": "error", "message": "Page not found"})

@router.post("/notionpage/{pageid}/threadid")
@checkInternalServer
async def set_thread_id(request: Request, pageid: str, items: notionItems, conn=Depends(get_db)):
    """
    Set the thread ID for the Notion page.
    """
    # Update the thread ID in the database
    res = await notionservice.set_thread_id(conn, pageid, items.threadid)
    return JSONResponse(content={"status": "success", "message": "Thread ID set successfully"})

class threadIDs(BaseModel):
    threadids: Sequence[int]
@router.post("/notionpage/updated")
@checkInternalServer
async def set_page_updated(request: Request, items: threadIDs, conn=Depends(get_db)):
    await notionservice.set_pages_updated(conn, items.threadids)
    return JSONResponse(content={"status": "success", "message": "Page updated successfully"})

@router.get("/getallupdated")
@checkInternalServer
async def get_all_updated(request:Request, conn=Depends(get_db)):
    """
    Get all updated pages from the database.
    """
    res = await notionservice.get_all_updated_pages(conn)
    if not res: return Response(status_code=status.HTTP_204_NO_CONTENT)
    returndict = []
    for row in res:
        page, channelid, token = row
        # Notion 페이지 정보 조회
        pagedict = {'pageid': page.page_id, 'threadid': page.thread_id, "channelid": channelid, 'status': True}
        pagedata = await get_page_func(page.page_id, token, forcereload=True)
        if pagedata:
            # 페이지 제목과 URL 파싱
            prop = pagedata['properties']
            pagedict['pageurl'] = pagedata['url']
            pagedict['props'] = {}
            for item in prop:
                if prop[item]['type'] == "title":
                    pagedict['pagetitle'] = prop[item]['title'][0]['plain_text']
                else:
                    match prop[item]['type']:
                        case "rich_text":
                            pagedict['props'][item] = prop[item]['rich_text'][0]['plain_text'] if prop[item]['rich_text'] else ""
                        case "select":
                            pagedict['props'][item] = prop[item]['select']['name'] if prop[item]['select'] else ""
                        case "multi_select":
                            pagedict['props'][item] = [tag['name'] for tag in prop[item]['multi_select']]
                        case "checkbox":
                            pagedict['props'][item] = prop[item]['checkbox']
                        case "number":
                            pagedict['props'][item] = prop[item]['number']
                        case "date":
                            if prop[item]['date'] is not None:
                                start = prop[item]['date']['start']
                                end = prop[item]['date']['end']
                                if start and end:
                                    pagedict['props'][item] = f"{start} ~ {end}"
                                elif start:
                                    pagedict['props'][item] = start
                                elif end:
                                    pagedict['props'][item] = end
                        case "people":
                            pagedict['props'][item] = [user['name'] for user in prop[item]['people']]
                        case "files":
                            pagedict['props'][item] = [file['name'] for file in prop[item]['files']]
                        case "url":
                            pagedict['props'][item] = prop[item]['url']
                        case 'status':
                            pagedict['props'][item] = prop[item]['status']['name'] if prop[item]['status'] else ""
                        case _:
                            print(f"Unknown type: {prop[item]['type']}")
                            pagedict['props'][item] = prop[item]['type'] + " under dev"
            # 페이지 정보 추가
            returndict.append(pagedict)
        else:
            pagedict["status"] = False
            # 페이지 정보를 노션에서 가져오지 못한 경우
            # 주로 페이지가 삭제된 경우 -> 디스코드에서도 적절히 조치

    # 결과를 JSON 형식으로 반환
    return JSONResponse(content={"status": "success", "data": returndict})


@router.post("/webhook/{serverid}")
async def notion_webhook_listener(request: Request, serverid: int, conn=Depends(get_db)):
    """
    Webhook listener for Notion events, intended to forward the data to a Discord bot.
    """
    webhookdata = {}
    # 해당 serverid의 Discord 서버 정보 조회 (DB에서)
    server = await discordservice.get_discord_server(conn, serverid)
    webhookdata["channelid"] = server.webhook_channel_id  # 메시지를 보낼 디스코드 채널 ID
    # Webhook 요청 본문을 JSON으로 파싱
    data = await request.json()
    # Webhook 인증 요청 처리 (verification_token 포함 여부 확인)
    if "verification_token" in data:
        webhookdata["verification_token"] = data["verification_token"]
    else:
        # 일반 웹훅 이벤트 처리
        author = data['authors'][0]['id']
        webhookdata['avatar_url'] = None
        # Notion 토큰 조회 (서버에 연결된 토큰)
        token = await notionservice.get_notion_token(conn, serverid)
        if not token:
            return JSONResponse(content={"status": "error", "message": "No token found"}, status_code=400)
        # Notion 사용자 정보 조회 (작성자)
        userdata = await get_user_func(author, token)
        if userdata:
            webhookdata['author'] = userdata['name']
            if userdata['avatar_url']:
                webhookdata['avatar_url'] = userdata['avatar_url']
        # 공통 필드 저장
        webhookdata["entity"] = data['entity']
        webhookdata["type"] = data["type"]
        webhookdata["timestamp"] = data["timestamp"]
        webhookdata["workspace_name"] = data["workspace_name"]
        # 페이지 관련 정보 기본값 초기화
        webhookdata['pageurl'] = None
        webhookdata['pagetitle'] = None
        webhookdata['pageid'] = None
        webhookdata['parentid'] = None
        # 웹훅 엔티티가 페이지일 경우 추가 정보 처리
        if data['entity']['type'] == "page":
            pageid = data['entity']['id']
            webhookdata['pageid'] = pageid
            if data['data']['parent']['type'] == "database":
                parentid = data['data']['parent']['id']
                # 부모 데이터베이스 캐시 조회 + 추후 디스코드에 정보 전송을 위해 업데이트 플래그 설정
                res = await notionservice.get_notion_database(conn, parentid)
                if res:
                    await updatePage(conn, pageid, parentid)
            # 페이지 정보 가져와서 제목과 URL 파싱
            pagedata = await get_page_func(pageid, token)
            if pagedata:
                for item in pagedata['properties']:
                    if pagedata['properties'][item]['type'] == "title":
                        webhookdata['pagetitle'] = pagedata['properties'][item]['title'][0]['text']['content']
                webhookdata['pageurl'] = pagedata['url']
    # webhookdata를 JSON 문자열로 직렬화
    webhookdata = json.dumps(webhookdata)
    # 채널이 연결되어 있는지 확인 (없으면 에러)
    if server.webhook_channel_id is None:
        return JSONResponse(content={"status": "error", "message": "No channel linked"}, status_code=400)
    # Discord bot 서버에 요청 전송 (notion webhook 전달)
    url = discordbot + DISCORD_APP_ROOT + f"/call/notionwebhook"
    status_code, response = await make_request(method="GET", url=url, params={"params": webhookdata})
    # 요청 결과에 따라 성공/실패 응답 반환
    if status_code != 200:
        return JSONResponse({"status": "error", "message": response}, status_code=status_code)
    return JSONResponse(content={"message": "Webhook received"})


#======================================================================

page_cache = TTLCache(maxsize=100, ttl=60 * 60)  # 1 hour
async def get_page_func(pageid: str, token: str, forcereload: bool = False) -> Optional[dict]:
    """
    Get the page information from Notion.
    """
    if not forcereload:
        cached = page_cache.get(pageid)
        if cached:
            return cached
    url = NOTION_API_URL + f"/pages/{pageid}"
    statuscode, response = await make_request(url=url, headers=notionHeaders(token), method="GET", internal=False)
    if statuscode != 200:
        raise None
    page_cache[pageid] = response
    return response

user_cache = TTLCache(maxsize=100, ttl=12 * 60 * 60)
async def get_user_func(notionuserid: str, token: str):
    """
    Get the user information from Notion.
    """
    response = user_cache.get(notionuserid)
    if response:
        return response
    url = NOTION_API_URL + f"/users/{notionuserid}"
    statuscode, response = await make_request(url=url, headers=notionHeaders(token), method="GET", internal=False)
    if statuscode != 200:
        raise None
    user_cache[notionuserid] = response
    return response

async def updatePage(conn, pageid: str, databaseid: str):
    """
    mark the page need to update
    """
    await notionservice.update_notion_page(conn, pageid, databaseid)
    return JSONResponse(content={"status": "success", "message": "Page updated successfully"})
