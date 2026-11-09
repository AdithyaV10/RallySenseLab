"""Write new Mode A production secrets locally. Does not start services or alter DNS."""

import argparse
import json
import os
import re
import secrets
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--domain", required=True)
parser.add_argument("--output", type=Path, default=Path("storage/release/demo.env"))
args = parser.parse_args()
if not re.fullmatch(
    r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", args.domain
) or args.domain.endswith((".test", ".invalid", ".localhost")):
    raise SystemExit(
        "Use a real exact lowercase DNS hostname without scheme, port, wildcard or path"
    )
path = args.output.resolve()
if not path.is_relative_to(Path("storage").resolve()) or path.exists():
    raise SystemExit("Output must be a NEW file inside ignored storage/")
manifest = json.loads(Path("infrastructure/mode-a-release-manifest.json").read_text())
images = {r["name"]: r["release_tag"] for r in manifest["images"]}
values = {
    k: secrets.token_hex(32)
    for k in ["POSTGRES_PASSWORD", "LOCAL_TOKEN", "SITE_ACCESS_PASSWORD"]
}
values.update(
    POSTGRES_IMAGE=images["postgres"],
    READONLY_API_IMAGE=images["api_readonly"],
    WEB_IMAGE=images["web"],
    CADDY_IMAGE=images["caddy"],
    RALLYSENSE_DOMAIN=args.domain,
    WEB_ALLOWED_HOSTS=args.domain,
    WEB_ALLOWED_ORIGINS="https://" + args.domain,
    BUILD_ID=manifest["build_id"],
    DEMO_SESSION_IDS=",".join(manifest["fixture_session_ids"]),
)
path.parent.mkdir(parents=True, exist_ok=True)
# O_EXCL prevents accidental replacement; POSIX permissions set before content write.
fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write("".join(f"{k}={v}\n" for k, v in values.items()))
print(
    "Generated unique Mode A secrets; file content intentionally withheld. No services started."
)
