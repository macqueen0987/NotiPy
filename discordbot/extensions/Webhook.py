import asyncio
from functools import partial
from typing import Optional

from commons import *
from fastapi import Request
from interactions import *

fastapi: MyFunctions = None

webhookBase = SlashCommand(name=getname("webhook"))


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

    @webhookBase.subcommand(
        sub_cmd_name=getname("set"), sub_cmd_description=getdesc("set_webhook")
    )
    @localize()
    async def set_notion_webhook(self, ctx: SlashContext, _):
        """
        Set the Notion webhook.
        """
        channelid = int(ctx.channel.id)
        guildid = int(ctx.guild_id)
        status, response = await apirequest(f"/discord/{guildid}/webhookchannel", method="PUT", json=channelid)
        if status != 200:
            raise ValueError("Error in /discord/setwebhookchannel")
        await ctx.send(_("set_webhook_channel_success"), ephemeral=True)

colors = {
    "page.content_updated": 0x7f8c8d,
    "page.created": 0xe74c3c,
    "page.deleted": 0x2ecc71,
    "page.locked": 0x9b59b6,
    "page.moved": 0x34495e,
    "page.properties_updated": 0xf1c40f,
    "page.undeleted": 0x3498db,
    "page.unlocked": 0x1abc9c,
    "database.content_updated": 0xe67e22,
    "database.created": 0xfd79a8,
    "database.deleted": 0x2d3436,
    "database.moved": 0x8e44ad,
    "database.schema_updated": 0x16a085,
    "database.undeleted": 0xf39c12,
    "comment.created": 0x2980b9,
    "comment.deleted": 0xc0392b,
    "comment.updated": 0x27ae60
}
async def notionWebhook(bot: Client, params: dict) -> None:
    """
    Notion webhook handler.
    """
    channelid = params["channelid"]
    channel = await bot.fetch_channel(channelid)
    guildid = int(channel.guild.id)
    if "verification_token" in params:
        await channel.send(
            f"Here is your verification token: ||{params["verification_token"]}||"
        )
        return
    locale = channel.guild.preferred_locale
    type_ = getlocale(params["type"], locale)
    embed = Embed(title=type_, color=colors[params["type"]],
                  description=params["workspace_name"])
    if params["pageurl"] is not None:
        embed.url = params["pageurl"]
    if params["pagetitle"] is not None:
        embed.description = params["workspace_name"] + " - " + params["pagetitle"]
    embed.set_author(name=str(params["author"]), icon_url=params["avatar_url"])
    if channel is None:
        return
    await channel.send(embeds=embed)
