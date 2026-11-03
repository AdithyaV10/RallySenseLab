import hashlib
import os
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models as m, schemas as s
from ..config import MAX_VIDEO_BYTES
from ..errors import DomainError
from ..jobs import enqueue
from ..storage import resolve, path_for
from .common import active_session, owned

router = APIRouter()


@router.post("/sessions/{session_id}/videos", response_model=s.JobOut, status_code=202)
async def upload_video(session_id: UUID, file: UploadFile = File(), db: Session = Depends(get_db)):
    session = active_session(db, session_id)
    if not file.filename or not file.filename.lower().endswith((".mp4", ".webm")):
        raise DomainError("Upload .mp4 (H.264) or .webm (VP8/VP9)", "UNSUPPORTED_MEDIA", 415)
    key = f"{session.id}/{uuid4()}"
    target = resolve(key)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_suffix(".part")
    size, digest = 0, hashlib.sha256()
    try:
        with staging.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_VIDEO_BYTES:
                    raise DomainError("Video exceeds 500 MiB", "RESOURCE_LIMIT", 413)
                digest.update(chunk)
                output.write(chunk)
        os.replace(staging, target)
        artifact = m.Artifact(
            session_id=session.id, storage_key=key, kind="raw_video", bytes=size, sha256=digest.hexdigest()
        )
        db.add(artifact)
        db.flush()
        video = m.VideoAsset(
            session_id=session.id,
            artifact_id=artifact.id,
            name=file.filename.replace("\\", "/").split("/")[-1][:160],
        )
        db.add(video)
        db.flush()
        return enqueue(db, session.id, "video_probe", video.id)
    finally:
        staging.unlink(missing_ok=True)


@router.get("/videos/{video_id}/content")
def content(video_id: UUID, db: Session = Depends(get_db)):
    video = owned(db, m.VideoAsset, video_id)
    if video.status != "ready":
        raise DomainError("Video not ready", "INVALID_STATE", 409)
    return FileResponse(
        path_for(db, video.artifact_id, video.session_id),
        media_type=video.metadata_json["media_type"],
        headers={"Cache-Control": "no-store"},
    )
