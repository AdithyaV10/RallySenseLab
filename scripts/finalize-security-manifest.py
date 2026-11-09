"""Freeze local candidate aliases and evidence identities. Does not approve or publish images."""

import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

root = Path("docs/evidence/step6_5")
reports = {
    "api": "final/api",
    "api_readonly": "final/api_readonly",
    "web": "final/web",
    "postgres": "final/postgres",
    "caddy": "caddy",
}
names = {
    "api": "api",
    "api_readonly": "api-readonly",
    "web": "web",
    "postgres": "postgres",
    "caddy": "caddy",
}
records = []
for name, path in reports.items():
    scan = json.loads((root / f"{path}.scan-command.json").read_text())
    inspected = json.loads(
        subprocess.check_output(["docker", "image", "inspect", scan["image"]])
    )[0]
    assert inspected["Id"] == scan["image_id"] and scan["exit_code"] == 0
    alias = f"rallysense-{names[name]}:release-step6_5-rc1"
    old = subprocess.run(
        ["docker", "image", "inspect", alias], capture_output=True, check=False
    )
    if old.returncode == 0:
        assert json.loads(old.stdout)[0]["Id"] == inspected["Id"], (
            "Frozen alias already belongs to a different candidate"
        )
    else:
        subprocess.run(["docker", "image", "tag", inspected["Id"], alias], check=True)
    archive = Path("storage/step6_5/scanner-inputs") / (
        f"final/{name}.tar" if path.startswith("final/") else f"{name}.tar"
    )
    with archive.open("rb") as stream:
        assert (
            hashlib.file_digest(stream, "sha256").hexdigest() == scan["archive_sha256"]
        )
    config_digest, platform_digest = None, None
    with tarfile.open(archive) as tar:
        manifest = json.load(tar.extractfile("manifest.json"))[0]
        config = tar.extractfile(manifest["Config"]).read()
        config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
        if "index.json" in tar.getnames():
            index = json.load(tar.extractfile("index.json"))
            descriptor = index["manifests"][0]
            blob = json.load(
                tar.extractfile("blobs/sha256/" + descriptor["digest"].split(":")[1])
            )
            if "manifests" in blob:
                platform_digest = next(
                    d["digest"]
                    for d in blob["manifests"]
                    if d.get("platform", {}).get("architecture") == "amd64"
                )
            else:
                platform_digest = descriptor["digest"]
    records.append(
        {
            "name": name,
            "image": scan["image"],
            "release_tag": alias,
            "image_id": inspected["Id"],
            "config_digest": config_digest,
            "platform_manifest_digest": platform_digest,
            "platform": f"{inspected['Os']}/{inspected['Architecture']}",
            "archive": str(archive).replace("\\", "/"),
            "archive_sha256": scan["archive_sha256"],
            "archive_bytes": scan["archive_bytes"],
            "scan_report": f"docs/evidence/step6_5/{path}.trivy.json",
            "security_approval": "human_review_required",
        }
    )
files = [
    p
    for folder in ["apps/api/src", "apps/web/src"]
    for p in Path(folder).rglob("*")
    if p.is_file() and p.suffix in [".py", ".ts", ".tsx", ".css"]
]
files += [
    Path(p)
    for p in [
        "apps/api/uv.lock",
        "apps/web/package-lock.json",
        "infrastructure/api.Dockerfile",
        "infrastructure/web.Dockerfile",
        "infrastructure/postgres.Dockerfile",
        "infrastructure/caddy.Dockerfile",
    ]
]
digests = {
    str(p).replace("\\", "/"): hashlib.sha256(
        p.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    for p in sorted(files)
}
target = Path("infrastructure/release-manifest.json")
previous = root / "previous-release-manifest.json"
if not previous.exists():
    previous.write_bytes(target.read_bytes())
output = {
    "source_checkpoint": "208e96dbe52d1a36670f16ae05656b6a5a700a23",
    "build_id": "step6_5-rc1-208e96d",
    "platform": "linux/amd64",
    "source_tree_sha256": hashlib.sha256(
        json.dumps(digests, sort_keys=True).encode()
    ).hexdigest(),
    "source_file_hashes": digests,
    "public_release_authorized": False,
    "image_security_gate_passed": False,
    "candidate_status": "ENGINEERING_VERIFICATION_FOR_HUMAN_SECURITY_REVIEW",
    "notes": "No images are security-approved. Exact local archive hashes plus OCI config/platform digests are retained; Docker image Id representation can depend on image-store mode. Custom static FFmpeg requires the separate native component/advisory review.",
    "rollback_manifest": "docs/evidence/step6_5/previous-release-manifest.json",
    "release_modes": {
        "A": {
            "software_acceptance": True,
            "security_approval": False,
            "ready_for_human_security_review": True,
            "conditions": [
                "Explicit PostgreSQL XML/gateway JWK/OS/SBOM residual-risk disposition",
                "Fixture/model/content approval",
                "External deployment authorization and verification",
            ],
        },
        "B": {
            "software_acceptance": True,
            "security_approval": False,
            "ready_for_release_approval": False,
            "blockers": [
                "CVE-2026-107678 reachable bounded native MOV/PSSH denial of service",
                "CVE-2026-107676 unresolved Matroska HDR10+ serialization applicability",
                "Shared residual-risk disposition and external gates",
            ],
        },
    },
    "images": records,
}
target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "frozen_local_candidate_aliases": [r["release_tag"] for r in records],
            "security_gate_passed": False,
            "public_actions": False,
        }
    )
)
