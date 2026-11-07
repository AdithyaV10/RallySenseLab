"""Readiness, ordinary demo pipeline, and persistence smoke check against local services."""
import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="docs/evidence/local-verification.json")
args = parser.parse_args()

base = "http://127.0.0.1:3000"
with httpx.Client(base_url=base, headers={"x-lab-client":"rallysense"}, timeout=10) as client:
    for attempt in range(30):
        try:
            response = client.get("/api/v1/health/ready")
            response.raise_for_status()
            break
        except httpx.HTTPError:
            if attempt == 29:
                raise
            time.sleep(1)
    assert client.get("/").status_code == 200
    assert client.get("/sessions").status_code == 200
    demo = client.post("/api/v1/demo-sessions")
    demo.raise_for_status()
    session_id = demo.json()["id"]
    for attempt in range(30):
        detail = client.get(f"/api/v1/sessions/{session_id}").json()
        if any(r["status"]=="succeeded" for r in detail["runs"]):
            break
        time.sleep(1)
    else:
        raise AssertionError("Demo processing did not finish")
    assert detail["dataset_kind"] == "synthetic"
    assert detail["sensors"][0]["samples"] == 1801
    assert len(detail["predictions"]) >= 5
    assert all(p["event_type"] == "gyro_peak_v1" for p in detail["predictions"])
    evidence = {"verified_at_utc":datetime.now(UTC).isoformat(),"base_url":base,
                "health":"ready","landing_http":200,"sessions_http":200,
                "demo_id":session_id,"dataset_kind":"synthetic","samples":1801,
                "successful_runs":sum(r["status"]=="succeeded" for r in detail["runs"]),
                "event_type":"gyro_peak_v1","scientific_accuracy_evaluated":False}
    target=Path(__file__).resolve().parents[1]/args.output
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(evidence,indent=2))
