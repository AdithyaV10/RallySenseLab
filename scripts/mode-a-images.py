"""Freeze/verify/load four local Mode A archives. Never pulls or publishes images.

Load verifies every archive before any Docker mutation, then sets reviewed aliases.
"""

import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["freeze", "verify", "load"])
args = parser.parse_args()
target = Path("infrastructure/mode-a-release-manifest.json")


def docker(*cmd):
    return subprocess.check_output(["docker", *cmd], text=True, encoding="utf-8")


def checksum(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def archive_info(path):
    with tarfile.open(path) as tar:
        m = json.load(tar.extractfile("manifest.json"))[0]
        raw = tar.extractfile(m["Config"]).read()
        config = json.loads(raw)
        return "sha256:" + hashlib.sha256(raw).hexdigest(), config


if args.action == "freeze":
    records = []
    for name, prefix, repo in [
        ("api_readonly", "", "api-readonly"),
        ("postgres", "maintained-helper/", "postgres-mode-a"),
        ("web", "", "web"),
        ("caddy", "", "caddy"),
    ]:
        folder = Path("docs/evidence/step6_6")
        scan = json.loads((folder / f"{prefix}{name}.scan-command.json").read_text())
        inspected = json.loads(docker("image", "inspect", scan["image"]))[0]
        assert scan["exit_code"] == 0 and scan["image_id"] == inspected["Id"]
        archive = Path("storage/step6_6/scanner-inputs") / prefix / f"{name}.tar"
        assert checksum(archive) == scan["archive_sha256"]
        config_digest, config = archive_info(archive)
        alias = f"rallysense-{repo}:release-step6_6-mode-a-rc1"
        existing = subprocess.run(
            ["docker", "image", "inspect", alias], check=False, capture_output=True
        )
        if not existing.returncode:
            assert json.loads(existing.stdout)[0]["Id"] == inspected["Id"], (
                "Frozen alias changed"
            )
        else:
            docker("image", "tag", scan["image"], alias)
        report = json.loads((folder / f"{prefix}{name}.trivy.json").read_text())
        counts = {}
        for r in report.get("Results", []):
            for v in r.get("Vulnerabilities", []):
                counts[v["Severity"]] = counts.get(v["Severity"], 0) + 1
        records.append(
            {
                "name": name,
                "image": scan["image"],
                "release_tag": alias,
                "image_id": inspected["Id"],
                "config_digest": config_digest,
                "platform": "linux/amd64",
                "rootfs_diff_ids": config["rootfs"]["diff_ids"],
                "archive": archive.as_posix(),
                "archive_sha256": checksum(archive),
                "archive_bytes": archive.stat().st_size,
                "scan_report": (folder / f"{prefix}{name}.trivy.json").as_posix(),
                "raw_findings": counts,
                "security_approved": False,
            }
        )
    fixture = json.loads(Path("docs/evidence/step6_6/demo-fixtures.json").read_text())
    backup = Path("storage/step6_6/generated-demo-pair")
    bm = json.loads((backup / "manifest.json").read_text())
    assert bm["quiesced"] and bm["inventory"]["artifact_files_verified"] == 6
    assert checksum(backup / "database.dump") == bm["database_sha256"]
    assert checksum(backup / "artifacts.tar") == bm["artifacts_sha256"]
    sources = [
        p
        for folder in ["apps/api/src", "apps/web/src"]
        for p in Path(folder).rglob("*")
        if p.is_file() and p.suffix in [".py", ".ts", ".tsx", ".css"]
    ]
    sources += [
        Path(p)
        for p in [
            "apps/api/uv.lock",
            "apps/web/package-lock.json",
            "infrastructure/api.Dockerfile",
            "infrastructure/web.Dockerfile",
            "infrastructure/postgres.mode-a.Dockerfile",
            "infrastructure/caddy.Dockerfile",
            "infrastructure/compose.mode-a.yml",
            "infrastructure/compose.mode-a.local.yml",
            "infrastructure/Caddyfile.mode-a",
        ]
    ]
    source_hashes = {
        p.as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for p in sorted(sources)
    }
    manifest = {
        "source_checkpoint": "6ec8a92ea03e9a58f4987d7a6f67309eefa4ac96",
        "build_id": "step6_6-mode-a-rc1",
        "platform": "linux/amd64",
        "mode": "A",
        "mode_b_included": False,
        "public_release_authorized": False,
        "security_approved": False,
        "content_model_approved": False,
        "verdict": "CONDITIONAL GO; mandatory human decisions and external checks outstanding; not approved",
        "images": records,
        "source_file_hashes": source_hashes,
        "fixture_session_ids": fixture["session_ids"],
        "paired_id": fixture["paired_id"],
        "generated_fixture_pair": {
            "directory": backup.as_posix(),
            "manifest_sha256": checksum(backup / "manifest.json"),
            "database_sha256": bm["database_sha256"],
            "artifacts_sha256": bm["artifacts_sha256"],
            "artifact_count": 6,
            "table_count": len(bm["inventory"]["tables"]),
            "private_data_imported": False,
        },
    }
    if target.exists():
        assert json.loads(target.read_text()) == manifest, (
            "Refusing to change frozen manifest"
        )
    else:
        target.write_text(json.dumps(manifest, indent=2) + "\n")
else:
    manifest = json.loads(target.read_text())
    assert manifest["mode"] == "A" and not manifest["mode_b_included"]
    for r in manifest["images"]:
        assert checksum(r["archive"]) == r["archive_sha256"], r["name"]
        digest, config = archive_info(r["archive"])
        assert (
            digest == r["config_digest"]
            and config["rootfs"]["diff_ids"] == r["rootfs_diff_ids"]
        )
    pair = manifest["generated_fixture_pair"]
    for name, key in [
        ("manifest.json", "manifest_sha256"),
        ("database.dump", "database_sha256"),
        ("artifacts.tar", "artifacts_sha256"),
    ]:
        assert checksum(Path(pair["directory"]) / name) == pair[key], name
    if args.action == "load":
        for r in manifest["images"]:
            docker("image", "load", "-i", r["archive"])
            # Archive SHA/config/rootfs already verified; Docker's Id is store-dependent.
            data = json.loads(docker("image", "inspect", r["image"]))[0]
            assert data["Id"] in [r["image_id"], r["config_digest"]]
            assert data["RootFS"]["Layers"] == r["rootfs_diff_ids"]
            docker("image", "tag", r["image"], r["release_tag"])
    for r in manifest["images"]:
        data = json.loads(docker("image", "inspect", r["release_tag"]))[0]
        assert data["Id"] in [r["image_id"], r["config_digest"]]
        assert data["RootFS"]["Layers"] == r["rootfs_diff_ids"]
        assert data["Os"] == "linux" and data["Architecture"] == "amd64"
print(
    json.dumps(
        {
            "action": args.action,
            "images_verified": 4,
            "fixture_artifacts": 6,
            "public_release_authorized": False,
        }
    )
)
