"""Real PostgreSQL tests in a unique, disposable schema; never use the live session tables."""

import json
import shutil
import subprocess
import os
import time
from datetime import timedelta
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from rallysense import models as m, jobs, storage
from rallysense.db import Base, engine, get_db
from rallysense.main import app
from rallysense.config import LOCAL_TOKEN
from rallysense.signals import demo_csv
from rallysense.worker import run_one


@pytest.fixture()
def lab(tmp_path, monkeypatch):
    schema = "test_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    test_engine = create_engine(engine.url, connect_args={"options": f"-csearch_path={schema}"})
    Base.metadata.create_all(test_engine)
    monkeypatch.setattr(jobs, "engine", test_engine)
    monkeypatch.setattr(storage, "STORAGE_ROOT", tmp_path)

    def override():
        with Session(test_engine) as db:
            try:
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise

    app.dependency_overrides[get_db] = override
    with TestClient(app, headers={"x-lab-token": LOCAL_TOKEN}) as client:
        yield client, test_engine
    app.dependency_overrides.clear()
    test_engine.dispose()
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))


def create(client, title="Integration test"):
    response = client.post("/api/v1/sessions", json={"title": title})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_ingestion_inference_alignment_labels_and_delete(lab):
    client, test_engine = lab
    sid = create(client)
    assert (
        client.post(
            "/api/v1/sessions", json={"title": "oversized"}, headers={"content-length": str(3 * 1024 * 1024)}
        ).status_code
        == 413
    )
    imported = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv(), "text/csv")}
    )
    assert imported.status_code == 202, imported.text
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    sensor = detail["sensors"][0]
    assert sensor["status"] == "ready" and sensor["samples"] == 1801
    assert "storage_key" not in json.dumps(detail)
    samples = client.get(f"/api/v1/sensor-recordings/{sensor['id']}/samples?max_points=100").json()
    assert samples["source_count"] == 1801 and samples["returned_count"] <= 100
    sync = client.post(
        f"/api/v1/sessions/{sid}/sync-configurations",
        json={"sensor_id": sensor["id"], "offset_us": 1_500_000},
    )
    assert sync.status_code == 201
    run = client.post(f"/api/v1/sessions/{sid}/inference-runs", json={"sensor_id": sensor["id"]})
    assert run.status_code == 202, run.text
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    assert len(detail["predictions"]) == 5
    assert min(p["t_session_us"] for p in detail["predictions"]) == pytest.approx(3_700_000, abs=20000)
    repeated = client.post(f"/api/v1/sessions/{sid}/inference-runs", json={"sensor_id": sensor["id"]})
    assert repeated.json()["id"] == run.json()["id"]
    label = client.post(
        f"/api/v1/sessions/{sid}/annotations",
        json={"t_session_us": 3_700_000, "note": "Independent visual observation"},
    ).json()
    edited = client.patch(f"/api/v1/annotations/{label['id']}", json={**label, "t_session_us": 3_710_000})
    assert edited.status_code == 200 and edited.json()["revision"] == 2
    assert client.patch(f"/api/v1/annotations/{label['id']}", json=label).status_code == 409
    with Session(test_engine) as db:
        assert db.get(m.RecordingSession, sid).title == "Integration test"
    deleted = client.delete(f"/api/v1/sessions/{sid}")
    assert deleted.status_code == 202
    assert client.get(f"/api/v1/sessions/{sid}").status_code == 404
    assert run_one()
    assert client.get(f"/api/v1/jobs/{deleted.json()['id']}").json()["state"] == "succeeded"
    assert not storage.resolve(sid).exists()


def test_invalid_inputs_missing_auth_and_cross_session_references(lab):
    client, _ = lab
    sid = create(client)
    assert (
        client.post("/api/v1/sessions", json={"title": "no"}, headers={"x-lab-token": "wrong"}).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/sessions", json={"title": "no"}, headers={"origin": "https://untrusted.example"}
        ).status_code
        == 403
    )
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("bad.csv", b"garbage", "text/csv")}
    )
    assert response.status_code == 202
    run_one()
    assert client.get(f"/api/v1/jobs/{response.json()['id']}").json()["state"] == "failed"
    assert (
        client.post(
            f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("archive.zip", b"x")}
        ).status_code
        == 415
    )
    assert client.get("/api/v1/sessions/not-a-uuid").status_code == 422
    with pytest.raises(Exception, match="Invalid storage"):
        storage.resolve("../../outside")
    other = create(client, "Other")
    with Session(jobs.engine) as db, db.begin():
        artifact = storage.put_bytes(db, other, b"test", "raw_csv")
        sensor = m.SensorRecording(session_id=other, raw_artifact_id=artifact.id, name="owned", mapping={})
        db.add(sensor)
        db.flush()
        sensor_id = sensor.id
        artifact_id = artifact.id
    assert (
        client.post(
            f"/api/v1/sessions/{sid}/sync-configurations", json={"sensor_id": sensor_id, "offset_us": 0}
        ).status_code
        == 409
    )
    with Session(jobs.engine) as db:
        db.add(m.SensorRecording(session_id=sid, raw_artifact_id=artifact_id, name="foreign", mapping={}))
        with pytest.raises(IntegrityError):
            db.commit()


def test_expired_lease_reclaimed_and_old_worker_fenced(lab):
    client, test_engine = lab
    sid = create(client)
    client.post(f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv())})
    old = jobs.claim_job()
    with Session(test_engine) as db, db.begin():
        job = db.get(m.ProcessingJob, old[0])
        job.lease_expires_at = m.now() - timedelta(seconds=1)
    new = jobs.claim_job()
    assert new[0] == old[0] and new[1] != old[1]
    jobs.execute_job(*old)
    with Session(test_engine) as db:
        assert db.get(m.ProcessingJob, new[0]).state == "running"
    jobs.execute_job(*new)
    with Session(test_engine) as db:
        assert db.get(m.ProcessingJob, new[0]).state == "succeeded"


def test_real_video_probe_range_and_pose_persistence(lab, tmp_path):
    if not shutil.which("ffmpeg"):
        pytest.skip("FFmpeg is provided by the API container; run this check there")
    client, _ = lab
    clip = tmp_path / "blank.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x180:d=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(clip),
        ],
        check=True,
    )
    sid = create(client)
    uploaded = client.post(
        f"/api/v1/sessions/{sid}/videos", files={"file": ("blank.mp4", clip.read_bytes(), "video/mp4")}
    )
    assert uploaded.status_code == 202, uploaded.text
    run_one()
    video = client.get(f"/api/v1/sessions/{sid}").json()["videos"][0]
    assert video["status"] == "ready", video
    ranged = client.get(f"/api/v1/videos/{video['id']}/content", headers={"range": "bytes=0-99"})
    assert ranged.status_code == 206 and len(ranged.content) == 100
    track = client.post(
        f"/api/v1/videos/{video['id']}/pose-tracks",
        json={"runtime_version": "test", "model_sha256": "a" * 64, "executor": "worker"},
    ).json()
    batch = {
        "frames": [
            {"t_video_us": 0, "landmarks": [], "world_landmarks": []},
            {"t_video_us": 100000, "landmarks": [], "world_landmarks": []},
        ]
    }
    endpoint = f"/api/v1/pose-tracks/{track['id']}/batches/0"
    assert client.put(endpoint, json=batch).status_code == 200
    assert client.put(endpoint, json=batch).status_code == 200
    assert client.put(endpoint, json={"frames": [{"t_video_us": 200000, "landmarks": []}]}).status_code == 409
    complete = client.post(f"/api/v1/pose-tracks/{track['id']}/complete")
    assert complete.status_code == 200, complete.text
    assert complete.json()["quality"]["detected_frames"] == 0
    assert len(client.get(f"/api/v1/pose-tracks/{track['id']}/frames").json()["frames"]) == 2


def test_deletion_fences_a_claimed_job_before_it_publishes(lab):
    client, test_engine = lab
    sid = create(client)
    client.post(f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", demo_csv())})
    claimed = jobs.claim_job()
    deleted = client.delete(f"/api/v1/sessions/{sid}")
    jobs.execute_job(*claimed)
    assert client.get(f"/api/v1/jobs/{claimed[0]}").json()["state"] == "cancelled"
    assert run_one()
    assert client.get(f"/api/v1/jobs/{deleted.json()['id']}").json()["state"] == "succeeded"
    with Session(test_engine) as db:
        assert not list(db.scalars(select(m.Artifact).where(m.Artifact.session_id == sid)))


def test_maintenance_preserves_referenced_and_unrelated_files(lab, monkeypatch):
    from rallysense import maintenance

    client, test_engine = lab
    sid = create(client)
    monkeypatch.setattr(maintenance, "engine", test_engine)
    monkeypatch.setattr(maintenance, "STORAGE_ROOT", storage.STORAGE_ROOT)
    with Session(test_engine) as db, db.begin():
        artifact = storage.put_bytes(db, sid, b"retained", "raw_csv")
        retained = storage.resolve(artifact.storage_key)
    directory = storage.resolve(sid)
    orphan = directory / str(uuid4())
    orphan.write_bytes(b"uncommitted orphan")
    unrelated = directory / "notes.txt"
    unrelated.write_text("Never remove unrelated files")
    for path in [retained, orphan, unrelated]:
        os.utime(path, (time.time() - 25 * 3600, time.time() - 25 * 3600))
    maintenance.reconcile_storage()
    assert retained.read_bytes() == b"retained"
    assert unrelated.exists()
    assert not orphan.exists()
