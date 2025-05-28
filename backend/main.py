import logging
import os
import pkgutil
import sys

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from common import templates

# from tasks.notion_poller import poll_notion_projects
os.makedirs("log", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("log/app.log", "a", "utf-8"),
    ],
)
logger = logging.getLogger("NoityPy-Backend")
logger.info("Starting NotiPy Backend...")

# 1) fastapi 메인앱, api 용 서브앱 선언
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{page}")
async def page_handler(request: Request, page: str):
    """
    Handles requests for pages that are not explicitly defined.
    This will render the page if it exists, otherwise it will return a 404 error.
    대에충 페이지 있으면 알아서 갔다 줌, 일일이 구현하기 싫어서 만듬
    """
    try:
        return templates.TemplateResponse(f"{page}.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering page {page}: {e}")
        raise HTTPException(status_code=404, detail="Page not found")


@app.exception_handler(404)
async def custom_404_handler(request, __):
    return templates.TemplateResponse(
        "404.html", {"request": request}, status_code=404)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


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
