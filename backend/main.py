import os
import pkgutil
import sys
from datetime import datetime
from threading import Thread

import aiohttp
from fastapi.exceptions import RequestValidationError
from interactions.client.errors import BadRequest

import db.models as models
import uvicorn
from common import get_db
from services import userservice as crud
from fastapi import BackgroundTasks, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from routers.notion import router as notion_router
from sqlalchemy import select
import logging
# from tasks.notion_poller import poll_notion_projects

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("NoityPy-Backend")
logger.info("Starting NotiPy Backend...")

# 1) fastapi 메인앱, api 용 서브앱 선언
app = FastAPI()
api = FastAPI()


# 2) 애플리케이션 시작 시 폴링 스레드 실행
# @app.on_event("startup")  # TODO: 이 메소드 더이상 지원 안하니 변경하기
# def start_poller():
#     Thread(target=poll_notion_projects, daemon=True).start()


@app.get("/")
async def root():
    return {"message": "Hello, NotiPy!"}


# @api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# @api.exception_handler(BadRequest)
async def bad_request_exception_handler(request: Request, exc: BadRequest):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)

# 3) 메인 실행부: 자동으로 routers 폴더 내에 존재하는 모든 라우터 api에 장착
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
