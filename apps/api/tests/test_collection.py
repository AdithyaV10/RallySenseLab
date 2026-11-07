import json
import shutil
import subprocess
import pytest
from datetime import timedelta
from sqlalchemy.orm import Session
from rallysense import config, models as m, policy
from rallysense.signals import demo_csv
from rallysense.worker import run_one
from rallysense.jobs import finalize_pose
from test_integration import lab, create  # noqa: F401


def test_capture_metadata_revision_and_alignment_evidence(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    profile = {"participant_pseudonym": "P01", "movement": "controlled reach", "consent_confirmed": True}
    saved = client.patch(f"/api/v1/sessions/{sid}/collection", json={"revision": 1, "profile": profile})
    assert saved.status_code == 200 and saved.json()["collection_revision"] == 2
    assert (
        client.patch(
            f"/api/v1/sessions/{sid}/collection", json={"revision": 1, "profile": profile}
        ).status_code
        == 409
    )
    capture = {
        "source": "browser_devicemotion",
        "timestamp_basis": "event timestamp normalized",
        "acceleration_kind": "linear",
        "source_rotation_unit": "deg/s",
        "sample_count": 1801,
        "original_first_timestamp_ms": 123.45,
    }
    mapping = {"provenance": "synthetic", "capture": capture, "acceleration_kind": "linear"}
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports",
        files={"file": ("capture.csv", demo_csv())},
        data={"mapping": json.dumps(mapping)},
    )
    assert response.status_code == 202
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    sensor = detail["sensors"][0]
    assert sensor["mapping"]["capture"]["original_first_timestamp_ms"] == 123.45
    assert sensor["status"] == "ready"
    with Session(engine) as db, db.begin():
        video = m.VideoAsset(
            session_id=sid,
            name="metadata fixture",
            artifact_id=db.get(m.SensorRecording, sensor["id"]).raw_artifact_id,
            status="ready",
            duration_us=20_000_000,
            width=640,
            height=480,
        )
        db.add(video)
        db.flush()
        vid = video.id
    body = {
        "sensor_id": sensor["id"],
        "video_id": vid,
        "offset_us": 500_000,
        "evidence": {
            "paired": True,
            "note": "Software cue fixture",
            "cues": [
                {"sensor_us": 0, "video_us": 500_000},
                {"sensor_us": 10_000_000, "video_us": 10_700_000},
            ],
        },
    }
    aligned = client.post(f"/api/v1/sessions/{sid}/sync-configurations", json=body)
    assert aligned.status_code == 201, aligned.text
    assert aligned.json()["evidence"]["end_residual_us"] == 200_000
    assert aligned.json()["evidence"]["drift_corrected"] is False
    body["evidence"]["cues"][1]["sensor_us"] = 0
    assert client.post(f"/api/v1/sessions/{sid}/sync-configurations", json=body).status_code == 422


def test_readonly_is_fail_closed_and_hides_private_sources(lab, monkeypatch):  # noqa: F811
    client, engine = lab
    private = create(client, "private recording")
    demo = client.post("/api/v1/demo-sessions").json()["id"]
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{demo}").json()
    sensor_id = detail["sensors"][0]["id"]
    job_id = detail["jobs"][0]["id"]
    monkeypatch.setattr(config, "APP_MODE", "demo_readonly")
    monkeypatch.setattr(config, "DEMO_SESSION_IDS", set())
    assert client.get("/api/v1/sessions").json() == []
    assert client.get(f"/api/v1/sensor-recordings/{sensor_id}/samples").status_code == 404
    assert client.get(f"/api/v1/jobs/{job_id}").status_code == 404
    monkeypatch.setattr(config, "DEMO_SESSION_IDS", {demo, private})
    assert [s["id"] for s in client.get("/api/v1/sessions").json()] == [demo]
    assert client.get(f"/api/v1/sessions/{private}").status_code == 404
    assert client.get(f"/api/v1/sensor-recordings/{sensor_id}/samples").status_code == 200
    assert client.post("/api/v1/sessions", json={"title": "blocked"}).status_code == 403
    assert client.patch(f"/api/v1/sessions/{demo}/collection", json={}).status_code == 403
    assert client.delete(f"/api/v1/sessions/{demo}").status_code == 403
    assert client.get("/api/v1/capabilities").json()["mutations_allowed"] is False
    # A known synthetic key cannot bypass the explicit allowlist once provenance changes.
    with Session(engine) as db, db.begin():
        db.get(m.RecordingSession, demo).dataset_kind = "mixed"
    assert client.get(f"/api/v1/sessions/{demo}").status_code == 404


def test_worker_diagnostics_and_safe_source_retry(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    response = client.post(f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("bad.csv", b"invalid")})
    assert run_one()
    job_id = response.json()["id"]
    assert client.get(f"/api/v1/jobs/{job_id}").json()["state"] == "failed"
    retry = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert retry.status_code == 202 and retry.json()["id"] != job_id
    assert client.post(f"/api/v1/jobs/{job_id}/retry").json()["id"] == retry.json()["id"]
    assert client.get(f"/api/v1/jobs/{job_id}").json()["state"] == "failed"
    diagnostic = client.get("/api/v1/diagnostics")
    assert diagnostic.status_code == 200, diagnostic.text
    assert diagnostic.json()["database"] == "reachable"
    assert diagnostic.json()["worker"] == "ready"
    assert "storage_key" not in diagnostic.text and config.LOCAL_TOKEN not in diagnostic.text
    with Session(engine) as db, db.begin():
        db.get(m.WorkerHeartbeat, "main").heartbeat_at = m.now() - timedelta(seconds=60)
    assert client.get("/api/v1/diagnostics").json()["worker"] == "stale"


def test_upload_burst_limiter_expires_without_silent_retries(monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOADS_PER_MINUTE", 2)
    assert policy.upload_allowed("test-burst", 100)
    assert policy.upload_allowed("test-burst", 101)
    assert not policy.upload_allowed("test-burst", 102)
    assert policy.upload_allowed("test-burst", 161)


def test_late_pose_window_and_summary_projection_preserve_full_results(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports",
        files={"file": ("fixture.csv", demo_csv())},
        data={"mapping": json.dumps({"provenance": "synthetic"})},
    )
    assert response.status_code == 202 and run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    sensor, sync = detail["sensors"][0], detail["syncs"][0]
    with Session(engine) as db, db.begin():
        source = db.get(m.SensorRecording, sensor["id"])
        video = m.VideoAsset(
            session_id=sid,
            name="window metadata fixture",
            artifact_id=source.raw_artifact_id,
            status="ready",
            duration_us=120_000_000,
            width=640,
            height=480,
        )
        db.add(video)
        db.flush()
        track = m.PoseTrack(
            session_id=sid, video_id=video.id, config={"provenance": "empty timestamp API fixture"}
        )
        db.add(track)
        db.flush()
        finalize_pose(
            db,
            track,
            [{"t_video_us": i * 10_000, "landmarks": [], "world_landmarks": []} for i in range(10_051)],
        )
        track_id = track.id
    window = client.get(
        f"/api/v1/pose-tracks/{track_id}/frames?start_us=100000000&end_us=101000000&max_frames=20"
    ).json()
    assert window["source_count"] == 51 and window["truncated"] is True
    assert len(window["frames"]) == 20 and window["frames"][0]["t_video_us"] == 100_000_000
    run = client.post(
        f"/api/v1/sessions/{sid}/experiments",
        json={"mode": "imu", "sensor_id": sensor["id"], "sync_id": sync["id"]},
    )
    assert run.status_code == 202 and run_one()
    run_id = run.json()["id"]
    before = client.get(f"/api/v1/experiments/{run_id}").json()
    summary = client.get(f"/api/v1/sessions/{sid}/experiments?summaries=true").json()[0]
    assert summary["result"]["events"] == []
    assert before["result"]["events"]
    assert client.get(f"/api/v1/experiments/{run_id}").json() == before


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="Native FFmpeg absent; required in container suite")
def test_streaming_camera_webm_is_remuxed_with_original_retained(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    # Pipe output deliberately lacks seekable duration metadata, like MediaRecorder streaming chunks.
    streamed = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=160x120:r=25",
            "-t",
            "1.2",
            "-c:v",
            "libvpx",
            "-live",
            "1",
            "-f",
            "webm",
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    ).stdout
    response = client.post(
        f"/api/v1/sessions/{sid}/videos",
        files={"file": ("camera.webm", streamed, "video/webm")},
        data={"metadata": json.dumps({"provenance": "synthetic", "capture": {"source": "browser_camera"}})},
    )
    assert response.status_code == 202 and run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    video = detail["videos"][0]
    assert video["status"] == "ready", detail["jobs"]
    assert video["duration_us"] >= 1_000_000
    assert "browser_webm_remux_v1" in video["metadata_json"]["container_repair"]
    with Session(engine) as db:
        original = db.get(m.Artifact, video["metadata_json"]["original_artifact_id"])
        assert original.sha256 == video["metadata_json"]["original_sha256"]
        assert original.id != db.get(m.VideoAsset, video["id"]).artifact_id
    assert (
        client.get(f"/api/v1/videos/{video['id']}/content", headers={"range": "bytes=0-63"}).status_code
        == 206
    )
