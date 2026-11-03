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

router = APIRouter()


@router.get("/sessions", response_model=list[s.SessionOut])
def sessions(limit: int = 100, db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(m.RecordingSession)
            .where(m.RecordingSession.deleted_at.is_(None))
            .order_by(m.RecordingSession.created_at.desc())
            .limit(max(1, min(limit, 100)))
        )
    )


@router.post("/sessions", response_model=s.SessionOut, status_code=201)
def create_session(payload: s.SessionCreate, db: Session = Depends(get_db)):
    session = m.RecordingSession(**payload.model_dump())
    db.add(session)
    db.flush()
    db.add(m.AnnotationSet(session_id=session.id, name="Manual observations", provenance="human"))
    return session


@router.get("/sessions/{session_id}", response_model=s.SessionDetail)
def detail(session_id: UUID, db: Session = Depends(get_db)):
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
def delete_session(session_id: UUID, db: Session = Depends(get_db)):
    session = active_session(db, session_id)
    session = db.get(m.RecordingSession, session.id, with_for_update=True)
    session.deleted_at, session.demo_key = m.now(), None
    for job in query_owned(db, m.ProcessingJob, session_id):
        job.cancel_requested = True
        if job.state == "queued":
            job.state = "cancelled"
    return enqueue(db, session.id, "delete_session", session.id)


@router.post("/demo-sessions", response_model=s.SessionOut)
def seed_demo(db: Session = Depends(get_db)):
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
def job_status(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(m.ProcessingJob, str(job_id))
    if not job:
        raise DomainError("Job not found", "NOT_FOUND", 404)
    return job


@router.post("/jobs/{job_id}/cancel", response_model=s.JobOut)
def cancel_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.get(m.ProcessingJob, str(job_id))
    if not job or job.kind == "delete_session":
        raise DomainError("Job cannot be cancelled", "INVALID_STATE", 409)
    job.cancel_requested = True
    if job.state == "queued":
        job.state = "cancelled"
    return job
