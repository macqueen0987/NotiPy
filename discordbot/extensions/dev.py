from interactions import Extension, SlashContext, Client, slash_command, slash_option, OptionType
import asyncio
from discordbot.commons import devserver, localize, getname, getdesc


def decor():
    """
    get ctx
    :return:
    """
    def wrapper(func):
        async def wrapped_func(self, ctx: SlashContext, *args, **kwargs):
            print(ctx)
            return await func(self, ctx, *args, **kwargs)
        return wrapped_func
    return wrapper


class Dev(Extension):
    bot: Client = None

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.async_init())

    async def async_init(self):
        pass

    @slash_command(name=getname("ping"), description=getdesc("ping"), scopes=[devserver])
    @slash_option(name=getname("ping_opt"), description=getdesc("ping_opt"), required=False, opt_type=OptionType.BOOLEAN) # noqa
    @localize()
    async def hello(self, ctx: SlashContext, _):
        await ctx.send(_("pong"), ephemeral=True)
