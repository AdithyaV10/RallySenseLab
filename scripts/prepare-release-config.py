"""Generate private production configuration only; never runs Docker, DNS or cloud actions."""

import argparse
import os
import re
import secrets
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--demo-host", required=True)
parser.add_argument("--workspace-host", required=True)
parser.add_argument("--directory", type=Path, default=Path("storage/release"))
args = parser.parse_args()
hosts = [args.demo_host, args.workspace_host]
pattern = r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}"
if hosts[0] == hosts[1] or any(not re.fullmatch(pattern, host) for host in hosts):
    raise SystemExit(
        "Supply two different lowercase DNS hostnames, without scheme/port/path"
    )
target = args.directory.resolve()
if not target.is_relative_to(Path.cwd().resolve() / "storage"):
    raise SystemExit("Secret destination must stay inside ignored storage/")
if target.exists():
    raise SystemExit("Destination exists; refusing to overwrite credentials")
target.mkdir(parents=True, mode=0o700)
for role, host in zip(["demo", "workspace"], hosts, strict=True):
    # Demo starts writable ONLY for private, port-free fixture preparation.
    # Add readonly override + inspected allowlist before starting its web service.
    values = {
        "POSTGRES_PASSWORD": secrets.token_hex(32),
        "LOCAL_TOKEN": secrets.token_hex(32),
        "SITE_ACCESS_PASSWORD": secrets.token_hex(32),
        "BUILD_ID": "ac75d818a168bfcf1b7f23a609121b18b0933e8e",
        "API_IMAGE": "rallysense-api:release-ac75d818",
        "WEB_IMAGE": "rallysense-web:release-ac75d818",
        "APP_MODE": "local",
        "DEMO_SESSION_IDS": "",
        "RALLYSENSE_DOMAIN": host,
        "WEB_ALLOWED_HOSTS": host,
        "WEB_ALLOWED_ORIGINS": f"https://{host}",
        "EDGE_WEB_ALIAS": f"{role}-web",
        "EDGE_NETWORK": f"rallysense-release-{role}-edge",
    }
    content = "".join(f"{key}={value}\n" for key, value in values.items())
    file = target / f"{role}.env"
    file.write_text(content, encoding="utf-8")
    if os.name != "nt":
        file.chmod(0o600)
edge = target / "edge.env"
edge.write_text(
    f"DEMO_HOST={hosts[0]}\nWORKSPACE_HOST={hosts[1]}\n"
    "DEMO_EDGE_NETWORK=rallysense-release-demo-edge\n"
    "WORKSPACE_EDGE_NETWORK=rallysense-release-workspace-edge\nTLS_POLICY=\n",
    encoding="utf-8",
)
if os.name != "nt":
    edge.chmod(0o600)
print(
    "Private configurations generated. No infrastructure started. Inspect image security gates before use."
)
