import hashlib
import os
from pathlib import Path
from uuid import uuid4
from .config import STORAGE_ROOT
from .errors import DomainError
from .models import Artifact


def resolve(key: str) -> Path:
    root = STORAGE_ROOT.resolve()
    target = (root / key).resolve()
    if target == root or not target.is_relative_to(root):
        raise DomainError("Invalid storage reference", "INVALID_PATH", 400)
    return target


def put_bytes(db, session_id: str, content: bytes, kind: str) -> Artifact:
    key = f"{session_id}/{uuid4()}"
    target = resolve(key)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_suffix(".part")
    try:
        staging.write_bytes(content)
        os.replace(staging, target)
    finally:
        # A failed write/rename must not leave a partial upload on disk.
        staging.unlink(missing_ok=True)
    artifact = Artifact(
        session_id=session_id,
        storage_key=key,
        kind=kind,
        sha256=hashlib.sha256(content).hexdigest(),
        bytes=len(content),
    )
    db.add(artifact)
    db.flush()
    return artifact


def path_for(db, artifact_id: str, session_id: str) -> Path:
    artifact = db.get(Artifact, artifact_id)
    if not artifact or artifact.session_id != session_id or artifact.state != "ready":
        raise DomainError("Artifact unavailable", "ARTIFACT_UNAVAILABLE", 404)
    path = resolve(artifact.storage_key)
    if not path.is_file():
        raise DomainError("Artifact missing; processing cannot continue", "ARTIFACT_UNAVAILABLE", 409)
    return path
