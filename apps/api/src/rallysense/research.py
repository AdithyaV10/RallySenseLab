"""Deterministic observation baselines, association, and event evaluation.

No trained tennis classifier, calibrated confidence, or physical reconstruction.
"""

import copy
import math
import numpy as np
import pyarrow as pa
from scipy.signal import find_peaks, peak_widths
from .errors import DomainError
from .signals import detect_gyro, round_us


def match_events(predictions, references, tolerance_us):
    """Ordered DP: maximum cardinality, then minimum absolute error.

    Equal-cost paths prefer match, then skip prediction, then skip reference.
    Stable timestamp/ID sorting makes ties deterministic, including duplicates.
    """
    if tolerance_us < 0:
        raise DomainError("Tolerance cannot be negative")
    p = sorted(enumerate(predictions), key=lambda x: (x[1]["t_session_us"], str(x[1].get("id", x[0]))))
    r = sorted(enumerate(references), key=lambda x: (x[1]["t_session_us"], str(x[1].get("id", x[0]))))
    n, m = len(p), len(r)
    if n > 2000 or m > 2000:
        raise DomainError("Evaluation is limited to 2,000 events per list", "RESOURCE_LIMIT", 413)
    count = np.zeros((n + 1, m + 1), dtype=np.int32)
    cost = np.zeros((n + 1, m + 1), dtype=np.int64)
    path = np.zeros((n + 1, m + 1), dtype=np.uint8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            choices = [
                (int(count[i - 1, j]), -int(cost[i - 1, j]), 1, 1),
                (int(count[i, j - 1]), -int(cost[i, j - 1]), 0, 2),
            ]
            error = abs(p[i - 1][1]["t_session_us"] - r[j - 1][1]["t_session_us"])
            if error <= tolerance_us:
                choices.append((int(count[i - 1, j - 1]) + 1, -int(cost[i - 1, j - 1]) - error, 2, 3))
            best = max(choices)
            count[i, j], cost[i, j], path[i, j] = best[0], -best[1], best[3]
    pairs = []
    i, j = n, m
    while i and j:
        move = path[i, j]
        if move == 3:
            pairs.append((p[i - 1][0], r[j - 1][0]))
            i, j = i - 1, j - 1
        elif move == 1:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def evaluate(predictions, references, tolerance_us, duration_us):
    pairs = match_events(predictions, references, tolerance_us)
    matched_p, matched_r = {p for p, _ in pairs}, {r for _, r in pairs}
    errors = [
        {
            "prediction_index": p,
            "reference_index": r,
            "prediction_us": predictions[p]["t_session_us"],
            "reference_us": references[r]["t_session_us"],
            "signed_error_us": predictions[p]["t_session_us"] - references[r]["t_session_us"],
            "absolute_error_us": abs(predictions[p]["t_session_us"] - references[r]["t_session_us"]),
        }
        for p, r in pairs
    ]
    tp, fp, fn = len(pairs), len(predictions) - len(pairs), len(references) - len(pairs)
    absolute = [e["absolute_error_us"] for e in errors]
    return {
        "evaluator": "ordered_cardinality_error_dp@1.0.0",
        "tolerance_us": tolerance_us,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        "mean_absolute_error_us": float(np.mean(absolute)) if absolute else None,
        "median_absolute_error_us": float(np.median(absolute)) if absolute else None,
        "mean_signed_error_us": float(np.mean([e["signed_error_us"] for e in errors])) if errors else None,
        "false_positives_per_minute": fp * 60e6 / duration_us if duration_us > 0 else None,
        "matches": errors,
        "unmatched_predictions": sorted(set(range(len(predictions))) - matched_p),
        "missed_references": sorted(set(range(len(references))) - matched_r),
        "undefined_rule": "Precision needs predictions; recall needs references; F1 needs either; timing needs matches.",
    }


def separate(events, minimum_s):
    selected = []
    for event in sorted(events, key=lambda e: (-e["magnitude"], e["t_session_us"])):
        if all(abs(event["t_session_us"] - old["t_session_us"]) >= minimum_s * 1e6 for old in selected):
            selected.append(event)
    return sorted(selected, key=lambda e: e["t_session_us"])


def detect_video(frames, config, handedness="right", aspect=1):
    """Median torso scale avoids introducing scale-derivative motion.

    Wrist finite differences belong to interval midpoints, not later frames.
    Invalid observations split segments; no interpolation across occlusion.
    """
    wrist = 15 if handedness == "left" else 16
    observations, scales = [], []
    for frame in frames:
        points = frame["landmarks"]
        value = None
        if len(points) == 33 and all(
            (points[i].get("visibility") or 0) >= config.visibility for i in [11, 12, 23, 24, wrist]
        ):

            def xy(i):
                return np.array([points[i]["x"] * aspect, points[i]["y"]], dtype=float)

            hip = (xy(23) + xy(24)) / 2
            shoulder = (xy(11) + xy(12)) / 2
            scale = float(np.linalg.norm(shoulder - hip))
            if scale >= 0.02:
                scales.append(scale)
                value = xy(wrist) - hip
        observations.append((frame["t_video_us"], value))
    if len(scales) < 5:
        raise DomainError("Insufficient visible torso and dominant wrist observations", "INSUFFICIENT_DATA")
    scale = float(np.median(scales))
    segments, segment, previous = [], [], None
    for time_us, xy in observations:
        if xy is not None and previous is not None:
            dt = (time_us - previous[0]) / 1e6
            if 0 < dt <= config.max_gap_s:
                segment.append(
                    ((time_us + previous[0]) // 2, float(np.linalg.norm(xy - previous[1]) / scale / dt), dt)
                )
            else:
                if segment:
                    segments.append(segment)
                segment = []
        else:
            if segment:
                segments.append(segment)
            segment = []
        previous = (time_us, xy) if xy is not None else None
    if segment:
        segments.append(segment)
    events, eligible, samples = [], [], []
    for segment in segments:
        if len(segment) < 5:
            continue
        times, speed, dt = np.asarray(segment).T
        # Centered time-window median on actual times, no assumed uniform cadence.
        smooth = np.array(
            [np.median(speed[np.abs(times - t) <= config.smooth_window_s * 5e5]) for t in times]
        )
        med = float(np.median(smooth))
        threshold = max(
            config.threshold, med + config.adaptive_k * 1.4826 * float(np.median(abs(smooth - med)))
        )
        peaks, props = find_peaks(smooth, height=threshold, prominence=config.prominence)
        widths = peak_widths(smooth, peaks, rel_height=0.5) if len(peaks) else None
        # One observation plus smoothing guard at either boundary.
        guard = max(config.smooth_window_s * 5e5, float(np.max(dt)) * 1e6)
        start, end = round_us(times[0] + guard), round_us(times[-1] - guard)
        if end <= start:
            continue
        eligible.append({"start_us": start, "end_us": end})
        for i, peak in enumerate(peaks):
            t = int(times[peak])
            if start <= t <= end:
                left = round_us(float(np.interp(widths[2][i], np.arange(len(times)), times)))
                right = round_us(float(np.interp(widths[3][i], np.arange(len(times)), times)))
                events.append(
                    {
                        "t_session_us": t,
                        "event_type": "wrist_speed_peak_v1",
                        "magnitude": float(smooth[peak]),
                        "prominence": float(props["prominences"][i]),
                        "window_start_us": left,
                        "window_end_us": right,
                        "sampling_interval_us": round_us(float(dt[peak]) * 1e6),
                    }
                )
        samples.extend({"t_session_us": int(t), "value": float(v)} for t, v in zip(times, smooth))
    if not eligible:
        raise DomainError("No visible pose segment long enough for event detection", "INSUFFICIENT_DATA")
    intervals = np.diff([f["t_video_us"] for f in frames])
    return {
        "events": separate(events, config.min_separation_s),
        "eligible_intervals": eligible,
        "signal": samples[:: max(1, math.ceil(len(samples) / 2000))],
        "quality": {
            "visible_frames": len(scales),
            "total_frames": len(frames),
            "visible_fraction": len(scales) / len(frames),
            "median_torso_scale": scale,
            "median_frame_interval_us": float(np.median(intervals)) if len(intervals) else None,
            "max_frame_gap_us": int(max(intervals)) if len(intervals) else None,
        },
        "score_kind": "image_torso_units_per_second",
        "limitations": [
            "Image-space speed peak, not maximal extension or impact.",
            "Finite differences average motion between sampled frames; sub-frame events may be missed.",
            "Camera motion, perspective and torso deformation can change the signal.",
        ],
    }


def detect_imu(table, config, offset_us):
    result = detect_gyro(table, config, offset_us)
    # v1 remains untouched; the research adapter uses a conservative cutoff-scaled guard.
    extra_guard = max(0, round_us(2e6 / config.cutoff_hz) - 250_000)
    result["eligible_intervals"] = [
        {"start_us": i["start_us"] + extra_guard, "end_us": i["end_us"] - extra_guard}
        for i in result["eligible_intervals"]
        if i["end_us"] - i["start_us"] > 2 * extra_guard
    ]
    if not result["eligible_intervals"]:
        raise DomainError("No segment survives the cutoff-scaled boundary guard", "INSUFFICIENT_DATA")
    result["events"] = [
        e
        for e in result["events"]
        if any(i["start_us"] <= e["t_session_us"] <= i["end_us"] for i in result["eligible_intervals"])
    ]
    # Preserve v1 peak times; add independently measured local observation summaries.
    times = table["t_us"].to_numpy()
    gyro = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in ["gx", "gy", "gz"]])
    acc = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in ["ax", "ay", "az"]])
    valid = np.all(np.isfinite(gyro), axis=1)
    magnitude = np.linalg.norm(gyro, axis=1)
    median_dt = float(np.median(np.diff(times[valid])))
    for event in result["events"]:
        peak = event["t_session_us"] - offset_us
        valid_indices = np.flatnonzero(valid)
        center = int(valid_indices[np.argmin(abs(times[valid] - peak))])
        left = right = center
        # Connected above-half-prominence window on measured (not fabricated) gyro samples.
        contour = event["magnitude"] - event["prominence"] / 2
        while (
            left > 0
            and valid[left - 1]
            and times[left] - times[left - 1] <= 3 * median_dt
            and magnitude[left - 1] >= contour
        ):
            left -= 1
        while (
            right + 1 < len(times)
            and valid[right + 1]
            and times[right + 1] - times[right] <= 3 * median_dt
            and magnitude[right + 1] >= contour
        ):
            right += 1
        acceleration = np.linalg.norm(acc[left : right + 1], axis=1)
        finite_acc = acceleration[np.isfinite(acceleration)]
        event.update(
            window_start_us=int(times[left]) + offset_us,
            window_end_us=int(times[right]) + offset_us,
            duration_us=int(times[right] - times[left]),
            acceleration_peak_m_s2=float(max(finite_acc)) if len(finite_acc) else None,
        )
    dts = np.diff(times[valid])
    result["quality"] = {
        "valid_gyro_samples": int(valid.sum()),
        "input_samples": len(table),
        "availability_fraction": float(valid.mean()),
        "jitter_p95_us": float(np.percentile(abs(dts - median_dt), 95)),
        "gap_count": int(sum(dts > 3 * median_dt)),
        "sample_interval_us": median_dt,
        "boundary_guard_us": 250_000 + extra_guard,
    }
    result["signal"] = [
        {"t_session_us": int(times[i]) + offset_us, "value": float(magnitude[i]) if valid[i] else None}
        for i in range(0, len(times), max(1, math.ceil(len(times) / 2000)))
    ]
    result["limitations"] = [
        "Angular-speed peaks are measured signal events, not confirmed swings.",
        "Window uses raw half-prominence crossings; acceleration may include gravity.",
        "Magnitude is rotation invariant, not placement invariant. No world-frame reconstruction.",
    ]
    return result


def associate(imu, video, tolerance_us):
    overlap = [
        {"start_us": max(a["start_us"], b["start_us"]), "end_us": min(a["end_us"], b["end_us"])}
        for a in imu["eligible_intervals"]
        for b in video["eligible_intervals"]
        if max(a["start_us"], b["start_us"]) < min(a["end_us"], b["end_us"])
    ]
    if not overlap:
        raise DomainError("No common eligible observation interval", "NO_OVERLAP")
    # Merge intersections, then associate within each continuous common interval.
    # Individually eligible anchors on opposite sides of an occlusion are not a pair.
    merged = []
    for interval in sorted(overlap, key=lambda item: item["start_us"]):
        if merged and interval["start_us"] <= merged[-1]["end_us"]:
            merged[-1]["end_us"] = max(merged[-1]["end_us"], interval["end_us"])
        else:
            merged.append(dict(interval))
    overlap = merged
    p, r = imu["events"], video["events"]
    pairs = []
    for interval in overlap:
        pi = [i for i, e in enumerate(p) if interval["start_us"] <= e["t_session_us"] <= interval["end_us"]]
        ri = [i for i, e in enumerate(r) if interval["start_us"] <= e["t_session_us"] <= interval["end_us"]]
        pairs.extend(
            (pi[i], ri[j]) for i, j in match_events([p[i] for i in pi], [r[j] for j in ri], tolerance_us)
        )
    events = []
    for i, j in pairs:
        events.append(
            {
                **p[i],
                "event_type": "multimodal_association_v1",
                "imu_event_index": i,
                "video_event_index": j,
                "imu_time_us": p[i]["t_session_us"],
                "video_time_us": r[j]["t_session_us"],
                "disagreement_us": r[j]["t_session_us"] - p[i]["t_session_us"],
                "video_strength": r[j]["magnitude"],
            }
        )
    return {
        "events": events,
        "eligible_intervals": overlap,
        "quality": {
            "matched_pairs": len(pairs),
            "imu_candidates": len(p),
            "video_candidates": len(r),
            "unmatched_imu": [i for i in range(len(p)) if i not in {a for a, _ in pairs}],
            "unmatched_video": [i for i in range(len(r)) if i not in {b for _, b in pairs}],
        },
        "score_kind": "angular_speed_rad_s_with_visual_association",
        "limitations": [
            "Association tests temporal co-occurrence of different observations; it does not prove a shared physical event.",
            "Timestamp remains the IMU anchor; averaging unlike event definitions would manufacture timing agreement.",
            "Matched-only output may lose recall; all unmatched observations remain visible.",
        ],
    }


def corrupt(table, frames, recipe):
    # Separate deterministic streams keep paired conditions stable when unrelated settings change.
    seeds = np.random.SeedSequence(recipe.seed).spawn(4)
    knobs = recipe.model_dump(exclude={"seed", "occluded_landmarks", "imu_gap_start_s", "occlusion_start_s"})
    summary = {"artificial": any(value != 0 for value in knobs.values()), "recipe": recipe.model_dump()}
    if table is not None:
        data = table.to_pydict()
        n = len(table)
        times = np.array(data["t_us"], dtype=np.int64)
        keep = np.random.default_rng(seeds[0]).random(n) >= recipe.dropout_fraction
        keep &= ~(
            (times >= recipe.imu_gap_start_s * 1e6)
            & (times < (recipe.imu_gap_start_s + recipe.imu_gap_duration_s) * 1e6)
        )
        rng = np.random.default_rng(seeds[1])
        for channel in ["ax", "ay", "az", "gx", "gy", "gz"]:
            sd = recipe.gyro_noise_sd if channel.startswith("g") else recipe.acceleration_noise_sd
            noise = rng.normal(0, sd, n)
            data[channel] = [None if v is None else float(v + noise[i]) for i, v in enumerate(data[channel])]
        # Local minimum neighbor spacing guarantees order and prevents timestamp reassignment.
        if n > 1 and recipe.timestamp_jitter_fraction:
            dt = np.diff(times)
            bound = np.minimum(np.r_[dt[0], dt], np.r_[dt, dt[-1]])
            # Bound integer shifts before rounding: sub-microsecond rounding of
            # opposite +/-0.9 us shifts could otherwise collide at a 2 us gap.
            radius = np.floor(bound * recipe.timestamp_jitter_fraction)
            jitter = np.random.default_rng(seeds[2]).uniform(-1, 1, n) * radius
            jitter[0] = jitter[-1] = 0
            times += np.rint(jitter).astype(np.int64)
        data["t_us"] = times.tolist()
        table = pa.table(data, schema=table.schema).filter(pa.array(keep))
        summary.update(original_sensor_samples=n, retained_sensor_samples=len(table))
    if frames is not None:
        frames = copy.deepcopy(frames)
        hidden = 0
        for frame in frames:
            if (
                recipe.occlusion_start_s * 1e6
                <= frame["t_video_us"]
                < (recipe.occlusion_start_s + recipe.occlusion_duration_s) * 1e6
            ):
                for i in recipe.occluded_landmarks:
                    if len(frame["landmarks"]) == 33:
                        frame["landmarks"][i]["visibility"] = 0
                hidden += 1
        summary["occluded_frames"] = hidden
    return table, frames, summary
