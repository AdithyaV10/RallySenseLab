"""Package the verified static output locally; never upload or create AWS resources."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    type=Path,
    default=Path("storage/static-showcase/rallysense-showcase.zip"),
)
args = parser.parse_args()
target = args.output.resolve()
assert target.is_relative_to(Path("storage").resolve()) and not target.exists(), (
    "Use a new package path inside ignored storage/"
)
manifest = json.loads(
    Path("docs/evidence/static-showcase/static-build-manifest.json").read_text()
)
root = Path("apps/showcase/dist")
assert len(manifest["files"]) == 28
for row in manifest["files"]:
    assert (
        hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
    ), row["path"]
target.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(
    target, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
) as archive:
    for row in manifest["files"]:
        info = zipfile.ZipInfo(row["path"], date_time=(2026, 11, 9, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, (root / row["path"]).read_bytes())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    assert sorted(archive.namelist()) == sorted(r["path"] for r in manifest["files"])
    for row in manifest["files"]:
        assert hashlib.sha256(archive.read(row["path"])).hexdigest() == row["sha256"]
result = {
    "package": str(target.relative_to(Path.cwd())),
    "bytes": target.stat().st_size,
    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "static_files_verified": 28,
    "network_actions": False,
    "aws_resources_created": [],
}
Path("docs/evidence/static-showcase/package.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print(json.dumps(result))
