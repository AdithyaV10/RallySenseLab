from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models as m
from .. import research_schemas as s
from ..errors import DomainError
from ..jobs import enqueue, fingerprint
from ..provenance import input_manifest
from ..experiments import ALGORITHMS, EVENTS, check_comparison, implementation_hash, report_markdown
from .common import active_session, owned

router = APIRouter()


@router.get("/sessions/{session_id}/annotation-sets", response_model=list[s.AnnotationSetOut])
def sets(session_id: UUID, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    return list(
        db.scalars(
            select(m.AnnotationSet)
            .where(m.AnnotationSet.session_id == session.id)
            .order_by(m.AnnotationSet.created_at)
        )
    )


@router.post("/sessions/{session_id}/annotation-sets", response_model=s.AnnotationSetOut, status_code=201)
def create_set(
    session_id: UUID, payload: s.AnnotationSetCreate, db: Session = Depends(get_db, scope="function")
):
    session = active_session(db, session_id)
    labels = m.AnnotationSet(session_id=session.id, name=payload.name, provenance="human")
    db.add(labels)
    db.flush()
    return labels


@router.post("/annotation-sets/{set_id}/freeze", response_model=s.ReferenceOut, status_code=201)
def freeze(set_id: UUID, payload: s.FreezeCreate, db: Session = Depends(get_db, scope="function")):
    labels = owned(db, m.AnnotationSet, set_id)
    labels = db.get(m.AnnotationSet, labels.id, with_for_update=True, populate_existing=True)
    if payload.revision != labels.revision:
        raise DomainError("Label set changed; reload before freezing", "REVISION_CONFLICT", 409)
    video_hash = None
    if payload.video_id:
        video = owned(db, m.VideoAsset, payload.video_id)
        if video.session_id != labels.session_id:
            raise DomainError("Video belongs to another session", "INVALID_REFERENCE", 409)
        video_hash = db.get(m.Artifact, video.artifact_id).sha256
    events = list(
        db.scalars(
            select(m.EventAnnotation)
            .where(m.EventAnnotation.set_id == labels.id, m.EventAnnotation.event_type == payload.event_type)
            .order_by(m.EventAnnotation.t_session_us, m.EventAnnotation.id)
        )
    )
    manifest = {
        **payload.model_dump(mode="json", exclude={"revision"}),
        "provenance": labels.provenance,
        "set_name": labels.name,
        "clock": "session_us",
        "video_sha256": video_hash,
        "independent": payload.independent and labels.provenance == "human",
    }
    data = [
        {
            "id": e.id,
            "t_session_us": e.t_session_us,
            "event_type": e.event_type,
            "note": e.note,
            "revision": e.revision,
        }
        for e in events
    ]
    snapshot = m.ReferenceSnapshot(
        session_id=labels.session_id,
        set_id=labels.id,
        revision=labels.revision,
        manifest=manifest,
        events=data,
        fingerprint=fingerprint(
            {"manifest": manifest, "events": data, "set": labels.id, "revision": labels.revision}
        ),
    )
    db.add(snapshot)
    db.flush()
    return snapshot


@router.get("/sessions/{session_id}/references", response_model=list[s.ReferenceOut])
def references(session_id: UUID, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    return list(
        db.scalars(
            select(m.ReferenceSnapshot)
            .where(m.ReferenceSnapshot.session_id == session.id)
            .order_by(m.ReferenceSnapshot.created_at.desc())
            .limit(100)
        )
    )


@router.post("/sessions/{session_id}/experiments", response_model=s.ExperimentOut, status_code=202)
def create_experiment(
    session_id: UUID, payload: s.ExperimentCreate, db: Session = Depends(get_db, scope="function")
):
    session = active_session(db, session_id)
    session = db.get(m.RecordingSession, session.id, with_for_update=True)
    inputs, sync_info = {}, None
    if payload.mode in ("imu", "fusion"):
        sensor = owned(db, m.SensorRecording, payload.sensor_id)
        sync = owned(db, m.SyncConfiguration, payload.sync_id)
        if sensor.session_id != session.id or sync.sensor_id != sensor.id or sensor.status != "ready":
            raise DomainError(
                "Choose ready same-session sensor and its sync revision", "INVALID_REFERENCE", 409
            )
        artifact = db.get(m.Artifact, sensor.normalized_artifact_id)
        inputs["sensor"] = {
            "id": sensor.id,
            "artifact_id": artifact.id,
            "sha256": artifact.sha256,
            "mapping": sensor.mapping,
            "quality": sensor.quality,
            "placement": sensor.placement,
        }
        sync_info = {
            "id": sync.id,
            "revision": sync.revision,
            "offset_us": sync.offset_us,
            "method": sync.method,
        }
    if payload.mode in ("video", "fusion"):
        pose = owned(db, m.PoseTrack, payload.pose_id)
        if pose.session_id != session.id or pose.status != "ready":
            raise DomainError("Choose a ready same-session pose track", "INVALID_REFERENCE", 409)
        video = db.get(m.VideoAsset, pose.video_id)
        artifact = db.get(m.Artifact, pose.artifact_id)
        aspect = video.width / video.height
        if abs(video.metadata_json.get("rotation", 0)) % 180 == 90:
            aspect = 1 / aspect
        inputs["pose"] = {
            "id": pose.id,
            "artifact_id": artifact.id,
            "sha256": artifact.sha256,
            "config": pose.config,
            "quality": pose.quality,
            "video_id": video.id,
            "aspect": aspect,
        }
    if payload.mode == "fusion":
        if session.dataset_kind == "mixed":
            raise DomainError(
                "Mixed unrelated inputs are not eligible for paired fusion. Import genuinely paired recordings into a new session.",
                "UNPAIRED_INPUT",
            )
        if (payload.pairing == "synthetic_fixture") != (session.dataset_kind == "synthetic"):
            raise DomainError("Pairing declaration conflicts with dataset provenance", "UNPAIRED_INPUT")
    reference, eligibility = None, "No frozen reference; accuracy unavailable"
    if payload.reference_id:
        reference = owned(db, m.ReferenceSnapshot, payload.reference_id)
        if reference.session_id != session.id:
            raise DomainError("Reference belongs to another session", "INVALID_REFERENCE", 409)
        eligibility = check_comparison(payload, reference, session.dataset_kind)
        if "pose" in inputs and reference.manifest.get("video_id") not in (None, inputs["pose"]["video_id"]):
            raise DomainError(
                "Pose and frozen visual references must use the same video", "INCOMPATIBLE_REFERENCE"
            )
    runtime = input_manifest(session.id, "", "", {})
    request = payload.model_dump(mode="json", exclude={"force_rerun"})
    manifest = {
        "schema_version": 1,
        "request": request,
        "algorithm": ALGORITHMS[payload.mode],
        "event_type": EVENTS[payload.mode],
        "session": {
            "id": session.id,
            "dataset_kind": session.dataset_kind,
            "title": session.title,
            "notes": session.notes,
            "handedness": session.handedness,
        },
        "inputs": inputs,
        "sync": sync_info,
        "reference": {
            "id": reference.id,
            "sha256": reference.fingerprint,
            "revision": reference.revision,
            "metadata": reference.manifest,
        }
        if reference
        else None,
        "implementation_sha256": implementation_hash(),
        "dependency_lock_sha256": runtime["dependency_lock_sha256"],
        "runtime": runtime["runtime"],
        "evaluation_eligibility": eligibility,
    }
    identity = fingerprint(manifest)
    old = db.scalars(
        select(m.Experiment)
        .where(
            m.Experiment.session_id == session.id,
            m.Experiment.fingerprint == identity,
            m.Experiment.status.in_(["queued", "running", "succeeded"]),
        )
        .order_by(m.Experiment.created_at.desc())
    ).first()
    if old and not payload.force_rerun:
        return old
    experiment = m.Experiment(
        session_id=session.id,
        name=payload.name,
        fingerprint=identity,
        reference_id=reference.id if reference else None,
        manifest=manifest,
    )
    db.add(experiment)
    db.flush()
    enqueue(db, session.id, "experiment", experiment.id)
    return experiment


@router.get("/sessions/{session_id}/experiments", response_model=list[s.ExperimentOut])
def experiments(
    session_id: UUID, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db, scope="function")
):
    session = active_session(db, session_id)
    return list(
        db.scalars(
            select(m.Experiment)
            .where(m.Experiment.session_id == session.id)
            .order_by(m.Experiment.created_at.desc())
            .limit(limit)
        )
    )


@router.get("/experiments/{experiment_id}", response_model=s.ExperimentOut)
def experiment(experiment_id: UUID, db: Session = Depends(get_db, scope="function")):
    return owned(db, m.Experiment, experiment_id)


@router.get("/experiments/{experiment_id}/report", response_class=PlainTextResponse)
def report(experiment_id: UUID, db: Session = Depends(get_db, scope="function")):
    row = owned(db, m.Experiment, experiment_id)
    return PlainTextResponse(
        report_markdown(row),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="rallysense-{row.id}.md"'},
    )


@router.post("/experiments/{experiment_id}/evaluate", response_model=s.ExperimentOut, status_code=202)
def evaluate_revision(
    experiment_id: UUID, payload: s.EvaluationCreate, db: Session = Depends(get_db, scope="function")
):
    old = owned(db, m.Experiment, experiment_id)
    if old.status != "succeeded":
        raise DomainError("Only completed experiments can be evaluated", "INVALID_STATE", 409)
    request = s.ExperimentCreate.model_validate(
        {**old.manifest["request"], **payload.model_dump(mode="json")}
    )
    # New immutable experiment; the original result is never patched.
    return create_experiment(UUID(old.session_id), request, db)


@router.get("/sessions/{session_id}/experiment-comparison", response_model=list[s.ExperimentOut])
def compare(
    session_id: UUID,
    ids: list[UUID] = Query(min_length=1, max_length=3),
    db: Session = Depends(get_db, scope="function"),
):
    session = active_session(db, session_id)
    rows = [owned(db, m.Experiment, item) for item in ids]
    if any(row.session_id != session.id for row in rows):
        raise DomainError("Comparison requires experiments from this session", "INVALID_REFERENCE", 409)
    return rows
