import numpy as np
import pyarrow.parquet as pq
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models as m, schemas as s
from ..config import MAX_CSV_BYTES
from ..errors import DomainError
from ..jobs import enqueue, fingerprint
from ..provenance import input_manifest
from ..storage import put_bytes, path_for
from .common import active_session, owned
from ..upload_route import BoundedUploadRoute

router = APIRouter(route_class=BoundedUploadRoute)


@router.get("/contracts/sensor-mapping", response_model=s.SensorMapping)
def mapping_contract():
    return s.SensorMapping()


@router.post("/sessions/{session_id}/sensor-imports", response_model=s.JobOut, status_code=202)
async def import_sensor(
    session_id: UUID,
    file: UploadFile = File(),
    mapping: str = Form("{}"),
    db: Session = Depends(get_db, scope="function"),
):
    session = active_session(db, session_id)
    try:
        config = s.SensorMapping.model_validate_json(mapping)
    except ValueError as exc:
        raise DomainError("Invalid CSV mapping; select a timestamp and complete xyz channel groups") from exc
    data = await file.read(MAX_CSV_BYTES + 1)
    if len(data) > MAX_CSV_BYTES:
        raise DomainError("CSV exceeds 50 MiB", "RESOURCE_LIMIT", 413)
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise DomainError("Upload an extracted .csv file", "UNSUPPORTED_MEDIA", 415)
    # Ingestion validates actual contents in the worker; filenames never determine storage paths.
    artifact = put_bytes(db, session.id, data, "raw_csv")
    if config.provenance == "synthetic" and session.dataset_kind == "recorded":
        has_sources = db.scalars(select(m.VideoAsset.id).where(m.VideoAsset.session_id == session.id)).first()
        has_sources = (
            has_sources
            or db.scalars(
                select(m.SensorRecording.id).where(m.SensorRecording.session_id == session.id)
            ).first()
        )
        session.dataset_kind = "mixed" if has_sources else "synthetic"
    elif config.provenance == "recorded" and session.dataset_kind == "synthetic":
        session.dataset_kind = "mixed"
    recording = m.SensorRecording(
        session_id=session.id,
        raw_artifact_id=artifact.id,
        name=file.filename.replace("\\", "/").split("/")[-1][:160],
        mapping=config.model_dump(),
        placement=config.placement,
    )
    db.add(recording)
    db.flush()
    return enqueue(db, session.id, "normalize", recording.id)


@router.get("/sensor-recordings/{sensor_id}/samples", response_model=s.SamplesOut)
def samples(
    sensor_id: UUID,
    start_us: int = Query(0, ge=0),
    end_us: int = Query(1_200_000_000, ge=0),
    max_points: int = Query(1600, ge=20, le=5000),
    db: Session = Depends(get_db, scope="function"),
):
    sensor = owned(db, m.SensorRecording, sensor_id)
    if sensor.status != "ready":
        raise DomainError("Sensor recording is not ready", "INVALID_STATE", 409)
    if end_us <= start_us:
        raise DomainError("Window end must follow start")
    table = pq.read_table(
        path_for(db, sensor.normalized_artifact_id, sensor.session_id),
        filters=[("t_us", ">=", start_us), ("t_us", "<=", end_us)],
    )
    data = table.to_pydict()
    n = len(table)
    ax = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in ["ax", "ay", "az"]])
    gx = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in ["gx", "gy", "gz"]])
    acc, gyro = np.linalg.norm(ax, axis=1), np.linalg.norm(gx, axis=1)
    if n <= max_points:
        indices = list(range(n))
    else:
        # Min/max angular or acceleration magnitude preserves spikes rather than just decimating.
        indices = {0, n - 1}
        measure = np.where(np.isfinite(gyro), gyro, np.nan_to_num(acc))
        for bucket in np.array_split(np.arange(n), max_points // 2 - 1):
            indices.update([int(bucket[np.argmin(measure[bucket])]), int(bucket[np.argmax(measure[bucket])])])
        indices = sorted(indices)

    def finite(value):
        return float(value) if value is not None and np.isfinite(value) else None

    rows = [
        {
            "t_us": data["t_us"][i],
            **{c: finite(data[c][i]) for c in ["ax", "ay", "az", "gx", "gy", "gz"]},
            "acc": finite(acc[i]),
            "gyro": finite(gyro[i]),
        }
        for i in indices
    ]
    return {"source_count": n, "returned_count": len(rows), "data": rows}


@router.post("/sessions/{session_id}/sync-configurations", response_model=s.SyncOut, status_code=201)
def save_sync(session_id: UUID, payload: s.SyncCreate, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    db.get(m.RecordingSession, session.id, with_for_update=True)
    sensor = owned(db, m.SensorRecording, payload.sensor_id)
    if sensor.session_id != session.id:
        raise DomainError("Sensor belongs to another session", "INVALID_REFERENCE", 409)
    if payload.video_id:
        video = owned(db, m.VideoAsset, payload.video_id)
        if video.session_id != session.id:
            raise DomainError("Video belongs to another session", "INVALID_REFERENCE", 409)
    evidence = payload.evidence.model_dump()
    if len(payload.evidence.cues) == 2:
        first, last = payload.evidence.cues
        if last.sensor_us <= first.sensor_us or last.video_us <= first.video_us:
            raise DomainError("End cues must follow start cues in both clocks", "INVALID_CONFIGURATION")
        evidence["end_residual_us"] = last.video_us - (last.sensor_us + payload.offset_us)
        evidence["drift_corrected"] = False
    latest = db.scalars(
        select(m.SyncConfiguration)
        .where(m.SyncConfiguration.session_id == session.id)
        .order_by(m.SyncConfiguration.revision.desc())
    ).first()
    sync = m.SyncConfiguration(
        session_id=session.id,
        sensor_id=sensor.id,
        offset_us=payload.offset_us,
        revision=latest.revision + 1 if latest else 1,
        video_id=str(payload.video_id) if payload.video_id else None,
        evidence=evidence,
        method="manual_cues" if payload.evidence.cues else "manual_offset",
    )
    db.add(sync)
    db.flush()
    return sync


@router.post("/sessions/{session_id}/inference-runs", response_model=s.RunOut, status_code=202)
def infer(session_id: UUID, payload: s.InferenceCreate, db: Session = Depends(get_db, scope="function")):
    session = active_session(db, session_id)
    sensor = owned(db, m.SensorRecording, payload.sensor_id)
    if sensor.session_id != session.id or sensor.status != "ready":
        raise DomainError("Choose a ready sensor recording in this session", "INVALID_REFERENCE", 409)
    sync = db.scalars(
        select(m.SyncConfiguration)
        .where(m.SyncConfiguration.sensor_id == sensor.id)
        .order_by(m.SyncConfiguration.revision.desc())
    ).first()
    if not sync:
        raise DomainError("Save an alignment first", "MISSING_INPUT")
    artifact = db.get(m.Artifact, sensor.normalized_artifact_id)
    config = payload.config.model_dump()
    manifest = input_manifest(session.id, artifact.sha256, sync.id, config)
    identity = fingerprint(manifest)
    existing = db.scalars(select(m.InferenceRun).where(m.InferenceRun.fingerprint == identity)).first()
    if existing:
        return existing
    run = m.InferenceRun(
        session_id=session.id,
        sensor_id=sensor.id,
        sync_id=sync.id,
        config=config,
        fingerprint=identity,
        result={"input_manifest": manifest},
    )
    db.add(run)
    db.flush()
    enqueue(db, session.id, "inference", run.id)
    return run
