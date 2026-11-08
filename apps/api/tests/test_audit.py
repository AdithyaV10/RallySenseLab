"""Independent Step 5 analytical and adversarial checks. Disposable database only."""

import copy
import itertools
from datetime import timedelta

import numpy as np
import pytest
from sqlalchemy.orm import Session

from rallysense import jobs, models as m
from rallysense.errors import DomainError
from rallysense.research import associate, corrupt, detect_video, evaluate, match_events
from rallysense.research_schemas import Corruption, VideoConfig
from rallysense.signals import demo_csv, normalize_csv
from rallysense.schemas import SensorMapping
from test_integration import lab, create  # noqa: F401


def test_audit_metrics_independently_calculated_with_unequal_errors():
    # 3 pairs with signed errors -10,+20,-30; one extra prediction and two misses.
    p = [{"t_session_us": t} for t in [90, 320, 570, 1500]]
    r = [{"t_session_us": t} for t in [100, 300, 600, 900, 1200]]
    result = evaluate(p, r, 30, 60_000_000)
    assert (result["tp"], result["fp"], result["fn"]) == (3, 1, 2)
    assert result["precision"] == 3 / 4
    assert result["recall"] == 3 / 5
    assert result["f1"] == 2 / 3
    assert result["mean_absolute_error_us"] == result["median_absolute_error_us"] == 20
    assert result["mean_signed_error_us"] == pytest.approx(-20 / 3)
    assert result["false_positives_per_minute"] == 1


def test_audit_matcher_unsorted_duplicates_against_independent_enumeration():
    rng = np.random.default_rng(517)
    for _ in range(120):
        p = rng.integers(-3, 8, 4).tolist()
        r = rng.integers(-3, 8, 3).tolist()
        tolerance = int(rng.integers(0, 4))
        objectives = [(0, 0)]
        for n in range(1, 4):
            for pi in itertools.combinations(range(4), n):
                for ri in itertools.permutations(range(3), n):
                    errors = [abs(p[i] - r[j]) for i, j in zip(pi, ri)]
                    if max(errors) <= tolerance:
                        objectives.append((n, -sum(errors)))
        pairs = match_events([{"t_session_us": t} for t in p], [{"t_session_us": t} for t in r], tolerance)
        assert (len(pairs), -sum(abs(p[i] - r[j]) for i, j in pairs)) == max(objectives)
        assert len({i for i, _ in pairs}) == len({j for _, j in pairs}) == len(pairs)


def test_audit_aspect_corrected_speed_uses_interval_midpoints_and_fixed_torso():
    # In x*aspect,y coordinates: torso length .5, wrist velocity .5/s => 1 torso/s.
    frames = []
    for i in range(41):
        points = [{"x": 0.5, "y": 0.5, "z": 0, "visibility": 1} for _ in range(33)]
        for j in [11, 12]:
            points[j]["y"] = 0.25
        for j in [23, 24]:
            points[j]["y"] = 0.75
        points[16]["x"] = 0.2 + 0.25 * i / 20
        frames.append({"t_video_us": i * 50_000, "landmarks": points})
    original = copy.deepcopy(frames)
    result = detect_video(frames, VideoConfig(smooth_window_s=0, threshold=10), aspect=2)
    assert [x["t_session_us"] for x in result["signal"]] == list(range(25_000, 2_000_000, 50_000))
    assert [x["value"] for x in result["signal"]] == pytest.approx([1] * 40)
    assert result["events"] == []
    assert frames == original


def test_audit_fusion_boundary_gate_and_unobserved_candidates():
    imu = {
        "events": [{"t_session_us": t, "magnitude": 2} for t in [100, 500, 900]],
        "eligible_intervals": [{"start_us": 0, "end_us": 1000}],
    }
    video = {
        "events": [{"t_session_us": t, "magnitude": 3} for t in [125, 525, 900]],
        "eligible_intervals": [{"start_us": 0, "end_us": 600}],
    }
    a = associate(imu, video, 25)
    assert [(e["imu_time_us"], e["video_time_us"]) for e in a["events"]] == [(100, 125), (500, 525)]
    assert a["quality"]["unmatched_imu"] == a["quality"]["unmatched_video"] == [2]
    assert associate(imu, video, 24)["events"] == []
    with pytest.raises(DomainError, match="common"):
        associate(imu, {**video, "eligible_intervals": [{"start_us": 1000, "end_us": 1100}]}, 25)


def test_audit_corruption_channels_seed_and_original_bytes():
    table, _ = normalize_csv(demo_csv(), SensorMapping())
    original = table.to_pydict()
    recipe = Corruption(seed=190, gyro_noise_sd=0.8, dropout_fraction=0.25)
    a, _, _ = corrupt(table, None, recipe)
    b, _, _ = corrupt(table, None, recipe)
    c, _, _ = corrupt(table, None, recipe.model_copy(update={"seed": 191}))
    assert a.equals(b) and not a.equals(c)
    assert table.to_pydict() == original
    assert len(a) < len(table)
    indexes = np.searchsorted(table["t_us"].to_numpy(), a["t_us"].to_numpy())
    assert a["ax"].to_numpy() == pytest.approx(table["ax"].to_numpy()[indexes])
    assert not np.allclose(a["gx"].to_numpy(), table["gx"].to_numpy()[indexes])


def test_audit_retry_exhaustion_sets_source_failed(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    job = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv())}
    ).json()
    with Session(engine) as db, db.begin():
        row = db.get(m.ProcessingJob, job["id"])
        row.state, row.attempt = "running", 3
        row.lease_expires_at = m.now() - timedelta(seconds=1)
    assert jobs.claim_job() is None
    with Session(engine) as db:
        assert db.get(m.ProcessingJob, job["id"]).state == "failed"
        assert db.get(m.SensorRecording, job["target_id"]).status == "failed"


def test_audit_cancelled_source_has_terminal_status(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    job = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv())}
    ).json()
    assert client.post(f"/api/v1/jobs/{job['id']}/cancel").status_code == 200
    with Session(engine) as db:
        assert db.get(m.ProcessingJob, job["id"]).state == "cancelled"
        assert db.get(m.SensorRecording, job["target_id"]).status == "cancelled"


def test_audit_running_cancel_does_not_publish_and_completed_cancel_is_noop(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    job = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv())}
    ).json()
    claimed = jobs.claim_job()
    assert client.post(f"/api/v1/jobs/{job['id']}/cancel").status_code == 200
    jobs.execute_job(*claimed)
    with Session(engine) as db:
        assert db.get(m.SensorRecording, job["target_id"]).status == "cancelled"
        assert db.get(m.SensorRecording, job["target_id"]).normalized_artifact_id is None
    retry = client.post(f"/api/v1/jobs/{job['id']}/retry").json()
    jobs.execute_job(*jobs.claim_job())
    assert client.post(f"/api/v1/jobs/{retry['id']}/cancel").json()["state"] == "succeeded"
    with Session(engine) as db:
        assert db.get(m.SensorRecording, job["target_id"]).status == "ready"
        assert db.get(m.ProcessingJob, retry["id"]).cancel_requested is False


def test_audit_readonly_alternate_endpoints_and_direct_references(lab, monkeypatch):  # noqa: F811
    from rallysense import config
    from rallysense.worker import run_one

    client, _ = lab
    sid = client.post("/api/v1/research-demo-sessions").json()["id"]
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    sensor, pose, video, sync = (
        detail["sensors"][0],
        detail["poses"][0],
        detail["videos"][0],
        detail["syncs"][0],
    )
    exp = client.post(
        f"/api/v1/sessions/{sid}/experiments",
        json={"mode": "imu", "sensor_id": sensor["id"], "sync_id": sync["id"]},
    ).json()
    assert run_one()
    paths = [
        f"/sessions/{sid}",
        f"/sessions/{sid}/annotation-sets",
        f"/sessions/{sid}/references",
        f"/sessions/{sid}/experiments",
        f"/sessions/{sid}/experiments?summaries=true",
        f"/sessions/{sid}/experiment-comparison?ids={exp['id']}",
        f"/experiments/{exp['id']}",
        f"/experiments/{exp['id']}/report",
        f"/videos/{video['id']}/content",
        f"/pose-tracks/{pose['id']}/frames",
        f"/sensor-recordings/{sensor['id']}/samples",
        f"/jobs/{detail['jobs'][0]['id']}",
    ]
    monkeypatch.setattr(config, "APP_MODE", "demo_readonly")
    monkeypatch.setattr(config, "DEMO_SESSION_IDS", set())
    for path in paths:
        response = client.get("/api/v1" + path, headers={"range": "bytes=0-31"})
        assert response.status_code == 404, (path, response.text)
    assert client.get("/api/v1/sessions").json() == client.get("/api/v1/demonstrations").json() == []
    assert sid not in client.get("/api/v1/diagnostics").text
    monkeypatch.setattr(config, "DEMO_SESSION_IDS", {sid})
    assert client.get(f"/api/v1/experiments/{exp['id']}/report").status_code == 200
    for method, path in [
        ("POST", f"/jobs/{detail['jobs'][0]['id']}/cancel"),
        ("POST", f"/jobs/{detail['jobs'][0]['id']}/retry"),
        ("POST", f"/experiments/{exp['id']}/evaluate"),
        ("PUT", f"/pose-tracks/{pose['id']}/batches/0"),
        ("POST", f"/pose-tracks/{pose['id']}/fail"),
    ]:
        assert client.request(method, "/api/v1" + path, json={}).status_code == 403


def test_audit_pose_batch_capacity_characterization(lab):  # noqa: F811
    """Retain the audited boundary and verify the repaired, still bounded batch cap."""
    from rallysense.storage import put_bytes

    client, engine = lab
    sid = create(client)
    with Session(engine) as db, db.begin():
        raw = put_bytes(db, sid, b"numerical metadata fixture; not video", "fixture")
        video = m.VideoAsset(
            session_id=sid,
            artifact_id=raw.id,
            name="capacity fixture",
            status="ready",
            width=100,
            height=100,
            duration_us=600_000_000,
        )
        db.add(video)
        db.flush()
        track = m.PoseTrack(session_id=sid, video_id=video.id, config={})
        db.add(track)
        db.flush()
        tid = track.id
    for batch in range(100):
        frames = [{"t_video_us": (batch * 100 + i) * 33333, "landmarks": []} for i in range(100)]
        assert (
            client.put(f"/api/v1/pose-tracks/{tid}/batches/{batch}", json={"frames": frames}).status_code
            == 200
        )
    result = client.put(
        f"/api/v1/pose-tracks/{tid}/batches/100",
        json={"frames": [{"t_video_us": 333_330_000, "landmarks": []}]},
    )
    assert result.status_code == 200
    result = client.put(
        f"/api/v1/pose-tracks/{tid}/batches/200",
        json={"frames": [{"t_video_us": 333_330_000, "landmarks": []}]},
    )
    assert result.status_code == 409 and result.json()["error"]["code"] == "INVALID_STATE"
