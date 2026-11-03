import hashlib
from pathlib import Path
import numpy
import scipy
import pyarrow


def input_manifest(session_id, artifact_sha256, sync_id, config):
    root = Path(__file__).resolve().parents[2]
    lock = root / "uv.lock"
    source = Path(__file__).with_name("signals.py")
    return {
        "session": session_id,
        "artifact_sha256": artifact_sha256,
        "sync_id": sync_id,
        "algorithm": "imu_gyro_peak@1.0.0",
        "contract": 1,
        "config": config,
        "implementation_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None,
        "runtime": {"numpy": numpy.__version__, "scipy": scipy.__version__, "pyarrow": pyarrow.__version__},
    }
