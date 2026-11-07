"""Record/verify pre-stage immutable rows without exporting private input arrays."""
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
parser.add_argument("--baseline", default="storage/step4-preservation.json")
args = parser.parse_args()
target = Path(__file__).resolve().parents[1] / args.baseline
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()
with Session(engine) as db:
    current = {}
    for model,fields in [
        (m.Experiment,["session_id","manifest","result","status","fingerprint"]),
        (m.ReferenceSnapshot,["session_id","manifest","events","fingerprint"]),
        (m.Artifact,["session_id","sha256","bytes","storage_key"]),
    ]:
        current[model.__tablename__] = {row.id:digest({k:getattr(row,k) for k in fields}) for row in db.scalars(select(model))}
    current["sessions"] = {s.id:digest({"title":s.title,"kind":s.dataset_kind,"handedness":s.handedness,"notes":s.notes}) for s in db.scalars(select(m.RecordingSession).where(m.RecordingSession.deleted_at.is_(None)))}
if args.action == "snapshot":
    if target.exists():
        raise SystemExit("Baseline exists; refusing to overwrite it")
    target.parent.mkdir(exist_ok=True,parents=True)
    target.write_text(json.dumps(current,indent=2),encoding="utf-8")
else:
    baseline = json.loads(target.read_text())
    changed = [(table,key) for table,rows in baseline.items() for key,value in rows.items() if current[table].get(key) != value]
    assert not changed, changed
print(json.dumps({"action":args.action,"baseline_counts":{k:len(v) for k,v in (current if args.action=='snapshot' else baseline).items()},"preserved":True}))
