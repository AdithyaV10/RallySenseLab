"""Offline seed/precompute for a NEW EMPTY demo database only. Never imports local recordings."""

import json

from rallysense import config
from rallysense import models as m
from rallysense.api.research import create_experiment
from rallysense.api.sessions import seed_demo, seed_research_demo
from rallysense.db import engine
from rallysense.research_schemas import ExperimentCreate
from rallysense.worker import run_one
from sqlalchemy import func, select
from sqlalchemy.orm import Session

if config.APP_MODE != "local":
    raise SystemExit(
        "Prepare fixtures privately in writable mode, then switch to demo_readonly"
    )
if config.STORAGE_ROOT.exists() and any(config.STORAGE_ROOT.iterdir()):
    raise SystemExit("Refusing nonempty artifact storage; use fresh demo volumes")
with Session(engine) as db, db.begin():
    # Refuse even a populated fixture workspace: this is for clean volumes, not sanitization.
    if db.scalar(select(func.count()).select_from(m.RecordingSession)):
        raise SystemExit("Refusing to seed a nonempty database; use fresh demo volumes")
    baseline = seed_demo(db)
    paired = seed_research_demo(db)
    ids, paired_id = [baseline.id, paired.id], paired.id
for _ in range(20):
    if not run_one():
        break
with Session(engine) as db, db.begin():
    if db.scalar(
        select(func.count())
        .select_from(m.ProcessingJob)
        .where(m.ProcessingJob.state != "succeeded")
    ):
        raise SystemExit(
            "Fixture preparation did not succeed; inspect private worker diagnostics"
        )
    sensor = db.scalar(
        select(m.SensorRecording).where(m.SensorRecording.session_id == paired_id)
    )
    pose = db.scalar(select(m.PoseTrack).where(m.PoseTrack.session_id == paired_id))
    sync = db.scalar(
        select(m.SyncConfiguration).where(m.SyncConfiguration.session_id == paired_id)
    )
    for mode in ["imu", "video", "fusion"]:
        payload = ExperimentCreate(
            mode=mode,
            sensor_id=sensor.id if mode != "video" else None,
            pose_id=pose.id if mode != "imu" else None,
            sync_id=sync.id if mode != "video" else None,
            end_us=8_000_000,
            pairing="synthetic_fixture",
            alignment_note="Analytical generator clock; not physical tennis validation",
            name=f"Precomputed synthetic {mode}",
            research_question="What measured signal events does the analytical fixture produce?",
        )
        create_experiment(paired_id, payload, db)
for _ in range(10):
    if not run_one():
        break
with Session(engine) as db:
    experiments = list(db.scalars(select(m.Experiment)))
    assert len(experiments) == 3 and all(e.status == "succeeded" for e in experiments)
print(
    json.dumps(
        {
            "demo_session_ids": ids,
            "precomputed_experiments": 3,
            "source": "Only built-in generated synthetic fixtures; no local media imported",
            "next": "Inspect content; set explicit allowlist and demo_readonly mode; do not start public gateway without authorization",
        }
    )
)
