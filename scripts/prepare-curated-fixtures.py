"""Run in a fresh isolated writable API container; generated fixtures only, no private imports."""

import json
import runpy

from rallysense import models as m
from rallysense.api.research import create_experiment, freeze
from rallysense.db import engine
from rallysense.research_schemas import ExperimentCreate, FreezeCreate
from rallysense.worker import run_one
from sqlalchemy import select
from sqlalchemy.orm import Session

# The baseline helper refuses populated DB/storage and computes the three unscored modes.
runpy.run_path("/tmp/prepare-demo-fixtures.py", run_name="__main__")
with Session(engine) as db, db.begin():
    paired = db.scalar(
        select(m.RecordingSession).where(
            m.RecordingSession.demo_key == "paired-research-v1"
        )
    )
    sid = paired.id
    sensor = db.scalar(
        select(m.SensorRecording).where(m.SensorRecording.session_id == sid)
    )
    pose = db.scalar(select(m.PoseTrack).where(m.PoseTrack.session_id == sid))
    video = db.scalar(select(m.VideoAsset).where(m.VideoAsset.session_id == sid))
    sync = db.scalar(
        select(m.SyncConfiguration).where(m.SyncConfiguration.session_id == sid)
    )
    labels = db.scalar(
        select(m.AnnotationSet).where(
            m.AnnotationSet.session_id == sid, m.AnnotationSet.provenance == "synthetic"
        )
    )
    reference = freeze(
        labels.id,
        FreezeCreate(
            revision=labels.revision,
            event_type="synthetic_reference",
            definition="Analytical generated pulse centers at 2 and 5 seconds; not independently labeled athlete events.",
            labeler="built-in synthetic fixture generator",
            procedure="Software-only generated reference clock; never interpreted as real tennis ground truth.",
            independent=False,
            video_id=video.id,
        ),
        db,
    )
    common = {
        "sensor_id": sensor.id,
        "pose_id": pose.id,
        "sync_id": sync.id,
        "reference_id": reference.id,
        "comparison": "synthetic_fixture",
        "end_us": 8_000_000,
        "pairing": "synthetic_fixture",
        "alignment_note": "Known generated clock, not a physical tennis recording",
    }
    inputs = {}
    for name, mode, corruption in [
        (
            "Missing IMU window / synthetic failure case",
            "imu",
            {"imu_gap_start_s": 1.5, "imu_gap_duration_s": 1},
        ),
        (
            "Wrist occlusion / synthetic failure case",
            "fusion",
            {"occlusion_start_s": 1.5, "occlusion_duration_s": 1},
        ),
        (
            "Offset +1 second / synthetic failure case",
            "fusion",
            {"sync_error_us": 1_000_000},
        ),
        (
            "Full occlusion / expected inference failure",
            "video",
            {"occlusion_duration_s": 8},
        ),
        ("Clean IMU / synthetic software verification", "imu", {}),
        ("Clean video / synthetic software verification", "video", {}),
        ("Clean fusion / synthetic software verification", "fusion", {}),
    ]:
        payload = {
            **common,
            "name": name,
            "mode": mode,
            "corruption": {"seed": 42, **corruption},
            "research_question": "How do generated observation failures change this analytical software fixture?",
        }
        if mode == "imu":
            payload["pose_id"] = None
        if mode == "video":
            payload["sensor_id"] = payload["sync_id"] = None
        exp = create_experiment(sid, ExperimentCreate.model_validate(payload), db)
        inputs[name] = exp.id
for _ in range(20):
    if not run_one():
        break
with Session(engine) as db:
    output = []
    for name, eid in inputs.items():
        exp = db.get(m.Experiment, eid)
        expected_failed = name.startswith("Full occlusion")
        assert exp.status == ("failed" if expected_failed else "succeeded"), (
            name,
            exp.status,
        )
        output.append(
            {
                "name": name,
                "id": eid,
                "status": exp.status,
                "events": len(exp.result.get("events", [])),
                "failure_code": exp.result.get("failure_code"),
                "evaluation": exp.result.get("evaluation"),
            }
        )
    sessions = list(db.scalars(select(m.RecordingSession)))
    assert len(sessions) == 2 and all(s.dataset_kind == "synthetic" for s in sessions)
print(
    json.dumps(
        {
            "session_ids": [s.id for s in sessions],
            "paired_id": sid,
            "private_data_imported": False,
            "dataset": "built-in generated analytical fixtures; no real-world accuracy evaluation",
            "curated_experiments": output,
        }
    )
)
