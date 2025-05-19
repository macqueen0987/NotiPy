from interactions import slash_option, OptionType

from .locale import getname, getdesc


def roleOption():
    def wrapper(func):
        return slash_option(name=getname("role"), description=getdesc("role"), opt_type=OptionType.ROLE, required=True)(func)
    return wrapper

def channelOption():
    def wrapper(func):
        return slash_option(name=getname("channel"), description=getdesc("channel"), opt_type=OptionType.CHANNEL, required=True)(func)
    return wrapper

def plainTextOption(name:str = "text"):
    def wrapper(func):
        return slash_option(name=getname(name), description=getdesc(name), opt_type=OptionType.STRING, required=True)(func)
    return wrapper