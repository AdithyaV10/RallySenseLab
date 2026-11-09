"""Prepare/run isolated release-shaped stacks on loopback only. Never starts a public gateway."""

import argparse
import hashlib
import json
import os
import secrets
import subprocess
from pathlib import Path

ROOT = Path.cwd()
STATE = ROOT / "storage/step6/local-release-state.json"
EVIDENCE = ROOT / "docs/evidence/step6"
CHECKPOINT = "ac75d818a168bfcf1b7f23a609121b18b0933e8e"
API = "rallysense-api:release-ac75d818"
WEB = "rallysense-web:release-ac75d818"
parser = argparse.ArgumentParser()
parser.add_argument(
    "action", choices=["init", "seed", "start", "stop", "verify-config"]
)
args = parser.parse_args()


def run(command, env=None, timeout=180):
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=timeout,
    )
    output = result.stdout + result.stderr
    if env:
        for key in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]:
            if env.get(key):
                output = output.replace(env[key], "[REDACTED]")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {output[-3500:]}")
    return result.stdout, output


def load_env(path):
    return dict(
        line.split("=", 1)
        for line in Path(path).read_text().splitlines()
        if line and not line.startswith("#")
    )


def save_env(path, values):
    Path(path).write_text(
        "".join(f"{key}={value}\n" for key, value in values.items()), encoding="utf-8"
    )
    if os.name != "nt":
        Path(path).chmod(0o600)


def persist():
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def app_command(role, readonly=None):
    info = state["roles"][role]
    values = load_env(info["env_file"])
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(ROOT),
        "--env-file",
        info["env_file"],
        "-p",
        info["project"],
        "-f",
        "docker-compose.yml",
        "-f",
        "infrastructure/compose.release.yml",
        "-f",
        "infrastructure/compose.application.yml",
    ]
    if readonly if readonly is not None else values["APP_MODE"] == "demo_readonly":
        command += ["-f", "infrastructure/compose.readonly.yml"]
    return command, {**os.environ, **values}


def edge_command():
    values = load_env(state["edge_env_file"])
    return [
        "docker",
        "compose",
        "--project-directory",
        str(ROOT),
        "--env-file",
        state["edge_env_file"],
        "-p",
        "rallysense-step6-edge",
        "-f",
        "infrastructure/compose.gateway.yml",
        "-f",
        "infrastructure/compose.gateway.local-test.yml",
    ], {**os.environ, **values}


if args.action == "init":
    if STATE.exists():
        raise SystemExit(
            "State exists; resume seed/start/verify-config instead of overwriting secrets or volumes"
        )
    # Operational documentation may advance HEAD; the approved application must not change.
    run(
        [
            "git",
            "-c",
            "safe.directory=C:/RallySenseLab",
            "diff",
            "--exit-code",
            CHECKPOINT,
            "--",
            "apps",
            "packages",
            "uv.lock",
            "package-lock.json",
            "infrastructure/api.Dockerfile",
            "infrastructure/web.Dockerfile",
        ]
    )
    state = {"source_checkpoint": CHECKPOINT, "roles": {}, "local_only": True}
    for name, source, tag in [
        ("api", "rallysense-api:local", API),
        ("web", "rallysense-web:latest", WEB),
    ]:
        data = json.loads(run(["docker", "image", "inspect", source])[0])[0]
        run(["docker", "image", "tag", data["Id"], tag])
        state[f"{name}_image"] = {
            "tag": tag,
            "id": data["Id"],
            "platform": f"{data['Os']}/{data['Architecture']}",
        }
    # Verify all source Python files shipped in the API, without starting the app or connecting to a DB.
    code = "import json,hashlib,pathlib; root=pathlib.Path('/app/src'); print(json.dumps({str(p.relative_to(root)).replace('\\\\','/'):hashlib.sha256(p.read_bytes().replace(b'\\r\\n',b'\\n')).hexdigest() for p in root.rglob('*.py')}))"
    actual = json.loads(
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "python",
                API,
                "-c",
                code,
            ]
        )[0]
    )
    expected = {
        str(p.relative_to(ROOT / "apps/api/src")).replace("\\", "/"): hashlib.sha256(
            p.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        for p in (ROOT / "apps/api/src").rglob("*.py")
    }
    assert actual == expected, (
        "Existing API image source does not match approved workspace"
    )
    state["api_source_files_verified"] = len(expected)
    for role in ["demo", "workspace"]:
        project = f"rallysense-step6-{role}"
        for kind in ["volume", "network"]:
            existing = run(
                [
                    "docker",
                    kind,
                    "ls",
                    "--filter",
                    f"label=com.docker.compose.project={project}",
                    "--format",
                    "{{.Name}}",
                ]
            )[0]
            assert not existing.strip(), (
                "Refusing pre-existing project volumes/networks"
            )
        host = f"{role}.rallysense.test"
        file = ROOT / f"storage/step6/{role}.env"
        assert not file.exists()
        values = {
            "POSTGRES_PASSWORD": secrets.token_hex(32),
            "LOCAL_TOKEN": secrets.token_hex(32),
            "SITE_ACCESS_PASSWORD": secrets.token_hex(32),
            "APP_MODE": "local",
            "DEMO_SESSION_IDS": "",
            "BUILD_ID": CHECKPOINT,
            "API_IMAGE": API,
            "WEB_IMAGE": WEB,
            "RALLYSENSE_DOMAIN": host,
            "WEB_ALLOWED_HOSTS": host,
            "WEB_ALLOWED_ORIGINS": f"https://{host}:18443",
            "EDGE_NETWORK": f"{project}-edge",
            "EDGE_WEB_ALIAS": f"{role}-web",
        }
        save_env(file, values)
        state["roles"][role] = {
            "project": project,
            "env_file": str(file),
            "host": host,
            "seeded": False,
        }
    file = ROOT / "storage/step6/edge.env"
    save_env(
        file,
        {
            "DEMO_HOST": "demo.rallysense.test",
            "WORKSPACE_HOST": "workspace.rallysense.test",
            "DEMO_EDGE_NETWORK": "rallysense-step6-demo-edge",
            "WORKSPACE_EDGE_NETWORK": "rallysense-step6-workspace-edge",
        },
    )
    state["edge_env_file"] = str(file)
    persist()
    (EVIDENCE / "release-images.json").write_text(
        json.dumps(
            {
                key: state[key]
                for key in [
                    "source_checkpoint",
                    "api_image",
                    "web_image",
                    "api_source_files_verified",
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        "Prepared isolated configuration and local release image aliases; secrets remain in ignored storage."
    )
    raise SystemExit(0)

state = json.loads(STATE.read_text())
assert state["source_checkpoint"] == CHECKPOINT and state["local_only"]
if args.action == "verify-config":
    summaries = []
    credentials = []
    for role in state["roles"]:
        command, env = app_command(role)
        config = json.loads(run([*command, "config", "--format", "json"], env=env)[0])
        services = config["services"]
        for name in ["db", "api", "worker", "web"]:
            assert not services[name].get("ports")
            assert services[name].get("mem_limit") and services[name].get("healthcheck")
        # Compose filters inactive profiles out of rendered services.
        assert "gateway" not in services or not services["gateway"].get("ports")
        assert config["networks"]["backend"]["internal"]
        assert services["api"]["image"] == services["worker"]["image"] == API
        assert services["web"]["environment"]["REQUIRE_WORKSPACE_AUTH"] == "true"
        assert services["api"]["environment"]["ENVIRONMENT"] == "production"
        assert all(
            len(env[key]) == 64
            for key in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
        )
        assert (
            "rallysense_local_only"
            not in services["api"]["environment"]["DATABASE_URL"]
        )
        assert env["LOCAL_TOKEN"] != "rallysense-local-development"
        credentials.extend(
            env[key]
            for key in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
        )
        summaries.append(
            {
                "role": role,
                "ports": [],
                "mode": env["APP_MODE"],
                "healthchecks": True,
                "resource_limits": True,
                "production_credentials": True,
                "private_backend": True,
            }
        )
    assert len(set(credentials)) == 6
    command, env = edge_command()
    config = json.loads(run([*command, "config", "--format", "json"], env=env)[0])
    assert all(
        p["host_ip"] == "127.0.0.1" for p in config["services"]["gateway"]["ports"]
    )
    (EVIDENCE / "isolated-config.json").write_text(
        json.dumps(
            {
                "roles": summaries,
                "credentials_distinct": True,
                "gateway_loopback_only": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summaries))
elif args.action == "seed":
    for role, info in state["roles"].items():
        if info["seeded"]:
            continue
        command, env = app_command(role, readonly=False)
        run(
            [
                *command,
                "up",
                "-d",
                "--no-build",
                "--wait",
                "--wait-timeout",
                "90",
                "db",
            ],
            env=env,
        )
        mounts = []
        for script in ["prepare-demo-fixtures.py", "prepare-curated-fixtures.py"]:
            mounts += ["--volume", f"{ROOT / 'scripts' / script}:/tmp/{script}:ro"]
        output, log = run(
            [
                *command,
                "run",
                "--rm",
                "--no-deps",
                "-T",
                *mounts,
                "api",
                "sh",
                "-c",
                "alembic upgrade head && python /tmp/prepare-curated-fixtures.py",
            ],
            env=env,
        )
        record = next(
            json.loads(line)
            for line in reversed(output.splitlines())
            if line.startswith("{") and "session_ids" in json.loads(line)
        )
        assert (
            record["private_data_imported"] is False and len(record["session_ids"]) == 2
        )
        (EVIDENCE / f"{role}-fixtures.json").write_text(
            json.dumps(record, indent=2), encoding="utf-8"
        )
        values = load_env(info["env_file"])
        if role == "demo":
            values.update(
                APP_MODE="demo_readonly",
                DEMO_SESSION_IDS=",".join(record["session_ids"]),
            )
            save_env(info["env_file"], values)
        info.update(
            seeded=True,
            fixture_ids=record["session_ids"],
            paired_id=record["paired_id"],
        )
        persist()
        print(
            f"{role}: fresh generated fixtures and precomputed failure/clean cases ready.",
            flush=True,
        )
elif args.action == "start":
    assert all(info["seeded"] for info in state["roles"].values())
    for role in state["roles"]:
        command, env = app_command(role)
        run(
            [
                *command,
                "up",
                "-d",
                "--no-build",
                "--wait",
                "--wait-timeout",
                "120",
                "db",
                "api",
                "worker",
                "web",
            ],
            env=env,
        )
        print(f"{role}: private application healthy.", flush=True)
    command, env = edge_command()
    run([*command, "up", "-d", "--no-build", "--wait", "--wait-timeout", "90"], env=env)
    print(
        "Gateway healthy on 127.0.0.1:18443/18080 only. Public CA and DNS were not used."
    )
elif args.action == "stop":
    command, env = edge_command()
    run([*command, "stop"], env=env)
    for role in state["roles"]:
        command, env = app_command(role)
        run([*command, "stop", "web", "worker", "api", "db"], env=env)
    print(
        "Isolated containers stopped; all test volumes and existing development data retained."
    )
