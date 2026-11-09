"""Real TLS/auth/isolation/workspace checks against fresh Step 6 projects only."""

import argparse
import json
import socket
import ssl
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path.cwd()
parser = argparse.ArgumentParser()
parser.add_argument("--stage", choices=["step6", "step6_5"], default="step6")
STAGE = parser.parse_args().stage
EVIDENCE = ROOT / f"docs/evidence/{STAGE}"
STATE = ROOT / f"storage/{STAGE}/local-release-state.json"
state = json.loads(STATE.read_text())
assert state["local_only"] and all(s["seeded"] for s in state["roles"].values())


def env_file(path):
    return dict(
        line.split("=", 1)
        for line in Path(path).read_text().splitlines()
        if line and not line.startswith("#")
    )


def docker(*args, input=None):
    result = subprocess.run(
        ["docker", *args],
        input=input,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
    )
    return result.stdout.strip()


gateway = json.loads(docker("inspect", f"rallysense-{STAGE}-edge-gateway-1"))[0]
cert = ROOT / f"storage/{STAGE}/test-root.crt"
docker("cp", f"{gateway['Id']}:/data/caddy/pki/authorities/local/root.crt", str(cert))
context = ssl.create_default_context(cafile=str(cert))
real_resolve = socket.getaddrinfo
hosts = {s["host"] for s in state["roles"].values()}


def resolve(host, *args, **kwargs):
    # Process-local resolver override, preserving real TLS SNI/hostname validation.
    return real_resolve("127.0.0.1" if host in hosts else host, *args, **kwargs)


socket.getaddrinfo = resolve
roles = {role: env_file(info["env_file"]) for role, info in state["roles"].items()}
checks = []
workspace_session = None


def record(name, **values):
    checks.append({"check": name, **values})
    (EVIDENCE / "release-http-progress.json").write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )


def api_python(role, code):
    assert role in state["roles"]
    return docker(
        "exec",
        "-i",
        f"{state['roles'][role]['project']}-api-1",
        "python",
        "-",
        input=code,
    )


def wait_job(client, job):
    for _ in range(200):
        result = client.get("/api/v1/jobs/" + job["id"]).json()
        if result["state"] in {"failed", "cancelled", "succeeded"}:
            assert result["state"] == "succeeded", result
            return result
        time.sleep(0.25)
    raise AssertionError("Job did not complete")


for role, info in state["roles"].items():
    base = f"https://{info['host']}:18443"
    password = roles[role]["SITE_ACCESS_PASSWORD"]
    with httpx.Client(
        base_url=base, verify=context, trust_env=False, timeout=30
    ) as client:
        for path in [
            "/",
            "/sessions",
            "/record",
            "/api/v1/sessions",
            "/api/v1/diagnostics",
        ]:
            for headers in [
                {},
                {"x-lab-token": "rallysense-local-development"},
                {"x-middleware-subrequest": "proxy:proxy:proxy:proxy:proxy"},
            ]:
                assert client.get(path, headers=headers).status_code == 401
        record(
            f"{role}_tls_and_unauthenticated_boundary",
            paths=5,
            forged_headers_denied=True,
            certificate_chain_and_hostname_verified=True,
        )
        other = "workspace" if role == "demo" else "demo"
        assert (
            client.get(
                "/api/v1/sessions", auth=("lab", roles[other]["SITE_ACCESS_PASSWORD"])
            ).status_code
            == 401
        )
        client.auth = ("lab", password)
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        expected_sessions = set(info["fixture_ids"])
        if role == "workspace":
            expected_sessions.update(state.get("workspace_acceptance_sessions", []))
            if state.get("workspace_acceptance_session"):
                expected_sessions.add(state["workspace_acceptance_session"])
        assert {s["id"] for s in response.json()} == expected_sessions
        assert all(s["dataset_kind"] == "synthetic" for s in response.json())
        assert (
            client.get(
                "/api/v1/sessions", headers={"origin": "https://foreign.invalid"}
            ).status_code
            == 403
        )
        assert (
            client.get(
                "/api/v1/sessions",
                headers={"origin": f"https://{state['roles'][other]['host']}:18443"},
            ).status_code
            == 403
        )
        wrong_host = client.get(
            "/api/v1/sessions", headers={"host": "foreign.invalid"}
        ).status_code
        assert wrong_host in {404, 421}, wrong_host
        assert (
            client.get(
                "/api/v1/sessions", headers={"x-lab-token": "spoofed-internal-token"}
            ).status_code
            == 200
        )
        assert (
            client.get(
                "/api/v1/sessions/" + state["roles"][other]["paired_id"]
            ).status_code
            == 404
        )
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["strict-transport-security"] == "max-age=31536000"
        assert "server" not in response.headers
        record(
            f"{role}_routing_origin_and_credentials",
            wrong_host_status=wrong_host,
            foreign_origin_status=403,
            cross_environment_password_status=401,
            cross_environment_session_status=404,
            internal_header_spoof_overridden=True,
        )
        paired = client.get("/api/v1/sessions/" + info["paired_id"]).json()
        vid = paired["videos"][0]["id"]
        pose = paired["poses"][0]["id"]
        sensor = paired["sensors"][0]["id"]
        assert (
            client.get(
                f"/api/v1/videos/{vid}/content", headers={"range": "bytes=0-63"}
            ).status_code
            == 206
        )
        assert (
            client.get(
                f"/api/v1/sensor-recordings/{sensor}/samples?start_us=3000000&end_us=5000000"
            ).json()["source_count"]
            > 0
        )
        assert client.get(
            f"/api/v1/pose-tracks/{pose}/frames?start_us=3000000&end_us=5000000"
        ).json()["frames"]
        history = client.get(f"/api/v1/sessions/{info['paired_id']}/experiments").json()
        assert len(history) == 10
        clean = next(e for e in history if e["name"].startswith("Clean fusion"))
        failure = next(e for e in history if e["name"].startswith("Offset +1"))
        assert clean["result"]["evaluation"]["tp"] == 2
        assert failure["result"]["evaluation"]["fn"] == 2
        compared = client.get(
            f"/api/v1/sessions/{info['paired_id']}/experiment-comparison?ids={clean['id']}&ids={failure['id']}"
        )
        assert compared.status_code == 200
        report = client.get(f"/api/v1/experiments/{clean['id']}/report")
        assert report.status_code == 200 and "synthetic" in report.text.lower()
        record(
            f"{role}_precomputed_replay_comparison_exports",
            experiments=10,
            range_media=206,
            graph_samples=True,
            pose_window=True,
            comparison=200,
            markdown_export=200,
            synthetic_software_only=True,
        )
        if role == "demo":
            paths = [
                ("POST", "/sessions"),
                ("POST", f"/sessions/{info['paired_id']}/videos"),
                ("POST", f"/sessions/{info['paired_id']}/sensor-imports"),
                ("POST", f"/sessions/{info['paired_id']}/experiments"),
                ("POST", f"/sessions/{info['paired_id']}/sync-configurations"),
                ("POST", f"/sessions/{info['paired_id']}/annotations"),
                ("PATCH", f"/sessions/{info['paired_id']}/collection"),
                ("DELETE", f"/sessions/{info['paired_id']}"),
                ("POST", f"/videos/{vid}/pose-tracks"),
                ("PUT", f"/pose-tracks/{pose}/batches/0"),
                ("POST", f"/experiments/{clean['id']}/evaluate"),
                ("POST", f"/jobs/{paired['jobs'][0]['id']}/retry"),
            ]
            for method, path in paths:
                response = client.request(
                    method,
                    "/api/v1" + path,
                    headers={"x-lab-client": "rallysense"},
                    json={},
                )
                assert response.status_code == 403, (path, response.status_code)
            # Test a real nonallowlisted row in this synthetic-only database, then remove only that ephemeral guard.
            guard = json.loads(
                api_python(
                    role,
                    "from sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nimport json\nwith Session(engine) as db, db.begin():\n s=m.RecordingSession(title='Ephemeral synthetic allowlist guard',dataset_kind='synthetic');db.add(s);db.flush();print(json.dumps({'id':s.id}))",
                )
            )["id"]
            try:
                assert client.get("/api/v1/sessions/" + guard).status_code == 404
                assert len(client.get("/api/v1/sessions").json()) == 2
                assert guard not in client.get("/api/v1/diagnostics").text
            finally:
                api_python(
                    role,
                    f"from sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nwith Session(engine) as db, db.begin():\n s=db.get(m.RecordingSession,'{guard}'); assert s.title=='Ephemeral synthetic allowlist guard' and s.dataset_kind=='synthetic'; db.delete(s)",
                )
            pulse = json.loads(
                api_python(
                    role,
                    "import json\nfrom sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nwith Session(engine) as db:\n s=db.get(m.WorkerHeartbeat,'main'); print(json.dumps({'state':s.state}))",
                )
            )
            assert pulse["state"] == "readonly_idle"
            record(
                "demo_mutation_allowlist_and_worker",
                mutation_families_denied=len(paths),
                real_hidden_synthetic_row_denied=True,
                final_sessions=2,
                worker_state=pulse["state"],
            )
        else:
            headers = {
                "x-lab-client": "rallysense",
                "origin": f"https://{info['host']}:18443",
            }
            response = client.post(
                "/api/v1/sessions",
                headers=headers,
                json={
                    "title": "Step 6 generated workspace acceptance",
                    "dataset_kind": "synthetic",
                },
            )
            assert response.status_code == 201
            sid = response.json()["id"]
            workspace_session = sid
            data = (ROOT / "data/fixtures/synthetic-imu.csv").read_bytes()
            imported = client.post(
                f"/api/v1/sessions/{sid}/sensor-imports",
                headers=headers,
                files={"file": ("synthetic.csv", data, "text/csv")},
                data={"mapping": '{"provenance":"synthetic"}'},
            )
            assert imported.status_code == 202, imported.text
            wait_job(client, imported.json())
            detail = client.get("/api/v1/sessions/" + sid).json()
            sensor = detail["sensors"][0]["id"]
            sync = client.post(
                f"/api/v1/sessions/{sid}/sync-configurations",
                headers=headers,
                json={"sensor_id": sensor, "offset_us": 0},
            )
            assert sync.status_code == 201
            labels = client.post(
                f"/api/v1/sessions/{sid}/annotation-sets",
                headers=headers,
                json={"name": "Generated acceptance markers"},
            ).json()
            annotation = client.post(
                f"/api/v1/sessions/{sid}/annotations?set_id={labels['id']}",
                headers=headers,
                json={
                    "t_session_us": 2_000_000,
                    "note": "Generated software check, not athlete ground truth",
                },
            ).json()
            edited = client.patch(
                f"/api/v1/annotations/{annotation['id']}",
                headers=headers,
                json={
                    "revision": annotation["revision"],
                    "t_session_us": 2_100_000,
                    "note": "Generated acceptance edit",
                },
            )
            assert edited.status_code == 200
            exp = client.post(
                f"/api/v1/sessions/{sid}/experiments",
                headers=headers,
                json={"mode": "imu", "sensor_id": sensor, "sync_id": sync.json()["id"]},
            )
            assert exp.status_code == 202
            eid = exp.json()["id"]
            for _ in range(150):
                result = client.get("/api/v1/experiments/" + eid).json()
                if result["status"] in {"failed", "succeeded"}:
                    break
                time.sleep(0.2)
            assert result["status"] == "succeeded", result
            assert result["result"]["executor"]["build_id"] == roles[role]["BUILD_ID"]
            assert result["result"]["evaluation"] is None
            raw_video = client.get(f"/api/v1/videos/{vid}/content").content
            imported = client.post(
                f"/api/v1/sessions/{sid}/videos",
                headers=headers,
                files={"file": ("generated.mp4", raw_video, "video/mp4")},
                data={"metadata": '{"provenance":"synthetic"}'},
            )
            assert imported.status_code == 202
            wait_job(client, imported.json())
            assert client.get(f"/api/v1/experiments/{eid}/report").status_code == 200
            record(
                "workspace_writes_and_worker",
                csv_upload=202,
                video_upload=202,
                sync=201,
                annotation_create=True,
                annotation_edit=200,
                experiment="succeeded",
                executor_build_verified=True,
                export=200,
            )

# Inspect actual networks, health, mounts and lack of host bindings, without recording secret environment values.
runtime = []
for role, info in state["roles"].items():
    for service in ["db", "api", "worker", "web"]:
        data = json.loads(docker("inspect", f"{info['project']}-{service}-1"))[0]
        assert not data["HostConfig"].get("PortBindings")
        assert data["State"]["Health"]["Status"] == "healthy", (role, service)
        assert data["HostConfig"]["Memory"] > 0 and data["HostConfig"]["PidsLimit"] > 0
        if role == "demo" and service in ["api", "worker"]:
            assert (
                next(m for m in data["Mounts"] if m["Destination"] == "/data/storage")[
                    "RW"
                ]
                is False
            )
        runtime.append(
            {
                "role": role,
                "service": service,
                "healthy": True,
                "host_ports": [],
                "memory_limit_bytes": data["HostConfig"]["Memory"],
                "networks": list(data["NetworkSettings"]["Networks"]),
            }
        )
    other = "workspace" if role == "demo" else "demo"
    target = json.loads(docker("inspect", f"{state['roles'][other]['project']}-api-1"))[
        0
    ]
    backend_ip = next(
        v["IPAddress"]
        for k, v in target["NetworkSettings"]["Networks"].items()
        if k.endswith("_backend")
    )
    code = (
        "import socket\ns=socket.socket();s.settimeout(2)\ntry:\n s.connect(('"
        + backend_ip
        + "',8000));raise SystemExit('Unexpected cross-environment API reachability')\nexcept (TimeoutError,OSError):\n print('isolated')\nfinally:s.close()"
    )
    assert "isolated" in docker(
        "exec", f"{info['project']}-api-1", "python", "-c", code
    )
record(
    "runtime_isolation_and_health",
    services=len(runtime),
    cross_backend_connections_denied=True,
    demo_storage_read_only=True,
)
owned = set(state.get("workspace_acceptance_sessions", []))
if state.get("workspace_acceptance_session"):
    owned.add(state["workspace_acceptance_session"])
owned.add(workspace_session)
state["workspace_acceptance_sessions"] = sorted(owned)
state["workspace_acceptance_session"] = workspace_session
STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
result = {
    "scope": "Real private-CA TLS on loopback; no public DNS/CA/listener",
    "checks": checks,
    "runtime": runtime,
    "public_tls_unverified": True,
    "private_development_data_used": False,
}
(EVIDENCE / "release-http.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "checks_passed": len(checks),
            "services_healthy": len(runtime),
            "tls_hostname_verified": True,
            "workspace_session": workspace_session,
        }
    )
)
