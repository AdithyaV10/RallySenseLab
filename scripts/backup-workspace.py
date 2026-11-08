"""Quiesced paired backup and fresh isolated restore. No live database/volume deletion."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["backup", "restore"])
parser.add_argument("--directory", type=Path, required=True)
parser.add_argument("--project", default="rallysense")
parser.add_argument("--env-file")
parser.add_argument("--file", action="append", dest="files")
args = parser.parse_args()
root = args.directory.resolve()
workspace = Path.cwd().resolve()
if not root.is_relative_to(workspace / "storage"):
    raise SystemExit("Backup directory must stay inside ignored workspace storage/")
compose = ["docker", "compose", "-p", args.project]
if args.env_file:
    compose += ["--env-file", args.env_file]
for file in args.files or ["docker-compose.yml"]:
    compose += ["-f", file]


def run(*command, **kwargs):
    try:
        result = subprocess.run(
            command,
            check=True,
            stderr=subprocess.PIPE,
            timeout=180,
            stdout=kwargs.pop("stdout", subprocess.PIPE),
            **kwargs,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            error.stderr.decode("utf-8", errors="replace")[-4000:]
        ) from error
    return result.stdout.decode() if result.stdout else ""


def service(*command, **kwargs):
    return run(*compose, *command, **kwargs)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


inventory_code = """import hashlib,json
from sqlalchemy import select
from sqlalchemy.orm import Session
from rallysense import models as m
from rallysense.db import Base,engine
from rallysense.storage import path_for
tables={}
with Session(engine) as db:
 for table in Base.metadata.sorted_tables:
  rows=[dict(r) for r in db.execute(select(table).order_by(*table.primary_key.columns)).mappings()]
  tables[table.name]={'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,default=str).encode()).hexdigest()}
 artifacts=list(db.scalars(select(m.Artifact)))
 for a in artifacts:
  with path_for(db,a.id,a.session_id).open('rb') as f:
   assert hashlib.file_digest(f,'sha256').hexdigest()==a.sha256
print(json.dumps({'tables':tables,'artifact_files_verified':len(artifacts)},sort_keys=True))"""


def inventory():
    return json.loads(
        service("run", "--rm", "--no-deps", "-T", "api", "python", "-c", inventory_code)
    )


if args.action == "backup":
    if root.exists():
        raise SystemExit("Refusing to overwrite an existing backup directory")
    root.mkdir(parents=True)
    running = service("ps", "--services", "--filter", "status=running").split()
    stopped = [name for name in ["web", "api", "worker"] if name in running]
    try:
        # Remove HTTP writers first, let the existing worker drain, then stop it.
        for name in ["web", "api"]:
            if name in stopped:
                service("stop", name)
        for _ in range(60):
            pending = int(
                service(
                    "exec",
                    "-T",
                    "db",
                    "psql",
                    "-U",
                    "rallysense",
                    "-d",
                    "rallysense",
                    "-Atc",
                    "SELECT count(*) FROM processing_jobs WHERE state IN ('queued','running')",
                )
            )
            if not pending:
                break
            time.sleep(2)
        else:
            raise SystemExit(
                "Queue did not drain; backup aborted without deleting data"
            )
        if "worker" in stopped:
            service("stop", "worker")
        recorded = inventory()
        with (root / "database.dump").open("wb") as output:
            service(
                "exec",
                "-T",
                "db",
                "pg_dump",
                "-U",
                "rallysense",
                "-d",
                "rallysense",
                "-Fc",
                stdout=output,
            )
        with (root / "artifacts.tar").open("wb") as output:
            service(
                "run",
                "--rm",
                "--no-deps",
                "-T",
                "--entrypoint",
                "tar",
                "api",
                "-C",
                "/data/storage",
                "-cf",
                "-",
                ".",
                stdout=output,
            )
        manifest = {
            "source_project": args.project,
            "quiesced": True,
            "inventory": recorded,
            "database_sha256": digest(root / "database.dump"),
            "artifacts_sha256": digest(root / "artifacts.tar"),
        }
        (root / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        if os.name != "nt":
            root.chmod(0o700)
            for path in root.iterdir():
                path.chmod(0o600)
        print(
            json.dumps(
                {
                    "backup_complete": True,
                    "directory": str(root),
                    "artifact_files_verified": recorded["artifact_files_verified"],
                }
            )
        )
    finally:
        if stopped:
            service("start", *stopped)
else:
    if not re.fullmatch(r"rallysense-restore-[a-z0-9-]+", args.project):
        raise SystemExit("Restore requires a unique rallysense-restore-* project name")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert args.project != manifest["source_project"]
    assert digest(root / "database.dump") == manifest["database_sha256"]
    assert digest(root / "artifacts.tar") == manifest["artifacts_sha256"]
    for kind in ["ps", "volume", "network"]:
        command = ["docker", kind, "ls"] if kind != "ps" else ["docker", "ps", "-a"]
        existing = run(
            *command,
            "--filter",
            f"label=com.docker.compose.project={args.project}",
            "--format",
            "{{.ID}}" if kind == "ps" else "{{.Name}}",
        )
        if existing.strip():
            raise SystemExit("Restore target already exists; refusing to overwrite it")
    compose += ["-f", "infrastructure/compose.restore-test.yml"]
    service("up", "-d", "db")
    try:
        for _ in range(60):
            try:
                service(
                    "exec",
                    "-T",
                    "db",
                    "sh",
                    "-c",
                    'PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U rallysense -d rallysense -Atc "SELECT 1"',
                )
                break
            except RuntimeError:
                time.sleep(1)
        else:
            raise SystemExit("Isolated restore database did not become ready")
        with (root / "database.dump").open("rb") as source:
            service(
                "exec",
                "-T",
                "db",
                "pg_restore",
                "-U",
                "rallysense",
                "-d",
                "rallysense",
                "--exit-on-error",
                stdin=source,
            )
        with (root / "artifacts.tar").open("rb") as source:
            service(
                "run",
                "--rm",
                "--no-deps",
                "-T",
                "--entrypoint",
                "tar",
                "api",
                "-C",
                "/data/storage",
                "-xf",
                "-",
                stdin=source,
            )
        restored = inventory()
        assert restored == manifest["inventory"], (
            "Restored rows or artifact hashes differ"
        )
        migration = service(
            "run", "--rm", "--no-deps", "-T", "api", "alembic", "current"
        ).strip()
        service(
            "run",
            "--rm",
            "--no-deps",
            "-T",
            "api",
            "python",
            "-c",
            'from rallysense.main import ready; assert ready()=={"status":"ready"}',
        )
        print(
            json.dumps(
                {
                    "restore_verified": True,
                    "project": args.project,
                    "published_ports": [],
                    "artifact_files_verified": restored["artifact_files_verified"],
                    "tables_verified": len(restored["tables"]),
                    "migration": migration,
                    "retained": "Isolated database/artifact volumes retained; original project untouched",
                }
            )
        )
    finally:
        service("stop", "db")
