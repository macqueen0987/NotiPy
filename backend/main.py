import os
import pkgutil
from datetime import datetime

import aiohttp
import db.models as models
import uvicorn
from common import get_db
from CRUDS import usercrud as crud
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

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
    for loader, module_name, is_pkg in pkgutil.iter_modules(
            ["./routers"], "routers."):
        routers.append(module_name)
    for router in routers:
        module = __import__(router, fromlist=["router"])
        api.include_router(module.router)
    app.mount("/api", api)
    port = int(os.environ.get("BACKEND_PORT", 9091))
    uvicorn.run(app, host="0.0.0.0", port=port)
