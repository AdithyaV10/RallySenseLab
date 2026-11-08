import hmac
import logging
import time
import json
import asyncio
import os
import tempfile
import shutil
from uuid import uuid4
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.exception_handlers import http_exception_handler
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
from .policy import upload_allowed, request_allowed
from .policy import visible
from . import models as m
from .storage import path_for
from sqlalchemy import select
from sqlalchemy.orm import Session

request_logger = logging.getLogger("rallysense.http")
if not request_logger.handlers:
    request_logger.addHandler(logging.StreamHandler())
request_logger.setLevel(logging.INFO)
request_logger.propagate = False
active_uploads = 0


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
    global active_uploads
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
        if not request_allowed():
            return JSONResponse(
                {
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Workspace request budget reached; retry in one minute",
                    }
                },
                status_code=429,
                headers={"Retry-After": "60"},
            )
        if request.headers.get("origin") and request.headers["origin"] not in ALLOWED_ORIGINS:
            return JSONResponse(
                {"error": {"code": "FORBIDDEN_ORIGIN", "message": "Origin is not allowed"}}, status_code=403
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
    body_error = None

    async def bounded_receive():
        nonlocal received, body_error
        try:
            message = await asyncio.wait_for(original_receive(), timeout=30)
        except TimeoutError as exc:
            body_error = (408, "Request body timed out")
            raise HTTPException(408, "Request body timed out") from exc
        received += len(message.get("body", b""))
        if received > limit:
            body_error = (413, "Request body exceeds limit")
            raise HTTPException(413, "Request body exceeds limit")
        return message

    request._receive = bounded_receive
    is_upload = request.method == "POST" and request.url.path.endswith(("/videos", "/sensor-imports"))
    if is_upload and active_uploads >= 2:
        return JSONResponse(
            {"error": {"code": "RESOURCE_LIMIT", "message": "Upload concurrency limit reached"}},
            status_code=429,
            headers={"Retry-After": "5"},
        )
    if is_upload:
        active_uploads += 1
    try:
        response = await call_next(request)
        # BaseHTTPMiddleware can wrap receive exceptions in an ExceptionGroup that
        # multipart parsing translates to 400. Preserve the actual bounded-body error.
        if body_error:
            status, message = body_error
            response = JSONResponse(
                {
                    "error": {
                        "code": "RESOURCE_LIMIT" if status == 413 else "REQUEST_TIMEOUT",
                        "message": message,
                    }
                },
                status_code=status,
            )
    except Exception:
        if not body_error:
            raise
        status, message = body_error
        response = JSONResponse(
            {"error": {"code": "RESOURCE_LIMIT" if status == 413 else "REQUEST_TIMEOUT", "message": message}},
            status_code=status,
        )
    finally:
        if is_upload:
            active_uploads -= 1
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


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    if exc.status_code in {408, 413}:
        return JSONResponse(
            {
                "error": {
                    "code": "RESOURCE_LIMIT" if exc.status_code == 413 else "REQUEST_TIMEOUT",
                    "message": str(exc.detail),
                }
            },
            status_code=exc.status_code,
        )
    return await http_exception_handler(request, exc)


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
        if config.APP_MODE == "demo_readonly":
            # Read every approved fixture artifact; do not create directories or demand writes.
            with Session(engine) as db:
                fixtures = list(
                    db.scalars(
                        select(m.RecordingSession).where(
                            m.RecordingSession.id.in_(config.DEMO_SESSION_IDS),
                            m.RecordingSession.deleted_at.is_(None),
                        )
                    )
                )
                if {s.id for s in fixtures if visible(s)} != config.DEMO_SESSION_IDS or not fixtures:
                    raise OSError("Approved fixture inventory unavailable")
                for fixture in fixtures:
                    artifacts = list(
                        db.scalars(select(m.Artifact).where(m.Artifact.session_id == fixture.id))
                    )
                    if not artifacts:
                        raise OSError("Approved fixture artifacts unavailable")
                    for artifact in artifacts:
                        with path_for(db, artifact.id, fixture.id).open("rb") as stream:
                            if artifact.bytes and not stream.read(1):
                                raise OSError("Fixture artifact unreadable")
        else:
            STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
            if shutil.disk_usage(STORAGE_ROOT).free < 1024 * 1024:
                raise OSError("Storage free space exhausted")
            with tempfile.NamedTemporaryFile(dir=STORAGE_ROOT, prefix=".ready-", delete=True) as probe:
                probe.write(b"rallysense-ready")
                probe.flush()
                os.fsync(probe.fileno())
                probe.seek(0)
                if probe.read() != b"rallysense-ready":
                    raise OSError("Storage readback failed")
    except (SQLAlchemyError, OSError, DomainError) as exc:
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
