import copy
import itertools
import math
import numpy as np
import pytest
from rallysense.research import match_events, evaluate, detect_video, detect_imu, associate, corrupt
from rallysense.research_schemas import VideoConfig, Corruption
from rallysense.schemas import DetectorConfig, SensorMapping
from rallysense.signals import normalize_csv, demo_csv
from rallysense.errors import DomainError


def events(times):
    return [{"t_session_us": t} for t in times]


def pose_fixture():
    """Analytical wrist displacement: integrated Gaussian speed pulses.

    Fixed torso length .4, aspect 1. Expected speed maxima at 2 and 5 seconds.
    These are generated landmarks, NOT MediaPipe outputs.
    """
    frames = []
    for i in range(241):
        t = i / 30
        dx = sum(0.12 * math.erf((t - center) / 0.18) for center in [2, 5])
        points = [{"x": 0.5, "y": 0.5, "z": 0, "visibility": 0.9} for _ in range(33)]
        for idx, xy in {
            11: (0.4, 0.4),
            12: (0.6, 0.4),
            23: (0.4, 0.8),
            24: (0.6, 0.8),
            16: (0.7 + dx, 0.4),
        }.items():
            points[idx].update(x=xy[0], y=xy[1])
        frames.append({"t_video_us": round(t * 1e6), "landmarks": points, "world_landmarks": []})
    return frames


def test_matching_adversarial_cardinality_and_metrics():
    p, r = events([0, 80_000]), events([60_000, 140_000])
    assert match_events(p, r, 70_000) == [(0, 0), (1, 1)]
    score = evaluate(p, r, 70_000, 1_000_000)
    assert (score["tp"], score["fp"], score["fn"]) == (2, 0, 0)
    assert score["f1"] == score["precision"] == score["recall"] == 1
    assert score["mean_absolute_error_us"] == score["median_absolute_error_us"] == 60_000
    assert score["mean_signed_error_us"] == -60_000


def test_matching_exhaustive_small_cases_against_brute_force():
    # Independent enumeration verifies both objective levels, not an implementation snapshot.
    for p_times in itertools.combinations(range(5), 3):
        for r_times in itertools.combinations(range(5), 2):
            possibilities = [(0, 0)]
            for count in [1, 2]:
                for pi in itertools.combinations(range(3), count):
                    for ri in itertools.permutations(range(2), count):
                        errors = [abs(p_times[a] - r_times[b]) for a, b in zip(pi, ri)]
                        if max(errors) <= 1:
                            possibilities.append((count, -sum(errors)))
            pairs = match_events(events(p_times), events(r_times), 1)
            actual = (len(pairs), -sum(abs(p_times[a] - r_times[b]) for a, b in pairs))
            assert actual == max(possibilities)


def test_matching_empty_duplicates_ties_shift_and_permutation():
    assert match_events(events([1, 1]), events([1]), 0) == [(1, 0)]
    empty = evaluate([], [], 0, 1)
    assert empty["f1"] is empty["recall"] is empty["precision"] is None
    miss = evaluate([], events([1]), 1, 100)
    assert miss["fn"] == 1 and miss["f1"] == 0 and miss["recall"] == 0
    false = evaluate(events([1]), [], 1, 100)
    assert false["fp"] == 1 and false["precision"] == 0 and false["recall"] is None
    a = evaluate(events([20, 0]), events([2, 22]), 2, 100)
    b = evaluate(events([100, 120]), events([122, 102]), 2, 100)
    assert a["tp"] == b["tp"] == 2 and a["mean_absolute_error_us"] == b["mean_absolute_error_us"] == 2


def test_video_analytical_speed_and_event_timing():
    frames = pose_fixture()
    original = copy.deepcopy(frames)
    result = detect_video(frames, VideoConfig())
    assert [e["t_session_us"] for e in result["events"]] == pytest.approx([2e6, 5e6], abs=60_000)
    # d(.12 erf((t-c)/.18)) / dt divided by .4 gives peak ~1.88 torso units/s.
    assert result["events"][0]["magnitude"] == pytest.approx(
        0.12 * 2 / math.sqrt(math.pi) / 0.18 / 0.4, rel=0.12
    )
    assert frames == original
    assert all(e["event_type"] == "wrist_speed_peak_v1" for e in result["events"])


def test_video_occlusion_splits_derivatives_and_sparse_input_abstains():
    _, frames, summary = corrupt(
        None, pose_fixture(), Corruption(occlusion_start_s=1.5, occlusion_duration_s=1)
    )
    result = detect_video(frames, VideoConfig())
    assert len(result["events"]) == 1 and result["events"][0]["t_session_us"] > 4e6
    assert summary["occluded_frames"] == 30
    with pytest.raises(DomainError, match="segment"):
        detect_video(pose_fixture()[::10], VideoConfig())
    with pytest.raises(DomainError, match="visible"):
        detect_video([{"t_video_us": 0, "landmarks": []}], VideoConfig())


def test_video_translation_invariance_and_parameter_sensitivity():
    frames = pose_fixture()
    baseline = detect_video(frames, VideoConfig())
    for frame in frames:
        for p in frame["landmarks"]:
            p["x"] += 0.2
            p["y"] += 0.1
    shifted = detect_video(frames, VideoConfig())
    assert [e["t_session_us"] for e in baseline["events"]] == [e["t_session_us"] for e in shifted["events"]]
    assert detect_video(frames, VideoConfig(threshold=100))["events"] == []


def test_imu_window_and_quality_keep_legacy_peak_definition():
    table, _ = normalize_csv(demo_csv(), SensorMapping())
    result = detect_imu(table, DetectorConfig(), 100_000)
    assert len(result["events"]) == 5
    for e in result["events"]:
        assert e["window_start_us"] < e["t_session_us"] < e["window_end_us"]
        assert 150_000 <= e["duration_us"] <= 300_000
        assert e["acceleration_peak_m_s2"] > 9
    assert result["quality"]["availability_fraction"] == 1


def test_fusion_uses_both_modalities_preserves_anchor_and_unmatched():
    imu = {
        "events": [{**e, "magnitude": 2, "prominence": 1} for e in events([100, 300, 700])],
        "eligible_intervals": [{"start_us": 0, "end_us": 1000}],
    }
    video = {
        "events": [{**e, "magnitude": 3} for e in events([120, 320])],
        "eligible_intervals": [{"start_us": 0, "end_us": 1000}],
    }
    result = associate(imu, video, 30)
    assert [e["t_session_us"] for e in result["events"]] == [100, 300]
    assert result["quality"]["unmatched_imu"] == [2]
    assert result["events"][0]["disagreement_us"] == 20
    assert associate(imu, {**video, "events": []}, 30)["events"] == []
    assert associate(imu, video, 10)["events"] == []
    with pytest.raises(DomainError, match="common"):
        associate(imu, {**video, "eligible_intervals": [{"start_us": 2000, "end_us": 3000}]}, 30)


def test_corruption_determinism_preserves_originals_and_time_order():
    table, _ = normalize_csv(demo_csv(), SensorMapping())
    frames = pose_fixture()
    original = copy.deepcopy(frames)
    recipe = Corruption(
        dropout_fraction=0.2,
        gyro_noise_sd=0.3,
        acceleration_noise_sd=0.1,
        timestamp_jitter_fraction=0.4,
        imu_gap_start_s=7,
        imu_gap_duration_s=2,
        occlusion_start_s=1,
        occlusion_duration_s=1,
    )
    a, f, info = corrupt(table, frames, recipe)
    b, g, _ = corrupt(table, frames, recipe)
    assert a.equals(b) and f == g and frames == original
    assert len(table) == 1801 and len(a) < 1600
    assert np.all(np.diff(a["t_us"].to_numpy()) > 0)
    assert info["artificial"]
    assert not np.any((a["t_us"].to_numpy() > 7.01e6) & (a["t_us"].to_numpy() < 8.99e6))


def test_fusion_does_not_associate_across_a_missing_common_interval():
    intervals = [{"start_us": 0, "end_us": 100}, {"start_us": 200, "end_us": 300}]
    imu = {"events": [{"t_session_us": 90, "magnitude": 2, "prominence": 1}], "eligible_intervals": intervals}
    video = {"events": [{"t_session_us": 210, "magnitude": 3}], "eligible_intervals": intervals}
    assert associate(imu, video, 150)["events"] == []


def test_research_boundary_guard_scales_with_filter_cutoff():
    table, _ = normalize_csv(demo_csv(), SensorMapping())
    result = detect_imu(table, DetectorConfig(cutoff_hz=1), 0)
    assert result["eligible_intervals"] == [{"start_us": 2_000_000, "end_us": 16_000_000}]
    assert result["quality"]["boundary_guard_us"] == 2_000_000
    with pytest.raises(DomainError, match="boundary guard"):
        detect_imu(table, DetectorConfig(cutoff_hz=0.1), 0)


def test_irrelevant_corruptions_and_undeclared_evaluation_hypotheses_are_rejected():
    from uuid import uuid4
    from pydantic import ValidationError
    from rallysense.research_schemas import ExperimentCreate, EvaluationCreate

    with pytest.raises(ValidationError, match="IMU input"):
        ExperimentCreate(mode="video", pose_id=uuid4(), corruption=Corruption(gyro_noise_sd=1))
    with pytest.raises(ValidationError, match="pose input"):
        ExperimentCreate(
            mode="imu", sensor_id=uuid4(), sync_id=uuid4(), corruption=Corruption(occlusion_duration_s=1)
        )
    with pytest.raises(ValidationError, match="hypothesis"):
        EvaluationCreate(reference_id=uuid4(), comparison="proxy_hypothesis")


def test_timestamp_jitter_remains_strict_after_integer_microsecond_rounding():
    import pyarrow as pa

    # Mixed 1/2/3 us spacings expose rounding collisions absent in 100 Hz fixtures.
    times = np.r_[0, np.cumsum(np.tile([1, 2, 3], 100))].astype(np.int64)
    table = pa.table(
        {"t_us": times, **{c: np.zeros(len(times)) for c in ["ax", "ay", "az", "gx", "gy", "gz"]}}
    )
    for seed in range(20):
        result, _, _ = corrupt(table, None, Corruption(seed=seed, timestamp_jitter_fraction=0.45))
        assert np.all(np.diff(result["t_us"].to_numpy()) > 0)
