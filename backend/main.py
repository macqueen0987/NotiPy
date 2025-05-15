import os
import pkgutil
from threading import Thread
from datetime import datetime

import aiohttp
import db.models as models
import uvicorn
from common import get_db
from CRUDS import usercrud as crud
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from routers.notion import router as notion_router
from tasks.notion_poller import poll_notion_projects



app = FastAPI(title="NotiPy")

# 1) API routers
app.include_router(notion_router)

api = FastAPI()

# 2) 애플리케이션 시작 시 폴링 스레드 실행
@app.on_event("startup")
def start_poller():
    Thread(target=poll_notion_projects, daemon=True).start()

@app.get("/")
async def root():
    return {"message": "Hello, NotiPy!"}


@app.get("/test")
async def test(request: Request, conn=Depends(get_db)):
    return JSONResponse(content={"message": "Test!"})


# 3) 메인 실행부: Uvicorn을 한 번만 호출
if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 9091))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
