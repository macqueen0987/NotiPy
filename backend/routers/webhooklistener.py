import json

from common import DISCORD_APP_ROOT, discordbot, make_request
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/webhooklistener", tags=["webhooklistener"])


@router.post("/notion/{discordchannelid}")
async def notion_webhook_listener(request: Request, discordchannelid: int):
    """
    Webhook listener for Notion.
    """
    data = await request.json()
    data["target_discord_channelid"] = discordchannelid
    data = json.dumps(data)
    # Process the data as needed
    url = discordbot + DISCORD_APP_ROOT + f"/call/notionwebhook"
    status, response = await make_request(
        method="GET", url=url, params={"params": data}
    )
    if status != 200:
        return JSONResponse(
            {"status": "error", "message": response}, status_code=status
        )
    return JSONResponse(content={"message": "Webhook received"})
