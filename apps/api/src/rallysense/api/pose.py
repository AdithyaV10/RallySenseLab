import hashlib
import json
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
import pyarrow.parquet as pq
from ..db import get_db
from .. import models as m, schemas as s
from ..errors import DomainError
from ..jobs import finalize_pose
from ..storage import path_for
from .common import owned

router = APIRouter()
MAX_BATCHES = 200
MAX_FRAMES = 30_000


@router.post("/videos/{video_id}/pose-tracks", response_model=s.PoseOut, status_code=201)
def start_pose(video_id: UUID, payload: s.PoseStart, db: Session = Depends(get_db, scope="function")):
    video = owned(db, m.VideoAsset, video_id)
    if video.status != "ready":
        raise DomainError("Video not ready", "INVALID_STATE", 409)
    raw = db.get(m.Artifact, video.artifact_id)
    track = m.PoseTrack(
        session_id=video.session_id,
        video_id=video.id,
        config={
            **payload.model_dump(),
            "video_sha256": raw.sha256,
            "running_mode": "VIDEO",
            "delegate": "CPU",
        },
    )
    db.add(track)
    db.flush()
    return track


@router.put("/pose-tracks/{track_id}/batches/{index}")
def pose_batch(
    track_id: UUID, index: int, payload: s.PoseBatchIn, db: Session = Depends(get_db, scope="function")
):
    track = owned(db, m.PoseTrack, track_id)
    track = db.get(m.PoseTrack, track.id, with_for_update=True)
    if track.status != "processing" or not 0 <= index < MAX_BATCHES:
        raise DomainError("Track is finalized or batch limit reached", "INVALID_STATE", 409)
    frames = payload.model_dump()["frames"]
    times = [frame["t_video_us"] for frame in frames]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise DomainError("Pose frame timestamps must strictly increase")
    video = db.get(m.VideoAsset, track.video_id)
    if times[-1] > video.duration_us + 100_000:
        raise DomainError("Pose timestamps exceed source video")
    digest = hashlib.sha256(json.dumps(frames, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    old = db.scalars(
        select(m.PoseBatch).where(m.PoseBatch.track_id == track.id, m.PoseBatch.batch_index == index)
    ).first()
    if old:
        if old.digest != digest:
            raise DomainError("Conflicting pose batch retry", "REVISION_CONFLICT", 409)
        return {"accepted": len(frames)}
    count = db.scalar(
        select(func.coalesce(func.sum(func.jsonb_array_length(m.PoseBatch.frames)), 0)).where(
            m.PoseBatch.track_id == track.id
        )
    )
    if count + len(frames) > MAX_FRAMES:
        raise DomainError("Pose track exceeds 30,000 observations", "RESOURCE_LIMIT", 413)
    db.add(m.PoseBatch(track_id=track.id, batch_index=index, digest=digest, frames=frames))
    return {"accepted": len(frames)}


@router.post("/pose-tracks/{track_id}/complete", response_model=s.PoseOut)
def complete_pose(
    track_id: UUID,
    payload: s.PoseComplete = Body(default=s.PoseComplete()),
    db: Session = Depends(get_db, scope="function"),
):
    track = owned(db, m.PoseTrack, track_id)
    track = db.get(m.PoseTrack, track.id, with_for_update=True)
    if track.status == "ready":
        return track
    if track.status != "processing":
        raise DomainError("Track is not processing", "INVALID_STATE", 409)
    batches = list(
        db.scalars(
            select(m.PoseBatch).where(m.PoseBatch.track_id == track.id).order_by(m.PoseBatch.batch_index)
        )
    )
    if [b.batch_index for b in batches] != list(range(len(batches))):
        raise DomainError("Pose batch sequence is incomplete", "MISSING_INPUT", 409)
    frames = [frame for batch in batches for frame in batch.frames]
    if len(frames) > MAX_FRAMES or (
        payload.expected_frames is not None and len(frames) != payload.expected_frames
    ):
        raise DomainError("Pose observation count is incomplete or exceeds capacity", "MISSING_INPUT", 409)
    finalize_pose(db, track, frames)
    db.execute(delete(m.PoseBatch).where(m.PoseBatch.track_id == track.id))
    return track


@router.post("/pose-tracks/{track_id}/fail", response_model=s.PoseOut)
def fail_pose(track_id: UUID, db: Session = Depends(get_db, scope="function")):
    track = owned(db, m.PoseTrack, track_id)
    if track.status == "processing":
        track.status = "failed"
        db.execute(delete(m.PoseBatch).where(m.PoseBatch.track_id == track.id))
    return track


@router.get("/pose-tracks/{track_id}/frames", response_model=s.PoseFramesOut)
def pose_frames(
    track_id: UUID,
    start_us: int = Query(0, ge=0),
    end_us: int = Query(600_000_000, ge=0),
    max_frames: int = Query(2000, ge=1, le=5000),
    db: Session = Depends(get_db, scope="function"),
):
    track = owned(db, m.PoseTrack, track_id)
    if track.status != "ready":
        raise DomainError("Pose track not ready", "INVALID_STATE", 409)
    if end_us < start_us:
        raise DomainError("Pose window end must follow start")
    table = pq.read_table(
        path_for(db, track.artifact_id, track.session_id),
        filters=[("t_video_us", ">=", start_us), ("t_video_us", "<=", end_us)],
    )
    return {
        "frames": table.slice(0, max_frames).to_pylist(),
        "source_count": len(table),
        "truncated": len(table) > max_frames,
    }
