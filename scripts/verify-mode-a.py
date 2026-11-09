"""Mode A-only live HTTPS/security checks, using fresh generated local fixtures.

No public DNS/listener, uploads, native inference, or private source data.
"""

import concurrent.futures
import json
import socket
import ssl
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path.cwd()
E = ROOT / "docs/evidence/step6_6"
state = json.loads((ROOT / "storage/step6_6/local-release-state.json").read_text())
assert state["local_only"] and set(state["roles"]) == {"demo"}
info = state["roles"]["demo"]
project = info["project"]
values = dict(
    line.split("=", 1) for line in Path(info["env_file"]).read_text().splitlines()
)


def docker(*args, input=None):
    return subprocess.run(
        ["docker", *args],
        input=input,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=90,
    ).stdout.strip()


def py(code):
    return docker("exec", "-i", f"{project}-api-1", "python", "-", input=code)


cert = ROOT / "storage/step6_6/test-root.crt"
docker(
    "cp", f"{project}-gateway-1:/data/caddy/pki/authorities/local/root.crt", str(cert)
)
tls = ssl.create_default_context(cafile=str(cert))
real_resolve = socket.getaddrinfo
socket.getaddrinfo = lambda host, *a, **k: real_resolve(
    "127.0.0.1" if host == info["host"] else host, *a, **k
)
checks = []


def record(name, **data):
    checks.append({"check": name, **data})
    (E / "mode-a-http-progress.json").write_text(json.dumps(checks, indent=2))


with httpx.Client(
    base_url=values["WEB_ALLOWED_ORIGINS"], verify=tls, trust_env=False, timeout=30
) as c:
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
            assert c.get(path, headers=headers).status_code == 401, path
    assert (
        c.get("/api/v1/sessions", auth=("lab", "incorrect-password")).status_code == 401
    )
    c.auth = ("lab", values["SITE_ACCESS_PASSWORD"])
    sessions = c.get("/api/v1/sessions")
    assert sessions.status_code == 200
    assert {s["id"] for s in sessions.json()} == set(info["fixture_ids"])
    assert all(s["dataset_kind"] == "synthetic" for s in sessions.json())
    assert c.get("/api/v1/health/ready").status_code == 200
    for origin in [
        "https://foreign.invalid",
        f"https://{info['host']}",
        f"https://{info['host']}.evil.invalid:18443",
    ]:
        assert c.get("/api/v1/sessions", headers={"origin": origin}).status_code == 403
    assert (
        c.get("/api/v1/sessions", headers={"host": "foreign.invalid"}).status_code
        == 421
    )
    assert (
        c.get(
            "/api/v1/sessions",
            headers={"origin": values["WEB_ALLOWED_ORIGINS"], "x-lab-token": "spoofed"},
        ).status_code
        == 200
    )
    assert sessions.headers["x-content-type-options"] == "nosniff"
    assert sessions.headers["strict-transport-security"] == "max-age=31536000"
    assert "server" not in sessions.headers
    record(
        "tls_auth_host_origin",
        unauthenticated_requests_denied=16,
        private_ca_and_hostname_verified=True,
        foreign_origins_denied=3,
        wrong_host=421,
        internal_header_spoof_overridden=True,
    )
    detail = c.get("/api/v1/sessions/" + info["paired_id"]).json()
    video, sensor, pose = (
        detail["videos"][0]["id"],
        detail["sensors"][0]["id"],
        detail["poses"][0]["id"],
    )
    media = c.get(f"/api/v1/videos/{video}/content", headers={"range": "bytes=0-63"})
    assert media.status_code == 206 and len(media.content) == 64
    assert (
        c.get(
            f"/api/v1/sensor-recordings/{sensor}/samples?start_us=3000000&end_us=5000000"
        ).json()["source_count"]
        > 0
    )
    assert c.get(
        f"/api/v1/pose-tracks/{pose}/frames?start_us=3000000&end_us=5000000"
    ).json()["frames"]
    history = c.get(f"/api/v1/sessions/{info['paired_id']}/experiments").json()
    assert len(history) == 10 and sum(e["status"] == "failed" for e in history) == 1
    clean = next(e for e in history if e["name"].startswith("Clean fusion"))
    corrupt = next(e for e in history if e["name"].startswith("Offset +1"))
    assert clean["result"]["evaluation"]["tp"] == 2
    assert corrupt["result"]["evaluation"]["fn"] == 2
    assert (
        c.get(
            f"/api/v1/sessions/{info['paired_id']}/experiment-comparison?ids={clean['id']}&ids={corrupt['id']}"
        ).status_code
        == 200
    )
    report = c.get(f"/api/v1/experiments/{clean['id']}/report")
    assert report.status_code == 200 and "synthetic" in report.text.lower()
    assert c.get(f"/experiments/{clean['id']}/report").status_code == 200
    for experiment in history:
        exported = c.get(f"/api/v1/experiments/{experiment['id']}/report")
        assert exported.status_code == 200 and "synthetic" in exported.text.lower()
        assert (
            "data/private" not in exported.text and "C:\\Users\\" not in exported.text
        )
    record(
        "replay_research_exports",
        video_range_status=206,
        imu_samples=True,
        stored_pose_frames=True,
        experiments=10,
        expected_failed_experiments=1,
        clean_generated_tp=2,
        corrupt_generated_fn=2,
        comparison=True,
        reports=True,
        real_world_accuracy_claim=False,
    )
    # Enumerate every currently registered mutating API method, not just selected UI buttons.
    # FastAPI's included routers are lazy in the installed version. OpenAPI expands
    # them; iterating only app.routes misses their nested methods.
    routes = json.loads(
        py(
            "import json\nfrom rallysense.main import app\nprint(json.dumps([{'path':p,'method':m.upper()} for p,v in app.openapi()['paths'].items() for m in v if m.upper() in {'POST','PUT','PATCH','DELETE'}]))"
        )
    )
    denied = []
    import re

    for route in routes:
        path = re.sub(
            r"\{[^}]+\}", "00000000-0000-0000-0000-000000000000", route["path"]
        ).replace("/batches/00000000-0000-0000-0000-000000000000", "/batches/0")
        assert path.startswith("/api/v1/")
        response = c.request(
            route["method"],
            path,
            json={},
            headers={
                "x-lab-client": "rallysense",
                "origin": values["WEB_ALLOWED_ORIGINS"],
            },
        )
        assert response.status_code == 403, (route, response.status_code)
        denied.append(route)
    assert len(denied) >= 20
    (E / "denied-mutation-routes.json").write_text(json.dumps(denied, indent=2))
    record(
        "all_registered_mutations_denied", methods_and_routes=len(denied), status=403
    )
    # Only this disposable synthetic database is modified; verify both exclusion predicates.
    guards = json.loads(
        py(
            "from sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nimport json\nwith Session(engine) as db, db.begin():\n a=m.RecordingSession(title='Step6.6 ephemeral synthetic guard',dataset_kind='synthetic'); b=m.RecordingSession(title='Step6.6 ephemeral synthetic guard',dataset_kind='synthetic',demo_key='unapproved-fixture'); db.add_all([a,b]); db.flush(); print(json.dumps([a.id,b.id]))"
        )
    )
    try:
        for guard in guards:
            assert c.get("/api/v1/sessions/" + guard).status_code == 404
            assert c.get(f"/api/v1/sessions/{guard}/experiments").status_code == 404
            assert guard not in c.get("/api/v1/diagnostics").text
        assert len(c.get("/api/v1/sessions").json()) == 2
    finally:
        py(
            "from sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nwith Session(engine) as db, db.begin():\n for key in "
            + repr(guards)
            + ":\n  s=db.get(m.RecordingSession,key); assert s.title=='Step6.6 ephemeral synthetic guard' and s.dataset_kind=='synthetic'; db.delete(s)"
        )
    record(
        "backend_allowlisting",
        real_hidden_synthetic_rows_denied=2,
        sessions_visible=2,
        private_database_mounted=False,
    )
    baseline = json.loads(
        (ROOT / "storage/step6_6-research-preservation.json").read_text()
    )
    # Read IDs only from the private preservation index; never copy those records.
    for table, template in [
        ("sessions", "/sessions/{id}"),
        ("video_assets", "/videos/{id}/content"),
        ("sensor_recordings", "/sensor-recordings/{id}/samples"),
        ("pose_tracks", "/pose-tracks/{id}/frames"),
        ("experiments", "/experiments/{id}/report"),
    ]:
        private_id = next(iter(baseline[table]))
        assert c.get("/api/v1" + template.format(id=private_id)).status_code == 404
    for path in ["/.env", "/storage", "/data/private", "/openapi.json"]:
        assert c.get(path).status_code == 404
    record(
        "private_sources_and_content_review",
        original_private_id_requests_denied=5,
        filesystem_source_paths_denied=4,
        synthetic_report_exports_reviewed=10,
        private_ids_in_evidence=False,
    )
    runtime = json.loads(
        py(
            "import json,shutil,importlib.util,hashlib,pathlib,os\nimport numpy,scipy,pyarrow,psycopg\nfrom sqlalchemy.orm import Session\nfrom rallysense.db import engine\nfrom rallysense import models as m\nwith Session(engine) as db:\n h=db.get(m.WorkerHeartbeat,'main'); pulse=h.state\nassert pulse=='readonly_idle'\nassert all(shutil.which(x) is None for x in ['ffmpeg','ffprobe','pip','pip3','uv'])\nassert importlib.util.find_spec('pip') is None and importlib.util.find_spec('ensurepip') is None\nprint(json.dumps({'uid':os.getuid(),'worker_state':pulse,'native_media_and_installers_absent':True,'numpy':numpy.__version__,'scipy':scipy.__version__,'pyarrow':pyarrow.__version__,'uv_lock_sha256':hashlib.sha256(pathlib.Path('/app/uv.lock').read_bytes()).hexdigest()}))"
        )
    )
    assert runtime["uid"] != 0
    record("readonly_runtime_and_idle_worker", **runtime)
    # Modest repeatable read pressure: evidence for sizing, not an internet SLA/load test.
    paths = [
        "/api/v1/sessions",
        f"/api/v1/videos/{video}/content",
        f"/api/v1/pose-tracks/{pose}/frames?start_us=3000000&end_us=5000000",
    ]
    started = time.monotonic()

    def read(i):
        response = c.get(
            paths[i % len(paths)],
            headers={"range": "bytes=0-65535"} if i % 3 == 1 else {},
        )
        assert response.status_code in [200, 206], response.status_code
        return response.elapsed.total_seconds()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        timings = list(pool.map(read, range(36)))
    record(
        "local_read_pressure",
        requests=36,
        concurrency=4,
        elapsed_s=round(time.monotonic() - started, 3),
        max_request_s=round(max(timings), 3),
        target_host_capacity_unverified=True,
    )

containers = []
for name in ["db", "api", "worker", "web", "gateway"]:
    data = json.loads(docker("inspect", f"{project}-{name}-1"))[0]
    hc = data["HostConfig"]
    assert data["State"]["Health"]["Status"] == "healthy", name
    if name != "gateway":
        assert not hc.get("PortBindings")
    else:
        assert all(
            b["HostIp"] == "127.0.0.1"
            for bindings in hc["PortBindings"].values()
            for b in bindings
        )
        assert set(data["NetworkSettings"]["Networks"]) == {project + "_edge"}
    if name in ["api", "worker"]:
        assert hc["ReadonlyRootfs"] and hc["CapDrop"] == ["ALL"]
        assert not next(
            m for m in data["Mounts"] if m["Destination"] == "/data/storage"
        )["RW"]
    assert hc["Memory"] and hc["NanoCpus"] and hc["PidsLimit"]
    memory = docker(
        "exec",
        f"{project}-{name}-1",
        "cat",
        "/sys/fs/cgroup/memory.current",
        "/sys/fs/cgroup/memory.peak",
    ).splitlines()
    containers.append(
        {
            "service": name,
            "image_id": data["Image"],
            "healthy": True,
            "memory_current_bytes": int(memory[0]),
            "memory_peak_bytes": int(memory[1]),
            "memory_limit_bytes": hc["Memory"],
            "cpu_limit": hc["NanoCpus"] / 1e9,
            "private_ports": name != "gateway",
            "networks": list(data["NetworkSettings"]["Networks"]),
        }
    )
assert json.loads(docker("network", "inspect", project + "_backend"))[0]["Internal"]
xml = docker(
    "exec",
    f"{project}-db-1",
    "psql",
    "-U",
    "rallysense",
    "-d",
    "rallysense",
    "-Atc",
    "SELECT xmlparse(document '<demo>generated</demo>'); SELECT count(*) FROM information_schema.columns WHERE table_schema='public' AND data_type='xml';",
)
assert xml.splitlines() == ["<demo>generated</demo>", "0"]
record(
    "sqlxml_reachability",
    sql_xml_function_confirmed=True,
    application_xml_columns=0,
    arbitrary_sql_http_endpoint=False,
    indirect_exposure_requires_review=True,
)
result = {
    "scope": "Fresh generated synthetic fixtures; loopback HTTPS with verified private CA",
    "checks": checks,
    "runtime": containers,
    "public_deployment_verified": False,
}
(E / "mode-a-http.json").write_text(json.dumps(result, indent=2))
print(
    json.dumps(
        {
            "check_groups_passed": len(checks),
            "healthy_services": len(containers),
            "registered_mutations_denied": len(denied),
            "measured_peak_bytes_sum": sum(c["memory_peak_bytes"] for c in containers),
        }
    )
)
