"""Compare actual extracted observation times with FFprobe frame presentation timestamps."""

import bisect
import json
import subprocess
from itertools import pairwise
from pathlib import Path

import pyarrow.parquet as pq
from rallysense import models as m
from rallysense.db import engine
from rallysense.storage import path_for
from sqlalchemy import select
from sqlalchemy.orm import Session

report = json.loads(Path("/tmp/step5-browser.json").read_text())
ids = set()


def visit(value):
    if isinstance(value, dict):
        if value.get("type") in {
            "measured-dense-pose-cadence",
            "measured-seek-pose-cadence",
        }:
            ids.add(json.loads(value["description"])["track_id"])
        for child in value.values():
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)


visit(report)
assert ids
results = []
with Session(engine) as db:
    sid = db.get(m.PoseTrack, next(iter(ids))).session_id
    for track in db.scalars(
        select(m.PoseTrack).where(
            m.PoseTrack.session_id == sid, m.PoseTrack.status == "ready"
        )
    ):
        video = db.get(m.VideoAsset, track.video_id)
        output = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "frame=best_effort_timestamp_time",
                "-of",
                "json",
                str(path_for(db, video.artifact_id, sid)),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        pts = sorted(
            round(float(f["best_effort_timestamp_time"]) * 1e6)
            for f in json.loads(output.stdout)["frames"]
            if "best_effort_timestamp_time" in f
        )
        times = pq.read_table(
            path_for(db, track.artifact_id, sid), columns=["t_video_us"]
        )["t_video_us"].to_pylist()
        errors = []
        for t in times:
            i = bisect.bisect_left(pts, t)
            errors.append(min(abs(p - t) for p in pts[max(0, i - 1) : i + 1]))
        assert all(b > a for a, b in pairwise(times))
        assert max(errors) <= 1, max(errors)
        results.append(
            {
                "track_id": track.id,
                "method": track.config.get("sampling_method"),
                "executor": track.config.get("executor"),
                "source_frames": len(pts),
                "observations": len(times),
                "max_distance_to_decoded_pts_us": max(errors),
                "quality": track.quality,
            }
        )
print(
    json.dumps(
        {
            "scope": "One actual permitted constant-rate clip; timing-grid correspondence, not pixel identity or frame-perfect generality",
            "tracks": results,
        },
        indent=2,
    )
)
