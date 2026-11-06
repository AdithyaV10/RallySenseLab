from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, allow_inf_nan=False)


class SessionCreate(DTO):
    title: str = Field(min_length=1, max_length=160)
    dataset_kind: Literal["recorded", "synthetic", "mixed"] = "recorded"
    handedness: Literal["left", "right"] = "right"
    notes: str = Field(default="", max_length=2000)


class SessionOut(SessionCreate):
    id: str
    dataset_kind: str
    created_at: datetime


class SensorMapping(DTO):
    provenance: Literal["recorded", "synthetic"] = "recorded"
    timestamp: str = "timestamp_s"
    time_unit: Literal["s", "ms", "us"] = "s"
    acceleration: list[str] = Field(default_factory=lambda: ["ax_m_s2", "ay_m_s2", "az_m_s2"], max_length=3)
    gyroscope: list[str] = Field(default_factory=lambda: ["gx_rad_s", "gy_rad_s", "gz_rad_s"], max_length=3)
    acceleration_unit: Literal["m/s2", "g"] = "m/s2"
    gyroscope_unit: Literal["rad/s", "deg/s"] = "rad/s"
    acceleration_kind: Literal["linear", "including_gravity", "unknown"] = "unknown"
    delimiter: Literal[",", ";", "\t"] = ","
    placement: str = Field(default="unknown", max_length=80)

    @model_validator(mode="after")
    def columns(self):
        if not any(len(v) == 3 for v in [self.acceleration, self.gyroscope]):
            raise ValueError("At least one complete xyz stream is required")
        if any(len(v) not in [0, 3] for v in [self.acceleration, self.gyroscope]):
            raise ValueError("Each stream must have zero or three columns")
        names = [self.timestamp, *self.acceleration, *self.gyroscope]
        if len(names) != len(set(names)):
            raise ValueError("Mapped column names must be distinct")
        return self


class DetectorConfig(DTO):
    cutoff_hz: float = Field(default=8, gt=0, le=50)
    threshold_rad_s: float = Field(default=1, gt=0, le=1000)
    prominence_rad_s: float = Field(default=0.5, gt=0, le=1000)
    min_separation_s: float = Field(default=0.3, ge=0.05, le=10)
    adaptive_k: float = Field(default=3, ge=0, le=20)


class InferenceCreate(DTO):
    sensor_id: UUID
    config: DetectorConfig = Field(default_factory=DetectorConfig)


class SyncCreate(DTO):
    sensor_id: UUID
    offset_us: int = Field(ge=-600_000_000, le=600_000_000)


class AnnotationCreate(DTO):
    t_session_us: int = Field(ge=0, le=1_200_000_000)
    event_type: Literal[
        "swing_apex_v1",
        "movement_reference",
        "sync_cue",
        "synthetic_reference",
        "gyro_peak_v1",
        "wrist_speed_peak_v1",
        "multimodal_association_v1",
    ] = "movement_reference"
    note: str = Field(default="", max_length=1000)


class AnnotationUpdate(AnnotationCreate):
    revision: int = Field(ge=1)


class SensorOut(DTO):
    id: str
    name: str
    status: str
    duration_us: int
    samples: int
    mapping: dict[str, JsonValue]
    quality: dict[str, JsonValue]
    placement: str


class VideoOut(DTO):
    id: str
    name: str
    status: str
    duration_us: int
    width: int
    height: int
    metadata_json: dict[str, JsonValue]


class PoseOut(DTO):
    id: str
    video_id: str
    status: str
    quality: dict[str, JsonValue]
    config: dict[str, JsonValue]


class PredictionOut(DTO):
    id: str
    run_id: str
    t_session_us: int
    event_type: str
    magnitude: float
    prominence: float


class RunOut(DTO):
    id: str
    sensor_id: str
    sync_id: str
    algorithm: str
    status: str
    config: dict[str, JsonValue]
    result: dict[str, JsonValue]
    created_at: datetime


class JobOut(DTO):
    id: str
    kind: str
    target_id: str
    state: str
    attempt: int
    error: str | None


class SyncOut(DTO):
    id: str
    revision: int
    sensor_id: str
    offset_us: int


class AnnotationOut(AnnotationCreate):
    id: str
    revision: int
    set_id: str


class SessionDetail(SessionOut):
    sensors: list[SensorOut]
    videos: list[VideoOut]
    poses: list[PoseOut]
    runs: list[RunOut]
    predictions: list[PredictionOut]
    annotations: list[AnnotationOut]
    syncs: list[SyncOut]
    jobs: list[JobOut]


class Sample(DTO):
    t_us: int
    ax: float | None
    ay: float | None
    az: float | None
    gx: float | None
    gy: float | None
    gz: float | None
    acc: float | None
    gyro: float | None


class SamplesOut(DTO):
    source_count: int
    returned_count: int
    clock: Literal["source_relative_us"] = "source_relative_us"
    data: list[Sample]


class Landmark(DTO):
    x: float = Field(ge=-10, le=10)
    y: float = Field(ge=-10, le=10)
    z: float = Field(ge=-100, le=100)
    visibility: float | None = Field(default=None, ge=0, le=1)
    presence: float | None = Field(default=None, ge=0, le=1)


class PoseFrame(DTO):
    t_video_us: int = Field(ge=0, le=600_000_000)
    landmarks: list[Landmark] = Field(max_length=33)
    world_landmarks: list[Landmark] = Field(default_factory=list, max_length=33)
    features: dict[str, float | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def count(self):
        if len(self.landmarks) not in [0, 33] or len(self.world_landmarks) not in [0, 33]:
            raise ValueError("Expected 0 or 33 landmarks")
        return self


class PoseBatchIn(DTO):
    frames: list[PoseFrame] = Field(min_length=1, max_length=300)


class PoseStart(DTO):
    runtime_version: str = Field(max_length=40)
    model_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    executor: Literal["worker", "main_thread_fallback"]
    sample_target_hz: Literal[10, 30] = 10
    playback_rate: Literal[0.5, 1.0] = 1.0


class PoseFramesOut(DTO):
    frames: list[PoseFrame]
