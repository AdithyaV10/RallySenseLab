import math
import pytest
from rallysense.signals import normalize_csv, detect_gyro, demo_csv, map_time, round_us
from rallysense.schemas import SensorMapping, DetectorConfig
from rallysense.errors import DomainError


def test_generated_pulses_are_detected_from_samples():
    table, quality = normalize_csv(demo_csv(), SensorMapping())
    result = detect_gyro(table, DetectorConfig())
    times = [e["t_session_us"] / 1e6 for e in result["events"]]
    assert times == pytest.approx([2.2, 5, 8.1, 11.4, 15], abs=0.03)
    assert quality["sample_rate_hz"] == pytest.approx(100)
    assert all(e["event_type"] == "gyro_peak_v1" for e in result["events"])
    assert "not a confirmed tennis swing" in result["interpretation"]


def test_equivalent_units_produce_identical_values():
    mapping = SensorMapping(
        acceleration=["a", "b", "c"],
        gyroscope=["u", "v", "w"],
        acceleration_unit="g",
        gyroscope_unit="deg/s",
        timestamp="t",
        time_unit="ms",
    )
    table, _ = normalize_csv(
        b"t,a,b,c,u,v,w\n1000,1,0,0,180,0,0\n1010,1,0,0,180,0,0\n1020,1,0,0,180,0,0", mapping
    )
    assert table["ax"][0].as_py() == pytest.approx(9.80665)
    assert table["gx"][0].as_py() == pytest.approx(math.pi)
    assert table["t_us"].to_pylist() == [0, 10000, 20000]


@pytest.mark.parametrize("bad", ["nan", "inf", "-inf", "=1+1"])
def test_nonfinite_and_formula_inputs_rejected(bad):
    content = f"t,x,y,z\n0,{bad},0,0\n0.01,1,0,0\n0.02,1,0,0".encode()
    with pytest.raises(DomainError):
        normalize_csv(content, SensorMapping(timestamp="t", acceleration=[], gyroscope=["x", "y", "z"]))


def test_flat_signal_and_missing_stream_behavior():
    data = b"t,x,y,z\n" + b"".join(f"{i / 100},0,0,0\n".encode() for i in range(200))
    table, _ = normalize_csv(data, SensorMapping(timestamp="t", acceleration=[], gyroscope=["x", "y", "z"]))
    assert detect_gyro(table, DetectorConfig())["events"] == []
    missing, _ = normalize_csv(data, SensorMapping(timestamp="t", acceleration=["x", "y", "z"], gyroscope=[]))
    with pytest.raises(DomainError, match="valid gyro"):
        detect_gyro(missing, DetectorConfig())


def test_timestamp_rejection_and_offset_sign():
    data = b"t,x,y,z\n1,0,0,0\n1,0,0,0\n2,0,0,0"
    with pytest.raises(DomainError, match="strictly increase"):
        normalize_csv(data, SensorMapping(timestamp="t", acceleration=[], gyroscope=["x", "y", "z"]))
    assert map_time(2_000_000, 1_500_000) == 3_500_000
    assert map_time(5_000_000, -1_500_000) == 3_500_000
    assert round_us(-0.5) == -1 and round_us(0.5) == 1


def test_gap_not_interpolated_and_parameters_matter():
    lines = demo_csv().decode().splitlines()
    gapped = "\n".join([lines[0], *[line for line in lines[1:] if not 7 < float(line.split(",")[0]) < 9]])
    table, _ = normalize_csv(gapped.encode(), SensorMapping())
    events = detect_gyro(table, DetectorConfig())["events"]
    assert len(events) == 4
    assert not any(7e6 < e["t_session_us"] < 9e6 for e in events)
    separated = detect_gyro(table, DetectorConfig(min_separation_s=8))["events"]
    assert all(b["t_session_us"] - a["t_session_us"] >= 8e6 for a, b in zip(separated, separated[1:]))
    table, _ = normalize_csv(demo_csv(), SensorMapping())
    # The vector magnitude of the 8 rad/s y pulse is ~8.25 due to its x component;
    # 8.5 separates that pulse from the 9 rad/s y pulse independently of peak indices.
    assert len(detect_gyro(table, DetectorConfig(threshold_rad_s=8.5))["events"]) == 1
    with pytest.raises(DomainError, match="Cutoff"):
        detect_gyro(table, DetectorConfig(cutoff_hz=45))
