import platform
import shutil
from fastapi import APIRouter, Depends
from sqlalchemy import select, text, inspect
from sqlalchemy.orm import Session
from .. import config, models as m, schemas as s
from ..db import get_db
from ..policy import DEMO_KEYS

router = APIRouter()


@router.get("/capabilities", response_model=s.CapabilitiesOut)
def capabilities():
    return {
        "mode": config.APP_MODE,
        "mutations_allowed": config.APP_MODE == "local",
        "build_id": config.BUILD_ID,
        "environment": config.ENVIRONMENT,
    }


@router.get("/diagnostics", response_model=s.DiagnosticsOut)
def diagnostics(db: Session = Depends(get_db, scope="function")):
    db.execute(text("SELECT 1"))
    pulse = db.get(m.WorkerHeartbeat, "main")
    age = max(0, (m.now() - pulse.heartbeat_at).total_seconds()) if pulse else None
    statement = select(m.ProcessingJob).join(m.RecordingSession)
    if config.APP_MODE == "demo_readonly":
        statement = statement.where(
            m.RecordingSession.id.in_(config.DEMO_SESSION_IDS),
            m.RecordingSession.demo_key.in_(DEMO_KEYS),
            m.RecordingSession.dataset_kind == "synthetic",
            m.RecordingSession.deleted_at.is_(None),
        )
    jobs = list(db.scalars(statement.order_by(m.ProcessingJob.created_at.desc()).limit(100)))
    counts = {}
    for job in jobs:
        counts[job.state] = counts.get(job.state, 0) + 1
    revision = (
        db.scalar(text("SELECT version_num FROM alembic_version"))
        if inspect(db.connection()).has_table("alembic_version")
        else "unversioned"
    )
    return {
        **capabilities(),
        "database": "reachable",
        "worker": "unknown" if age is None else "ready" if age <= 45 else "stale",
        "worker_age_s": age,
        "worker_state": pulse.state if pulse else None,
        "python_version": platform.python_version(),
        "ffprobe_available": shutil.which("ffprobe") is not None,
        "storage_free_bytes": shutil.disk_usage(config.STORAGE_ROOT).free
        if config.STORAGE_ROOT.exists()
        else None,
        "migration": revision,
        "job_counts": counts,
        "recent_jobs": jobs[:20],
    }
