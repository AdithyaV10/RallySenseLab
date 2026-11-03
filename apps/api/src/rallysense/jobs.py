"""Durable PostgreSQL jobs with lease fencing and atomic metadata publication."""

import hashlib
import json
import shutil
import time
from datetime import timedelta
from sqlalchemy import select, or_, delete
from sqlalchemy.orm import Session
import pyarrow as pa
import pyarrow.parquet as pq
from .db import engine
from . import models as m
from .errors import DomainError
from .schemas import SensorMapping, DetectorConfig
from .signals import normalize_csv, parquet_bytes, detect_gyro
from .storage import put_bytes, path_for, resolve
from .media import probe_video
from .provenance import input_manifest
from .pose_features import derive_features


def enqueue(db, session_id, kind, target_id):
    job = m.ProcessingJob(session_id=session_id, kind=kind, target_id=target_id)
    db.add(job)
    db.flush()
    return job


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def claim_job():
    with Session(engine) as db, db.begin():
        job = db.scalars(
            select(m.ProcessingJob)
            .where(
                or_(
                    m.ProcessingJob.state == "queued",
                    (m.ProcessingJob.state == "running") & (m.ProcessingJob.lease_expires_at < m.now()),
                )
            )
            .order_by(m.ProcessingJob.created_at)
            .with_for_update(skip_locked=True)
        ).first()
        if not job:
            return None
        if job.attempt >= 3:
            job.state, job.error = "failed", "Retry limit reached"
            return None
        job.state, job.lease_token = "running", m.uid()
        job.attempt += 1
        job.lease_expires_at = m.now() + timedelta(seconds=120)
        return job.id, job.lease_token


def heartbeat(job_id, token):
    with Session(engine) as db, db.begin():
        job = db.get(m.ProcessingJob, job_id, with_for_update=True)
        if job and job.lease_token == token and job.state == "running":
            job.lease_expires_at = m.now() + timedelta(seconds=120)


def compute(db, job):
    if job.kind == "normalize":
        sensor = db.get(m.SensorRecording, job.target_id)
        table, quality = normalize_csv(
            path_for(db, sensor.raw_artifact_id, job.session_id).read_bytes(),
            SensorMapping.model_validate(sensor.mapping),
        )
        return table, quality
    if job.kind == "video_probe":
        video = db.get(m.VideoAsset, job.target_id)
        return probe_video(path_for(db, video.artifact_id, job.session_id))
    if job.kind == "inference":
        run = db.get(m.InferenceRun, job.target_id)
        sensor = db.get(m.SensorRecording, run.sensor_id)
        sync = db.get(m.SyncConfiguration, run.sync_id)
        table = pq.read_table(path_for(db, sensor.normalized_artifact_id, job.session_id))
        return detect_gyro(table, DetectorConfig.model_validate(run.config), sync.offset_us)
    if job.kind == "delete_session":
        return None
    raise DomainError("Unknown job kind")


def publish(db, job, output, elapsed_ms):
    if job.kind == "normalize":
        sensor = db.get(m.SensorRecording, job.target_id)
        table, quality = output
        artifact = put_bytes(db, job.session_id, parquet_bytes(table), "sensor_parquet_v1")
        sensor.normalized_artifact_id, sensor.quality = artifact.id, quality
        sensor.duration_us, sensor.samples, sensor.status = (
            int(table["t_us"][-1].as_py()),
            len(table),
            "ready",
        )
        db.add(
            m.DataQualityReport(
                session_id=job.session_id, target_id=sensor.id, detector="csv_si@1.0.0", summary=quality
            )
        )
        # Serializing on the session row prevents concurrent revision collisions.
        db.get(m.RecordingSession, job.session_id, with_for_update=True)
        latest = db.scalars(
            select(m.SyncConfiguration)
            .where(m.SyncConfiguration.session_id == job.session_id)
            .order_by(m.SyncConfiguration.revision.desc())
        ).first()
        sync = m.SyncConfiguration(
            session_id=job.session_id,
            sensor_id=sensor.id,
            revision=latest.revision + 1 if latest else 1,
            offset_us=0,
        )
        db.add(sync)
        db.flush()
        session = db.get(m.RecordingSession, job.session_id)
        if session.demo_key == "synthetic-v1":
            config = DetectorConfig().model_dump()
            manifest = input_manifest(session.id, artifact.sha256, sync.id, config)
            identity = fingerprint(manifest)
            run = m.InferenceRun(
                session_id=session.id,
                sensor_id=sensor.id,
                sync_id=sync.id,
                fingerprint=identity,
                config=config,
                result={"input_manifest": manifest},
            )
            db.add(run)
            db.flush()
            enqueue(db, session.id, "inference", run.id)
    elif job.kind == "video_probe":
        video = db.get(m.VideoAsset, job.target_id)
        video.duration_us, video.width, video.height = (
            output["duration_us"],
            output["width"],
            output["height"],
        )
        video.metadata_json, video.status = output, "ready"
    elif job.kind == "inference":
        run = db.get(m.InferenceRun, job.target_id)
        for event in output.pop("events"):
            db.add(m.Prediction(session_id=job.session_id, run_id=run.id, **event))
        run.result = {**run.result, **output, "processing_ms": elapsed_ms}
        run.status = "succeeded"


def cleanup_session(db, session_id):
    # Fixed generated session directory, checked by resolve; no user paths.
    directory = resolve(session_id)
    if directory.is_dir():
        shutil.rmtree(directory)
    track_ids = select(m.PoseTrack.id).where(m.PoseTrack.session_id == session_id)
    db.execute(delete(m.PoseBatch).where(m.PoseBatch.track_id.in_(track_ids)))
    for model in [
        m.Prediction,
        m.EventAnnotation,
        m.AnnotationSet,
        m.DataQualityReport,
        m.InferenceRun,
        m.SyncConfiguration,
        m.PoseTrack,
        m.VideoAsset,
        m.SensorRecording,
        m.Artifact,
    ]:
        db.execute(delete(model).where(model.session_id == session_id))


def execute_job(job_id, token):
    start = time.perf_counter()
    try:
        with Session(engine) as db:
            job = db.get(m.ProcessingJob, job_id)
            if not job or job.lease_token != token or job.state != "running":
                return
            session = db.get(m.RecordingSession, job.session_id)
            if job.cancel_requested or (session.deleted_at and job.kind != "delete_session"):
                job.state = "cancelled"
                db.commit()
                return
            output = compute(db, job)
        with Session(engine) as db, db.begin():
            job = db.get(m.ProcessingJob, job_id)
            # Lock session before job, matching deletion's lock order.
            session = db.get(m.RecordingSession, job.session_id, with_for_update=True)
            job = db.get(m.ProcessingJob, job_id, with_for_update=True, populate_existing=True)
            if job.lease_token != token or job.state != "running" or job.lease_expires_at <= m.now():
                return
            if job.cancel_requested or (session.deleted_at and job.kind != "delete_session"):
                job.state = "cancelled"
                return
            if job.kind == "delete_session":
                cleanup_session(db, job.session_id)
            else:
                publish(db, job, output, round((time.perf_counter() - start) * 1000))
            job.state = "succeeded"
    except Exception as exc:
        with Session(engine) as db, db.begin():
            job = db.get(m.ProcessingJob, job_id, with_for_update=True)
            if job and job.lease_token == token:
                job.state = "failed"
                job.error = (
                    exc.message[:400]
                    if isinstance(exc, DomainError)
                    else "Processing failed; consult local worker logs"
                )
                model = {
                    "normalize": m.SensorRecording,
                    "video_probe": m.VideoAsset,
                    "inference": m.InferenceRun,
                }.get(job.kind)
                if model and (target := db.get(model, job.target_id)):
                    target.status = "failed"
        if not isinstance(exc, DomainError):
            import logging

            logging.exception("Job %s failed", job_id)


def finalize_pose(db, track, frames):
    if not frames:
        raise DomainError("No pose frames were submitted")
    times = [f["t_video_us"] for f in frames]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise DomainError("Pose frame timestamps must strictly increase")
    video = db.get(m.VideoAsset, track.video_id)
    if times[-1] > video.duration_us + 100_000:
        raise DomainError("Pose timestamps exceed source video")
    session = db.get(m.RecordingSession, track.session_id)
    aspect = video.width / video.height
    if abs(video.metadata_json.get("rotation", 0)) % 180 == 90:
        aspect = 1 / aspect
    frames = derive_features(frames, session.handedness, aspect)
    # Nested Parquet preserves per-frame no-person observations and landmark arrays.
    artifact = put_bytes(db, track.session_id, parquet_bytes(pa.Table.from_pylist(frames)), "pose_parquet_v1")
    track.artifact_id, track.status = artifact.id, "ready"
    detected = sum(bool(f["landmarks"]) for f in frames)
    gaps = [b - a for a, b in zip(times, times[1:])]
    track.quality = {
        "processed_frames": len(frames),
        "detected_frames": detected,
        "detection_fraction": detected / len(frames),
        "max_gap_us": max(gaps, default=0),
        "start_us": times[0],
        "end_us": times[-1],
        "coverage_note": "Sampled browser frames; not exhaustive video decoding",
    }
    db.add(
        m.DataQualityReport(
            session_id=track.session_id,
            target_id=track.id,
            detector="pose_coverage@1.0.0",
            summary=track.quality,
        )
    )
