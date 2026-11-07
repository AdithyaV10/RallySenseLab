"""Run real local synthetic experiments; never claim athlete accuracy."""
import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="docs/evidence/step3-local-verification.json")
args = parser.parse_args()

base = "http://127.0.0.1:3000"


def checked(response):
    response.raise_for_status()
    return response.json()


with httpx.Client(base_url=base, headers={"x-lab-client": "rallysense"}, timeout=20) as client:
    demo = checked(client.post("/api/v1/research-demo-sessions"))
    sid = demo["id"]
    for _ in range(100):
        detail = checked(client.get(f"/api/v1/sessions/{sid}"))
        if detail["poses"] and detail["sensors"]:
            break
        time.sleep(.3)
    else:
        raise AssertionError("Paired fixture did not become ready")
    assert detail["dataset_kind"] == "synthetic"
    sensor, pose, sync = detail["sensors"][0], detail["poses"][0], detail["syncs"][0]
    assert sensor["samples"] == 801
    assert pose["config"]["provenance"] == "generated_analytical_landmarks"
    label_set = next(s for s in checked(client.get(f"/api/v1/sessions/{sid}/annotation-sets")) if s["provenance"] == "synthetic")
    reference = checked(client.post(f"/api/v1/annotation-sets/{label_set['id']}/freeze", json={
        "revision":label_set["revision"],"event_type":"synthetic_reference",
        "definition":"Analytical Gaussian pulse centers at 2 and 5 seconds on the generated fixture clock.",
        "labeler":"fixture-generator","procedure":"Programmatically generated centers; software verification only, not independent athlete labels.",
        "independent":False,"video_id":detail["videos"][0]["id"],
    }))
    summaries=[]
    conditions=[
        ("IMU clean","imu",{}), ("Video clean","video",{}), ("Fusion clean","fusion",{}),
        ("IMU dropout 20%","imu",{"dropout_fraction":.2}),
        ("IMU gyro noise 0.3 rad/s","imu",{"gyro_noise_sd":.3}),
        ("IMU acceleration noise 1 m/s2","imu",{"acceleration_noise_sd":1}),
        ("IMU timestamp jitter 40%","imu",{"timestamp_jitter_fraction":.4}),
        ("IMU missing window","imu",{"imu_gap_start_s":1.5,"imu_gap_duration_s":1}),
        ("Fusion wrist occlusion","fusion",{"occlusion_start_s":1.5,"occlusion_duration_s":1}),
        ("Fusion offset +1 second","fusion",{"sync_error_us":1_000_000}),
        ("Video full occlusion","video",{"occlusion_duration_s":8}),
    ]
    for name,mode,recipe in conditions:
        payload={"name":name,"research_question":"How do controlled observation failures change this paired numerical fixture?",
                 "mode":mode,"end_us":8_000_000,"reference_id":reference["id"],"comparison":"synthetic_fixture",
                 "corruption":{"seed":42,**recipe}}
        if mode != "video":
            payload.update(sensor_id=sensor["id"],sync_id=sync["id"])
        if mode != "imu":
            payload["pose_id"]=pose["id"]
        if mode == "fusion":
            payload.update(pairing="synthetic_fixture",alignment_note="Known analytical generator clock; not a physically recorded tennis alignment.")
        exp=checked(client.post(f"/api/v1/sessions/{sid}/experiments",json=payload))
        for _ in range(200):
            exp=checked(client.get(f"/api/v1/experiments/{exp['id']}"))
            if exp["status"] in ("succeeded","failed","cancelled"):
                break
            time.sleep(.15)
        else:
            raise AssertionError(f"Experiment timed out: {name}")
        result=exp["result"]
        summaries.append({"name":name,"mode":mode,"id":exp["id"],"fingerprint":exp["fingerprint"],
                          "status":exp["status"],"events":len(result["events"]),"metrics":result["evaluation"],
                          "processing_ms":result["processing_ms"],"recipe":recipe,"error":exp["error"],
                          "quality":result.get("quality"),"coverage":result.get("coverage")})
    by_name={r["name"]:r for r in summaries}
    assert all(by_name[name]["events"] == 2 and by_name[name]["status"] == "succeeded" for name in ["IMU clean","Video clean","Fusion clean"])
    assert by_name["Fusion offset +1 second"]["metrics"]["fn"] == 2
    assert by_name["Fusion offset +1 second"]["events"] == 0
    assert by_name["Video full occlusion"]["status"] == "failed"
    after=checked(client.get(f"/api/v1/sessions/{sid}"))
    assert after["sensors"][0] == sensor and after["poses"][0] == pose
    report=client.get(f"/api/v1/experiments/{by_name['Fusion clean']['id']}/report")
    report.raise_for_status()
    assert "synthetic software verification" in report.text
    original_meta=checked(client.post("/api/v1/demo-sessions"))
    for _ in range(100):
        original=checked(client.get(f"/api/v1/sessions/{original_meta['id']}"))
        if original["sensors"] and original["sensors"][0]["status"] == "ready":
            break
        time.sleep(.2)
    assert original["sensors"][0]["samples"] == 1801
    original_samples=checked(client.get(f"/api/v1/sensor-recordings/{original['sensors'][0]['id']}/samples",params={"max_points":20}))
    assert original_samples["source_count"] == 1801
    evidence={"verified_at_utc":datetime.now(UTC).isoformat(),"base_url":base,
              "evidence_level":"synthetic software verification only; no real-world accuracy study",
              "session_id":sid,"reference_id":reference["id"],"original_step2_demo_id":original["id"],
              "original_step2_samples":1801,"sources_unchanged":True,"report_http":report.status_code,"experiments":summaries}
    evidence["original_step2_parquet_samples_read"]=original_samples["source_count"]
    target=Path(__file__).resolve().parents[1]/args.output
    target.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"evidence_file":str(target),"session_id":sid,"original_step2_samples":1801,
                      "sources_unchanged":True,"experiments":[{k:r[k] for k in ["name","status","events","processing_ms"]} for r in summaries]},indent=2))
