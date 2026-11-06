import json
from sqlalchemy.orm import Session
from rallysense import models as m
from rallysense.jobs import finalize_pose
from rallysense.worker import run_one
from rallysense.signals import demo_csv
from test_integration import lab, create  # noqa: F401
from test_research import pose_fixture
import pytest
import shutil


def sensor_input(client, sid):
    response = client.post(
        f"/api/v1/sessions/{sid}/sensor-imports",
        files={"file": ("synthetic.csv", demo_csv())},
        data={"mapping": json.dumps({"provenance": "synthetic"})},
    )
    assert response.status_code == 202
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{sid}").json()
    return detail["sensors"][0]["id"], detail["syncs"][0]["id"]


def test_frozen_labels_experiments_reruns_and_safe_deletion(lab):  # noqa: F811
    client, _ = lab
    sid = create(client)
    sensor, sync = sensor_input(client, sid)
    label = client.post(
        f"/api/v1/sessions/{sid}/annotations", json={"event_type": "gyro_peak_v1", "t_session_us": 2_200_000}
    ).json()
    labels = client.get(f"/api/v1/sessions/{sid}/annotation-sets").json()[0]
    body = {
        "revision": labels["revision"],
        "event_type": "gyro_peak_v1",
        "definition": "Filtered angular-speed maximum",
        "labeler": "test-fixture-author",
        "procedure": "Analytical fixture label for software verification only",
        "independent": True,
    }
    frozen = client.post(f"/api/v1/annotation-sets/{labels['id']}/freeze", json=body)
    assert frozen.status_code == 201, frozen.text
    ref = frozen.json()
    request = {"mode": "imu", "sensor_id": sensor, "sync_id": sync, "reference_id": ref["id"]}
    response = client.post(f"/api/v1/sessions/{sid}/experiments", json=request)
    assert response.status_code == 202, response.text
    exp = response.json()
    assert run_one()
    result = client.get(f"/api/v1/experiments/{exp['id']}").json()
    assert result["status"] == "succeeded", result
    assert len(result["result"]["events"]) == 5
    assert result["result"]["evaluation"]["tp"] == 1
    assert result["result"]["evaluation"]["fp"] == 4
    assert result["result"]["processing_ms"] >= 0
    assert client.post(f"/api/v1/sessions/{sid}/experiments", json=request).json()["id"] == exp["id"]
    updated = client.patch(f"/api/v1/annotations/{label['id']}", json={**label, "t_session_us": 3_000_000})
    assert updated.status_code == 200
    assert client.post(f"/api/v1/annotation-sets/{labels['id']}/freeze", json=body).status_code == 409
    assert (
        client.get(f"/api/v1/sessions/{sid}/references").json()[0]["events"][0]["t_session_us"] == 2_200_000
    )
    rerun = client.post(f"/api/v1/sessions/{sid}/experiments", json={**request, "force_rerun": True}).json()
    assert rerun["id"] != exp["id"] and run_one()
    assert (
        client.get(f"/api/v1/experiments/{rerun['id']}").json()["result"]["events"]
        == result["result"]["events"]
    )
    assert client.get(f"/api/v1/experiments/{exp['id']}").json() == result
    report = client.get(f"/api/v1/experiments/{exp['id']}/report")
    assert report.status_code == 200 and "synthetic" in report.text
    assert '"tp": 1' in report.text and '"fp": 4' in report.text
    assert exp["id"] in report.text and "not tennis accuracy" in report.text
    incompatible = client.post(
        f"/api/v1/sessions/{sid}/annotations", json={"t_session_us": 2_000_000, "event_type": "swing_apex_v1"}
    )
    assert incompatible.status_code == 201
    labels = client.get(f"/api/v1/sessions/{sid}/annotation-sets").json()[0]
    ref2 = client.post(
        f"/api/v1/annotation-sets/{labels['id']}/freeze",
        json={**body, "revision": labels["revision"], "event_type": "swing_apex_v1"},
    ).json()
    rejected = client.post(
        f"/api/v1/sessions/{sid}/experiments", json={**request, "reference_id": ref2["id"]}
    )
    assert rejected.status_code == 422
    accepted = client.post(
        f"/api/v1/sessions/{sid}/experiments",
        json={
            **request,
            "reference_id": ref2["id"],
            "comparison": "proxy_hypothesis",
            "hypothesis": "Gyro peaks are hypothesized proxies for visible wrist extension.",
        },
    )
    assert accepted.status_code == 202 and run_one()
    assert client.delete(f"/api/v1/sessions/{sid}").status_code == 202 and run_one()
    assert client.get(f"/api/v1/experiments/{exp['id']}").status_code == 404


def test_stored_pose_fusion_corruption_failure_and_ownership(lab):  # noqa: F811
    client, engine = lab
    sid = create(client, "Generated paired numerical fixture")
    sensor, sync = sensor_input(client, sid)
    with Session(engine) as db, db.begin():
        from rallysense.storage import put_bytes

        artifact = put_bytes(db, sid, b"explicit non-video test placeholder", "fixture_metadata")
        fixture_artifact_id = artifact.id
        video = m.VideoAsset(
            session_id=sid,
            artifact_id=fixture_artifact_id,
            name="Generated landmark fixture (not MediaPipe)",
            status="ready",
            duration_us=8_000_000,
            width=100,
            height=100,
            metadata_json={},
        )
        db.add(video)
        db.flush()
        pose = m.PoseTrack(
            session_id=sid, video_id=video.id, config={"provenance": "generated numerical fixture"}
        )
        db.add(pose)
        db.flush()
        finalize_pose(db, pose, pose_fixture())
        pose_id = pose.id
    body = {"mode": "video", "pose_id": pose_id, "end_us": 8_000_000}
    video_run = client.post(f"/api/v1/sessions/{sid}/experiments", json=body)
    assert video_run.status_code == 202 and run_one()
    result = client.get(f"/api/v1/experiments/{video_run.json()['id']}").json()
    assert len(result["result"]["events"]) == 2 and result["result"]["evaluation"] is None
    # A second clip is a separate visual clock, even inside the same session.
    with Session(engine) as db, db.begin():
        other_video = m.VideoAsset(
            session_id=sid,
            artifact_id=fixture_artifact_id,
            name="Other generated fixture",
            status="ready",
            duration_us=8_000_000,
            width=100,
            height=100,
            metadata_json={},
        )
        db.add(other_video)
        db.flush()
        other_video_id = other_video.id
    labels = client.get(f"/api/v1/sessions/{sid}/annotation-sets").json()[0]
    mismatched_ref = client.post(
        f"/api/v1/annotation-sets/{labels['id']}/freeze",
        json={
            "revision": labels["revision"],
            "event_type": "wrist_speed_peak_v1",
            "definition": "Visible image wrist speed maximum",
            "labeler": "software-test",
            "procedure": "Empty numerical API fixture for source mismatch verification",
            "independent": True,
            "video_id": other_video_id,
        },
    ).json()
    mismatch = client.post(
        f"/api/v1/sessions/{sid}/experiments", json={**body, "reference_id": mismatched_ref["id"]}
    )
    assert mismatch.status_code == 422 and mismatch.json()["error"]["code"] == "INCOMPATIBLE_REFERENCE"
    fusion = {
        **body,
        "mode": "fusion",
        "sensor_id": sensor,
        "sync_id": sync,
        "pairing": "synthetic_fixture",
        "alignment_note": "Shared generated fixture clock; no recorded tennis claim",
        "association_tolerance_us": 300_000,
    }
    paired = client.post(f"/api/v1/sessions/{sid}/experiments", json=fusion)
    assert paired.status_code == 202 and run_one()
    clean = client.get(f"/api/v1/experiments/{paired.json()['id']}").json()
    assert len(clean["result"]["events"]) == 2, clean
    corrupted = client.post(
        f"/api/v1/sessions/{sid}/experiments", json={**fusion, "corruption": {"sync_error_us": 1_000_000}}
    )
    assert corrupted.status_code == 202 and run_one()
    degraded = client.get(f"/api/v1/experiments/{corrupted.json()['id']}").json()
    assert degraded["status"] == "succeeded" and degraded["result"]["events"] == []
    bad = client.post(
        f"/api/v1/sessions/{sid}/experiments", json={**body, "corruption": {"occlusion_duration_s": 8}}
    )
    assert bad.status_code == 202 and run_one()
    failed = client.get(f"/api/v1/experiments/{bad.json()['id']}").json()
    assert failed["status"] == "failed" and "visible" in failed["error"]
    other = create(client)
    assert client.post(f"/api/v1/sessions/{other}/experiments", json=body).status_code == 409
    assert (
        client.post(f"/api/v1/sessions/{sid}/experiments", json={**fusion, "pairing": "unpaired"}).status_code
        == 422
    )
    with Session(engine) as db, db.begin():
        db.get(m.RecordingSession, sid).dataset_kind = "mixed"
    assert client.post(f"/api/v1/sessions/{sid}/experiments", json=fusion).status_code == 422


def test_generated_paired_demo_runs_real_pipeline(lab):  # noqa: F811
    if not shutil.which("ffmpeg"):
        pytest.skip("Generated fixture video requires container FFmpeg")
    client, _ = lab
    demo = client.post("/api/v1/research-demo-sessions").json()
    assert demo["dataset_kind"] == "synthetic"
    assert run_one()
    detail = client.get(f"/api/v1/sessions/{demo['id']}").json()
    assert detail["jobs"][0]["state"] == "succeeded", detail["jobs"]
    assert detail["poses"][0]["config"]["provenance"] == "generated_analytical_landmarks"
    video = client.get(f"/api/v1/videos/{detail['videos'][0]['id']}/content")
    assert video.status_code == 200 and video.headers["content-type"] == "video/mp4"
    request = {
        "mode": "fusion",
        "sensor_id": detail["sensors"][0]["id"],
        "sync_id": detail["syncs"][0]["id"],
        "pose_id": detail["poses"][0]["id"],
        "end_us": 8_000_000,
        "pairing": "synthetic_fixture",
        "alignment_note": "Generated shared clock, not athlete data",
    }
    run = client.post(f"/api/v1/sessions/{demo['id']}/experiments", json=request)
    assert run.status_code == 202 and run_one()
    result = client.get(f"/api/v1/experiments/{run.json()['id']}").json()
    assert result["status"] == "succeeded" and len(result["result"]["events"]) == 2
    assert client.post("/api/v1/research-demo-sessions").json()["id"] == demo["id"]


def test_experiment_cancellation_expired_lease_evaluation_and_comparison(lab):  # noqa: F811
    from datetime import timedelta
    from sqlalchemy import select
    from rallysense import jobs

    client, engine = lab
    sid = create(client)
    sensor, sync = sensor_input(client, sid)
    payload = {"mode": "imu", "sensor_id": sensor, "sync_id": sync}
    exp = client.post(f"/api/v1/sessions/{sid}/experiments", json=payload).json()
    with Session(engine) as db:
        job_id = db.scalar(select(m.ProcessingJob.id).where(m.ProcessingJob.target_id == exp["id"]))
    assert client.post(f"/api/v1/jobs/{job_id}/cancel").status_code == 200
    assert client.get(f"/api/v1/experiments/{exp['id']}").json()["status"] == "cancelled"
    exp = client.post(f"/api/v1/sessions/{sid}/experiments", json=payload).json()
    old_claim = jobs.claim_job()
    with Session(engine) as db, db.begin():
        db.get(m.ProcessingJob, old_claim[0]).lease_expires_at = m.now() - timedelta(seconds=1)
    replacement = jobs.claim_job()
    assert replacement[0] == old_claim[0] and replacement[1] != old_claim[1]
    jobs.execute_job(*old_claim)
    assert client.get(f"/api/v1/experiments/{exp['id']}").json()["status"] == "running"
    jobs.execute_job(*replacement)
    original = client.get(f"/api/v1/experiments/{exp['id']}").json()
    assert original["status"] == "succeeded" and original["result"]["evaluation"] is None
    label = client.post(
        f"/api/v1/sessions/{sid}/annotations", json={"event_type": "gyro_peak_v1", "t_session_us": 2_200_000}
    ).json()
    labels = client.get(f"/api/v1/sessions/{sid}/annotation-sets").json()[0]
    reference = client.post(
        f"/api/v1/annotation-sets/{labels['id']}/freeze",
        json={
            "revision": labels["revision"],
            "event_type": "gyro_peak_v1",
            "definition": "Known fixture angular maximum",
            "labeler": "software-test",
            "procedure": "Analytical fixture reference; no real-world validation",
            "independent": True,
        },
    ).json()
    invalid = client.post(
        f"/api/v1/experiments/{exp['id']}/evaluate",
        json={"reference_id": reference["id"], "comparison": "proxy_hypothesis"},
    )
    assert invalid.status_code == 422
    evaluated = client.post(
        f"/api/v1/experiments/{exp['id']}/evaluate", json={"reference_id": reference["id"]}
    )
    assert evaluated.status_code == 202 and run_one()
    evaluated = client.get(f"/api/v1/experiments/{evaluated.json()['id']}").json()
    assert evaluated["result"]["evaluation"]["tp"] == 1
    assert client.get(f"/api/v1/experiments/{exp['id']}").json() == original
    comparison = client.get(
        f"/api/v1/sessions/{sid}/experiment-comparison", params=[("ids", exp["id"]), ("ids", evaluated["id"])]
    )
    assert comparison.status_code == 200 and len(comparison.json()) == 2
    other = create(client)
    assert (
        client.get(f"/api/v1/sessions/{other}/experiment-comparison", params={"ids": exp["id"]}).status_code
        == 409
    )
    assert (
        client.patch(
            f"/api/v1/annotations/{label['id']}", json={**label, "t_session_us": 2_300_000}
        ).status_code
        == 200
    )


def test_commit_is_visible_before_http_success_and_commit_failure_is_not_success(lab):  # noqa: F811
    from fastapi.testclient import TestClient
    from sqlalchemy import select
    from rallysense.main import app
    from rallysense.db import get_db
    from rallysense.config import LOCAL_TOKEN
    from rallysense.errors import DomainError

    _, engine = lab
    visible_at_headers = []

    async def observed_app(scope, receive, send):
        async def observed_send(message):
            if message["type"] == "http.response.start" and scope["path"] == "/api/v1/sessions":
                with Session(engine) as db:
                    visible_at_headers.append(
                        db.scalar(
                            select(m.RecordingSession.id).where(
                                m.RecordingSession.title == "Commit visibility fixture"
                            )
                        )
                        is not None
                    )
            await send(message)

        await app(scope, receive, observed_send)

    with TestClient(observed_app, headers={"x-lab-token": LOCAL_TOKEN}) as client:
        response = client.post("/api/v1/sessions", json={"title": "Commit visibility fixture"})
        assert response.status_code == 201 and visible_at_headers == [True]
    original_override = app.dependency_overrides[get_db]

    def failing_commit():
        with Session(engine) as db:
            yield db
            raise DomainError("Injected transaction failure", "TRANSACTION_FAILED", 503)

    app.dependency_overrides[get_db] = failing_commit
    try:
        with TestClient(app, headers={"x-lab-token": LOCAL_TOKEN}) as client:
            response = client.post(
                "/api/v1/sessions", json={"title": "Must not acknowledge failed persistence"}
            )
            assert response.status_code == 503 and response.json()["error"]["code"] == "TRANSACTION_FAILED"
        with Session(engine) as db:
            assert (
                db.scalar(
                    select(m.RecordingSession.id).where(
                        m.RecordingSession.title == "Must not acknowledge failed persistence"
                    )
                )
                is None
            )
    finally:
        app.dependency_overrides[get_db] = original_override
