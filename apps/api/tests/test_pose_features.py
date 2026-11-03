import math
import pytest
from rallysense.pose_features import derive_features


def frame(t, dx=0):
    points = [{"x": 0.5, "y": 0.5, "visibility": 0.9} for _ in range(33)]
    for i, xy in {
        11: (0.4, 0.4),
        12: (0.6, 0.4),
        23: (0.4, 0.8),
        24: (0.6, 0.8),
        14: (0.7, 0.4),
        16: (0.9 + dx, 0.4),
    }.items():
        points[i].update(x=xy[0], y=xy[1])
    return {"t_video_us": t, "landmarks": points}


def test_pose_features_use_actual_times_and_normalized_image_geometry():
    frames = derive_features([frame(0), frame(100000, 0.04)], "right", 1)
    assert frames[0]["features"]["wrist_radius_torso_units"] == pytest.approx(math.sqrt(2))
    assert frames[0]["features"]["elbow_angle_deg_2d"] == pytest.approx(180)
    assert frames[1]["features"]["wrist_speed_torso_units_s"] == pytest.approx(1)


def test_features_do_not_differentiate_across_missing_frames_or_long_gaps():
    frames = derive_features(
        [frame(0), {"t_video_us": 50000, "landmarks": []}, frame(100000, 0.04), frame(400000, 0.1)],
        "right",
        1,
    )
    assert frames[1]["features"]["elbow_angle_deg_2d"] is None
    assert frames[2]["features"]["wrist_speed_torso_units_s"] is None
    assert frames[3]["features"]["wrist_speed_torso_units_s"] is None
