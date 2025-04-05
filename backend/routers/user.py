from functools import partial
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from common import make_request, DISCORD_API_ENDPOINT, REDIRECT_URI, discord_auth, get_db, GITHUB_TOKEN, GITHUB_API_ENDPOINT
from functools import wraps
from datetime import datetime

from CRUDS import usercrud as crud

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def root(request: Request):
    return JSONResponse(content={"message": "Hello World from User!"})


def checkTokenExpired(func):
    """
    Decorator to check if the token is expired.
    """
    @wraps(func)
    async def wrapper(conn, tokens:crud.Tokens):
        user = await crud.get_user_by_token(conn, access_token=tokens.access_token)
        refreshed = True
        if user:
            refreshed = False
            if user.token_expires is not None:
                if user.token_expires < datetime.now():
                    tokens = await refresh_token(tokens)
                    refreshed = True
        return await func(conn, tokens, refreshed)
    return wrapper


@router.get("/auth")
async def auth(code: str, background_tasks: BackgroundTasks, conn=Depends(get_db)):
    """
    Authenticates the user with Discord using the provided code.
    :param code: The authorization code received from Discord
    :return: JSON response with the access token and user information
    """
    background_tasks.add_task(exchange_code, conn=conn, code=code)
    return JSONResponse(content={"message": "Success!"})


async def exchange_code(conn, code: str):
    """
    Exchanges the authorization code for an access token.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, response = await make_request("POST", f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers, auth=discord_auth)
    if status != 200:
        return
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]
    expires_in = response["expires_in"]
    tokens = crud.Tokens(access_token, refresh_token, expires_in)
    await get_user_info(conn, tokens)


async def refresh_token(tokens:crud.Tokens) -> crud.Tokens:
    """
    Refreshes the access token using the refresh token.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens.refresh_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, response = await make_request("POST", f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers, auth=discord_auth)
    if status != 200:
        return
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]
    expires_in = response["expires_in"]
    tokens = crud.Tokens(access_token, refresh_token, expires_in)
    return tokens


@checkTokenExpired
async def get_user_info(conn, tokens: crud.Tokens, refreshed: bool = False):
    """
    Retrieves user information from Discord using the access token.
    Then uses github id and github api to and login.
    store github id and login in database.
    :param tokens: tokens object containing access_token, refresh_token and expires_in
    :param refreshed: if the token was refreshed
    """
    headers = {"Authorization": f"Bearer {tokens.access_token}"}
    status, response = await make_request("GET", f"{DISCORD_API_ENDPOINT}/users/@me", headers=headers)
    if status != 200: return
    discordid = int(response["id"])
    if refreshed:
        await crud.setTokens(conn, discordid, tokens)
    status, response = await make_request("GET", f"{DISCORD_API_ENDPOINT}/users/@me/connections", headers=headers)
    if status != 200: return
    githubid = None
    for i in response:
        if i["type"] == "github":
            githubid = i["id"]
            break
    # headers = {"Authorization": "Bearer " + GITHUB_TOKEN} # Works without this... damn
    status, response = await make_request("GET", f"{GITHUB_API_ENDPOINT}/user/{githubid}")
    if status != 200: return
    gitlogin = response["login"]
    await crud.link_github(conn, discordid, githubid, gitlogin)
    return response
