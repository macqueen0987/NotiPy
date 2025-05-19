import asyncio
from typing import Optional

from commons import *
from interactions import *
from interactions.api.events import Component

#TODO: ADD task to update notion page when notion page is updated

notionBase = SlashCommand(name=getname("notion"))
notionTokenGroup = notionBase.group(name=getname("notiontoken"))
notiondbGroup = notionBase.group(name=getname("notiondb"))

def getNotionToken():
    """
    Decorator for injecting the Notion token (as a str) into a class method.\
    """
    def wrapper(func):
        @wraps(func)
        async def wrapped_func(self, ctx: SlashContext | ComponentContext, _: Callable[[str], str], *args, **kwargs):
            await ctx.defer(ephemeral=True)
            if not ctx.guild:
                raise ValueError(_("guild_only_command"))  # optional localized message

            guildid = ctx.guild_id
            status, response = await apirequest(f"/notion/getnotiontoken?serverid={guildid}")

            if status != 200 or "token" not in response:
                await ctx.send(_("notion_token_not_found"), ephemeral=True)
                return None

            notion_token = response["token"]

            # `_`는 그대로 넘기기
            return await func(self, ctx, _, notion_token, *args, **kwargs)

        return wrapped_func
    return wrapper


async def getNotionDatabases(notion_token: str) -> Optional[list[dict]]:
    """
    Get the Notion databases.
    """
    status, response = await apirequest("/notion/databases", json={"token": notion_token}, method="POST")
    if status != 200:
        return None
    data = response["data"]
    data = data["results"]
    results = []
    for result in data:
        title = result["title"][0]["plain_text"]
        url = result["url"]
        id_ = result["id"]
        results.append({"title": title, "url": url, "id": id_})
    return results


class Notion(Extension):
    bot: Client = None

    def __init__(self, bot):
        self.bot = bot

    @notionTokenGroup.subcommand(sub_cmd_name=getname("set"), sub_cmd_description=getdesc("set_notion_token"))
    @localize()
    async def set_notion_token(self, ctx: SlashContext, _):
        my_modal = Modal(ShortText(label="Notion API Token", placeholder=_("notion_token_placeholder"), required=True, custom_id="notion_token"),
                         title=_("set_notion_token"))
        await ctx.send_modal(modal=my_modal)
        modalctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)
        notion_token = modalctx.responses["notion_token"]
        data = {"token": notion_token, "serverid": ctx.guild_id}
        status, response = await apirequest("/notion/setnotiontoken", data=data, method="POST")
        if status != 200:
            raise ValueError("Error in /notion/setnotiontoken")
        await modalctx.send(_("notion_token_set"), ephemeral=True)

    @notionTokenGroup.subcommand(sub_cmd_name=getname("remove"), sub_cmd_description=getdesc("remove_notion_token"))
    @localize()
    async def remove_notion_token(self, ctx: SlashContext, _):
        status, response = await apirequest("/notion/removenotiontoken?serverid=" + str(ctx.guild_id))
        if status != 200:
            raise ValueError("Error in /notion/removenotiontoken")
        await ctx.send(_("notion_token_removed"), ephemeral=True)

    @notiondbGroup.subcommand(sub_cmd_name=getname("view"), sub_cmd_description=getdesc("view_notion_db"))
    @cooldown(Buckets.USER, 1, 10)
    @localize()
    @getNotionToken()
    async def view_notion_databases(self, ctx: SlashContext, _, notion_token: str):
        """
        Test the Notion API.
        """
        results = await getNotionDatabases(notion_token)
        if results is None:
            await ctx.send(_("notion_api_error"), ephemeral=True)
            return
        embed = Embed(title=_("notion_api_results"), color=createRandomColor())
        for result in results:
            title = result["title"]
            url = result["url"]
            embed.add_field(name=title, value=f"[{_('goto')}]({url})", inline=True)
        await ctx.send(embed=embed, ephemeral=True)

    @notiondbGroup.subcommand(sub_cmd_name=getname("connect"), sub_cmd_description=getdesc("connect_notion_db"))
    @cooldown(Buckets.USER, 1, 10)
    @localize()
    @getNotionToken()
    async def connect_notion(self, ctx: SlashContext, _, notion_token: str):
        """
        Connect to a Notion database.
        """
        # 일단 채널을 고릅니다
        results = await getNotionDatabases(notion_token)
        channelselect = ChannelSelectMenu(channel_types=[ChannelType.GUILD_TEXT, ChannelType.GUILD_FORUM],
                                          placeholder=_("select_channel"))
        message = await ctx.send(content=_("select_notion_channel"), components=channelselect, ephemeral=True)
        res = await wait_for_component_interaction(ctx, channelselect, message)
        if res is None: return
        usedctx, channel = res
        # 채널을 고른 후 notion db를 고릅니다
        dbselect = StringSelectMenu(*[StringSelectOption(label=result["title"], value=result["id"]) for result in results],
                                    placeholder=_("select_notion_db"))
        await usedctx.edit_origin(content=_("select_notion_db"), components=dbselect)
        res = await wait_for_component_interaction(usedctx, dbselect, message)
        if res is None: return
        usedctx, databaseid = res
        # 이제 고른값들을 서버에 저장합니다
        await usedctx.defer(ephemeral=True, edit_origin=True)
        channelid = int(channel.id)
        guildid = int(ctx.guild_id)
        json = {"channelid": channelid, "databaseid": databaseid, "serverid": guildid}
        status, response = await apirequest("/notion/linknotiondatabase", json=json, method="POST")
        # 서버 응답에 따라 메시지를 보냅니다
        if status == 400:
            await usedctx.edit_origin(content=_(response['message']), components=[])
            return
        if status != 200:
            raise ValueError("Error in /notion/linknotiondatabase")
        await usedctx.edit_origin(content=_("notion_db_linked"), components=[])

    @Task.create(IntervalTrigger(minutes=5))
    async def update_notion_page(self):
        """
        Update the Notion page.
        """



def setup(bot, functions):
    Notion(bot)


def teardown():
    pass
