"""Versioned research requests; all timing is integer session microseconds."""

from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import Field, model_validator
from .schemas import DTO, DetectorConfig


class VideoConfig(DTO):
    visibility: float = Field(0.5, ge=0, le=1)
    max_gap_s: float = Field(0.15, ge=0.03, le=0.5)
    threshold: float = Field(1, gt=0, le=1000)
    prominence: float = Field(0.5, gt=0, le=1000)
    adaptive_k: float = Field(3, ge=0, le=20)
    min_separation_s: float = Field(0.3, ge=0.05, le=10)
    smooth_window_s: float = Field(0.15, ge=0, le=1)


class Corruption(DTO):
    seed: int = Field(42, ge=0, le=2**32 - 1)
    dropout_fraction: float = Field(0, ge=0, le=0.95)
    gyro_noise_sd: float = Field(0, ge=0, le=100)
    acceleration_noise_sd: float = Field(0, ge=0, le=100)
    timestamp_jitter_fraction: float = Field(0, ge=0, le=0.45)
    imu_gap_start_s: float = Field(0, ge=0, le=1200)
    imu_gap_duration_s: float = Field(0, ge=0, le=1200)
    occlusion_start_s: float = Field(0, ge=0, le=600)
    occlusion_duration_s: float = Field(0, ge=0, le=600)
    occluded_landmarks: list[int] = Field(default_factory=lambda: [15, 16], max_length=33)
    sync_error_us: int = Field(0, ge=-10_000_000, le=10_000_000)

    @model_validator(mode="after")
    def indices(self):
        if any(i < 0 or i > 32 for i in self.occluded_landmarks):
            raise ValueError("Landmark indices must be 0 through 32")
        return self


class ExperimentCreate(DTO):
    name: str = Field("Motion experiment", min_length=1, max_length=160)
    research_question: str = Field("How do observations support movement-event detection?", max_length=2000)
    mode: Literal["imu", "video", "fusion"]
    sensor_id: UUID | None = None
    pose_id: UUID | None = None
    sync_id: UUID | None = None
    reference_id: UUID | None = None
    imu: DetectorConfig = Field(default_factory=DetectorConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    association_tolerance_us: int = Field(150_000, ge=0, le=2_000_000)
    tolerance_us: int = Field(150_000, ge=0, le=2_000_000)
    start_us: int = Field(0, ge=0, le=1_200_000_000)
    end_us: int = Field(18_000_000, gt=0, le=1_800_000_000)
    pairing: Literal["unpaired", "same_recording", "synthetic_fixture"] = "unpaired"
    alignment_note: str = Field("", max_length=1000)
    comparison: Literal["exact", "proxy_hypothesis", "synthetic_fixture"] = "exact"
    hypothesis: str = Field("", max_length=2000)
    corruption: Corruption = Field(default_factory=Corruption)
    force_rerun: bool = False

    @model_validator(mode="after")
    def required(self):
        if self.end_us <= self.start_us:
            raise ValueError("End must follow start")
        if self.mode in ("imu", "fusion") and (not self.sensor_id or not self.sync_id):
            raise ValueError("IMU requires sensor and explicit sync revision")
        if self.mode in ("video", "fusion") and not self.pose_id:
            raise ValueError("Video requires a stored pose track")
        if self.mode == "fusion" and (self.pairing == "unpaired" or len(self.alignment_note.strip()) < 8):
            raise ValueError("Fusion requires declared paired observations and alignment evidence")
        if self.comparison == "proxy_hypothesis" and len(self.hypothesis.strip()) < 12:
            raise ValueError("Declare the proxy-to-reference hypothesis")
        if self.mode == "video" and any(
            [
                self.corruption.dropout_fraction,
                self.corruption.gyro_noise_sd,
                self.corruption.acceleration_noise_sd,
                self.corruption.timestamp_jitter_fraction,
                self.corruption.imu_gap_duration_s,
                self.corruption.sync_error_us,
            ]
        ):
            raise ValueError("Inertial corruption requires an IMU input")
        if self.mode == "imu" and self.corruption.occlusion_duration_s:
            raise ValueError("Landmark occlusion requires a pose input")
        return self


class AnnotationSetCreate(DTO):
    name: str = Field(min_length=1, max_length=120)


class EvaluationCreate(DTO):
    reference_id: UUID
    tolerance_us: int = Field(150_000, ge=0, le=2_000_000)
    comparison: Literal["exact", "proxy_hypothesis", "synthetic_fixture"] = "exact"
    hypothesis: str = Field("", max_length=2000)

    @model_validator(mode="after")
    def declared_hypothesis(self):
        if self.comparison == "proxy_hypothesis" and len(self.hypothesis.strip()) < 12:
            raise ValueError("Declare the proxy-to-reference hypothesis")
        return self


class AnnotationSetOut(DTO):
    id: str
    name: str
    provenance: str
    revision: int


class FreezeCreate(DTO):
    revision: int = Field(ge=1)
    event_type: Literal[
        "swing_apex_v1",
        "movement_reference",
        "synthetic_reference",
        "gyro_peak_v1",
        "wrist_speed_peak_v1",
        "multimodal_association_v1",
    ]
    definition: str = Field(min_length=12, max_length=2000)
    labeler: str = Field(min_length=1, max_length=80)
    procedure: str = Field(min_length=12, max_length=2000)
    independent: bool = False
    video_id: UUID | None = None


class ReferenceOut(DTO):
    id: str
    set_id: str
    revision: int
    created_at: datetime
    manifest: dict
    events: list[dict]
    fingerprint: str


class ExperimentOut(DTO):
    id: str
    session_id: str
    created_at: datetime
    name: str
    status: str
    fingerprint: str
    manifest: dict
    result: "ExperimentResult"
    error: str | None
    reused_from_id: str | None


class ResearchEvent(DTO):
    t_session_us: int
    event_type: str
    magnitude: float
    prominence: float = 0
    window_start_us: int | None = None
    window_end_us: int | None = None
    sampling_interval_us: int | None = None
    duration_us: int | None = None
    acceleration_peak_m_s2: float | None = None
    imu_event_index: int | None = None
    video_event_index: int | None = None
    imu_time_us: int | None = None
    video_time_us: int | None = None
    disagreement_us: int | None = None
    video_strength: float | None = None
    id: str | None = None


class TimingMatch(DTO):
    prediction_index: int
    reference_index: int
    prediction_us: int
    reference_us: int
    signed_error_us: int
    absolute_error_us: int


class Evaluation(DTO):
    evaluator: str
    tolerance_us: int
    tp: int
    fp: int
    fn: int
    precision: float | None
    recall: float | None
    f1: float | None
    mean_absolute_error_us: float | None
    median_absolute_error_us: float | None
    mean_signed_error_us: float | None
    false_positives_per_minute: float | None
    matches: list[TimingMatch]
    unmatched_predictions: list[int]
    missed_references: list[int]
    undefined_rule: str


class SignalPoint(DTO):
    t_session_us: int
    value: float | None


class Interval(DTO):
    start_us: int
    end_us: int


class ComponentResult(DTO):
    model_config = {"extra": "allow"}
    events: list[ResearchEvent] = Field(default_factory=list)
    signal: list[SignalPoint] = Field(default_factory=list)
    quality: dict = Field(default_factory=dict)
    eligible_intervals: list[Interval] = Field(default_factory=list)
    score_kind: str = ""
    limitations: list[str] = Field(default_factory=list)


class ExperimentResult(ComponentResult):
    components: dict[str, ComponentResult] = Field(default_factory=dict)
    evaluation: Evaluation | None = None
    evaluation_note: str = "Not evaluated"
    references: list[dict] = Field(default_factory=list)
    corruption: dict = Field(default_factory=dict)
    processing_ms: float | None = None


# Typed numerical payload while manifests remain extensible, versioned JSON.
ExperimentOut.model_rebuild(force=True)
