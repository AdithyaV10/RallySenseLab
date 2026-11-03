# Development and inference contracts

Contract design version 1, 2026-11-03. These are specifications for future code. Step 2 implements only the MVP interfaces marked below; Step 3 implements video-event, fusion, and evaluation behavior.

## Clocks, units, and coordinates

- API and persisted movement timestamps are signed integer microseconds (`*_us`). Restrict JSON integers to JavaScript's safe integer range. Internal numerical arrays may convert to float64 seconds after subtracting a local origin.
- Each source has a stable ID, original origin, time unit, and normalization version. Preserve these when converting source time to zero-relative microseconds. Reject decreasing time and ambiguous units; exact duplicate timestamps require a documented import policy, default rejection. Quantization collisions are reported.
- Video time uses presentation time relative to the beginning of the displayed media. Keep the original PTS/time-base offset so frame metadata and HTML video time agree, including variable-frame-rate files. Never use `frame_index / nominal_fps` as the authoritative clock.
- Session time is defined by a chosen primary source, ordinarily video time. Map each other source using `t_session = round_half_away_from_zero(scale * (t_source - source_anchor) + session_anchor)`. The same rounding rule must be implemented in Python and TypeScript; do not rely on their differing default round functions.
- Step 2 fixes `scale=1`. In the equivalent notation `t_session=t_sensor+offset`, a sensor peak at 2.0 s aligned to video 3.5 s requires **+1.5 s**. At session 5 s, read sensor 3.5 s. Negative mapped times are retained in raw coverage metadata and clipped only to the explicit viewing/evaluation window.
- Step 3 may estimate drift (`scale`) from independent cues near the beginning and end. Store cue pairs, fit residuals, and method; one cue supports offset only. Never align using held-out reference event labels to maximize reported accuracy.
- Acceleration is m/s²; convert g with 9.80665. Angular rate is rad/s; convert deg/s with pi/180. Keep `linear` and `including_gravity` acceleration distinct. No undocumented gravity subtraction.
- Device frame is right-handed x across screen, y up screen, z out of screen for browser motion capture. Browser rotation rate `beta/gamma/alpha` maps to x/y/z respectively; record orientation and API source, and validate physical signs on devices. CSV column maps declare axes explicitly; do not assume all exporters use browser conventions. [W3C motion specification](https://www.w3.org/TR/orientation-event/) and [MDN rotation rates](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent/rotationRate)
- Pose normalized x/y refer to the processed image rectangle. Store rotation/mirroring transforms and use the identical transform for display. Relative z and model world coordinates are separate fields; neither is calibrated full-body motion capture.

## Import contract (Step 2)

Canonical wide CSV header: `timestamp_s,ax_m_s2,ay_m_s2,az_m_s2,gx_rad_s,gy_rad_s,gz_rad_s`. A mapping request declares timestamp unit/origin, column names, delimiter/decimal convention, acceleration kind, placement, and device frame. At least one complete xyz stream is required. Missing gyro is viewable but cannot run the gyro baseline.

Support UTF-8 with optional BOM, quoted headers, finite decimal numeric fields, and empty values as missing. Reject duplicate column names, oversized rows, ambiguous decimal separators, decreasing timestamps, and malformed numeric tokens with a bounded row/error summary. Reject files exceeding resource limits while streaming. Do not execute spreadsheet formulas. Escape untrusted text in CSV exports to prevent formula execution in spreadsheets.

Separate phyphox accelerometer/gyro CSVs become separate streams with source clocks; do not join rows by index. Preview recognized header/unit mappings and require explicit confirmation for ambiguous units. Preserve export metadata about experiment start/pause/resume. Where clock continuity is unclear, split recording segments or reject alignment pending user mapping. MVP accepts extracted CSV files, not ZIP archives. Phyphox exports can contain a CSV per data set, so a single universal column layout is not assumed. [Phyphox file-format documentation](https://phyphox.org/docs/file-format/)

Normalization output: immutable artifact reference, accepted/rejected counts, per-stream coverage, unit/frame metadata, and quality report. Estimate sampling rate as `1 / median(positive dt_seconds)` per contiguous stream; report interval spread and gaps independently. Do not infer hardware sample rate from nominal metadata alone.

## Pose extraction contract (Step 2)

Start request names video ID/hash, model ID/hash, runtime version, sampling policy, delegate, and configuration. Batches contain increasing `frame_index`, `t_video_us`, per-frame detection status, and landmark arrays. Expected timestamp passed to MediaPipe is `t_video_us / 1000` in milliseconds. Repeated frames are skipped and counted. Backward seeks require a new extraction, not reordered tracker inputs.

Each batch has an index and payload hash; duplicate same-content submissions are idempotent, conflicting duplicates return 409. Finalization checks batch continuity, actual coverage, landmark schema, finite values, and source duration before publishing. Browser reports are untrusted input; the backend validates all bounds and ownership. Some projected landmarks may lie outside [0,1]; flag or clip for rendering, not silently discard valid model observations. Missing visibility remains null, not confidence=1.

## Common inference interface

Conceptual interface: `infer(request: InferenceRequest, inputs: InputBundle) -> InferenceResult`. `InputBundle` resolves only immutable server-owned artifacts, exposing arrays, quality masks, and source metadata. No browser-supplied file path or arbitrary Python name can choose an executable algorithm.

**Request fields:**

| Field | Meaning |
| --- | --- |
| `contract_version` | `1` |
| `session_id`, `run_id` | UUID identifiers |
| `algorithm` | registered `name` and semantic `version` |
| `input_artifacts` | IDs, hashes, schema versions, role (`sensor`, `pose`, derived feature) |
| `sync_configuration_id` | immutable source mappings |
| `window` | half-open `[start_us,end_us)` session interval |
| `configuration` | validated algorithm-specific parameters with all defaults expanded |
| `seed` | integer when randomness exists, otherwise null |

**Result fields:** `status` (`succeeded`, `failed`, `cancelled`), `events`, `quality_report_id`, `eligible_intervals`, `excluded_intervals` with reasons, `warnings`, `failure` nullable, `provenance`, and `latency`. Failed runs have no published partial predictions; diagnostic partial artifacts can remain inaccessible as staging. Successful empty events means the algorithm ran on eligible data and found none. No eligible data is `INSUFFICIENT_DATA`, not an apparently successful zero-event run.

An event contains `event_id`, `event_type`, `event_definition_version`, `t_session_us`, optional interval bounds, `score` nullable, `score_kind`, units, and `evidence`. Evidence carries the source peak time, feature/amplitude, contributing artifacts, quality flags, and (for fusion) contributing event IDs. Scores are strengths or normalized prominence unless independently calibrated; do not label them probability or accuracy.

Latency contains integer `queue_ms`, `compute_ms`, `io_ms`, and `total_ms`, measured with a monotonic clock with explicitly nonoverlapping components. Record CPU/browser, algorithm/runtime version, sample/frame counts, and thread settings. Wall-clock creation timestamps are administrative fields. A cache hit identifies the reused run and reports retrieval latency separately.

Typed failures: `MISSING_INPUT`, `UNSUPPORTED_SCHEMA`, `INVALID_TIMESTAMPS`, `UNKNOWN_UNITS`, `UNSUPPORTED_PLACEMENT`, `INSUFFICIENT_DATA`, `NO_USABLE_POSE`, `NO_OVERLAP`, `INVALID_CONFIGURATION`, `ARTIFACT_UNAVAILABLE`, `RESOURCE_LIMIT`, `INTERNAL_ERROR`. Include a safe message and actionable details; no private paths or stack traces in API responses.

Run fingerprint: SHA-256 of canonicalized request fields plus source hashes, synchronization revision/hash, expanded config, algorithm implementation/code revision, runtime lock hash, and model hash where applicable. Sort keys, reject NaN/Infinity, and normalize number serialization. Deterministic CPU numerics should reproduce within specified tolerances; browser model floating-point output is not promised bit-identical across devices.

## Event definitions and modality adapters

`swing_apex_v1` is the research target: the frame of greatest visible dominant-wrist extension from the torso during the forward portion of a manually identified swing, before follow-through, as operationalized in [research design](RESEARCH_DESIGN.md). It is not ball contact. Predictions are estimates of this target under a declared proxy hypothesis. Raw `gyro_peak` and `wrist_speed_peak` evidence remain distinct diagnostic feature events, not interchangeable ground truth.

| Algorithm | Required inputs | Output / hypothesis | Stage |
| --- | --- | --- | --- |
| `imu_gyro_peak@1.0.0` | Known-placement gyro xyz in rad/s, timestamps, quality masks, sync revision | `swing_apex_v1` candidate at filtered angular-speed peak; timing may systematically differ from human extension reference | 2 |
| `video_wrist_speed@1.0.0` | Dominant wrist, shoulder/hip landmarks, visibility, actual times, camera geometry metadata | Same target estimated from torso-relative image wrist-speed peaks; perspective-dependent proxy | 3 |
| `late_event_fusion@1.0.0` | Compatible IMU/video candidate runs, source quality, same sync and event definition | Matched multimodal candidate events with explicit timing combination and disagreement | 3 |

Algorithm versions above are planned initial identifiers, not available software. A hip-pocket phone is not a racket sensor. The initial IMU hypothesis requires fixed documented placement linked to the swing; unknown placement requires explicit experimental override and a warning. Different placements form different evaluation strata.

### IMU v1 specification

1. Mask missing/nonfinite samples. Split at gaps exceeding three median sample intervals. Keep gap boundaries and reasons; never interpolate across them.
2. Resample each sufficiently long segment to its measured median sample rate by linear interpolation, marking interpolated samples. Avoid upsampling beyond useful input resolution. Any later downsampling needs anti-alias filtering.
3. Compute gyro magnitude `sqrt(gx²+gy²+gz²)`. Apply an offline fourth-order Butterworth low-pass using second-order sections and forward/backward filtering. Initial proposed cutoff 8 Hz; require `0 < cutoff < 0.4 * fs`. Reject incompatible settings rather than silently changing them. Short segments that cannot meet padding requirements are excluded.
4. Set candidate height using either an explicit rad/s threshold or `median + k * 1.4826 * MAD` per segment, with an explicit nonzero floor. Initial engineering parameters: `k=3`, height floor 1 rad/s, prominence 0.5 rad/s, minimum separation 0.30 s. They are unvalidated starting settings, not learned tennis constants.
5. Detect peaks with separation in samples `ceil(separation_s * fs)`, minimum 1. Exclude a configurable 0.25 s boundary guard and report reduced coverage. Constant/zero-MAD signals use the height floor; they do not produce arbitrary events.
6. Map peak timestamps to session time; enforce minimum separation again after mapping/merging segments. Save peak magnitude/prominence and preprocessing configuration. Intensity is relative measured angular speed, not force, racket speed, or athletic skill.

The design uses SciPy's documented peak height/prominence/distance behavior and second-order-section forward/backward filter. Zero-phase filtering is offline and still has edge effects; a future causal/live detector requires a separate version and delay analysis. [find_peaks](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html), [sosfiltfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html)

### Video and fusion specifications (Step 3 only)

Video: transform landmarks to aspect-corrected image coordinates, subtract torso center, and normalize by a robust torso-length scale from valid frames. Derive wrist velocity using actual adjacent timestamps, with quality gates and no differentiation across gaps. Start with visibility >=0.5 and gap <=100 ms, explicitly unvalidated configuration values. Smooth and peak-detect in an independent versioned pipeline. Occlusion, side-on perspective, multiple people, camera motion, or a near-zero torso scale produce warnings/exclusions. No metric m/s claim from normalized image motion.

Fusion: convert both candidate lists to the same session clock and target definition, pair one-to-one within a fixed 150 ms agreement gate using the same deterministic cardinality-first matching principle as evaluation. Initially use equal weights and timestamp midpoint for matched candidates; record both original timestamps and disagreement. A parameterized quality weighting extension must define its numerical meaning and be tuned only on development data. Default output is matched pairs only. Unmatched observations are reported, not silently invented or dropped from diagnostics. Missing modality causes `MISSING_INPUT`/`NO_OVERLAP`; the UI can explicitly run a separate unimodal algorithm. Fusion may improve precision while reducing recall, and is not presumed superior.

## API surface and consistency

All routes are planned under `/api/v1`. JSON errors use `{error:{code,message,details,request_id}}`. 400 malformed input; 404 absent/inaccessible object; 409 revision/idempotency conflict; 413 limit; 415 unsupported file; 422 invalid semantic configuration; 503 unavailable dependency. Use explicit response models and no private storage keys.

| Operation | Planned contract | Stage |
| --- | --- | --- |
| Health | `GET /health/live`, `/health/ready` | 2 |
| Session CRUD | `POST/GET /sessions`; `GET/PATCH/DELETE /sessions/{id}`; cursor list; delete returns 202 cleanup job | 2 |
| Video upload | `POST /sessions/{id}/videos` multipart stream; 202 validation job | 2 |
| Sensor import | `POST /sessions/{id}/sensor-imports` upload plus mapping; preview does not publish; `POST /sensor-imports/{id}/commit` returns job | 2 |
| Jobs | `GET /jobs/{id}`, `POST /jobs/{id}/cancel`; poll with backoff | 2 |
| Media | `GET /videos/{id}/content` with Range; safe inline media type | 2 |
| Pose | `POST /videos/{id}/pose-tracks`; `PUT /pose-tracks/{id}/batches/{index}`; `POST /pose-tracks/{id}/complete` | 2 |
| Synchronization | `POST /sessions/{id}/sync-configurations`; `GET /sessions/{id}/sync-configurations` | 2 |
| Signal/pose windows | `GET /sensor-recordings/{id}/samples` and `/pose-tracks/{id}/frames` with explicit source-time bounds | 2 |
| Inference | `POST /sessions/{id}/inference-runs`; `GET /inference-runs/{id}` and `/predictions` | 2 IMU; 3 other adapters |
| Labels | `POST /sessions/{id}/annotation-sets`; `GET /annotation-sets/{id}`; event create/update/delete under set; `POST .../freeze` | 2 |
| Quality/demo | `GET /sessions/{id}/quality`; `POST /demo-sessions` idempotent deterministic seed import | 2 |
| Experiments/results | `POST/GET /experiments`; `POST /experiments/{id}/evaluate`; `GET /evaluations/{id}`; report export | 3 |

Window responses identify the source clock, original count, returned count, resolution, and gaps. Cap chart points, initially 2,000 per channel. Use min/max buckets for visual spikes; inference always reads full normalized data. Do not connect lines through missing intervals. List endpoints paginate; exact annotation edits use an ETag/revision token and reject stale updates.

Immutable completed run results are never overwritten by retry. Editing sync, labels, or algorithm settings creates a new reference version; explicitly rerun downstream computations. Contract-generation and cross-language timestamp tests are Step 2 acceptance checks.
