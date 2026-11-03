"""Pure ingestion and offline signal processing; no tennis classification claims."""

import csv
import io
import math
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.signal import butter, find_peaks, sosfiltfilt
from .errors import DomainError
from .schemas import SensorMapping, DetectorConfig

CHANNELS = ["ax", "ay", "az", "gx", "gy", "gz"]


def round_us(value: float) -> int:
    return int(math.copysign(math.floor(abs(value) + 0.5), value))


def map_time(t_source_us: int, offset_us: int) -> int:
    return t_source_us + offset_us


def normalize_csv(content: bytes, mapping: SensorMapping) -> tuple[pa.Table, dict]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DomainError("CSV must be UTF-8 encoded") from exc
    try:
        reader = csv.DictReader(io.StringIO(text), delimiter=mapping.delimiter)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise DomainError("CSV contains duplicate header names")
        required = [mapping.timestamp, *mapping.acceleration, *mapping.gyroscope]
        missing = [h for h in required if h not in headers]
        if missing:
            raise DomainError(f"Missing mapped columns: {', '.join(missing)[:180]}")
        timestamps, values = [], []
        factor = {"s": 1_000_000, "ms": 1000, "us": 1}[mapping.time_unit]
        origin = None
        for row_number, row in enumerate(reader, start=2):
            if row_number > 1_000_001:
                raise DomainError("CSV exceeds 1,000,000 sample rows", "RESOURCE_LIMIT", 413)
            if None in row or any(v is None for v in row.values()):
                raise DomainError(f"Row {row_number}: inconsistent column count")
            try:
                timestamp = float(row[mapping.timestamp])
                if not math.isfinite(timestamp):
                    raise ValueError
                if origin is None:
                    origin = timestamp
                t = round_us((timestamp - origin) * factor)
                if timestamps and t <= timestamps[-1]:
                    raise DomainError(
                        f"Row {row_number}: timestamps must strictly increase after unit conversion"
                    )
                channels = []
                for columns, conversion in [
                    (mapping.acceleration, 9.80665 if mapping.acceleration_unit == "g" else 1),
                    (mapping.gyroscope, math.pi / 180 if mapping.gyroscope_unit == "deg/s" else 1),
                ]:
                    if not columns:
                        channels.extend([None] * 3)
                        continue
                    for column in columns:
                        value = float(row[column]) * conversion if row[column].strip() else None
                        if value is not None and (not math.isfinite(value) or abs(value) > 1e9):
                            raise ValueError
                        channels.append(value)
                timestamps.append(t)
                values.append(channels)
            except (ValueError, TypeError, OverflowError) as exc:
                raise DomainError(f"Row {row_number}: invalid or nonfinite numeric value") from exc
    except csv.Error as exc:
        raise DomainError("Malformed CSV") from exc
    if len(timestamps) < 3:
        raise DomainError("At least three increasing samples are required")
    if timestamps[-1] > 1_200_000_000:
        raise DomainError("Recording exceeds the 20 minute sensor limit", "RESOURCE_LIMIT", 413)
    table = pa.table(
        {
            "t_us": pa.array(timestamps, type=pa.int64()),
            **{name: pa.array([v[i] for v in values], type=pa.float64()) for i, name in enumerate(CHANNELS)},
        }
    )
    dt = np.diff(timestamps).astype(float)
    median = float(np.median(dt))
    gaps = [{"start_us": timestamps[i], "end_us": timestamps[i + 1]} for i in np.flatnonzero(dt > 3 * median)]
    stream_stats = {}
    for name, columns in [("acceleration", ["ax", "ay", "az"]), ("gyroscope", ["gx", "gy", "gz"])]:
        matrix = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in columns])
        stream_times = np.asarray(timestamps)[np.all(np.isfinite(matrix), axis=1)]
        stream_stats[name] = {
            "valid_samples": len(stream_times),
            "sample_rate_hz": float(1e6 / np.median(np.diff(stream_times)))
            if len(stream_times) > 1
            else None,
        }
    quality = {
        "normalizer": "csv_si@1.0.0",
        "source_origin": origin,
        "source_time_unit": mapping.time_unit,
        "sample_rate_hz": 1_000_000 / median,
        "jitter_p95_us": float(np.percentile(np.abs(dt - median), 95)),
        "gaps": gaps,
        "streams": stream_stats,
        "missing_values": sum(
            v is None
            for row in values
            for i, v in enumerate(row)
            if (i < 3 and mapping.acceleration) or (i >= 3 and mapping.gyroscope)
        ),
        "acceleration_kind": mapping.acceleration_kind,
        "coordinate_frame": "device_as_mapped",
        "provenance": mapping.provenance,
        "units": {"acceleration": "m/s²", "gyroscope": "rad/s"},
    }
    return table, quality


def parquet_bytes(table: pa.Table) -> bytes:
    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer, compression="zstd", row_group_size=65536)
    return buffer.getvalue().to_pybytes()


def detect_gyro(table: pa.Table, config: DetectorConfig, offset_us: int = 0) -> dict:
    times = table["t_us"].to_numpy().astype(np.int64)
    gyro = np.column_stack([table[c].to_numpy(zero_copy_only=False) for c in ["gx", "gy", "gz"]])
    valid = np.all(np.isfinite(gyro), axis=1)
    if valid.sum() < 30:
        raise DomainError("At least 30 valid gyro samples are required", "INSUFFICIENT_DATA")
    times, gyro = times[valid], gyro[valid]
    median_us = float(np.median(np.diff(times)))
    fs = 1_000_000 / median_us
    if config.cutoff_hz >= 0.4 * fs:
        raise DomainError(f"Cutoff must be below 0.4 × measured rate ({fs:.1f} Hz)", "INVALID_CONFIGURATION")
    breaks = np.flatnonzero(np.diff(times) > median_us * 3) + 1
    segments = np.split(np.arange(len(times)), breaks)
    sos = butter(4, config.cutoff_hz, fs=fs, output="sos")
    events, eligible, excluded = [], [], []
    for indices in segments:
        t = times[indices]
        if len(indices) < max(30, math.ceil(fs * 0.6)):
            excluded.append(
                {
                    "start_us": int(t[0]) + offset_us,
                    "end_us": int(t[-1]) + offset_us,
                    "reason": "short_segment",
                }
            )
            continue
        grid = np.arange(t[0], t[-1] + 0.1, median_us)
        magnitude = np.linalg.norm(gyro[indices], axis=1)
        filtered = sosfiltfilt(sos, np.interp(grid, t, magnitude))
        mad = float(np.median(np.abs(filtered - np.median(filtered))))
        height = max(config.threshold_rad_s, float(np.median(filtered)) + config.adaptive_k * 1.4826 * mad)
        peaks, properties = find_peaks(
            filtered,
            height=height,
            prominence=config.prominence_rad_s,
            distance=1,
        )
        start, end = int(t[0] + 250_000) + offset_us, int(t[-1] - 250_000) + offset_us
        eligible.append({"start_us": start, "end_us": end})
        for i, peak in enumerate(peaks):
            event_time = round_us(float(grid[peak])) + offset_us
            if start <= event_time <= end:
                events.append(
                    {
                        "t_session_us": event_time,
                        "magnitude": float(filtered[peak]),
                        "prominence": float(properties["prominences"][i]),
                        "event_type": "gyro_peak_v1",
                    }
                )
    if not eligible:
        raise DomainError("No segment long enough for offline filtering", "INSUFFICIENT_DATA")
    # Enforce separation in actual time across segment boundaries, strongest first.
    separated = []
    for event in sorted(events, key=lambda e: (-e["magnitude"], e["t_session_us"])):
        if all(
            abs(event["t_session_us"] - old["t_session_us"]) >= config.min_separation_s * 1e6
            for old in separated
        ):
            separated.append(event)
    events = sorted(separated, key=lambda e: e["t_session_us"])
    return {
        "events": events,
        "eligible_intervals": eligible,
        "excluded_intervals": excluded,
        "sample_rate_hz": fs,
        "event_definition": "Filtered angular-speed local maximum",
        "interpretation": "Measured signal event; unvalidated proxy for movement, not a confirmed tennis swing",
        "score_kind": "angular_speed_rad_s",
        "filter": "4th-order Butterworth, SOS forward/backward; offline",
    }


def demo_csv() -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["timestamp_s", "ax_m_s2", "ay_m_s2", "az_m_s2", "gx_rad_s", "gy_rad_s", "gz_rad_s"])
    for i in range(1801):
        t = i / 100
        pulse = sum(
            a * math.exp(-(((t - c) / 0.13) ** 2))
            for c, a in [(2.2, 6), (5, 8), (8.1, 5), (11.4, 9), (15, 7)]
        )
        writer.writerow(
            [
                f"{t:.2f}",
                0.2 * math.sin(t * 3) + pulse * 0.35,
                pulse * 0.12,
                9.80665 + 0.08 * math.cos(t * 5),
                pulse * 0.25,
                pulse,
                0.1 * math.sin(t * 4),
            ]
        )
    return output.getvalue().encode()
