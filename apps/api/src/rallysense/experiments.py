"""Research jobs reuse immutable input artifacts, never recording-sized copies."""

import hashlib
from pathlib import Path
import pyarrow.parquet as pq
from . import models as m
from .errors import DomainError
from .storage import path_for
from .research_schemas import ExperimentCreate
from .research import detect_imu, detect_video, associate, corrupt, evaluate

ALGORITHMS = {
    "imu": "imu_motion_window@1.0.0",
    "video": "video_wrist_speed@1.0.0",
    "fusion": "multimodal_temporal_association@1.0.0",
}
EVENTS = {"imu": "gyro_peak_v1", "video": "wrist_speed_peak_v1", "fusion": "multimodal_association_v1"}


def implementation_hash():
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for name in ["research.py", "research_schemas.py", "experiments.py", "signals.py"]:
        digest.update(name.encode())
        digest.update((root / name).read_bytes())
    return digest.hexdigest()


def check_comparison(request, reference, dataset_kind):
    meta = reference.manifest
    if request.comparison == "synthetic_fixture":
        if meta["provenance"] != "synthetic" or dataset_kind != "synthetic":
            raise DomainError(
                "Fixture scoring requires synthetic session and generated references",
                "INCOMPATIBLE_REFERENCE",
            )
        return "synthetic software verification; not real-world accuracy"
    if meta["provenance"] != "human" or not meta["independent"]:
        raise DomainError("Scoring requires independently declared human references", "INELIGIBLE_REFERENCE")
    if request.comparison == "exact" and meta["event_type"] != EVENTS[request.mode]:
        raise DomainError(
            "Event definitions differ. Declare an explicit proxy hypothesis or choose matching labels.",
            "INCOMPATIBLE_REFERENCE",
        )
    if request.comparison == "proxy_hypothesis" and meta["event_type"] not in (
        "swing_apex_v1",
        "movement_reference",
    ):
        raise DomainError(
            "Proxy hypotheses support operational human movement or extension references only",
            "INCOMPATIBLE_REFERENCE",
        )
    return f"{dataset_kind} dataset with declared independent human labels; no real-world accuracy claim from synthetic inputs; generalization unverified"


def compute_experiment(db, experiment):
    manifest = experiment.manifest
    request = ExperimentCreate.model_validate(manifest["request"])
    if manifest["implementation_sha256"] != implementation_hash():
        raise DomainError(
            "Implementation changed since enqueue; create a new experiment", "IMPLEMENTATION_CHANGED"
        )
    table, frames = None, None
    for key in ["sensor", "pose"]:
        if key in manifest["inputs"]:
            asset = manifest["inputs"][key]
            path = path_for(db, asset["artifact_id"], experiment.session_id)
            if hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
                raise DomainError("Input artifact checksum differs from frozen manifest", "INPUT_CHANGED")
            loaded = pq.read_table(path)
            if key == "sensor":
                table = loaded
            else:
                frames = loaded.to_pylist()
    table, frames, corruption = corrupt(table, frames, request.corruption)
    outputs = {}
    if request.mode in ("imu", "fusion"):
        outputs["imu"] = detect_imu(
            table, request.imu, manifest["sync"]["offset_us"] + request.corruption.sync_error_us
        )
    if request.mode in ("video", "fusion"):
        outputs["video"] = detect_video(
            frames, request.video, manifest["session"]["handedness"], manifest["inputs"]["pose"]["aspect"]
        )
    if request.mode == "fusion":
        output = associate(outputs["imu"], outputs["video"], request.association_tolerance_us)
    else:
        output = outputs[request.mode]
    all_events = output["events"]
    events = [
        {**e, "id": f"event-{i}"}
        for i, e in enumerate(all_events)
        if request.start_us <= e["t_session_us"] <= request.end_us
    ]
    result = {
        **output,
        "events": events,
        "outside_interval_predictions": len(all_events) - len(events),
        "components": outputs,
        "corruption": corruption,
        "evaluation": None,
        "evaluation_note": "No frozen independent reference; accuracy is unavailable.",
    }
    clipped = sorted(
        (max(request.start_us, i["start_us"]), min(request.end_us, i["end_us"]))
        for i in output["eligible_intervals"]
        if max(request.start_us, i["start_us"]) < min(request.end_us, i["end_us"])
    )
    merged = []
    for start, end in clipped:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    observed = sum(end - start for start, end in merged)
    result["coverage"] = {
        "eligible_us": observed,
        "declared_interval_us": request.end_us - request.start_us,
        "fraction": observed / (request.end_us - request.start_us),
        "rule": "Full declared interval is scored; unobserved reference events remain misses.",
    }
    if not observed:
        raise DomainError("No usable observations in the declared evaluation interval", "NO_OVERLAP")
    # Full declared interval: loss of coverage does not erase missed references.
    if experiment.reference_id:
        reference = db.get(m.ReferenceSnapshot, experiment.reference_id)
        refs = [e for e in reference.events if request.start_us <= e["t_session_us"] <= request.end_us]
        result["references"] = refs
        result["evaluation"] = evaluate(events, refs, request.tolerance_us, request.end_us - request.start_us)
        result["evaluation_note"] = manifest["evaluation_eligibility"]
        result["excluded_reference_count"] = len(reference.events) - len(refs)
    return result


def report_markdown(experiment):
    import json

    mft, result = experiment.manifest, experiment.result
    return "\n".join(
        [
            f"# {experiment.name}",
            "",
            f"Experiment: `{experiment.id}` · state: **{experiment.status}**",
            "",
            "## Research question",
            mft["request"]["research_question"],
            "",
            "## Evidence and provenance",
            f"Dataset: **{mft['session']['dataset_kind']}**. {result.get('evaluation_note', 'Not evaluated.')}",
            "No cross-player generalization, racket impact timing, or calibrated model confidence is established.",
            "",
            "## Frozen manifest",
            "```json",
            json.dumps(mft, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Actual stored results",
            "```json",
            json.dumps(result, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Failure",
            experiment.error or "No recorded processing failure.",
            "",
            "## Reproduction",
            "Start the local Compose stack, retain the source artifacts identified above, and POST the manifest request",
            f"to `/api/v1/sessions/{experiment.session_id}/experiments` with `force_rerun: true`.",
            "Use the same implementation and dependency hashes. A changed runtime creates a distinct fingerprint.",
            "",
            "## Limitations",
            "This is a per-session observation experiment. Synthetic and artificially corrupted inputs verify software behavior, not tennis accuracy.",
            "Declared pairing, annotation independence, placement and alignment are user attestations, not automatically verified facts.",
        ]
    )
