from datetime import datetime, timedelta
from typing import Any, Coroutine, Optional, Sequence

from db.models import ServerInfo
from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession
from caches import get_discord_server_cache_service

discordServerCache = get_discord_server_cache_service()

async def remove_discord_server(conn: AsyncSession, server_id: int) -> None | ServerInfo:
    query = select(ServerInfo).where(ServerInfo.server_id == server_id)
    server = await conn.execute(query)
    server = server.scalars().first()
    if not server:
        return None
    await conn.delete(server)
    await conn.commit()
    discordServerCache.delete(server_id)
    return server

async def update_discord_server(conn: AsyncSession, server_id: int) -> ServerInfo:
    """
    this updates or adds a discord server to the database
    :param conn: database connection
    :param server_id: discord server id
    :return: server info object
    """
    query = select(ServerInfo).where(ServerInfo.server_id == server_id)
    server = await conn.execute(query)
    server = server.scalars().first()
    if not server:
        server = ServerInfo(server_id=server_id)
        conn.add(server)
    else:
        server.server_id = server_id
    await conn.commit()
    discordServerCache.set(server_id, server)
    return server

async def get_discord_server(conn: AsyncSession, server_id: int) -> ServerInfo:
    """
    this gets a discord server from the database, if it does not exist it will be created
    :param conn: database connection
    :param server_id: discord server id
    :return: server info object
    """
    server = discordServerCache.get(server_id)
    if server:
        return server
    query = select(ServerInfo).where(ServerInfo.server_id == server_id)
    server = await conn.execute(query)
    server = server.scalars().first()
    if not server:
        server = await update_discord_server(conn, server_id)
    return server

async def remove_unupdated_server(conn: AsyncSession) -> None:
    """
    this deletes all servers that have not been updated in the last 24 hours
    """
    query = select(ServerInfo).where(ServerInfo.updated < datetime.now() - timedelta(days=1))
    servers = await conn.execute(query)
    servers = servers.scalars().all()
    if not servers:
        return
    for server in servers:
        await conn.delete(server)
    await conn.commit()
    return

async def set_mod_role(conn: AsyncSession, server_id: int, mod_id: int) -> Optional[ServerInfo]:
    """
    this sets the mod role for a discord server
    :param conn: database connection
    :param server_id: discord server id
    :param mod_id: discord role id
    :return: server info object
    """
    server = await get_discord_server(conn, server_id)
    server.mod_id = mod_id
    await conn.commit()
    discordServerCache.set(server_id, server)
    return server


async def get_mod_role(conn: AsyncSession, server_id: int) -> Optional[int]:
    """
    this gets the mod role for a discord server
    :param conn: database connection
    :param server_id: discord server id
    :return: discord role id
    """
    server = await get_discord_server(conn, server_id)
    return server.mod_id

async def set_webhook_channel(conn: AsyncSession, server_id: int, channel_id: int) -> Optional[ServerInfo]:
    """
    this sets the webhook channel for a discord server
    :param conn: database connection
    :param server_id: discord server id
    :param channel_id: discord channel id
    :return: server info object
    """
    server = await get_discord_server(conn, server_id)
    server.webhook_channel_id = channel_id
    await conn.commit()
    discordServerCache.set(server_id, server)
    return server