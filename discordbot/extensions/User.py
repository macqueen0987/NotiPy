import asyncio
import os

from commons import (apirequest, devserver, getdesc, getname, githuburl,
                     localize)
from emoji.unicode_codes.data_dict import component
from interactions import (Button, ButtonStyle, Client, ComponentContext,
                          Extension, OptionType, SlashCommand, SlashContext,
                          component_callback, slash_command, slash_option)

oauth2_url = os.environ["DISCORD_OAUTH2_URL"]

githubBase = SlashCommand(
    name=getname("github"),
    description=getdesc("github"))


class User(Extension):
    bot: Client = None

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @githubBase.subcommand(
        sub_cmd_name=getname("gitlink"), sub_cmd_description=getdesc("gitlink")
    )
    @localize()
    async def gitlink(self, ctx: SlashContext, _):
        discordid = int(ctx.author.id)
        status, response = await apirequest(f"/user/get?discordid={discordid}")
        gitbuttons = [
            Button(
                style=ButtonStyle.URL,
                label=_("link_github_button"),
                url=oauth2_url),
            Button(
                style=ButtonStyle.PRIMARY,
                label=_("check_github_linked_button"),
                custom_id="check_github_linked",
            ),
        ]
        if status == 204:  # No content which means user not found, create user
            await ctx.send(_("link_github"), ephemeral=True, components=gitbuttons)
            return
        if status != 200:
            raise ValueError("Error in /user/get")
        if response["github"] is not None:
            github = response["github"]
            mainurl = githuburl + "/" + github["github_login"]
            msg = _("already_linked_github") + "\n" + mainurl
            await ctx.send(msg, ephemeral=True)
            return
        await ctx.send(_("link_github"), ephemeral=True, components=gitbuttons)

    @component_callback("check_github_linked")
    @localize()
    async def check_github_linked(self, ctx: ComponentContext, _):
        discordid = int(ctx.author.id)
        status, response = await apirequest(f"/user/get?discordid={discordid}")
        if status == 204:
            await ctx.send(_("not_linked_github"), ephemeral=True)
            return
        if status != 200:
            raise ValueError("Error in /user/get")
        github = response["github"]
        mainurl = githuburl + "/" + github["github_login"]
        await ctx.edit_origin(
            content=_("success_linked_github") + "\n" + mainurl, components=[]
        )


def setup(bot, functions):
    User(bot)


def teardown():
    pass
