"""Audit only the static build and reviewed synthetic exports. No cloud actions."""

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    type=Path,
    default=Path("docs/evidence/static-showcase/static-build-manifest.json"),
)
args = parser.parse_args()
app = Path("apps/showcase")
dist = app / "dist"
data = json.loads((dist / "data/showcase.json").read_text(encoding="utf-8"))
provenance = json.loads((dist / "data/provenance.json").read_text())
approved = json.loads(Path("docs/evidence/step6_6/demo-fixtures.json").read_text())
inventory = json.loads(Path("docs/evidence/step6_6/fixture-inventory.json").read_text())
assert (
    data["dataset_kind"] == "synthetic"
    and data["reference"]["manifest"]["independent"] is False
)
assert data["pose"]["config"]["provenance"] == "generated_analytical_landmarks"
assert len(data["sensor"]["samples"]) == 801 and len(data["pose"]["frames"]) == 241
assert len(data["experiments"]) == 10
assert (
    hashlib.sha256((dist / "data/showcase.json").read_bytes()).hexdigest()
    == provenance["dataset_sha256"]
)
assert (
    hashlib.sha256((dist / "data/generated-motion.mp4").read_bytes()).hexdigest()
    == data["video"]["sha256"]
)
assert data["video"]["sha256"] in {
    a["sha256"] for a in inventory["artifacts"] if a["kind"] == "video_mp4"
}
for expected in approved["curated_experiments"]:
    actual = next(e for e in data["experiments"] if e["id"] == expected["id"])
    assert (
        actual["status"] == expected["status"]
        and actual["result"].get("evaluation") == expected["evaluation"]
    )
for e in data["experiments"]:
    report = json.loads((dist / f"reports/{e['id']}.json").read_text(encoding="utf-8"))
    assert (
        report["experiment"] == e
        and report["source_dataset_sha256"] == provenance["dataset_sha256"]
    )
    assert report["reference"]["manifest"]["independent"] is False
    md = (dist / f"reports/{e['id']}.md").read_text(encoding="utf-8")
    assert e["fingerprint"] in md and "not real-world model accuracy" in md
    if e["status"] == "failed":
        assert "Explicit failure code" in md
allow = {
    "index.html",
    "favicon.svg",
    "NOTICES.txt",
    "data/showcase.json",
    "data/provenance.json",
    "data/generated-motion.mp4",
}
allow.update(
    f"reports/{e['id']}.{ext}" for e in data["experiments"] for ext in ["json", "md"]
)
secrets = []
for file in [
    Path("storage/step6_6/demo.env"),
    Path("storage/step6_6/production-render.env"),
    Path(".env"),
]:
    if file.exists():
        for line in file.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                if (
                    k in ["LOCAL_TOKEN", "SITE_ACCESS_PASSWORD", "POSTGRES_PASSWORD"]
                    and len(v) >= 16
                ):
                    secrets.append(v)
records = []
for p in sorted(dist.rglob("*")):
    if not p.is_file():
        continue
    name = p.relative_to(dist).as_posix()
    assert name in allow or re.fullmatch(r"assets/[A-Za-z0-9_-]+\.(?:js|css)", name), (
        f"Unapproved build file {name}"
    )
    raw = p.read_bytes()
    if name in allow and name != "index.html":
        assert (app / "public" / name).read_bytes() == raw, (
            f"Stale copied asset: {name}"
        )
    assert not any(s.encode() in raw for s in secrets), "Secret found (value withheld)"
    if p.suffix != ".mp4":
        assert not re.search(
            rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|aws_secret_access_key|postgresql\+psycopg://|data/private|C:\\\\Users\\\\",
            raw,
        ), f"Sensitive material pattern: {name}"
    records.append(
        {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    )
assert not any(
    p.suffix in [".wasm", ".task", ".exe", ".dll", ".so", ".map", ".key", ".pem"]
    for p in dist.rglob("*")
)
notices = (dist / "NOTICES.txt").read_text(encoding="utf-8")
assert all(
    n in notices
    for n in ["react ", "react-dom ", "scheduler ", "lucide-react ", "Permission"]
)


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ["src", "href"] and value and not value.startswith("#"):
                assert not value.startswith(("http:", "https:", "//"))
                assert (dist / value.removeprefix("./").lstrip("/")).is_file(), value


Links().feed((dist / "index.html").read_text())
result = {
    "production_files": len(records),
    "total_bytes": sum(r["bytes"] for r in records),
    "dataset_sha256": provenance["dataset_sha256"],
    "source_release": data["source_release"],
    "reviewed_artifact_hashes": True,
    "stored_experiments_verified": 10,
    "reports_verified": 20,
    "generated_only": True,
    "mediapipe_runtime_or_weights": False,
    "native_executables": False,
    "backend_or_credentials": False,
    "secret_values_checked": len(secrets),
    "secret_matches": 0,
    "html_asset_paths_verified": True,
    "files": records,
    "aws_resources_created": [],
    "public_deployment_verified": False,
}
out = args.output
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "files"}))
