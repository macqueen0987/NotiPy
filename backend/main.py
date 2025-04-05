import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
import os
import uvicorn
import pkgutil

from datetime import datetime
import db.models as models
from common import get_db
from CRUDS import usercrud as crud

app = FastAPI()
api = FastAPI()

@app.get("/")
async def root(request: Request):
    return JSONResponse(content={"message": "Hello World!"})


@app.get("/test")
async def test(request: Request, conn=Depends(get_db)):
    return JSONResponse(content={"message": "Test!"})

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

