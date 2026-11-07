"""Run inside API container. Check hashes and demonstrate read-only-storage readiness defect."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from rallysense import main, storage
from rallysense import models as m
from rallysense.db import engine
from sqlalchemy import select
from sqlalchemy.orm import Session

checked, missing, mismatched = 0, [], []
with Session(engine) as db:
    for row in db.scalars(select(m.Artifact)):
        path = storage.resolve(row.storage_key)
        if not path.is_file():
            missing.append(row.id)
        else:
            with path.open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != row.sha256:
                    mismatched.append(row.id)
        checked += 1
assert not missing and not mismatched, (missing, mismatched)
with tempfile.TemporaryDirectory(prefix="step5-readiness-") as temp:
    directory = Path(temp)
    original = main.STORAGE_ROOT
    try:
        os.chmod(directory, 0o555)
        main.STORAGE_ROOT = directory
        response = main.ready()
        writable = True
        try:
            (directory / "write-probe").write_bytes(b"probe")
        except PermissionError:
            writable = False
        assert not writable, "Test precondition: run as nonroot API user"
        assert response == {"status": "ready"}
    finally:
        main.STORAGE_ROOT = original
        os.chmod(directory, 0o755)
print(
    json.dumps(
        {
            "artifact_files_checked": checked,
            "missing": missing,
            "mismatched": mismatched,
            "readonly_directory_write_succeeds": writable,
            "readiness_response": response,
            "finding": "Readiness checks mkdir(exist_ok=True), not artifact writability",
        }
    )
)
