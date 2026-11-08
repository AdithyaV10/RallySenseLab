"""Snapshot/verify full research rows locally; the baseline must remain private."""

import argparse
import hashlib
import json
from pathlib import Path

from rallysense import models as m
from rallysense.db import engine
from sqlalchemy import select
from sqlalchemy.orm import Session

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["snapshot", "verify"])
parser.add_argument("--baseline", default="storage/step5_5-research-preservation.json")
args = parser.parse_args()
target = Path(args.baseline)
current = {}
with Session(engine) as db:
    for model in [
        m.RecordingSession,
        m.SensorRecording,
        m.VideoAsset,
        m.PoseTrack,
        m.InferenceRun,
        m.Prediction,
        m.EventAnnotation,
        m.AnnotationSet,
        m.SyncConfiguration,
        m.ReferenceSnapshot,
        m.Experiment,
        m.Artifact,
    ]:
        current[model.__tablename__] = {
            row.id: hashlib.sha256(
                json.dumps(
                    {
                        column.key: getattr(row, column.key)
                        for column in model.__mapper__.column_attrs
                    },
                    sort_keys=True,
                    default=str,
                ).encode()
            ).hexdigest()
            for row in db.scalars(select(model))
        }
if args.action == "snapshot":
    if target.exists():
        raise SystemExit("Baseline exists; refusing to overwrite it")
    target.write_text(json.dumps(current, indent=2), encoding="utf-8")
    baseline = current
else:
    baseline = json.loads(target.read_text(encoding="utf-8"))
    changed = [
        (table, key)
        for table, rows in baseline.items()
        for key, digest in rows.items()
        if current[table].get(key) != digest
    ]
    assert not changed, changed
print(
    json.dumps(
        {
            "action": args.action,
            "preserved": True,
            "baseline_counts": {k: len(v) for k, v in baseline.items()},
        }
    )
)
