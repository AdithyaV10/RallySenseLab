"""Step 5.5 regressions use disposable PostgreSQL schemas and temporary storage."""

import copy
import errno
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from rallysense import config, main, models as m, storage
from rallysense.errors import DomainError
from rallysense.provenance import execution_environment
from rallysense.schemas import DetectorConfig
from rallysense.signals import detect_gyro
from rallysense.worker import run_one
from test_integration import lab, create  # noqa: F401
from test_research_integration import sensor_input


def test_readonly_worker_does_not_claim_queued_jobs(lab, monkeypatch):  # noqa: F811
    client, engine = lab
    sid = create(client)
    job = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", b"test")}
    ).json()
    monkeypatch.setattr(config, "APP_MODE", "demo_readonly")
    assert not run_one()
    with Session(engine) as db:
        assert db.get(m.ProcessingJob, job["id"]).state == "queued"


def test_workspace_request_budget_expires_without_spoofable_client_keys(monkeypatch):
    from rallysense import policy

    monkeypatch.setattr(policy, "_requests", policy.deque())
    monkeypatch.setattr(config, "MAX_REQUESTS_PER_MINUTE", 2)
    assert policy.request_allowed(0)
    assert policy.request_allowed(1)
    assert not policy.request_allowed(2)
    assert policy.request_allowed(60)


def test_failed_artifact_rename_cleans_partial_upload(lab, monkeypatch, tmp_path):  # noqa: F811
    client, engine = lab
    sid = create(client)

    def unavailable(*args):
        raise OSError(errno.ENOSPC, "temporary storage failure")

    monkeypatch.setattr(storage.os, "replace", unavailable)
    with pytest.raises(OSError):
        client.post(f"/api/v1/sessions/{sid}/sensor-imports", files={"file": ("fixture.csv", b"test")})
    assert not list(tmp_path.rglob("*.part"))
    with Session(engine) as db:
        assert not list(db.scalars(select(m.Artifact)))


@pytest.mark.parametrize("field", ["dependency_lock_sha256", "runtime", "implementation_sha256"])
def test_legacy_runtime_mismatch_fails_without_rewriting_manifest(lab, field):  # noqa: F811
    client, engine = lab
    sid = create(client)
    sensor, _ = sensor_input(client, sid)
    run = client.post(f"/api/v1/sessions/{sid}/inference-runs", json={"sensor_id": sensor}).json()
    with Session(engine) as db, db.begin():
        row = db.get(m.InferenceRun, run["id"])
        manifest = {**row.result["input_manifest"], field: "mismatched"}
        row.result = {"input_manifest": manifest}
    assert run_one()
    with Session(engine) as db:
        row = db.get(m.InferenceRun, run["id"])
        assert row.status == "failed"
        assert row.result["input_manifest"] == manifest
        assert row.result["executor"] == execution_environment()
        assert row.result["failure_code"] == (
            "IMPLEMENTATION_CHANGED" if field == "implementation_sha256" else "EXECUTION_ENVIRONMENT_MISMATCH"
        )
        assert not list(db.scalars(select(m.Prediction).where(m.Prediction.run_id == row.id)))


def test_matching_runtime_retains_deterministic_results_and_completed_history(lab):  # noqa: F811
    import pyarrow.parquet as pq

    client, engine = lab
    sid = create(client)
    sensor, sync = sensor_input(client, sid)
    payload = {"mode": "imu", "sensor_id": sensor, "sync_id": sync}
    first = client.post(f"/api/v1/sessions/{sid}/experiments", json=payload).json()
    assert run_one()
    frozen = copy.deepcopy(client.get(f"/api/v1/experiments/{first['id']}").json())
    assert frozen["status"] == "succeeded"
    assert frozen["result"]["executor"] == execution_environment()
    second = client.post(f"/api/v1/sessions/{sid}/experiments", json={**payload, "force_rerun": True}).json()
    assert run_one()
    again = client.get(f"/api/v1/experiments/{second['id']}").json()
    assert again["result"]["events"] == frozen["result"]["events"]
    assert client.get(f"/api/v1/experiments/{first['id']}").json() == frozen
    legacy = client.post(f"/api/v1/sessions/{sid}/inference-runs", json={"sensor_id": sensor}).json()
    assert run_one()
    with Session(engine) as db:
        row = db.get(m.InferenceRun, legacy["id"])
        recording = db.get(m.SensorRecording, sensor)
        table = pq.read_table(storage.path_for(db, recording.normalized_artifact_id, sid))
        expected = detect_gyro(table, DetectorConfig.model_validate(row.config), 0)
        actual = list(
            db.scalars(
                select(m.Prediction).where(m.Prediction.run_id == row.id).order_by(m.Prediction.t_session_us)
            )
        )
        assert [p.t_session_us for p in actual] == [p["t_session_us"] for p in expected["events"]]
        assert [p.magnitude for p in actual] == [p["magnitude"] for p in expected["events"]]
        assert row.result["executor"] == execution_environment()


def test_staged_pose_18000_frames_retry_conflict_missing_and_monotonic(lab):  # noqa: F811
    client, engine = lab
    sid = create(client)
    with Session(engine) as db, db.begin():
        artifact = storage.put_bytes(db, sid, b"metadata fixture; not model evidence", "fixture")
        video = m.VideoAsset(
            session_id=sid,
            artifact_id=artifact.id,
            name="capacity",
            status="ready",
            width=160,
            height=120,
            duration_us=600_000_000,
        )
        db.add(video)
        db.flush()
        vid = video.id
    started = client.post(
        f"/api/v1/videos/{vid}/pose-tracks",
        json={
            "runtime_version": "capacity test",
            "model_sha256": "a" * 64,
            "executor": "worker",
            "sample_target_hz": 30,
        },
    ).json()
    tid = started["id"]
    # Real 33-landmark schema through ordinary staged API, not direct finalization.
    points = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0} for _ in range(33)]
    for j in [11, 12]:
        points[j]["y"] = 0.25
    for j in [23, 24]:
        points[j]["y"] = 0.75
    for batch in range(90):
        frames = [{"t_video_us": (batch * 200 + i) * 33333, "landmarks": points} for i in range(200)]
        endpoint = f"/api/v1/pose-tracks/{tid}/batches/{batch}"
        assert client.put(endpoint, json={"frames": frames}).status_code == 200
        if batch == 0:
            assert client.put(endpoint, json={"frames": frames}).status_code == 200
            altered = copy.deepcopy(frames)
            altered[0]["landmarks"][0]["x"] = 0.6
            assert client.put(endpoint, json={"frames": altered}).status_code == 409
            assert client.put(endpoint + "1", json={"frames": [frames[1], frames[0]]}).status_code == 422
        if batch == 1:
            assert (
                client.post(
                    f"/api/v1/pose-tracks/{tid}/complete", json={"expected_frames": 18_000}
                ).status_code
                == 409
            )
    completed = client.post(f"/api/v1/pose-tracks/{tid}/complete", json={"expected_frames": 18_000})
    assert completed.status_code == 200, completed.text
    assert completed.json()["quality"]["processed_frames"] == 18_000
    assert client.post(f"/api/v1/pose-tracks/{tid}/complete").json() == completed.json()
    window = client.get(f"/api/v1/pose-tracks/{tid}/frames?start_us=590000000&max_frames=5000").json()
    assert window["frames"] and window["frames"][-1]["t_video_us"] == 17999 * 33333
    other = client.post(
        f"/api/v1/videos/{vid}/pose-tracks",
        json={"runtime_version": "test", "model_sha256": "a" * 64, "executor": "worker"},
    ).json()["id"]
    assert (
        client.put(
            f"/api/v1/pose-tracks/{other}/batches/1", json={"frames": [{"t_video_us": 100, "landmarks": []}]}
        ).status_code
        == 200
    )
    assert client.post(f"/api/v1/pose-tracks/{other}/complete").status_code == 409


@pytest.mark.parametrize("failure", ["permissions", "disk_full", "readback"])
def test_writable_readiness_rejects_storage_failure_without_paths(lab, monkeypatch, tmp_path, failure):  # noqa: F811
    _, engine = lab
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "STORAGE_ROOT", tmp_path)
    if failure == "disk_full":
        monkeypatch.setattr(main.shutil, "disk_usage", lambda _: SimpleNamespace(free=0))
    else:

        def broken(**kwargs):
            raise OSError(errno.EACCES if failure == "permissions" else errno.EIO, "private path")

        monkeypatch.setattr(main.tempfile, "NamedTemporaryFile", broken)
    with pytest.raises(DomainError) as error:
        main.ready()
    assert error.value.code == "NOT_READY" and error.value.status == 503
    assert "private path" not in error.value.message
    assert not list(tmp_path.glob(".ready-*"))


def test_readiness_modes_read_actual_approved_fixture_and_clean_probe(lab, monkeypatch, tmp_path):  # noqa: F811
    client, engine = lab
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "STORAGE_ROOT", tmp_path)
    assert main.ready() == {"status": "ready"}
    assert not list(tmp_path.glob(".ready-*"))
    sid = client.post("/api/v1/research-demo-sessions").json()["id"]
    assert run_one()
    monkeypatch.setattr(config, "APP_MODE", "demo_readonly")
    monkeypatch.setattr(config, "DEMO_SESSION_IDS", {sid})
    monkeypatch.setattr(
        main.tempfile, "NamedTemporaryFile", lambda **_: pytest.fail("Readonly readiness must not write")
    )
    assert main.ready() == {"status": "ready"}
    with Session(engine) as db:
        artifact = db.scalars(select(m.Artifact).where(m.Artifact.session_id == sid)).first()
        storage.resolve(artifact.storage_key).unlink()  # Only this disposable-schema fixture.
    with pytest.raises(DomainError, match="unavailable"):
        main.ready()


def test_chunked_body_limit_is_413_and_malformed_upload_creates_no_source(lab, monkeypatch):  # noqa: F811
    client, engine = lab
    sid = create(client)
    parts = [
        b'--absent\r\nContent-Disposition: form-data; name="file"; filename="test.csv"\r\nContent-Type: text/csv\r\n\r\n',
        *([b"x" * (1024 * 1024)] * 52),
        b"\r\n--absent--\r\n",
    ]
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports",
        content=iter(parts),
        headers={"content-type": "multipart/form-data; boundary=absent"},
    )
    assert response.status_code == 413, response.text
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports",
        content=b"broken",
        headers={"content-type": "multipart/form-data; boundary=absent"},
    )
    assert response.status_code in {400, 422}
    with Session(engine) as db:
        assert not list(db.scalars(select(m.SensorRecording)))
        assert not list(db.scalars(select(m.Artifact)))
