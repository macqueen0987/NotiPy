import asyncio

from commons import *
from interactions import *
from interactions.api.events import GuildJoin, GuildLeft, Ready

settingsBase = SlashCommand(name=getname("settings"))
modroleGroup = settingsBase.group(name=getname("modrole"))


class Misc(Extension):
    bot: Client = None

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        """
        on ready, update all servers, and remove servers that are not in the bot's guilds
        """
        guilds = self.bot.guilds
        guilids = [int(guild.id) for guild in guilds]
        await apirequest(f"/discord/clean", json=guilids, method="POST")

    @listen(GuildJoin)
    async def on_guild_join(self, guild: GuildJoin):
        if not self.bot.is_ready:
            return
        guildname = guild.guild.name
        guildid = guild.guild_id
        await apirequest(f"/discord/{guildid}", method="POST")
        dmchannel = await self.bot.owner.fetch_dm(force=True)
        await dmchannel.send(f"bot invited: {guildname}")

    @listen(GuildLeft)
    async def on_guild_left(self, guild: GuildLeft):
        guildname = guild.guild.name
        guildid = guild.guild_id
        await apirequest(f"/discord/{guildid}", method="DELETE")
        dmchannel = await self.bot.owner.fetch_dm(force=True)
        await dmchannel.send(f"bot removed: {guildname}")

    @modroleGroup.subcommand(
        sub_cmd_name=getname("set"), sub_cmd_description=getdesc("set_modrole")
    )
    @check(is_moderator)
    @localize()
    @roleOption()
    async def set_modrole(self, ctx: SlashContext, _, role):
        """
        Set the moderator role for the server.
        """
        guildid = int(ctx.guild_id)
        roleid = int(role.id)
        status, response = await apirequest(endpoint=f"/discord/{guildid}/modrole", method="PUT", json=roleid)
        if status != 200:
            raise ValueError(f"Error in /discord/{guildid}/modrole")
        modcache[guildid] = roleid
        await ctx.send(_("set_modrole_success"), ephemeral=True)

    @settingsBase.subcommand(sub_cmd_name=getname("view"),
                             sub_cmd_description=getdesc("view_settings"))
    @check(is_moderator)
    @localize()
    async def view_settings(self, ctx: SlashContext, _):
        """
        View the settings for the server.
        """
        guild = ctx.guild
        guildid = int(ctx.guild_id)
        status, response = await apirequest(f"/discord/{guildid}", params={"eager_load": 1})
        if status != 200:
            raise ValueError(f"Error in /discord/{guildid}")
        if response["server"] is None:
            await ctx.send(_("no_settings"), ephemeral=True)
            return
        server = response["server"]
        mod = server["mod_id"]
        embed = Embed(title=_("settings_embed_title"), color=0x00FF00)
        if mod is None:
            mod = _("not_set")
        else:
            mod = await guild.fetch_role(mod)
            if mod is None:
                mod = _("none_role")
            else:
                mod = f"<@&{mod.id}>"
        embed.add_field(name=_("modrole"), value=mod, inline=True)
        webhookchannel = server["webhook_channel_id"]
        if webhookchannel is None:
            webhookchannel = _("not_set")
        else:
            webhookchannel = await guild.fetch_channel(webhookchannel)
            if webhookchannel is None:
                webhookchannel = _("none_channel")
            else:
                webhookchannel = webhookchannel.mention
        embed.add_field(name=_("webhook_channel"), value=webhookchannel, inline=True)
        notiontoken = server["notion_token"]
        if notiontoken is None:
            notiontoken = _("not_set")
        else:
            notiontoken = _("setted")
        embed.add_field(name=_("notiontoken"), value=notiontoken, inline=True)
        notion_tags = server["notion_tags"]
        tags = []
        for tag in notion_tags:
            tags.append(tag["tag"])
        if not tags:
            tags = [_("not_set")]
        else:
            tags = ", ".join(tags)
        embed.add_field(name=_("notiontag"), value=tags, inline=True)
        notion_databases = server["notion_databases"]
        databases = []
        for database in notion_databases:
            channel = database['channel_id']
            channel = await guild.fetch_channel(channel)
            if channel is None:
                channel = _("none_channel")
            else:
                channel = channel.mention
            msg = f"{database['database_name']} → {channel}"
            databases.append(msg)
        if not databases:
            databases = [_("not_set")]
        else:
            databases = "\n".join(databases)
        embed.add_field(name=_("notion_databases"), value=databases, inline=False)
        await ctx.send(embeds=embed, ephemeral=True)


def setup(bot, functions):
    Misc(bot)
