"""Run as the nonroot API user; inspect real artifacts and only alter temporary permissions."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from rallysense import main
from rallysense import models as m
from rallysense.db import engine
from rallysense.errors import DomainError
from rallysense.storage import path_for
from sqlalchemy import select
from sqlalchemy.orm import Session

checked = 0
with Session(engine) as db:
    for artifact in db.scalars(select(m.Artifact)):
        with path_for(db, artifact.id, artifact.session_id).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == artifact.sha256
        checked += 1
assert os.getuid() != 0, "Permission regression must execute as a nonroot user"
original = main.STORAGE_ROOT
with tempfile.TemporaryDirectory(prefix="step55-readiness-") as temp:
    directory = Path(temp)
    try:
        os.chmod(directory, 0o555)
        main.STORAGE_ROOT = directory
        try:
            main.ready()
        except DomainError as error:
            assert error.code == "NOT_READY" and error.status == 503
            assert str(directory) not in error.message
        else:
            raise AssertionError("Unwritable storage falsely reported ready")
    finally:
        main.STORAGE_ROOT = original
        os.chmod(directory, 0o755)
assert main.ready() == {"status": "ready"}
assert not list(original.glob(".ready-*"))
print(
    json.dumps(
        {
            "artifact_files_checked": checked,
            "missing": 0,
            "mismatched": 0,
            "nonroot_unwritable_storage_status": 503,
            "writable_ready": True,
            "probe_files_remaining": 0,
        }
    )
)
