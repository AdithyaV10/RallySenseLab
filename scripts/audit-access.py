"""Step 5 disposable loopback-only gate/read-only integration. Never provisions hosting."""

import argparse
import json
import subprocess
import time
from pathlib import Path

import httpx

names = ["rallysense-step5-web", "rallysense-step5-api"]
parser = argparse.ArgumentParser()
parser.add_argument("--output", default="docs/evidence/step5/access.json")
args = parser.parse_args()
password = "step5-disposable-local-gate-password"
result = {
    "scope": "Temporary loopback production images, existing data read-only; no public exposure"
}


def command(*args):
    return subprocess.run(args, check=True, capture_output=True, timeout=90)


with httpx.Client(timeout=20) as client:
    demos = client.get("http://127.0.0.1:3000/api/v1/demonstrations").json()
    ids = ",".join(row["id"] for row in demos)
    try:
        command(
            "docker",
            "compose",
            "run",
            "--no-deps",
            "-d",
            "--name",
            names[1],
            "-p",
            "127.0.0.1:8004:8000",
            "-e",
            "APP_MODE=demo_readonly",
            "-e",
            f"DEMO_SESSION_IDS={ids}",
            "-e",
            f"ALLOWED_HOSTS=127.0.0.1,localhost,{names[1]}",
            "api",
            "uvicorn",
            "rallysense.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        )
        command(
            "docker",
            "compose",
            "run",
            "--no-deps",
            "-d",
            "--name",
            names[0],
            "-p",
            "127.0.0.1:3004:3000",
            "-e",
            f"API_INTERNAL_URL=http://{names[1]}:8000",
            "-e",
            f"SITE_ACCESS_PASSWORD={password}",
            "web",
        )
        base = "http://127.0.0.1:3004"
        for _ in range(40):
            try:
                if client.get(base).status_code == 401:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.5)
        unauthorized = {}
        for route in [
            "/",
            "/sessions",
            "/record",
            "/api/v1/sessions",
            "/api/v1/diagnostics",
        ]:
            for headers in [
                {},
                {"x-middleware-subrequest": "proxy:proxy:proxy:proxy:proxy"},
                {"x-lab-token": "rallysense-local-development"},
            ]:
                status = client.get(base + route, headers=headers).status_code
                assert status == 401, (route, status)
                unauthorized[route] = status
        result["unauthorized_routes_including_spoofed_middleware_header"] = unauthorized
        client.auth = ("lab", password)
        assert client.get(base).status_code == 200
        for _ in range(40):
            response = client.get(base + "/api/v1/sessions")
            if response.status_code == 200:
                break
            time.sleep(0.5)
        assert response.status_code == 200, (response.status_code, response.text)
        spoofed = client.get(
            base + "/api/v1/sessions",
            headers={"x-lab-token": "spoofed-client-credential"},
        )
        assert spoofed.status_code == 200, (spoofed.status_code, spoofed.text)
        assert (
            client.get(
                base + "/api/v1/sessions", headers={"origin": "https://foreign.invalid"}
            ).status_code
            == 403
        )
        assert (
            client.get(
                base + "/api/v1/sessions", headers={"host": "foreign.invalid"}
            ).status_code
            == 403
        )
        visible = response.json()
        assert {s["id"] for s in visible} == {s["id"] for s in demos}
        private = next(
            s
            for s in client.get("http://127.0.0.1:3000/api/v1/sessions").json()
            if s["id"] not in ids
        )
        assert client.get(base + f"/api/v1/sessions/{private['id']}").status_code == 404
        assert (
            client.post(
                base + "/api/v1/sessions",
                headers={"x-lab-client": "rallysense"},
                json={"title": "must not persist"},
            ).status_code
            == 403
        )
        direct = "http://127.0.0.1:8004/api/v1"
        assert client.get(direct + "/sessions").status_code == 401
        token = {"x-lab-token": "rallysense-local-development"}
        assert (
            client.get(direct + f"/sessions/{private['id']}", headers=token).status_code
            == 404
        )
        assert (
            client.post(
                direct + "/sessions", headers=token, json={"title": "must not persist"}
            ).status_code
            == 403
        )
        result.update(
            authorized_status=200,
            visible_fixture_count=len(visible),
            private_status=404,
            mutation_status=403,
            direct_no_token=401,
            direct_private=404,
            direct_mutation=403,
        )
    finally:
        # These exact disposable names are created above; never remove default services or volumes.
        for name in names:
            subprocess.run(
                ["docker", "rm", "-f", name],
                check=False,
                capture_output=True,
                timeout=60,
            )
Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
