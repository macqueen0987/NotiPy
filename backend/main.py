import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
import os
import uvicorn
import pkgutil

from var import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, API_ENDPOINT
from datetime import datetime
import db.models as models
from common import get_db

app = FastAPI()
api = FastAPI()
auth = aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET)

@app.get("/")
async def root(request: Request):
    return JSONResponse(content={"message": "Hello World!"})


@app.get("/test")
async def test(request: Request, conn=Depends(get_db)):
    query = select(models.User)
    result = await conn.execute(query)
    print(result)

if __name__ == "__main__":
    routers = []
    for loader, module_name, is_pkg in pkgutil.iter_modules(["./routers"], "routers."):
        routers.append(module_name)
    for router in routers:
        module = __import__(router, fromlist=["router"])
        api.include_router(module.router)
    app.mount("/api", api)
    port = int(os.environ.get("BACKEND_PORT", 9091))
    uvicorn.run(app, host="0.0.0.0", port=port)

