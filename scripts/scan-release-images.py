"""Scan exact local release archives with pinned Trivy; no registry push or Docker socket mount."""

import hashlib
import json
import subprocess
import time
from pathlib import Path

SCANNER = "aquasec/trivy@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
IMAGES = {
    "api": "rallysense-api:local",
    "web": "rallysense-web:latest",
    "postgres": "postgres:17.11@sha256:3b0cda93be7c8dba2ed484d19393d93845dc3dafb88973e248ba8e6d99d784e1",
    "caddy": "caddy@sha256:78bd35025c7ba85961dd149ae670315129954e77abe2383ac47c89106b35ade9",
}
root = Path.cwd()
inputs = root / "storage/step6/scanner-inputs"
reports = root / "docs/evidence/step6"
inputs.mkdir(parents=True, exist_ok=True)
reports.mkdir(parents=True, exist_ok=True)
results = []


def run(command, timeout=900):
    started = time.monotonic()
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return {
        "command": command,
        "exit_code": result.returncode,
        "elapsed_s": round(time.monotonic() - started, 3),
        "output": result.stdout + result.stderr,
    }


for index, (name, ref) in enumerate(IMAGES.items()):
    inspected = json.loads(
        subprocess.check_output(["docker", "image", "inspect", ref])
    )[0]
    archive = inputs / f"{name}.tar"
    if archive.exists():
        raise SystemExit(f"Refusing to overwrite existing scan archive: {archive.name}")
    exported = run(["docker", "image", "save", "--output", str(archive), ref])
    assert exported["exit_code"] == 0, exported["output"]
    with archive.open("rb") as stream:
        checksum = hashlib.file_digest(stream, "sha256").hexdigest()
    command = [
        "docker",
        "run",
        "--rm",
        "--memory",
        "2g",
        "--cpus",
        "2",
        "--mount",
        f"type=bind,source={inputs},target=/inputs,readonly",
        "--mount",
        f"type=bind,source={reports},target=/reports",
        "--mount",
        "type=volume,source=rallysense_step6_trivy_cache,target=/cache",
        SCANNER,
        "image",
        "--cache-dir",
        "/cache",
        "--scanners",
        "vuln",
        "--format",
        "json",
        "--list-all-pkgs",
        "--timeout",
        "10m",
        "--output",
        f"/reports/{name}.trivy.json",
        "--input",
        f"/inputs/{name}.tar",
    ]
    if index:
        command += ["--skip-db-update"]
    result = run(command)
    result.update(
        image=ref,
        image_id=inspected["Id"],
        os=inspected["Os"],
        architecture=inspected["Architecture"],
        archive_sha256=checksum,
        archive_bytes=archive.stat().st_size,
    )
    (reports / f"{name}.scan-command.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    results.append(
        {
            key: result[key]
            for key in [
                "image",
                "image_id",
                "exit_code",
                "elapsed_s",
                "archive_sha256",
                "archive_bytes",
            ]
        }
    )
    (reports / "scan-progress.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print(json.dumps(results[-1]), flush=True)
    if result["exit_code"]:
        raise SystemExit(result["output"][-4000:])

version = run(
    [
        "docker",
        "run",
        "--rm",
        "--mount",
        "type=volume,source=rallysense_step6_trivy_cache,target=/cache",
        SCANNER,
        "--cache-dir",
        "/cache",
        "--version",
        "--format",
        "json",
    ]
)
(reports / "scanner-version.json").write_text(
    json.dumps(version, indent=2), encoding="utf-8"
)
summary = []
for name in IMAGES:
    data = json.loads((reports / f"{name}.trivy.json").read_text())
    counts = {}
    high = []
    for target in data.get("Results", []):
        for item in target.get("Vulnerabilities", []):
            severity = item.get("Severity", "UNKNOWN")
            counts[severity] = counts.get(severity, 0) + 1
            if severity in {"HIGH", "CRITICAL"}:
                high.append(
                    {
                        key: item.get(key)
                        for key in [
                            "VulnerabilityID",
                            "PkgName",
                            "InstalledVersion",
                            "FixedVersion",
                            "Severity",
                            "Status",
                            "PrimaryURL",
                            "Title",
                        ]
                    }
                )
    summary.append({"image": name, "counts": counts, "high_critical": high})
(reports / "vulnerability-summary.json").write_text(
    json.dumps(
        {
            "scanner": SCANNER,
            "scan_completed": True,
            "release_gate_passed": not any(s["high_critical"] for s in summary),
            "images": summary,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(
    json.dumps(
        [{"image": row["image"], "counts": row["counts"]} for row in summary], indent=2
    )
)
