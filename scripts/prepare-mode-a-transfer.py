"""Create a private local allowlisted transfer directory; no network actions.

Requires a clean checkpoint. Excludes Git history, old evidence, private data,
development volumes/secrets, and the full upload-enabled API image.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output", type=Path, default=Path("storage/step6_6/mode-a-transfer")
)
args = parser.parse_args()
root = args.output.resolve()
assert root.is_relative_to(Path("storage").resolve()) and not root.exists()
git = ["git", "-c", "safe.directory=" + Path.cwd().as_posix()]
assert not subprocess.check_output(
    [*git, "status", "--porcelain"], text=True
).strip(), "Commit/review local changes first"
m = json.loads(Path("infrastructure/mode-a-release-manifest.json").read_text())
assert m["mode"] == "A" and not m["mode_b_included"]
assert {r["name"] for r in m["images"]} == {"api_readonly", "web", "postgres", "caddy"}
assert m["generated_fixture_pair"]["private_data_imported"] is False
files = sorted(
    set(m["source_file_hashes"])
    | {
        "apps/api/pyproject.toml",
        "infrastructure/mode-a-release-manifest.json",
        "infrastructure/compose.restore-test.yml",
        "data/assets.lock.json",
        "scripts/mode-a-images.py",
        "scripts/prepare-mode-a-env.py",
        "scripts/check-mode-a-production.py",
        "scripts/smoke-release.py",
        "scripts/backup-workspace.py",
        "scripts/prepare-mode-a-transfer.py",
        "docs/STEP6_6_MODE_A_REVIEW.md",
        "docs/MODE_A_DEPLOYMENT_CHECKLIST.md",
        "docs/MODE_A_RELEASE_DECISION.md",
        "docs/THIRD_PARTY_NOTICES.md",
    }
)
root.mkdir(parents=True, mode=0o700)
subprocess.run(
    [
        *git,
        "archive",
        "--format=tar",
        "--output",
        str(root / "mode-a-source.tar"),
        "HEAD",
        *files,
    ],
    check=True,
)
for r in m["images"]:
    destination = root / r["archive"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(r["archive"], destination)
pair = Path(m["generated_fixture_pair"]["directory"])
for filename in ["manifest.json", "database.dump", "artifacts.tar"]:
    destination = root / pair / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pair / filename, destination)
checksums = []
for p in sorted(root.rglob("*")):
    if p.is_file():
        with p.open("rb") as f:
            checksum = hashlib.file_digest(f, "sha256").hexdigest()
        checksums.append(f"{checksum}  {p.relative_to(root).as_posix()}")
(root / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
print(
    json.dumps(
        {
            "local_bundle": str(root),
            "files": len(checksums),
            "source_commit": subprocess.check_output(
                [*git, "rev-parse", "HEAD"], text=True
            ).strip(),
            "private_data_or_secrets_copied": False,
            "full_api_image_included": False,
            "network_actions": False,
        }
    )
)
