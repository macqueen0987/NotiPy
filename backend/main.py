import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from var import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, API_ENDPOINT
from datetime import datetime
import db.models as models
from common import get_db

app = FastAPI()
auth = aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET)

@app.get("/")
async def root(request: Request, bgtask: BackgroundTasks, code: str = None):
    print(request.headers)
    bgtask.add_task(exchange_code, code)
    return JSONResponse({"hello": "world"})

async def exchange_code(code: str):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {"content-type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers, auth=auth) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return
            data = await response.json()
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            print(await response.json())
    await get_connected(access_token)

async def get_connected(access_token:str):
    headers = {"content-type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{API_ENDPOINT}/users/@me/connections', headers=headers) as response:
            print(response.status)
            print(response.text)
            print(await response.json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

