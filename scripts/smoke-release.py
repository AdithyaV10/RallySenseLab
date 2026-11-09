"""Credentialed HTTPS deployment smoke test; default validates public CA/DNS, never uploads data."""

import argparse
import json
import socket
import ssl
from pathlib import Path

import httpx

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--env-directory", type=Path, default=Path("storage/release"))
parser.add_argument(
    "--local-step6",
    action="store_true",
    help="Only the isolated .test stacks, with their private CA",
)
parser.add_argument("--local-stage", choices=["step6", "step6_5"])
parser.add_argument("--role", choices=["demo", "workspace", "both"], default="both")
args = parser.parse_args()
local_stage = args.local_stage or ("step6" if args.local_step6 else None)
tls = ssl.create_default_context()
if local_stage:
    args.env_directory = Path(f"storage/{local_stage}")
    tls = ssl.create_default_context(cafile=f"storage/{local_stage}/test-root.crt")
    original = socket.getaddrinfo

    def resolve(host, *positional, **keywords):
        return original(
            "127.0.0.1"
            if host in {"demo.rallysense.test", "workspace.rallysense.test"}
            else host,
            *positional,
            **keywords,
        )

    socket.getaddrinfo = resolve
checks = []
for role in ["demo", "workspace"] if args.role == "both" else [args.role]:
    values = dict(
        line.split("=", 1)
        for line in (args.env_directory / f"{role}.env").read_text().splitlines()
        if line and not line.startswith("#")
    )
    origin = values["WEB_ALLOWED_ORIGINS"]
    assert origin.startswith("https://") and "," not in origin
    with httpx.Client(
        base_url=origin, verify=tls, trust_env=False, timeout=30
    ) as client:
        assert client.get("/api/v1/sessions").status_code == 401
        client.auth = ("lab", values["SITE_ACCESS_PASSWORD"])
        assert client.get("/api/v1/health/ready").status_code == 200
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        assert (
            client.get(
                "/api/v1/sessions", headers={"origin": "https://foreign.invalid"}
            ).status_code
            == 403
        )
        assert (
            client.get(
                "/api/v1/sessions", headers={"host": "foreign.invalid"}
            ).status_code
            == 421
        )
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "max-age=" in response.headers["strict-transport-security"]
        assert "server" not in response.headers
        if role == "demo":
            sessions = response.json()
            assert {s["id"] for s in sessions} == set(
                values["DEMO_SESSION_IDS"].split(",")
            )
            assert all(s["dataset_kind"] == "synthetic" for s in sessions)
            assert (
                client.post(
                    "/api/v1/sessions", json={"title": "must be rejected"}
                ).status_code
                == 403
            )
            history = [
                e
                for s in sessions
                for e in client.get(f"/api/v1/sessions/{s['id']}/experiments").json()
            ]
            clean = next(e for e in history if e["name"].startswith("Clean fusion"))
            assert client.get(f"/experiments/{clean['id']}/report").status_code == 200
        checks.append(
            {
                "role": role,
                "tls": True,
                "auth": True,
                "origin_host": True,
                "ready": True,
            }
        )
print(
    json.dumps(
        {
            "passed": checks,
            "tls_scope": "private CA and loopback"
            if local_stage
            else "system public CA and real DNS",
            "uploads_exercised": False,
        }
    )
)
