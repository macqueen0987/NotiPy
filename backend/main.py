import logging
import os
import pkgutil
import sys

import uvicorn
from starlette.responses import RedirectResponse

from common import templates
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

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
    return RedirectResponse(url="/ko/index")

@app.get("/{lang}")
@app.get("/{lang}/")
async def lang_handler(lang: str):
    # 언어만 들어온 경우 기본 페이지로 리디렉션
    return RedirectResponse(url=f"/{lang}/index")

@app.get("/{lang}/{page}")
async def page_handler(request: Request, lang: str = "ko", page: str = "index"):
    """
    페이지 핸들러: lang과 page에 따라 적절한 HTML 파일을 반환합니다.
    """
    try:
        return templates.TemplateResponse(
            f"{lang}/{page}.html", {"request": request}, status_code=200)
    except Exception as e:
        logging.error(f"Error rendering page {lang}/{page}: {e}")
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


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
