"""Render both release modes with disposable secrets; never start services or print secrets."""

import json
import os
import secrets
import subprocess
from pathlib import Path

summaries = []
for mode in ["demo_readonly", "local"]:
    env = {
        **os.environ,
        "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
        "LOCAL_TOKEN": secrets.token_urlsafe(32),
        "SITE_ACCESS_PASSWORD": secrets.token_urlsafe(24),
        "APP_MODE": mode,
        "DEMO_SESSION_IDS": "00000000-0000-0000-0000-000000000001",
        "BUILD_ID": "step5_5-config-validation",
        "API_IMAGE": "rallysense-api:local",
        "WEB_IMAGE": "rallysense-web:latest",
        "RALLYSENSE_DOMAIN": "lab.example.invalid",
        "WEB_ALLOWED_HOSTS": "lab.example.invalid",
        "WEB_ALLOWED_ORIGINS": "https://lab.example.invalid",
    }
    command = [
        "docker",
        "compose",
        "-p",
        "rallysense-release-check",
        "-f",
        "docker-compose.yml",
        "-f",
        "infrastructure/compose.release.yml",
    ]
    if mode == "demo_readonly":
        command += ["-f", "infrastructure/compose.readonly.yml"]
    result = subprocess.run(
        [*command, "config", "--format", "json"],
        env=env,
        capture_output=True,
        check=True,
        text=True,
    )
    config = json.loads(result.stdout)
    services = config["services"]
    for service in ["db", "api", "web", "worker"]:
        assert not services[service].get("ports"), service
    assert {port["published"] for port in services["gateway"]["ports"]} == {"80", "443"}
    assert services["api"]["image"] == services["worker"]["image"]
    assert (
        services["api"]["environment"]["LOCAL_TOKEN"]
        == services["worker"]["environment"]["LOCAL_TOKEN"]
        == services["web"]["environment"]["LOCAL_TOKEN"]
    )
    assert (
        services["api"]["environment"]["APP_MODE"]
        == services["worker"]["environment"]["APP_MODE"]
        == mode
    )
    assert services["web"]["environment"]["REQUIRE_WORKSPACE_AUTH"] == "true"
    assert config["networks"]["backend"]["internal"]
    assert set(services["gateway"]["networks"]) == {"edge"}
    if mode == "demo_readonly":
        for service in ["api", "worker"]:
            mount = next(
                v
                for v in services[service]["volumes"]
                if v["target"] == "/data/storage"
            )
            assert mount["read_only"] is True
    summaries.append(
        {
            "mode": mode,
            "private_service_ports": [],
            "gateway_ports": [80, 443],
            "api_worker_identical_image": True,
            "required_authentication": True,
            "backend_network_internal": True,
            "readonly_artifact_mounts": mode == "demo_readonly",
            "resource_limits_present": all(
                services[name].get("mem_limit") for name in services
            ),
        }
    )
output = {
    "scope": "Configuration rendering/assertions only; no services provisioned or public listeners started",
    "modes": summaries,
}
Path("docs/evidence/step5_5/release-config-results.json").write_text(
    json.dumps(output, indent=2), encoding="utf-8"
)
print(json.dumps(output, indent=2))
