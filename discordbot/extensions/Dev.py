import asyncio

from commons import devserver, getdesc, getname, localize
from interactions import (Client, Extension, OptionType, SlashContext,
                          slash_command, slash_option)


class Dev(Extension):
    bot: Client = None

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @slash_command(
        name=getname("ping"), description=getdesc("ping"), scopes=[devserver]
    )
    @slash_option(
        name=getname("ping_opt"),
        description=getdesc("ping_opt"),
        required=False,
        opt_type=OptionType.BOOLEAN,
    )  # noqa
    @localize()
    async def hello(self, ctx: SlashContext, _):
        await ctx.send(_("pong"), ephemeral=True)


def setup(bot, functions):
    Dev(bot)


def teardown():
    pass
