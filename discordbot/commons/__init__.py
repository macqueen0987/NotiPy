import inspect
import json

from interactions import SlashContext, LocalisedName, LocalisedDesc
from typing import Callable, Awaitable, Any, Coroutine
from commons.var import *
from os import listdir
from os.path import dirname, abspath, isfile, join
from functools import partial
from commons.localization import language_codes

wd = dirname(abspath(__file__))  # 현재 작업 디렉토리 (discordbot/commons/localization.py의 위치)
rootdir = dirname(dirname(abspath(__file__)))  # 현재 작업 디렉토리 (discordbot/main.py의 위치)
logfilepath = rootdir + "/logs/"  # 로그 파일 경로
locales = {}
default_locale = "en-US"  # 기본 로케일
AsyncFuncType = Callable[..., Coroutine[Any, Any, Any]]

for file in listdir(wd+"/localization"):
    if file.endswith(".json") and isfile(join(wd+"/localization", file)):
        with open(join(wd+"/localization", file), "r", encoding="utf-8") as f:
            locales[file[:-5]] = json.load(f)


async def is_dev(ctx) -> bool:
    return int(ctx.author.id) in developers

def localize():
    """
    Decorator for localizing slash commands.
    """
    def wrapper(func):
        async def wrapped_func(self, ctx: SlashContext, *args, **kwargs):
            if not ctx.guild:
                return
            locale = ctx.locale
            if locale not in locales:
                locale = ctx.guild.preferred_locale
            return await func(self, ctx, localizator(locale), *args, **kwargs)
        return wrapped_func
    return wrapper

def localizator(locale):
    return partial(getlocale, locale=locale)

def getlocale(key_, locale) -> str:
    if key_ in locales[locale]:
        return locales[locale][key_]
    if key_ in locales[default_locale]:
        return locales[default_locale][key_]
    return key_


def getname(name) -> LocalisedName:
    """
    Create a LocalisedName object for the given name.
    """
    names = {}
    for locale in locales:
        if name in locales[locale]:
            names[language_codes[locale]] = locales[locale][name]

    return LocalisedName(**names)

def getdesc(name) -> LocalisedDesc:
    """
    Create a LocalisedDesc object for the given name.
    """
    name += "_desc"
    descs = {}
    for locale in locales:
        if name in locales[locale]:
            descs[language_codes[locale]] = locales[locale][name]

    return LocalisedDesc(**descs)

class MyFunctions:
    logger = None
    def __init__(self, logger):
        self.logger = logger

    def set(self, name, value: AsyncFuncType) -> None:
        """
        Set the function by name
        :param name: name of the function
        :param value: Async function that will be called
        """
        if not inspect.iscoroutinefunction(value):
            raise ValueError(f"{name} is not a coroutine function")
        setattr(self, name, value)

    def remove(self, name: str) -> None:
        """
        Remove the function by name
        :param name: name of the function
        """
        if hasattr(self, name):
            delattr(self, name)
        print(f"Function {name} removed")
        print(f"Functions: {dir(self)}")

    def get(self, name) -> AsyncFuncType or None:
        """
        Get the function by name
        :param name: name of the function
        :return: function
        """
        return getattr(self, name)

    async def run(self, name: str, **kwargs):
        """
        Run the function by name
        :param name: name of the function
        :param args: arguments to pass to the function
        :param kwargs: keyword arguments to pass to the function
        :return: result of the function
        """
        func = self.get(name)
        if func is None:
            return None
        try:
            result = await func(**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error running function {name}: {e}")
            return None