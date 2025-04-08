import json
from functools import wraps

from aiohttp import BasicAuth, ClientSession
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from var import *

engine = create_async_engine(
    f"mysql+aiomysql://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}",
    echo=False,
    future=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


discord_auth = BasicAuth(CLIENT_ID, CLIENT_SECRET)


async def make_request(
    method: str,
    url: str,
    params: dict = None,
    data: dict = None,
    headers: dict = None,
    auth: BasicAuth = None,
) -> (int, dict | str):
    """
    Make a request url
    :param method: HTTP method (GET, POST, etc.)
    :param url: URL endpoint
    :param params: Query parameters
    :param data: Request body
    :param headers: Additional headers
    :param auth: Basic authentication credentials
    :return: tuple of response status and response data
    """
    async with ClientSession() as session:
        async with session.request(
            method, url, headers=headers, params=params, data=data, auth=auth
        ) as response:
            response_status = response.status
            response_data = await response.json()
            return response_status, response_data


def checkInternalServer(func):
    """
    Decorator to check if the request is from the internal server.
    """

    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        print(request.headers)
        if request.headers.get("X-Internal-Request") != "true":
            return JSONResponse(
                content={
                    "message": "Unauthorized"},
                status_code=401)
        return await func(request, *args, **kwargs)

    return wrapper
