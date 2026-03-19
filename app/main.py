import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware

import app.models  # noqa: F401 — registra todos los modelos antes de create_all
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.seed import seed_admin
from app.db.session import create_db_and_tables, get_session
from app.services.cleanup import expired_user_cleanup_loop

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' blob:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https://flagcdn.com https://*.tile.openstreetmap.org; "
    "connect-src 'self' https://*.tile.openstreetmap.org https://nominatim.openstreetmap.org; "
    "media-src 'self' blob:; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = _CSP
        # Cache-Control: assets amb hash (Vite) → cache llarga; HTML → no cache
        path = request.url.path
        if path.startswith("/static/assets/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.endswith(".html") or path in ("/", "/app"):
            response.headers["Cache-Control"] = "no-cache"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
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
app.add_middleware(GZipMiddleware, minimum_size=500)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    logger.error(
        "Unhandled exception on %s %s", request.method, request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "landing.html")


@app.get("/app")
def app_view():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    try:
        session.exec(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        logger.error("Health check: database unreachable", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "error"},
        )
