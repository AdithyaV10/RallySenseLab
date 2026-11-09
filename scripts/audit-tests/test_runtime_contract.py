"""Deployment-blocker regression: a changed worker runtime must reject a frozen job.

Original Step 5 failure is retained in historical evidence; Step 5.5 repaired it.
Keep these assertions as a separate release regression gate.
"""

import pytest
from rallysense import models as m
from rallysense.worker import run_one
from sqlalchemy.orm import Session
from test_integration import create, lab  # noqa: F401
from test_research_integration import sensor_input


@pytest.mark.parametrize("field", ["dependency_lock_sha256", "runtime"])
def test_worker_rejects_mismatched_enqueue_environment(lab, field):  # noqa: F811
    client, engine = lab
    sid = create(client)
    sensor, sync = sensor_input(client, sid)
    response = client.post(
        f"/api/v1/sessions/{sid}/experiments",
        json={"mode": "imu", "sensor_id": sensor, "sync_id": sync},
    )
    assert response.status_code == 202
    eid = response.json()["id"]
    with Session(engine) as db, db.begin():
        exp = db.get(m.Experiment, eid)
        # Simulate a job enqueued by a different API environment without changing live packages.
        exp.manifest = {
            **exp.manifest,
            field: "0" * 64
            if field == "dependency_lock_sha256"
            else {
                "numpy": "audit-other-runtime",
                "scipy": "audit-other-runtime",
                "pyarrow": "audit-other-runtime",
            },
        }
    assert run_one()
    result = client.get(f"/api/v1/experiments/{eid}").json()
    assert result["status"] == "failed", (
        "Worker published results under a mismatched frozen environment"
    )
