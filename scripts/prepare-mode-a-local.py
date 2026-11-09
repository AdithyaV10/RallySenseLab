"""Fresh Mode A-only rehearsal. Every gateway start is forced onto loopback.

Trusted offline fixture generation uses the existing full image once; that image
is not part of the Mode A deployment manifest or runtime configuration.
"""

import argparse
import json
import os
import secrets
import subprocess
from pathlib import Path

ROOT = Path.cwd()
BASE = ROOT / "storage/step6_6"
STATE = BASE / "local-release-state.json"
EVIDENCE = ROOT / "docs/evidence/step6_6"
parser = argparse.ArgumentParser()
parser.add_argument(
    "action", choices=["init", "seed", "start", "stop", "verify-config"]
)
args = parser.parse_args()


def run(command, timeout=180):
    p = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if p.returncode:
        # Do not leak rendered environment or database credentials on failure.
        raise RuntimeError(
            f"Command failed ({p.returncode}); inspect locally, output withheld"
        )
    return p.stdout


def save_env(values):
    path = BASE / "demo.env"
    path.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)


if args.action == "init":
    if STATE.exists():
        raise SystemExit("Existing state: resume, never replace its secrets/volumes")
    project = "rallysense-step6-6-mode-a"
    for kind in ["volume", "network"]:
        assert not run(
            [
                "docker",
                kind,
                "ls",
                "--filter",
                f"label=com.docker.compose.project={project}",
                "--format",
                "{{.Name}}",
            ]
        ).strip()
    BASE.mkdir(parents=True, exist_ok=True)
    values = {
        k: secrets.token_hex(32)
        for k in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
    }
    values.update(
        POSTGRES_IMAGE="rallysense-postgres-mode-a:rc-step6_6",
        READONLY_API_IMAGE="rallysense-api-readonly:rc-step6_6",
        WEB_IMAGE="rallysense-web:release-step6_5-rc1",
        CADDY_IMAGE="rallysense-caddy:release-step6_5-rc1",
        RALLYSENSE_DOMAIN="demo.rallysense.test",
        WEB_ALLOWED_HOSTS="demo.rallysense.test",
        WEB_ALLOWED_ORIGINS="https://demo.rallysense.test:18443",
        BUILD_ID="step6_6-mode-a-rc1",
        DEMO_SESSION_IDS="not-seeded",
    )
    save_env(values)
    state = {
        "local_only": True,
        "source_checkpoint": "6ec8a92ea03e9a58f4987d7a6f67309eefa4ac96",
        "roles": {
            "demo": {
                "project": project,
                "host": values["RALLYSENSE_DOMAIN"],
                "env_file": str(BASE / "demo.env"),
                "seeded": False,
            }
        },
    }
    STATE.write_text(json.dumps(state, indent=2))
    print("Created isolated Mode A configuration; secrets remain in ignored storage")
    raise SystemExit(0)

state = json.loads(STATE.read_text())
assert state["local_only"] and set(state["roles"]) == {"demo"}
info = state["roles"]["demo"]
values = dict(
    line.split("=", 1) for line in Path(info["env_file"]).read_text().splitlines()
)
compose = [
    "docker",
    "compose",
    "-p",
    info["project"],
    "--env-file",
    info["env_file"],
    "-f",
    "infrastructure/compose.mode-a.yml",
    "-f",
    "infrastructure/compose.mode-a.local.yml",
]
if args.action == "verify-config":
    for local in [False, True]:
        command = compose if local else compose[:-2]
        config = json.loads(run([*command, "config", "--format", "json"]))
        services = config["services"]
        assert set(services) == {"db", "api", "worker", "web", "gateway"}
        assert config["networks"]["backend"]["internal"]
        assert set(services["gateway"]["networks"]) == {"edge"}
        assert services["api"]["environment"]["APP_MODE"] == "demo_readonly"
        assert (
            services["worker"]["image"]
            == services["api"]["image"]
            == values["READONLY_API_IMAGE"]
        )
        assert all(
            services[s].get("healthcheck")
            and services[s].get("mem_limit")
            and services[s].get("pids_limit")
            for s in services
        )
        assert all(not services[s].get("ports") for s in ["db", "api", "worker", "web"])
        assert services["web"]["environment"]["REQUIRE_WORKSPACE_AUTH"] == "true"
        for s in ["api", "worker"]:
            assert services[s]["read_only"] and services[s]["volumes"][0]["read_only"]
            assert services[s]["cap_drop"] == ["ALL"]
        if local:
            assert all(
                p["host_ip"] == "127.0.0.1" for p in services["gateway"]["ports"]
            )
        else:
            assert "TLS_POLICY" not in services["gateway"]["environment"]
    assert (
        len(
            {
                values[k]
                for k in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
            }
        )
        == 3
    )
    assert all(
        len(values[k]) == 64
        for k in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
    )
    (EVIDENCE / "mode-a-config.json").write_text(
        json.dumps(
            {
                "passed": True,
                "modes": ["production-render-only", "loopback-rehearsal"],
                "services": sorted(services),
                "private_backend": True,
                "all_healthchecks_and_limits": True,
                "distinct_generated_credentials": True,
                "no_workspace": True,
            },
            indent=2,
        )
    )
    print("Both Mode A configurations validated; no production listener started")
elif args.action == "seed":
    assert not info["seeded"], "Already seeded: do not overwrite generated fixtures"
    run([*compose, "up", "-d", "--wait", "--wait-timeout", "90", "db"])
    # The writable override is private/ignored and never shipped to the public host.
    overlay = BASE / "trusted-offline-seed.yml"
    overlay.write_text(
        'services:\n  api:\n    image: rallysense-api:release-step6_5-rc1\n    environment:\n      APP_MODE: local\n    volumes: ["artifact_data:/data/storage"]\n'
    )
    mounts = []
    for filename in ["prepare-demo-fixtures.py", "prepare-curated-fixtures.py"]:
        mounts += ["--volume", f"{ROOT / 'scripts' / filename}:/tmp/{filename}:ro"]
    output = run(
        [
            *compose,
            "-f",
            str(overlay),
            "run",
            "--rm",
            "--no-deps",
            "-T",
            *mounts,
            "api",
            "sh",
            "-c",
            "alembic upgrade head && python /tmp/prepare-curated-fixtures.py",
        ]
    )
    record = next(
        json.loads(line)
        for line in reversed(output.splitlines())
        if line.startswith("{") and "session_ids" in json.loads(line)
    )
    assert not record["private_data_imported"] and len(record["session_ids"]) == 2
    values["DEMO_SESSION_IDS"] = ",".join(record["session_ids"])
    save_env(values)
    info.update(
        seeded=True, fixture_ids=record["session_ids"], paired_id=record["paired_id"]
    )
    STATE.write_text(json.dumps(state, indent=2))
    (EVIDENCE / "demo-fixtures.json").write_text(json.dumps(record, indent=2))
    print("Fresh generated fixtures and ten precomputed experiments prepared")
elif args.action == "start":
    assert info["seeded"]
    run([*compose, "up", "-d", "--no-build", "--wait", "--wait-timeout", "150"])
    print("Five Mode A services healthy; gateway bound only to 127.0.0.1")
elif args.action == "stop":
    run([*compose, "stop"])
    print("Mode A rehearsal stopped; all volumes retained")
