"""Image-space feature primitives, not calibrated biomechanics or event classification."""

import math


def derive_features(frames, handedness, aspect):
    previous = None
    shoulder, elbow, wrist = (11, 13, 15) if handedness == "left" else (12, 14, 16)
    for frame in frames:
        points = frame["landmarks"]
        features = {
            "wrist_radius_torso_units": None,
            "elbow_angle_deg_2d": None,
            "wrist_speed_torso_units_s": None,
        }
        frame["features"] = features
        if len(points) != 33 or any(
            (points[i].get("visibility") or 0) < 0.5 for i in {11, 12, 23, 24, shoulder, elbow, wrist}
        ):
            previous = None
            continue

        def xy(i):
            return points[i]["x"] * aspect, points[i]["y"]

        hips = tuple((a + b) / 2 for a, b in zip(xy(23), xy(24)))
        shoulders = tuple((a + b) / 2 for a, b in zip(xy(11), xy(12)))
        scale = math.dist(hips, shoulders)
        if scale < 0.02:
            previous = None
            continue
        current = tuple((a - b) / scale for a, b in zip(xy(wrist), hips))
        features["wrist_radius_torso_units"] = math.hypot(*current)
        a, b, c = xy(shoulder), xy(elbow), xy(wrist)
        u, v = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        denominator = math.hypot(*u) * math.hypot(*v)
        if denominator > 1e-9:
            features["elbow_angle_deg_2d"] = math.degrees(
                math.acos(max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / denominator)))
            )
        if previous:
            dt = (frame["t_video_us"] - previous[0]) / 1e6
            if 0 < dt <= 0.15:
                features["wrist_speed_torso_units_s"] = math.dist(current, previous[1]) / dt
        previous = frame["t_video_us"], current
    return frames
