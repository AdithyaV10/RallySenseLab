import hmac
import logging
import time
import json
from uuid import uuid4
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import LOCAL_TOKEN, ALLOWED_ORIGINS, STORAGE_ROOT
from .db import engine
from .errors import DomainError
from .api import sessions, sensors, videos, annotations, pose, research, diagnostics
from . import config
from .policy import upload_allowed

request_logger = logging.getLogger("rallysense.http")
if not request_logger.handlers:
    request_logger.addHandler(logging.StreamHandler())
request_logger.setLevel(logging.INFO)
request_logger.propagate = False


async def authorize(request: Request):
    if not hmac.compare_digest(request.headers.get("x-lab-token", ""), LOCAL_TOKEN):
        raise DomainError("Local API credential required", "UNAUTHORIZED", 401)
    origin = request.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        raise DomainError("Origin is not allowed", "FORBIDDEN_ORIGIN", 403)


app = FastAPI(title="RallySense Lab API", version="0.2.0")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.ALLOWED_HOSTS)


@app.middleware("http")
async def safe_headers(request: Request, call_next):
    started = time.perf_counter()
    request.state.request_id = str(uuid4())
    if (
        request.url.path.startswith("/api/v1/")
        and config.APP_MODE == "demo_readonly"
        and request.method not in {"GET", "HEAD", "OPTIONS"}
    ):
        return JSONResponse(
            {
                "error": {
                    "code": "READ_ONLY_DEMO",
                    "message": "This demonstration is read-only. Uploads, capture saves, edits and experiment mutations are disabled.",
                }
            },
            status_code=403,
        )
    if (
        request.method == "POST"
        and request.url.path.endswith(("/videos", "/sensor-imports"))
        and not upload_allowed(request.client.host if request.client else "unknown")
    ):
        return JSONResponse(
            {
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Upload limit reached; wait one minute before retrying.",
                }
            },
            status_code=429,
            headers={"Retry-After": "60"},
        )
    if request.url.path.startswith("/api/v1/") and "/health/" not in request.url.path:
        if not hmac.compare_digest(request.headers.get("x-lab-token", ""), LOCAL_TOKEN):
            return JSONResponse(
                {"error": {"code": "UNAUTHORIZED", "message": "Local API credential required"}},
                status_code=401,
            )
    content_length = request.headers.get("content-length")
    limit = (
        501 * 1024 * 1024
        if request.url.path.endswith("/videos")
        else 51 * 1024 * 1024
        if request.url.path.endswith("/sensor-imports")
        else 2 * 1024 * 1024
    )
    if content_length and (not content_length.isdigit() or int(content_length) > limit):
        return JSONResponse(
            {"error": {"code": "RESOURCE_LIMIT", "message": "Request body exceeds limit"}}, status_code=413
        )
    original_receive = request._receive
    received = 0

    async def bounded_receive():
        nonlocal received
        message = await original_receive()
        received += len(message.get("body", b""))
        if received > limit:
            raise DomainError("Request body exceeds limit", "RESOURCE_LIMIT", 413)
        return message

    request._receive = bounded_receive
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Request-ID"] = request.state.request_id
    route = getattr(request.scope.get("route"), "path", "unmatched")
    request_logger.info(
        json.dumps(
            {
                "event": "http_request",
                "request_id": request.state.request_id,
                "method": request.method,
                "route": route,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response


@app.exception_handler(DomainError)
async def domain_error(request: Request, exc: DomainError):
    return JSONResponse(
        {
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
        status_code=exc.status,
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Exclude input values from errors; uploaded content and private data never echo back.
    return JSONResponse(
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request fields",
                "fields": [str(e["loc"][-1]) for e in exc.errors()],
            }
        },
        status_code=422,
    )


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    logging.error(
        "Unhandled request error %s: %s", getattr(request.state, "request_id", None), type(exc).__name__
    )
    return JSONResponse(
        {"error": {"code": "INTERNAL_ERROR", "message": "Request failed; inspect local server logs"}},
        status_code=500,
    )


@app.get("/api/v1/health/live")
def live():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/v1/health/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    except (SQLAlchemyError, OSError) as exc:
        raise DomainError("Database or artifact storage unavailable", "NOT_READY", 503) from exc
    return {"status": "ready"}


for router in [
    sessions.router,
    sensors.router,
    videos.router,
    annotations.router,
    pose.router,
    research.router,
    diagnostics.router,
]:
    app.include_router(router, prefix="/api/v1", dependencies=[Depends(authorize)])
