"""Export only the reviewed Step 6.6 synthetic fixture; never access the private DB.

The fixed isolated project must already have its private DB running. No servers,
workers, native processing, inference or data mutations are started by this tool.
"""

import base64
import hashlib
import json
import subprocess
from pathlib import Path

root = Path.cwd()
manifest = json.loads(
    (root / "infrastructure/mode-a-release-manifest.json").read_text()
)
inventory = json.loads(
    (root / "docs/evidence/step6_6/fixture-inventory.json").read_text()
)
approved = json.loads((root / "docs/evidence/step6_6/demo-fixtures.json").read_text())
guard = {
    "ids": manifest["fixture_session_ids"],
    "paired": manifest["paired_id"],
    "artifacts": {a["id"]: a["sha256"] for a in inventory["artifacts"]},
    "experiments": approved["curated_experiments"],
}
code = """
import base64,hashlib,json
import pyarrow.parquet as pq
from sqlalchemy import select
from sqlalchemy.orm import Session
from rallysense.db import engine
from rallysense import models as m
from rallysense.storage import path_for
GUARD = __GUARD__
with Session(engine) as db:
 sessions=list(db.scalars(select(m.RecordingSession)))
 assert {s.id for s in sessions}==set(GUARD['ids'])
 assert all(s.dataset_kind=='synthetic' and s.participant_id is None and s.demo_key in {'synthetic-v1','paired-research-v1'} for s in sessions)
 artifacts=list(db.scalars(select(m.Artifact)))
 assert {a.id:a.sha256 for a in artifacts}==GUARD['artifacts']
 for a in artifacts:
  with path_for(db,a.id,a.session_id).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==a.sha256
 sid=GUARD['paired'];session=db.get(m.RecordingSession,sid)
 sensor=db.scalar(select(m.SensorRecording).where(m.SensorRecording.session_id==sid))
 pose=db.scalar(select(m.PoseTrack).where(m.PoseTrack.session_id==sid))
 video=db.scalar(select(m.VideoAsset).where(m.VideoAsset.session_id==sid))
 assert sensor.status==pose.status==video.status=='ready'
 assert pose.config['provenance']=='generated_analytical_landmarks'
 rows=pq.read_table(path_for(db,sensor.normalized_artifact_id,sid)).to_pylist()
 frames=pq.read_table(path_for(db,pose.artifact_id,sid)).to_pylist()
 reference=db.scalar(select(m.ReferenceSnapshot).where(m.ReferenceSnapshot.session_id==sid))
 assert reference.manifest['independent'] is False and reference.manifest['provenance']=='synthetic'
 experiments=[]
 for e in db.scalars(select(m.Experiment).where(m.Experiment.session_id==sid).order_by(m.Experiment.name)):
  assert e.status in {'succeeded','failed'}
  experiments.append({'id':e.id,'name':e.name,'status':e.status,'fingerprint':e.fingerprint,
   'mode':e.manifest['request']['mode'],'request':e.manifest['request'],'algorithm':e.manifest['algorithm'],
   'runtime':e.manifest['runtime'],'dependency_lock_sha256':e.manifest['dependency_lock_sha256'],
   'implementation_sha256':e.manifest['implementation_sha256'],'result':e.result})
 assert len(experiments)==10
 for expected in GUARD['experiments']:
  actual=next(e for e in experiments if e['id']==expected['id'])
  assert actual['status']==expected['status'] and actual['result'].get('evaluation')==expected['evaluation']
 va=db.get(m.Artifact,video.artifact_id);content=path_for(db,va.id,sid).read_bytes()
 sources=[{'kind':a.kind,'sha256':a.sha256,'bytes':a.bytes} for a in artifacts if a.session_id==sid]
 data={'schema_version':1,'source_release':'253e407e2a8bbef5f2002e3c7e67b67c658341f8',
  'title':session.title,'notes':session.notes,'dataset_kind':'synthetic',
  'duration_us':8000000,'sample_rate_hz':sensor.quality['sample_rate_hz'],
  'video':{'file':'generated-motion.mp4','sha256':va.sha256,'bytes':va.bytes,'duration_us':video.duration_us,'width':video.width,'height':video.height},
  'sensor':{'samples':rows,'quality':sensor.quality,'mapping':sensor.mapping},
  'pose':{'frames':frames,'config':pose.config},
  'reference':{'manifest':reference.manifest,'events':reference.events,'fingerprint':reference.fingerprint},
  'experiments':experiments,'sources':sources,
  'limitations':['Generated analytical observations, not athlete data or MediaPipe extraction.',
   'Stored software results only. No uploads, new inference, or real tennis accuracy.',
   'Angular-speed peaks and wrist-speed observations do not confirm swings, impacts or biomechanics.']}
 print(json.dumps({'dataset':data,'video_base64':base64.b64encode(content).decode()},sort_keys=True,allow_nan=False,separators=(',',':')))
""".replace("__GUARD__", repr(guard))
command = [
    "docker",
    "compose",
    "-p",
    "rallysense-step6-6-mode-a",
    "--env-file",
    "storage/step6_6/demo.env",
    "-f",
    "infrastructure/compose.mode-a.yml",
    "run",
    "--rm",
    "--no-deps",
    "-T",
    "api",
    "python",
    "-",
]
p = subprocess.run(
    command,
    input=code,
    capture_output=True,
    text=True,
    encoding="utf-8",
    check=False,
    timeout=90,
)
if p.returncode:
    raise SystemExit(
        "Synthetic export failed; no database credentials or raw diagnostics printed"
    )
payload = json.loads(p.stdout)
data = payload["dataset"]
video = base64.b64decode(payload["video_base64"], validate=True)
assert hashlib.sha256(video).hexdigest() == data["video"]["sha256"]
out = root / "apps/showcase/public/data"
out.mkdir(parents=True, exist_ok=True)
blob = (
    json.dumps(
        data, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )
    + "\n"
).encode()
# Exact repeatable bytes for the same immutable source; no wall-clock export fields.
(out / "showcase.json").write_bytes(blob)
(out / "generated-motion.mp4").write_bytes(video)
record = {
    "source_release": data["source_release"],
    "generated_only": True,
    "source_artifacts_verified": len(guard["artifacts"]),
    "samples": len(data["sensor"]["samples"]),
    "pose_frames": len(data["pose"]["frames"]),
    "experiments": len(data["experiments"]),
    "failed_experiments": sum(e["status"] == "failed" for e in data["experiments"]),
    "dataset_sha256": hashlib.sha256(blob).hexdigest(),
    "video_sha256": data["video"]["sha256"],
    "video_bytes": len(video),
    "dataset_bytes": len(blob),
    "private_source_used": False,
}
(out / "provenance.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
reports = root / "apps/showcase/public/reports"
reports.mkdir(parents=True, exist_ok=True)
for e in data["experiments"]:
    exported = {
        "notice": data["limitations"],
        "source_dataset_sha256": record["dataset_sha256"],
        "sources": data["sources"],
        "reference": data["reference"],
        "experiment": e,
    }
    (reports / f"{e['id']}.json").write_text(
        json.dumps(
            exported, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    score = e["result"].get("evaluation")
    lines = [
        "# RallySense Lab — stored synthetic experiment",
        "",
        e["name"],
        "",
        "**Synthetic software verification, not real-world model accuracy.**",
        "",
        f"Status: {e['status']} | Mode: {e['mode']} | Algorithm: {e['algorithm']}",
        "",
        f"Experiment: `{e['id']}`",
        f"Fingerprint: `{e['fingerprint']}`",
        "",
        "Reference independence: false. Generated pulse centers are not independent athlete labels.",
        "",
    ]
    if score:
        lines += [
            f"TP {score['tp']} | FP {score['fp']} | FN {score['fn']}",
            " | ".join(
                f"{k}: " + ("undefined" if score[k] is None else str(score[k]))
                for k in ["precision", "recall", "f1"]
            ),
            f"Matching tolerance: {score['tolerance_us']} microseconds",
            "",
        ]
    else:
        lines += ["Evaluation unavailable; no successful score is implied.", ""]
    if e["status"] == "failed":
        lines += [f"Explicit failure code: {e['result'].get('failure_code')}", ""]
    lines += [
        "## Stored event times",
        "",
        "Session microseconds | Event definition | Visual minus IMU microseconds",
        "--- | --- | ---",
    ]
    lines += [
        f"{v['t_session_us']} | {v['event_type']} | {v.get('disagreement_us', 'not applicable')}"
        for v in e["result"].get("events", [])
    ]
    lines += [
        "",
        "## Provenance",
        "",
        f"Source dataset SHA-256: `{record['dataset_sha256']}`",
        f"Source release: `{data['source_release']}`",
        "",
        *data["limitations"],
        "",
        "No uploads, live inference, private recording, model weights or backend service is included.",
        "",
    ]
    (reports / f"{e['id']}.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps(record))
