"""Render-only production preflight; never opens a listener or approves a release."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--env-file", type=Path, required=True)
args = parser.parse_args()
values = dict(
    line.split("=", 1)
    for line in args.env_file.read_text().splitlines()
    if line and not line.startswith("#")
)
m = json.loads(Path("infrastructure/mode-a-release-manifest.json").read_text())
for path, checksum in m["source_file_hashes"].items():
    assert (
        hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        == checksum
    ), path
credentials = [
    values[k] for k in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
]
assert len(set(credentials)) == 3 and all(
    re.fullmatch(r"[a-f0-9]{64}", s) for s in credentials
)
domain = values["RALLYSENSE_DOMAIN"]
assert (
    values["WEB_ALLOWED_HOSTS"] == domain
    and values["WEB_ALLOWED_ORIGINS"] == "https://" + domain
)
assert set(values["DEMO_SESSION_IDS"].split(",")) == set(m["fixture_session_ids"])
cmd = [
    "docker",
    "compose",
    "-p",
    "rallysense-mode-a-preflight",
    "--env-file",
    str(args.env_file),
    "-f",
    "infrastructure/compose.mode-a.yml",
    "config",
    "--format",
    "json",
]
p = subprocess.run(cmd, check=False, capture_output=True, text=True)
assert p.returncode == 0, (
    "Invalid Compose input (rendered secrets intentionally withheld)"
)
c = json.loads(p.stdout)
s = c["services"]
assert set(s) == {"db", "api", "worker", "web", "gateway"}
images = {r["name"]: r["release_tag"] for r in m["images"]}
assert s["api"]["image"] == s["worker"]["image"] == images["api_readonly"]
assert (
    s["db"]["image"] == images["postgres"]
    and s["web"]["image"] == images["web"]
    and s["gateway"]["image"] == images["caddy"]
)
assert (
    s["api"]["environment"]["APP_MODE"]
    == s["worker"]["environment"]["APP_MODE"]
    == "demo_readonly"
)
assert s["api"]["read_only"] and s["worker"]["read_only"]
assert s["web"]["environment"]["REQUIRE_WORKSPACE_AUTH"] == "true"
assert c["networks"]["backend"]["internal"]
assert set(s["gateway"]["networks"]) == {"edge"}
assert all(not s[n].get("ports") for n in ["db", "api", "worker", "web"])
assert {p["target"] for p in s["gateway"]["ports"]} == {80, 443}
assert "TLS_POLICY" not in s["gateway"]["environment"]
assert all(
    s[n].get("healthcheck")
    and s[n].get("mem_limit")
    and s[n].get("cpus")
    and s[n].get("pids_limit")
    for n in s
)
print(
    json.dumps(
        {
            "production_render_passed": True,
            "source_hashes_verified": len(m["source_file_hashes"]),
            "readonly_images_only": True,
            "unique_credentials": True,
            "private_backend": True,
            "total_container_memory_limit_bytes": sum(
                int(s[n]["mem_limit"]) for n in s
            ),
            "dns_domain_ownership_public_tls_firewall_unverified": True,
            "security_and_legal_approvals_not_granted": True,
            "public_listener_started": False,
        }
    )
)
