from datetime import datetime, timedelta
from typing import Any, Coroutine, Optional, Sequence, Tuple

from sqlalchemy import select, Row, RowMapping

from db.models import *
from sqlalchemy.ext.asyncio import AsyncSession

from .discordservice import get_discord_server
from caches import *

notion_user_cache = get_notion_user_cache_service()
notion_page_cache = get_notion_page_cache_service()
notion_database_cache = get_notion_database_cache_service()
discord_server_cache = get_discord_server_cache_service()

async def set_notion_token(conn: AsyncSession, discordid: int, token: str) -> Optional[ServerInfo]:
    """
    Set the notion token for a user
    :param conn: database connection
    :param discordid: discord id of user
    :param token: notion token
    """
    server = await get_discord_server(conn, discordid)
    if server is None:
        return
    server.notion_token = token
    await conn.commit()
    discord_server_cache.set(discordid, server)
    return server

async def get_notion_token(conn: AsyncSession, discordid: int) -> Optional[str]:
    """
    Get the notion token for a user
    :param conn: database connection
    :param discordid: discord id of user
    :return: notion token
    """
    server = discord_server_cache.get(discordid)
    if server:
        if server.notion_token:
            return server.notion_token
    server = await get_discord_server(conn, discordid)
    return server.notion_token

async def remove_notion_token(conn: AsyncSession, discordid: int) -> None:
    """
    Remove the notion token for a user
    :param conn: database connection
    :param discordid: discord id of user
    """
    server = await get_discord_server(conn, discordid)
    server.notion_token = None
    discord_server_cache.set(discordid, server)
    await conn.commit()

async def get_notion_database(conn: AsyncSession, databaseid: str) -> Optional[NotionDatabase]:
    """
    Get the notion database for a user
    :param conn: database connection
    :param databaseid: notion database id
    :return: notion database
    """
    notionlink = notion_database_cache.get(databaseid)
    if notionlink:
        return notionlink
    query = select(NotionDatabase).where(NotionDatabase.database_id == databaseid)
    result = await conn.execute(query)
    notionlink = result.scalars().first()
    if notionlink is None:
        return None
    notion_database_cache.set(databaseid, notionlink)
    return notionlink


async def get_linked_notion_database(conn: AsyncSession, channelid: int) -> Optional[NotionDatabase]:
    """
    Get the linked notion database for a discord channel
    :param conn: database connection
    :param channelid: discord channel id
    :return: notion database
    """
    query = select(NotionDatabase).where(NotionDatabase.channel_id == channelid)
    result = await conn.execute(query)
    notionlink = result.scalars().first()
    if notionlink is None:
        return None
    notion_database_cache.set(notionlink.database_id, notionlink)
    return notionlink

async def link_notion_database(conn: AsyncSession, discordid: int, databaseid: str, channelid:int) -> None:
    """
    Link a notion database to a discord channel
    :param conn: database connection
    :param discordid: discord id of user
    :param databaseid: notion database id
    :param channelid: discord channel id
    """
    notionlink = NotionDatabase(server_id=discordid, database_id=databaseid, channel_id=channelid)
    # 캐시에서 안찾아볼겁니다. 왜냐: 캐시는 channelid를 키 값으로 사용을 안하니까요
    conn.add(notionlink)
    notion_database_cache.set(databaseid, notionlink)
    await conn.commit()

async def create_notion_page(conn: AsyncSession, pageid: str, databaseid: str) -> NotionPages:
    """
    Create a notion page
    :param conn: database connection
    :param pageid: notion page id
    :param databaseid: notion database id
    :return: notion page
    """
    notionpage = NotionPages(page_id=pageid, database_id=databaseid)
    conn.add(notionpage)
    notion_page_cache.set(pageid, notionpage)
    await conn.commit()
    return notionpage

async def get_notion_page(conn: AsyncSession, pageid: str) -> Optional[NotionPages]:
    """
    Get the notion page
    :param conn: database connection
    :param pageid: notion page id
    :return: notion page
    """
    notionpage = notion_page_cache.get(pageid)
    if notionpage:
        await conn.merge(notionpage)
        return notionpage
    query = select(NotionPages).where(NotionPages.page_id == pageid)
    result = await conn.execute(query)
    notionpage = result.scalars().first()
    if notionpage is None:
        return None
    notion_page_cache.set(pageid, notionpage)
    return notionpage

async def update_notion_page(conn: AsyncSession, pageid: str, databaseid:str) -> Optional[NotionPages]:
    """
    this sets the updated flag for a notion page
    :param conn: database connection
    :param pageid: notion page id
    :return: notion page
    """
    notionpage = await get_notion_page(conn, pageid)
    if notionpage is None:
        notionpage = await create_notion_page(conn, pageid, databaseid)
    if notionpage.updated:
        return notionpage
    notionpage.updated = True
    notion_page_cache.set(pageid, notionpage)
    await conn.commit()
    return notionpage

async def get_all_updated_pages(conn: AsyncSession) -> Sequence[Row[tuple[NotionPages, int, str]]]:
    """
    Get all updated notion pages
    :param conn: database connection
    :return: list of updated notion pages, notion database channel id, and server info notion token
    """
    query = (
        select(
            NotionPages,
            NotionDatabase.channel_id,
            ServerInfo.notion_token
        )
        .join(NotionDatabase, NotionPages.database_id == NotionDatabase.database_id)
        .join(ServerInfo, NotionDatabase.server_id == ServerInfo.server_id)
        .where(NotionPages.updated == True)
    )
    result = await conn.execute(query)
    return result.all()


async def set_thread_id(conn: AsyncSession, pageid: str, threadid: int) -> Optional[NotionPages]:
    """
    Set the thread id for a notion page
    :param conn: database connection
    :param pageid: notion page id
    :param threadid: discord thread id
    :return: notion page
    """
    print("set_thread_id", pageid, threadid)
    notionpage = await get_notion_page(conn, pageid)
    print("notionpage", notionpage)
    if notionpage is None:
        return None
    notionpage.thread_id = threadid
    await conn.commit()
    notion_page_cache.set(pageid, notionpage)
    return notionpage

async def set_pages_updated(conn: AsyncSession, threadids: Sequence[int]) -> Sequence[NotionPages] | None:
    """
    Set the updated flag for a notion page
    :param conn: database connection
    :param threadids: list of discord thread ids
    :return: notion page
    """
    query = select(NotionPages).where(NotionPages.thread_id.in_(threadids))
    result = await conn.execute(query)
    notionpages = result.scalars().all()
    if not notionpages:
        return None
    for notionpage in notionpages:
        notionpage.updated = False
        notion_page_cache.set(notionpage.page_id, notionpage)
    await conn.commit()
    return notionpages