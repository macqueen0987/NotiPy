import json

from interactions import SlashContext, LocalisedName, LocalisedDesc

from discordbot.commons.var import *
from os import listdir
from os.path import dirname, abspath, isfile, join
from functools import partial
from discordbot.commons.localization import language_codes

wd = dirname(abspath(__file__))  # 현재 작업 디렉토리 (discordbot/commons/localization.py의 위치)
rootdir = dirname(dirname(abspath(__file__)))  # 현재 작업 디렉토리 (discordbot/main.py의 위치)
logfilepath = rootdir + "/logs/"  # 로그 파일 경로
locales = {}
default_locale = "en-US"  # 기본 로케일

for file in listdir(wd+"/localization"):
    if file.endswith(".json") and isfile(join(wd+"/localization", file)):
        with open(join(wd+"/localization", file), "r", encoding="utf-8") as f:
            locales[file[:-5]] = json.load(f)


async def is_dev(ctx) -> bool:
    return ctx.author.id in developers

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