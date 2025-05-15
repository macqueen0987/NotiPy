import asyncio
from functools import partial

from commons import devserver, getdesc, getname, localize, MyFunctions, makerequest, notion_token
from interactions import Client, Extension, OptionType, SlashContext, slash_command, slash_option, Embed
from fastapi import Request


fastapi: MyFunctions = None
class Webhook(Extension):
    bot: Client = None
    functions: MyFunctions = None

    def __init__(self, bot: Client, functions: MyFunctions):
        self.bot = bot
        self.functions = functions
        self.functions.set("notionwebhook", notionWebhook)

    def drop(self) -> None:
        """
        Drop the extension.
        """
        self.functions.remove("notionwebhook")
        super().drop()

notion_webhook_events = {
    "page.content_updated": "페이지 내용이 변경됨",
    "page.created": "페이지가 생성됨",
    "page.deleted": "페이지가 삭제됨",
    "page.locked": "페이지가 잠김",
    "page.moved": "페이지가 이동됨",
    "page.properties_updated": "페이지 속성이 업데이트됨",
    "page.undeleted": "페이지가 복원됨",
    "page.unlocked": "페이지 잠금이 해제됨",
    "database.content_updated": "데이터베이스 내용이 업데이트됨",
    "database.created": "데이터베이스가 생성됨",
    "database.deleted": "데이터베이스가 삭제됨",
    "database.moved": "데이터베이스가 이동됨",
    "database.schema_updated": "데이터베이스 스키마가 업데이트됨",
    "database.undeleted": "데이터베이스가 복원됨",
    "comment.created": "댓글이 생성됨",
    "comment.deleted": "댓글이 삭제됨",
    "comment.updated": "댓글이 수정됨"
}

async def notionWebhook(bot: Client, params:dict) -> None:
    """
    Notion webhook handler.
    """
    channelid = params['target_discord_channelid']
    del params['target_discord_channelid']
    channel = await bot.fetch_channel(channelid)
    if "verification_token" in params:
        await channel.send("Here is your verification token: "+params['verification_token'])
        return
    workspacename = params['workspace_name']
    authorid = params['authors'][0]['id']
    entityid = params['entity']
    type_ = notion_webhook_events[params['type']]
    timestamp = params['timestamp']
    if channel is None:
        return
    header = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28"
    }
    # TODO: Notion-Version should be in env file
    status, response = await makerequest(f"https://api.notion.com/v1/users/{authorid}", "GET", headers=header)
    if status != 200:
        return
    author = response['name']
    avatar_url = response['avatar_url']
    embed = Embed(title=type_, description="Workspace: "+workspacename, color=0x00ff00)
    embed.set_author(name=author, icon_url=avatar_url)
    embed.add_field(name="Entity ID", value=entityid, inline=False)
    embed.set_footer(text=f"timestamp: {timestamp}")
    await channel.send(embeds=embed)
    return {"status": "ok"}
