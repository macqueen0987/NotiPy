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

    @listen(GuildJoin)
    async def on_guild_join(self, guild: GuildJoin):
        if not self.bot.is_ready:
            return
        guildname = guild.guild.name
        guildid = guild.guild_id
        await apirequest(f"/discord/updateserver?serverid={guildid}")
        dmchannel = await self.bot.owner.fetch_dm()
        await dmchannel.send(f"bot invited: {guildname}")

    @listen(GuildLeft)
    async def on_guild_left(self, guild: GuildLeft):
        guildname = guild.guild.name
        guildid = guild.guild_id
        await apirequest(f"/discord/removeserver?serverid={guildid}")
        dmchannel = await self.bot.owner.fetch_dm()
        await dmchannel.send(f"bot removed: {guildname}")

    @listen(Ready)
    async def on_ready(self):
        """
        on ready, update all servers, and remove servers that are not in the bot's guilds
        """
        guilds = self.bot.guilds
        for guild in guilds:
            guildid = guild.id
            await apirequest(f"/discord/updateserver?serverid={guildid}")
        await apirequest("/discord/removeoldservers")

    @modroleGroup.subcommand(sub_cmd_name=getname("set"), sub_cmd_description=getdesc("set_modrole"))
    @localize()
    @roleOption()
    async def set_modrole(self, ctx: SlashContext, _, role):
        """
        Set the moderator role for the server.
        """
        guildid = int(ctx.guild_id)
        roleid = int(role.id)
        status, response = await apirequest(f"/discord/setmodrole?serverid={guildid}&roleid={roleid}")
        if status != 200:
            raise ValueError("Error in /discord/setmodrole")
        modcache[guildid] = roleid
        await ctx.send(_("set_modrole_success"), ephemeral=True)

    @settingsBase.subcommand(sub_cmd_name=getname("view"), sub_cmd_description=getdesc("view_settings"))
    @localize()
    async def view_settings(self, ctx: SlashContext, _):
        """
        View the settings for the server.
        """
        guild = ctx.guild
        guildid = int(ctx.guild_id)
        status, response = await apirequest(f"/discord/get?serverid={guildid}")
        if status != 200:
            raise ValueError("Error in /discord/getsettings")
        if response["server"] is None:
            await ctx.send(_("no_settings"), ephemeral=True)
            return
        server = response["server"]
        mod = server["mod_id"]
        embed = Embed(title=_("settings_embed_title"), color=0x00ff00)
        if mod is None:
            mod = _("not_set")
        else:
            mod = await guild.fetch_role(mod)
            if mod is None:
                mod = _("none_role")
            else:
                mod = f"<@&{mod.id}>"
        embed.add_field(name=_("modrole"), value=mod, inline=True)
        await ctx.send(embeds=embed, ephemeral=True)





def setup(bot, functions):
    Misc(bot)