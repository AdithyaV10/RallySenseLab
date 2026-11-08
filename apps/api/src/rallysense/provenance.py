import hashlib
import platform
from pathlib import Path
import numpy
import scipy
import pyarrow
from .config import BUILD_ID
from .errors import DomainError


def execution_environment():
    lock = Path(__file__).resolve().parents[2] / "uv.lock"
    return {
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None,
        "runtime": {
            "numpy": numpy.__version__,
            "scipy": scipy.__version__,
            "pyarrow": pyarrow.__version__,
            "python": platform.python_version(),
        },
        "build_id": BUILD_ID,
    }


def validate_execution_environment(manifest):
    actual = execution_environment()
    if not actual["dependency_lock_sha256"] or any(
        manifest.get(field) != actual[field] for field in ["dependency_lock_sha256", "runtime"]
    ):
        raise DomainError(
            "Frozen dependency/runtime environment differs from this worker; create a new run under the reviewed release",
            "EXECUTION_ENVIRONMENT_MISMATCH",
            409,
        )
    return actual


def input_manifest(session_id, artifact_sha256, sync_id, config):
    source = Path(__file__).with_name("signals.py")
    return {
        "session": session_id,
        "artifact_sha256": artifact_sha256,
        "sync_id": sync_id,
        "algorithm": "imu_gyro_peak@1.0.0",
        "contract": 1,
        "config": config,
        "implementation_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dependency_lock_sha256": execution_environment()["dependency_lock_sha256"],
        "runtime": execution_environment()["runtime"],
    }
