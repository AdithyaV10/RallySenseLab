from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Boolean,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc)


class Row:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Participant(Row, Base):
    __tablename__ = "participants"
    pseudonym: Mapped[str] = mapped_column(String(80), unique=True)


class RecordingSession(Row, Base):
    __tablename__ = "sessions"
    title: Mapped[str] = mapped_column(String(160))
    participant_id: Mapped[str | None] = mapped_column(ForeignKey("participants.id"))
    dataset_kind: Mapped[str] = mapped_column(String(20), default="recorded")
    handedness: Mapped[str] = mapped_column(String(12), default="right")
    notes: Mapped[str] = mapped_column(String(2000), default="")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    demo_key: Mapped[str | None] = mapped_column(String(80), unique=True)
    collection_profile: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    collection_revision: Mapped[int] = mapped_column(Integer, default=1, server_default="1")


class Owned(Row):
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)


class Artifact(Owned, Base):
    __tablename__ = "artifacts"
    storage_key: Mapped[str] = mapped_column(String(200), unique=True)
    kind: Mapped[str] = mapped_column(String(40))
    sha256: Mapped[str] = mapped_column(String(64))
    bytes: Mapped[int] = mapped_column(BigInteger)
    state: Mapped[str] = mapped_column(String(20), default="ready")


class SensorRecording(Owned, Base):
    __tablename__ = "sensor_recordings"
    raw_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"))
    normalized_artifact_id: Mapped[str | None] = mapped_column(ForeignKey("artifacts.id"))
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    mapping: Mapped[dict] = mapped_column(JSONB)
    quality: Mapped[dict] = mapped_column(JSONB, default=dict)
    duration_us: Mapped[int] = mapped_column(BigInteger, default=0)
    samples: Mapped[int] = mapped_column(Integer, default=0)
    placement: Mapped[str] = mapped_column(String(80), default="unknown")


class VideoAsset(Owned, Base):
    __tablename__ = "video_assets"
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"))
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    duration_us: Mapped[int] = mapped_column(BigInteger, default=0)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class PoseTrack(Owned, Base):
    __tablename__ = "pose_tracks"
    video_id: Mapped[str] = mapped_column(ForeignKey("video_assets.id"))
    artifact_id: Mapped[str | None] = mapped_column(ForeignKey("artifacts.id"))
    status: Mapped[str] = mapped_column(String(20), default="processing")
    config: Mapped[dict] = mapped_column(JSONB)
    quality: Mapped[dict] = mapped_column(JSONB, default=dict)


class PoseBatch(Row, Base):
    __tablename__ = "pose_batches"
    track_id: Mapped[str] = mapped_column(ForeignKey("pose_tracks.id"), index=True)
    batch_index: Mapped[int] = mapped_column(Integer)
    digest: Mapped[str] = mapped_column(String(64))
    frames: Mapped[list] = mapped_column(JSONB)
    __table_args__ = (UniqueConstraint("track_id", "batch_index"),)


class SyncConfiguration(Owned, Base):
    __tablename__ = "sync_configurations"
    revision: Mapped[int] = mapped_column(Integer)
    sensor_id: Mapped[str] = mapped_column(ForeignKey("sensor_recordings.id"))
    offset_us: Mapped[int] = mapped_column(BigInteger)
    method: Mapped[str] = mapped_column(String(40), default="manual_offset")
    video_id: Mapped[str | None] = mapped_column(ForeignKey("video_assets.id"))
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    __table_args__ = (UniqueConstraint("session_id", "revision"),)


class AnnotationSet(Owned, Base):
    __tablename__ = "annotation_sets"
    name: Mapped[str] = mapped_column(String(120), default="Manual reference")
    provenance: Mapped[str] = mapped_column(String(30), default="human")
    revision: Mapped[int] = mapped_column(Integer, default=1)


class EventAnnotation(Owned, Base):
    __tablename__ = "event_annotations"
    set_id: Mapped[str] = mapped_column(ForeignKey("annotation_sets.id"))
    t_session_us: Mapped[int] = mapped_column(BigInteger)
    event_type: Mapped[str] = mapped_column(String(60), default="swing_apex_v1")
    note: Mapped[str] = mapped_column(String(1000), default="")
    revision: Mapped[int] = mapped_column(Integer, default=1)


class InferenceRun(Owned, Base):
    __tablename__ = "inference_runs"
    sensor_id: Mapped[str] = mapped_column(ForeignKey("sensor_recordings.id"))
    sync_id: Mapped[str] = mapped_column(ForeignKey("sync_configurations.id"))
    algorithm: Mapped[str] = mapped_column(String(80), default="imu_gyro_peak@1.0.0")
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    config: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    result: Mapped[dict] = mapped_column(JSONB, default=dict)


class Prediction(Owned, Base):
    __tablename__ = "predictions"
    run_id: Mapped[str] = mapped_column(ForeignKey("inference_runs.id"), index=True)
    t_session_us: Mapped[int] = mapped_column(BigInteger)
    event_type: Mapped[str] = mapped_column(String(40), default="gyro_peak_v1")
    magnitude: Mapped[float] = mapped_column(Float)
    prominence: Mapped[float] = mapped_column(Float)


class ProcessingJob(Owned, Base):
    __tablename__ = "processing_jobs"
    kind: Mapped[str] = mapped_column(String(40))
    target_id: Mapped[str] = mapped_column(String(36))
    state: Mapped[str] = mapped_column(String(20), default="queued")
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[str | None] = mapped_column(String(36))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(String(400))
    __table_args__ = (Index("ix_job_claim", "state", "lease_expires_at", "created_at"),)


class DataQualityReport(Owned, Base):
    __tablename__ = "data_quality_reports"
    target_id: Mapped[str] = mapped_column(String(36))
    detector: Mapped[str] = mapped_column(String(80))
    summary: Mapped[dict] = mapped_column(JSONB)


class ReferenceSnapshot(Owned, Base):
    __tablename__ = "reference_snapshots"
    set_id: Mapped[str] = mapped_column(ForeignKey("annotation_sets.id"))
    revision: Mapped[int] = mapped_column(Integer)
    manifest: Mapped[dict] = mapped_column(JSONB)
    events: Mapped[list] = mapped_column(JSONB)
    fingerprint: Mapped[str] = mapped_column(String(64))


class Experiment(Owned, Base):
    __tablename__ = "experiments"
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    reference_id: Mapped[str | None] = mapped_column(ForeignKey("reference_snapshots.id"))
    manifest: Mapped[dict] = mapped_column(JSONB)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    error: Mapped[str | None] = mapped_column(String(400))
    reused_from_id: Mapped[str | None] = mapped_column(String(36))


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state: Mapped[str] = mapped_column(String(20))


# Enforce ownership in PostgreSQL as well as at the API boundary.
for _table in list(Base.metadata.tables.values()):
    if "session_id" in _table.c:
        _table.append_constraint(UniqueConstraint("session_id", "id", name=f"uq_{_table.name}_owner"))

for _model, _references in [
    (SensorRecording, {"raw_artifact_id": "artifacts", "normalized_artifact_id": "artifacts"}),
    (VideoAsset, {"artifact_id": "artifacts"}),
    (PoseTrack, {"video_id": "video_assets", "artifact_id": "artifacts"}),
    (SyncConfiguration, {"sensor_id": "sensor_recordings", "video_id": "video_assets"}),
    (EventAnnotation, {"set_id": "annotation_sets"}),
    (InferenceRun, {"sensor_id": "sensor_recordings", "sync_id": "sync_configurations"}),
    (Prediction, {"run_id": "inference_runs"}),
    (ReferenceSnapshot, {"set_id": "annotation_sets"}),
    (Experiment, {"reference_id": "reference_snapshots"}),
]:
    for _column, _target in _references.items():
        _model.__table__.append_constraint(
            ForeignKeyConstraint(
                ["session_id", _column],
                [f"{_target}.session_id", f"{_target}.id"],
                name=f"fk_{_model.__tablename__}_{_column}_owner",
            )
        )
