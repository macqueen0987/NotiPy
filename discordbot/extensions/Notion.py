import asyncio
from datetime import datetime, timezone
from typing import Optional

from commons import *
from interactions import *
from interactions.api.events import Component

# TODO: ADD task to update notion page when notion page is updated

notionBase = SlashCommand(name=getname("notion"))
notionTokenGroup = notionBase.group(name=getname("notiontoken"))
notiondbGroup = notionBase.group(name=getname("notiondb"))


def getNotionToken():
    """
    Decorator for injecting the Notion token (as a str) into a class method.\
    """

    def wrapper(func):
        @wraps(func)
        async def wrapped_func(
            self,
            ctx: SlashContext | ComponentContext,
            _: Callable[[str], str],
            *args,
            **kwargs,
        ):
            await ctx.defer(ephemeral=True)
            if not ctx.guild:
                # optional localized message
                raise ValueError(_("guild_only_command"))

            guildid = ctx.guild_id
            status, response = await apirequest(
                f"/notion/getnotiontoken?serverid={guildid}"
            )

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
    status, response = await apirequest(
        "/notion/databases", json={"token": notion_token}, method="POST"
    )
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
        self.update_notion_page.start()
        asyncio.create_task(self.async_init())

    async def async_init(self):
        """
        Async init function.
        """
        await self.update_notion_page()

    @notionTokenGroup.subcommand(sub_cmd_name=getname("set"),
                                 sub_cmd_description=getdesc("set_notion_token"))
    @localize()
    async def set_notion_token(self, ctx: SlashContext, _):
        my_modal = Modal(
            ShortText(
                label="Notion API Token",
                placeholder=_("notion_token_placeholder"),
                required=True,
                custom_id="notion_token",
            ),
            title=_("set_notion_token"),
        )
        await ctx.send_modal(modal=my_modal)
        modalctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)
        notion_token = modalctx.responses["notion_token"]
        data = {"token": notion_token, "serverid": ctx.guild_id}
        status, response = await apirequest(
            "/notion/setnotiontoken", data=data, method="POST"
        )
        if status != 200:
            raise ValueError("Error in /notion/setnotiontoken")
        await modalctx.send(_("notion_token_set"), ephemeral=True)

    @notionTokenGroup.subcommand(
        sub_cmd_name=getname("remove"),
        sub_cmd_description=getdesc("remove_notion_token"),
    )
    @localize()
    async def remove_notion_token(self, ctx: SlashContext, _):
        status, response = await apirequest(
            "/notion/removenotiontoken?serverid=" + str(ctx.guild_id)
        )
        if status != 200:
            raise ValueError("Error in /notion/removenotiontoken")
        await ctx.send(_("notion_token_removed"), ephemeral=True)

    @notiondbGroup.subcommand(sub_cmd_name=getname("view"),
                              sub_cmd_description=getdesc("view_notion_db"))
    @cooldown(Buckets.USER, 1, 10)
    @localize()
    @getNotionToken()
    async def view_notion_databases(
            self,
            ctx: SlashContext,
            _,
            notion_token: str):
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
            embed.add_field(name=title,
                            value=f"[{_('goto')}]({url})",
                            inline=True)
        await ctx.send(embed=embed, ephemeral=True)

    @notiondbGroup.subcommand(
        sub_cmd_name=getname("connect"),
        sub_cmd_description=getdesc("connect_notion_db"),
    )
    @cooldown(Buckets.USER, 1, 10)
    @localize()
    @getNotionToken()
    async def connect_notion(self, ctx: SlashContext, _, notion_token: str):
        """
        Connect to a Notion database.
        """
        # 일단 채널을 고릅니다
        results = await getNotionDatabases(notion_token)
        channelselect = ChannelSelectMenu(
            channel_types=[ChannelType.GUILD_TEXT, ChannelType.GUILD_FORUM],
            placeholder=_("select_channel"),
        )
        message = await ctx.send(
            content=_("select_notion_channel"), components=channelselect, ephemeral=True
        )
        res = await wait_for_component_interaction(ctx, channelselect, message)
        if res is None:
            return
        usedctx, channel = res
        # 채널을 고른 후 notion db를 고릅니다
        dbselect = StringSelectMenu(
            *[
                StringSelectOption(label=result["title"], value=result["id"])
                for result in results
            ],
            placeholder=_("select_notion_db"),
        )
        await usedctx.edit_origin(content=_("select_notion_db"), components=dbselect)
        res = await wait_for_component_interaction(usedctx, dbselect, message)
        if res is None:
            return
        usedctx, databaseid = res
        # 이제 고른값들을 서버에 저장합니다
        await usedctx.defer(edit_origin=True)
        channelid = int(channel.id)
        guildid = int(ctx.guild_id)
        json = {
            "channelid": channelid,
            "databaseid": databaseid,
            "serverid": guildid}
        status, response = await apirequest(
            "/notion/linknotiondatabase", json=json, method="POST"
        )
        # 서버 응답에 따라 메시지를 보냅니다
        if status == 400:
            await usedctx.edit_origin(content=_(response["message"]), components=[])
            return
        if status != 200:
            raise ValueError("Error in /notion/linknotiondatabase")
        await usedctx.edit_origin(content=_("notion_db_linked"), components=[])

    @Task.create(IntervalTrigger(minutes=5))
    async def update_notion_page(self):
        """
        Update the Notion page.
        """
        status, res = await apirequest("/notion/getallupdated", method="GET")
        if status == 204:
            return
        if status != 200:
            raise ValueError("Error in /notion/getallupdated")
        if res["data"] is None:
            return
        success = []
        for result in res["data"]:
            status = result["status"]
            if not status:
                continue
            channelid = result["channelid"]
            channel = await self.bot.fetch_channel(channelid)
            if not channel:
                return  # TODO: delete subscription
            embed = Embed(title=result["pagetitle"], color=createRandomColor())
            embed.url = result["pageurl"]
            embed.set_footer(
                text="Updated: "
                + datetime.now(timezone.utc).strftime("%B %d, %Y, %I:%M %p")
            )
            for key, value in result["props"].items():
                if key == "title":
                    continue
                if isinstance(value, list):
                    value = "\n".join(value)
                if value is None or value.strip() == "":
                    value = getlocale(
                        "not_set", channel.guild.preferred_locale)
                embed.add_field(name=key, value=value, inline=False)
            try:
                if isinstance(channel, GuildForum):
                    res = await self.send_to_forum(channel, result, embed)
                else:
                    res = await self.send_to_channel(channel, result, embed)
                if res:
                    success.append(res)
            except Exception as e:
                self.bot.logger.warning("Error in Notion webhook: %s", e)
        if success:
            await apirequest(
                "/notion/notionpage/updated", method="POST", json={"threadids": success}
            )

    async def send_to_forum(
            self,
            channel: GuildForum,
            pagedata: dict,
            embed: Embed):
        thread: GuildForumPost = None
        threadid = pagedata.get("threadid")
        if threadid:
            thread = await channel.fetch_post(threadid)
        if thread:
            await thread.edit(name=pagedata["pagetitle"])
            # fetch the message to edit
            message = await thread.fetch_message(threadid)
            await message.edit(embed=embed)
            return None
        thread = await channel.create_post(
            name=pagedata["pagetitle"], content="", embed=embed
        )
        await apirequest(
            f"/notion/notionpage/{pagedata['pageid']}/threadid",
            method="POST",
            json={"threadid": thread.id},
        )
        return thread.id

    async def send_to_channel(
            self,
            channel: GuildText,
            pagedata: dict,
            embed: Embed):
        message = None
        messageid = pagedata.get("threadid")
        guild = channel.guild
        if messageid:
            message = await guild.fetch_thread(messageid)
        if message:
            message = await channel.fetch_message(messageid)
            await message.edit(embed=embed)
            return None
        message = await channel.send(embed=embed)
        await message.create_thread(name=pagedata["pagetitle"])
        await apirequest(
            f"/notion/notionpage/{pagedata['pageid']}/threadid",
            method="POST",
            json={"threadid": message.id},
        )
        return message.id


def setup(bot, functions):
    Notion(bot)


def teardown():
    pass
