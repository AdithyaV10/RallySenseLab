export type Mode = "imu" | "video" | "fusion";
export interface SignalPoint {
  t_session_us: number;
  value: number | null;
}
export interface MotionEvent {
  t_session_us: number;
  event_type: string;
  magnitude?: number;
  imu_time_us?: number;
  video_time_us?: number;
  disagreement_us?: number;
}
export interface Evaluation {
  tp: number;
  fp: number;
  fn: number;
  precision: number | null;
  recall: number | null;
  f1: number | null;
  tolerance_us: number;
  mean_absolute_error_us: number | null;
  matches: {
    reference_us: number;
    prediction_us: number;
    signed_error_us: number;
    absolute_error_us: number;
  }[];
  missed_references: number[];
  unmatched_predictions: number[];
}
export interface Observation {
  events: MotionEvent[];
  signal?: SignalPoint[];
}
export interface Result extends Observation {
  evaluation?: Evaluation | null;
  components?: Partial<Record<"imu" | "video", Observation>>;
  quality?: {
    matched_pairs?: number;
    imu_candidates?: number;
    video_candidates?: number;
    unmatched_imu?: number[];
    unmatched_video?: number[];
  };
  coverage?: { fraction: number; rule: string };
  failure_code?: string;
  limitations?: string[];
  processing_ms?: number;
}
export interface Experiment {
  id: string;
  name: string;
  status: "succeeded" | "failed";
  fingerprint: string;
  mode: Mode;
  algorithm: string;
  request: {
    mode: Mode;
    corruption: {
      imu_gap_duration_s: number;
      imu_gap_start_s: number;
      occlusion_duration_s: number;
      occlusion_start_s: number;
      sync_error_us: number;
      seed: number;
    };
  };
  runtime: Record<string, string>;
  dependency_lock_sha256: string;
  implementation_sha256: string;
  result: Result;
}
export interface Landmark {
  x: number;
  y: number;
  z: number;
  visibility: number;
}
export interface PoseFrame {
  t_video_us: number;
  landmarks: Landmark[];
}
export interface Dataset {
  schema_version: number;
  source_release: string;
  dataset_kind: "synthetic";
  title: string;
  notes: string;
  duration_us: number;
  sample_rate_hz: number;
  video: {
    file: string;
    width: number;
    height: number;
    duration_us: number;
    sha256: string;
    bytes: number;
  };
  sensor: {
    samples: {
      t_us: number;
      ax: number | null;
      ay: number | null;
      az: number | null;
      gx: number | null;
      gy: number | null;
      gz: number | null;
    }[];
  };
  pose: {
    frames: PoseFrame[];
    config: { provenance: string; sample_target_hz: number };
  };
  reference: {
    events: MotionEvent[];
    manifest: { independent: false; provenance: string; definition: string };
    fingerprint: string;
  };
  experiments: Experiment[];
  sources: { kind: string; sha256: string; bytes: number }[];
  limitations: string[];
}
export const asset = (path: string) => `${import.meta.env.BASE_URL}${path}`;
export const modeName = (mode: Mode) =>
  ({ imu: "IMU only", video: "Video only", fusion: "Temporal association" })[
    mode
  ];
export const seconds = (us: number, digits = 2) =>
  `${(us / 1e6).toFixed(digits)} s`;
export const percent = (value: number | null | undefined) =>
  value == null ? "—" : `${(value * 100).toFixed(1)}%`;
export const clampTime = (us: number, duration: number) =>
  Number.isFinite(us) ? Math.max(0, Math.min(duration, us)) : 0;
export function nearestFrame(frames: PoseFrame[], time: number) {
  let lo = 0,
    hi = frames.length - 1;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (frames[mid].t_video_us < time) lo = mid + 1;
    else hi = mid;
  }
  return lo > 0 &&
    Math.abs(frames[lo - 1].t_video_us - time) <=
      Math.abs(frames[lo].t_video_us - time)
    ? frames[lo - 1]
    : frames[lo];
}
export function modalitySignal(
  experiment: Experiment,
  mode: "imu" | "video",
): SignalPoint[] {
  return (
    experiment.result.components?.[mode]?.signal ??
    (experiment.mode === mode ? (experiment.result.signal ?? []) : [])
  );
}
export function validateDataset(value: unknown): Dataset {
  const data = value as Dataset;
  if (
    !data ||
    data.schema_version !== 1 ||
    data.dataset_kind !== "synthetic" ||
    data.reference?.manifest?.independent !== false ||
    data.pose?.config?.provenance !== "generated_analytical_landmarks" ||
    data.experiments?.length !== 10 ||
    !data.sensor?.samples?.length ||
    !data.pose?.frames?.length
  )
    throw new Error("The reviewed synthetic dataset could not be verified.");
  return data;
}
export function description(experiment: Experiment) {
  const c = experiment.request.corruption;
  if (c.sync_error_us)
    return `Stored IMU clock shifted by ${seconds(c.sync_error_us)}. Temporal disagreement can remove otherwise present associations.`;
  if (c.imu_gap_duration_s)
    return `A generated ${c.imu_gap_duration_s.toFixed(1)} s IMU gap begins at ${c.imu_gap_start_s.toFixed(1)} s. Missing observations retain reference misses.`;
  if (c.occlusion_duration_s)
    return `Generated wrist observations are occluded for ${c.occlusion_duration_s.toFixed(1)} s from ${c.occlusion_start_s.toFixed(1)} s. This is a configured software condition.`;
  if (!experiment.result.evaluation)
    return "Stored inference without a frozen scoring reference. Accuracy metrics are intentionally unavailable.";
  return "Uncorrupted generated observations on a known shared clock, evaluated against non-independent synthetic pulse references.";
}
