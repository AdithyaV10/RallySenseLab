from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models as m, schemas as s
from ..errors import DomainError
from ..jobs import enqueue
from ..storage import put_bytes
from ..signals import demo_csv
from .common import active_session, query_owned
from .. import config
from ..policy import DEMO_KEYS, visible

router = APIRouter()


@router.get("/sessions", response_model=list[s.SessionOut])
def sessions(limit: int = 100, db: Session = Depends(get_db, scope="function")):
    statement = select(m.RecordingSession).where(m.RecordingSession.deleted_at.is_(None))
    if config.APP_MODE == "demo_readonly":
        statement = statement.where(
            m.RecordingSession.id.in_(config.DEMO_SESSION_IDS),
            m.RecordingSession.demo_key.in_(DEMO_KEYS),
            m.RecordingSession.dataset_kind == "synthetic",
        )
    return list(
        db.scalars(statement.order_by(m.RecordingSession.created_at.desc()).limit(max(1, min(limit, 100))))
    )


@router.post("/sessions", response_model=s.SessionOut, status_code=201)
def create_session(payload: s.SessionCreate, db: Session = Depends(get_db, scope="function")):
    session = m.RecordingSession(**payload.model_dump())
    db.add(session)
    db.flush()
    db.add(m.AnnotationSet(session_id=session.id, name="Manual observations", provenance="human"))
    return session


@router.patch("/sessions/{session_id}/collection", response_model=s.SessionOut)
def save_collection(
    session_id: UUID, payload: s.CollectionUpdate, db: Session = Depends(get_db, scope="function")
):
    session = active_session(db, session_id)
    session = db.get(m.RecordingSession, session.id, with_for_update=True, populate_existing=True)
    if session.collection_revision != payload.revision:
        raise DomainError("Collection metadata changed; reload before saving", "REVISION_CONFLICT", 409)
    session.collection_profile = payload.profile.model_dump()
    session.collection_revision += 1
    return session


@router.get("/sessions/{session_id}", response_model=s.SessionDetail)
def detail(session_id: UUID, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    result = s.SessionOut.model_validate(session).model_dump()
    for key, model in [
        ("sensors", m.SensorRecording),
        ("videos", m.VideoAsset),
        ("poses", m.PoseTrack),
        ("runs", m.InferenceRun),
        ("predictions", m.Prediction),
        ("annotations", m.EventAnnotation),
        ("syncs", m.SyncConfiguration),
        ("jobs", m.ProcessingJob),
    ]:
        result[key] = query_owned(db, model, session_id)
    return result


@router.delete("/sessions/{session_id}", response_model=s.JobOut, status_code=202)
def delete_session(session_id: UUID, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    session = db.get(m.RecordingSession, session.id, with_for_update=True)
    session.deleted_at, session.demo_key = m.now(), None
    for job in query_owned(db, m.ProcessingJob, session_id):
        job.cancel_requested = True
        if job.state == "queued":
            job.state = "cancelled"
    return enqueue(db, session.id, "delete_session", session.id)


@router.post("/demo-sessions", response_model=s.SessionOut)
def seed_demo(db: Session = Depends(get_db, scope="function")):
    # Transaction advisory lock makes concurrent clicks/import retries idempotent.
    from sqlalchemy import text

    db.execute(text("SELECT pg_advisory_xact_lock(7316393)"))
    existing = db.scalars(
        select(m.RecordingSession).where(m.RecordingSession.demo_key == "synthetic-v1")
    ).first()
    if existing:
        return existing
    session = m.RecordingSession(
        title="Baseline / synthetic motion",
        dataset_kind="synthetic",
        demo_key="synthetic-v1",
        notes="Deterministic signal fixture. Animation is programmatic, not athlete footage or pose estimation.",
    )
    db.add(session)
    db.flush()
    labels = m.AnnotationSet(
        session_id=session.id, name="Generated fixture references", provenance="synthetic"
    )
    db.add(labels)
    db.flush()
    for t in [2.2, 5, 8.1, 11.4, 15]:
        db.add(
            m.EventAnnotation(
                session_id=session.id,
                set_id=labels.id,
                t_session_us=round(t * 1_000_000),
                event_type="synthetic_reference",
                note="Generated pulse center; not a human annotation",
            )
        )
    raw = put_bytes(db, session.id, demo_csv(), "raw_csv")
    mapping = s.SensorMapping(
        placement="synthetic_fixture", acceleration_kind="including_gravity", provenance="synthetic"
    )
    sensor = m.SensorRecording(
        session_id=session.id,
        raw_artifact_id=raw.id,
        name="Synthetic IMU · 100 Hz",
        mapping=mapping.model_dump(),
        placement=mapping.placement,
    )
    db.add(sensor)
    db.flush()
    enqueue(db, session.id, "normalize", sensor.id)
    return session


@router.get("/jobs/{job_id}", response_model=s.JobOut)
def job_status(job_id: UUID, db: Session = Depends(get_db, scope="function")):
    job = db.get(m.ProcessingJob, str(job_id))
    if not job:
        raise DomainError("Job not found", "NOT_FOUND", 404)
    if config.APP_MODE == "demo_readonly":
        active_session(db, job.session_id)
    return job


@router.get("/demonstrations", response_model=list[s.SessionOut])
def demonstrations(db: Session = Depends(get_db, scope="function")):
    return [
        row
        for row in db.scalars(
            select(m.RecordingSession).where(
                m.RecordingSession.demo_key.in_(DEMO_KEYS), m.RecordingSession.deleted_at.is_(None)
            )
        )
        if visible(row)
    ]


@router.post("/jobs/{job_id}/retry", response_model=s.JobOut, status_code=202)
def retry_source_job(job_id: UUID, db: Session = Depends(get_db, scope="function")):
    job = db.get(m.ProcessingJob, str(job_id))
    if not job:
        raise DomainError("Job not found", "NOT_FOUND", 404)
    session = active_session(db, job.session_id)
    db.get(m.RecordingSession, session.id, with_for_update=True)
    job = db.get(m.ProcessingJob, job.id, with_for_update=True, populate_existing=True)
    if job.kind not in {"normalize", "video_probe"} or job.state not in {"failed", "cancelled"}:
        raise DomainError(
            "Only failed source validation can be retried; rerun experiments as new runs",
            "INVALID_STATE",
            409,
        )
    pending = db.scalars(
        select(m.ProcessingJob).where(
            m.ProcessingJob.target_id == job.target_id, m.ProcessingJob.state.in_(["queued", "running"])
        )
    ).first()
    if pending:
        return pending
    target = db.get(m.SensorRecording if job.kind == "normalize" else m.VideoAsset, job.target_id)
    if not target or target.status == "ready":
        raise DomainError("Source is missing or already ready", "INVALID_STATE", 409)
    target.status = "queued"
    return enqueue(db, session.id, job.kind, job.target_id)


@router.post("/research-demo-sessions", response_model=s.SessionOut)
def seed_research_demo(db: Session = Depends(get_db, scope="function")):
    from sqlalchemy import text

    db.execute(text("SELECT pg_advisory_xact_lock(7316394)"))
    existing = db.scalars(
        select(m.RecordingSession).where(m.RecordingSession.demo_key == "paired-research-v1")
    ).first()
    if existing:
        return existing
    session = m.RecordingSession(
        title="Paired motion / synthetic research",
        dataset_kind="synthetic",
        demo_key="paired-research-v1",
        notes="Generated stick figure, analytical landmarks and Gaussian IMU pulses on a shared clock. NOT MediaPipe extraction, athlete footage, or real-world tennis evidence.",
    )
    db.add(session)
    db.flush()
    enqueue(db, session.id, "research_fixture", session.id)
    return session


@router.post("/jobs/{job_id}/cancel", response_model=s.JobOut)
def cancel_job(job_id: UUID, db: Session = Depends(get_db, scope="function")):
    job = db.get(m.ProcessingJob, str(job_id))
    if not job or job.kind == "delete_session":
        raise DomainError("Job cannot be cancelled", "INVALID_STATE", 409)
    job.cancel_requested = True
    if job.state == "queued":
        job.state = "cancelled"
        if job.kind == "experiment" and (target := db.get(m.Experiment, job.target_id)):
            target.status = "cancelled"
    return job
