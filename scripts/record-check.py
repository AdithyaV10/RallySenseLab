"""Record actual local command outcomes without losing failures or console output."""

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("output")
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
started = time.monotonic()
run = subprocess.run(
    args.command, check=False, capture_output=True, encoding="utf-8", errors="replace"
)
result = {
    "at_utc": datetime.now(UTC).isoformat(),
    "command": args.command,
    "exit_code": run.returncode,
    "elapsed_s": round(time.monotonic() - started, 3),
    "output": run.stdout + run.stderr,
}
target = Path(args.output)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(result["output"][-12000:])
print(f"Recorded exit {run.returncode}: {target}")
raise SystemExit(run.returncode)
