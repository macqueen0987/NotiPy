from functools import partial, wraps
from os import listdir
import json
from os.path import abspath, dirname, isfile, join
from typing import Callable
from .localization import language_codes
from interactions import LocalisedName, LocalisedDesc, SlashContext, ComponentContext

locales = {}
default_locale = "en-US"  # 기본 로케일

wd = dirname(
    abspath(__file__)
)  # 현재 작업 디렉토리 (discordbot/commons/localization.py의 위치)
for file in listdir(wd + "/localization"):
    if file.endswith(".json") and isfile(join(wd + "/localization", file)):
        with open(join(wd + "/localization", file), "r", encoding="utf-8") as f:
            locales[file[:-5]] = json.load(f)


def localize():
    """
    Decorator for localizing slash commands.
    """

    def wrapper(func):
        @wraps(func)
        async def wrapped_func(
            self, ctx: SlashContext | ComponentContext, *args, **kwargs
        ):
            if not ctx.guild:
                raise ValueError("This command can only be used in a server.")
                return
            locale = ctx.locale
            if locale not in locales:
                locale = ctx.guild.preferred_locale
            return await func(self, ctx, localizator(locale), *args, **kwargs)

        return wrapped_func

    return wrapper


def localizator(locale) -> Callable[[str], str]:
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
    if default_locale not in names:
        names[language_codes[default_locale]] = name
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
    if default_locale not in descs:
        descs[language_codes[default_locale]] = name
    return LocalisedDesc(**descs)

