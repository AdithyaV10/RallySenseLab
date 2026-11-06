"""Paired synthetic observations for software verification, never athlete data.

The rendered stick figure and stored landmarks use the same analytical trajectory.
They bypass MediaPipe intentionally and retain explicit generated provenance.
"""

import csv
import io
import math
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from .errors import DomainError


def fixture_inputs():
    frames = []
    for i in range(241):
        t = i / 30
        dx = sum(0.12 * math.erf((t - c) / 0.18) for c in [2, 5])
        points = [{"x": 0.5, "y": 0.5, "z": 0, "visibility": 0} for _ in range(33)]
        positions = {
            11: (0.4, 0.4),
            12: (0.6, 0.4),
            23: (0.4, 0.8),
            24: (0.6, 0.8),
            13: (0.3, 0.55),
            15: (0.2, 0.6),
            14: (0.65, 0.4),
            16: (0.7 + dx, 0.4),
            25: (0.4, 0.9),
            26: (0.6, 0.9),
            27: (0.4, 0.98),
            28: (0.6, 0.98),
        }
        for idx, (x, y) in positions.items():
            points[idx].update(x=x, y=y, visibility=1)
        frames.append({"t_video_us": round(t * 1e6), "landmarks": points, "world_landmarks": []})
    text = io.StringIO()
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(["timestamp_s", "ax_m_s2", "ay_m_s2", "az_m_s2", "gx_rad_s", "gy_rad_s", "gz_rad_s"])
    for i in range(801):
        t = i / 100
        pulse = sum(6 * math.exp(-(((t - c) / 0.13) ** 2)) for c in [2, 5])
        writer.writerow([t, 0, 0, 9.80665, 0, pulse, 0])
    return text.getvalue().encode(), frames


def render_fixture_video(frames):
    connections = [
        (11, 12),
        (11, 23),
        (12, 24),
        (23, 24),
        (11, 13),
        (13, 15),
        (12, 14),
        (14, 16),
        (23, 25),
        (25, 27),
        (24, 26),
        (26, 28),
    ]
    buffers = []
    for frame in frames[:-1]:
        canvas = np.full((240, 320, 3), (16, 23, 21), dtype=np.uint8)
        for a, b in connections:
            p, q = frame["landmarks"][a], frame["landmarks"][b]
            x = np.linspace(p["x"] * 319, q["x"] * 319, 150).astype(int).clip(1, 318)
            y = np.linspace(p["y"] * 239, q["y"] * 239, 150).astype(int).clip(1, 238)
            for dy in [-1, 0, 1]:
                canvas[y + dy, x] = (115, 223, 187)
        buffers.append(canvas.tobytes())
    with tempfile.TemporaryDirectory(prefix="rallysense-fixture-") as temp:
        output = Path(temp) / "fixture.mp4"
        try:
            process = subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-f",
                    "rawvideo",
                    "-pixel_format",
                    "rgb24",
                    "-video_size",
                    "320x240",
                    "-framerate",
                    "30",
                    "-i",
                    "pipe:0",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-g",
                    "30",
                    "-movflags",
                    "+faststart",
                    str(output),
                ],
                input=b"".join(buffers),
                capture_output=True,
                timeout=45,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DomainError(
                "FFmpeg is required to render the synthetic research fixture", "DEPENDENCY_UNAVAILABLE"
            ) from exc
        if process.returncode:
            raise DomainError("Synthetic video rendering failed", "PROCESSING_FAILED")
        return output.read_bytes()
