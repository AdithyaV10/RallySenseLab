"""Render production configuration and validate Caddy offline. Starts no application/listener."""

import json
import subprocess
from pathlib import Path

root = Path.cwd()
private = root / "storage/step6-production-render"


def run(command):
    result = subprocess.run(
        command, check=False, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    # Never include rendered Compose/secrets in a failure log.
    assert result.returncode == 0, (
        f"Configuration check failed: {command[0]} ({result.returncode})"
    )
    return result.stdout


if not private.exists():
    run(
        [
            "uv",
            "run",
            "--project",
            "apps/api",
            "python",
            "scripts/prepare-release-config.py",
            "--demo-host",
            "demo.example.invalid",
            "--workspace-host",
            "research.example.invalid",
            "--directory",
            str(private),
        ]
    )
checks = []
for role, host in [
    ("demo", "demo.example.invalid"),
    ("workspace", "research.example.invalid"),
]:
    file = private / f"{role}.env"
    values = dict(line.split("=", 1) for line in file.read_text().splitlines())
    if role == "demo":
        # Rendering-only fixture ID, not a deployed/claimed populated database.
        values.update(
            APP_MODE="demo_readonly",
            DEMO_SESSION_IDS="00000000-0000-0000-0000-000000000001",
        )
        file.write_text(
            "".join(f"{key}={value}\n" for key, value in values.items()),
            encoding="utf-8",
        )
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--env-file",
        str(file),
        "-p",
        f"rallysense-release-{role}",
        "-f",
        "docker-compose.yml",
        "-f",
        "infrastructure/compose.release.yml",
        "-f",
        "infrastructure/compose.application.yml",
    ]
    if role == "demo":
        command += ["-f", "infrastructure/compose.readonly.yml"]
    config = json.loads(run([*command, "config", "--format", "json"]))
    services = config["services"]
    for name in ["db", "api", "worker", "web"]:
        service = services[name]
        assert not service.get("ports"), name
        assert service["healthcheck"]["test"]
        assert int(service["mem_limit"]) > 0 and int(service["pids_limit"]) > 0
        assert service.get("cpus")
    assert config["networks"]["backend"]["internal"] is True
    for name in ["api", "worker"]:
        assert services[name]["environment"]["ENVIRONMENT"] == "production"
        assert services[name]["environment"]["ALLOWED_ORIGINS"] == f"https://{host}"
        assert set(services[name]["networks"]) == {"backend"}
    assert set(services["db"]["networks"]) == {"backend"}
    web = services["web"]["environment"]
    assert (
        web["WEB_ALLOWED_HOSTS"] == host
        and web["WEB_ALLOWED_ORIGINS"] == f"https://{host}"
    )
    assert web["REQUIRE_WORKSPACE_AUTH"] == "true"
    assert services["api"]["image"] == services["worker"]["image"]
    for key in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]:
        assert len(values[key]) == 64 and "CHANGE_ME" not in values[key]
    assert "rallysense_local_only" not in json.dumps(config)
    assert "rallysense-local-development" not in json.dumps(config)
    if role == "demo":
        for name in ["api", "worker"]:
            assert all(
                v.get("read_only")
                for v in services[name]["volumes"]
                if v["target"] == "/data/storage"
            )
    checks.append(
        {
            "role": role,
            "exact_host_origin": True,
            "no_host_ports": True,
            "health_and_resource_limits": True,
            "private_backend": True,
            "random_credentials": True,
        }
    )
edge = json.loads(
    run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(root),
            "--env-file",
            str(private / "edge.env"),
            "-f",
            "infrastructure/compose.gateway.yml",
            "config",
            "--format",
            "json",
        ]
    )
)
gateway = edge["services"]["gateway"]
assert sorted(int(p["published"]) for p in gateway["ports"]) == [80, 443]
assert gateway["environment"]["TLS_POLICY"] == ""
image = gateway["image"]
run(
    [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--entrypoint",
        "caddy",
        "--mount",
        f"type=bind,source={root / 'infrastructure/Caddyfile.release'},target=/etc/caddy/Caddyfile,readonly",
        "--env",
        "DEMO_HOST=demo.example.invalid",
        "--env",
        "WORKSPACE_HOST=research.example.invalid",
        image,
        "validate",
        "--config",
        "/etc/caddy/Caddyfile",
        "--adapter",
        "caddyfile",
    ]
)
print(
    json.dumps(
        {
            "production_render_passed": True,
            "checks": checks,
            "caddy_offline_validation": True,
            "public_listeners_started": False,
            "cloud_dns_acme_verified": False,
        }
    )
)
