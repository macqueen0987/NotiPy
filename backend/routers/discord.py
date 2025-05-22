from common import *
from fastapi import (APIRouter, BackgroundTasks, Depends, Request, Response,
                     status)
from fastapi.responses import JSONResponse
from services import discordservice as crud

router = APIRouter(prefix="/discord", tags=["Discord"])


@router.get("/get")
@checkInternalServer
async def get_server(request: Request, serverid: int, conn=Depends(get_db)):
    """
    Get a Discord server by its ID.
    """
    server = await crud.get_discord_server(conn, serverid)
    if not server:
        return JSONResponse("", status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse({"success": True, "server": server.todict()})


@router.get("/updateserver")
@checkInternalServer
async def add_server(request: Request, serverid: int, conn=Depends(get_db)):
    """
    Update or add a Discord server to the database.
    """
    await crud.update_discord_server(conn, serverid)
    return JSONResponse({"success": True})


@router.get("/removeserver")
@checkInternalServer
async def remove_server(request: Request, serverid: int, conn=Depends(get_db)):
    await crud.remove_discord_server(conn, serverid)
    return JSONResponse({"success": True})


@router.get("/removeoldservers")
@checkInternalServer
async def remove_old_servers(request: Request, conn=Depends(get_db)):
    await crud.remove_unupdated_server(conn)
    return JSONResponse({"success": True})


@router.get("/getmodrole")
@checkInternalServer
async def get_mod_role(request: Request, serverid: int, conn=Depends(get_db)):
    """
    Get the mod role for a Discord server.
    """
    modrole = await crud.get_mod_role(conn, serverid)
    if not modrole:
        return JSONResponse("", status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse({"success": True, "modrole": modrole})


@router.get("/setmodrole")
@checkInternalServer
async def set_mod_role(
    request: Request, serverid: int, roleid: int, conn=Depends(get_db)
):
    """
    Set the mod role for a Discord server.
    """
    print(roleid)
    server = await crud.set_mod_role(conn, serverid, roleid)
    print(server.mod_id)
    print("==========================")
    if not server:
        return JSONResponse("", status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse({"success": True, "server": server.todict()})


@router.get("/setwebhookchannel")
@checkInternalServer
async def set_webhook_channel(
    request: Request, serverid: int, channelid: int, conn=Depends(get_db)
):
    """
    Set the webhook channel for a Discord server.
    """
    server = await crud.set_webhook_channel(conn, serverid, channelid)
    if not server:
        return JSONResponse("", status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse({"success": True, "server": server.todict()})
