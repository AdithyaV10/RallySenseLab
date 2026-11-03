"""Recover storage orphans after the documented 24-hour grace period."""

import time
from datetime import timedelta
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from .db import engine
from .config import STORAGE_ROOT
from .models import Artifact, PoseTrack, PoseBatch, now


def reconcile_storage():
    with Session(engine) as db, db.begin():
        keys = set(db.scalars(select(Artifact.storage_key)))
        tracks = list(
            db.scalars(
                select(PoseTrack).where(
                    PoseTrack.status == "processing", PoseTrack.created_at < now() - timedelta(hours=24)
                )
            )
        )
        for track in tracks:
            track.status = "failed"
            db.execute(delete(PoseBatch).where(PoseBatch.track_id == track.id))
    root = STORAGE_ROOT.resolve()
    if not root.exists():
        return
    for directory in root.iterdir():
        if directory.is_symlink() or not directory.is_dir():
            continue
        try:
            UUID(directory.name)
        except ValueError:
            continue
        for path in directory.iterdir():
            if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
                continue
            try:
                UUID(path.stem if path.suffix == ".part" else path.name)
            except ValueError:
                continue
            key = f"{directory.name}/{path.name}"
            if key not in keys and time.time() - path.stat().st_mtime > 24 * 3600:
                path.unlink()
