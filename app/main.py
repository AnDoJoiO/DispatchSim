import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

import app.models  # noqa: F401 — registra todos los modelos antes de create_all
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.seed import seed_admin
from app.db.session import create_db_and_tables
from app.services.cleanup import expired_user_cleanup_loop

STATIC_DIR = Path(__file__).parent / "static"

_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https://flagcdn.com; "
    "connect-src 'self'; "
    "frame-ancestors 'none';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = _CSP
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    if settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        seed_admin(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)
    task = asyncio.create_task(expired_user_cleanup_loop())
    yield
    task.cancel()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

_allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "landing.html")


@app.get("/app")
def app_view():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}
