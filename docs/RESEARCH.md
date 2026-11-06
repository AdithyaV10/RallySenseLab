# Research implementation and scientific limits

Step 3 implements observation baselines, reproducible per-session experiments, and a falsifiable association hypothesis. It does not train a tennis classifier. There are no independently labeled paired tennis recordings, held-out players, empirical tennis accuracy estimates, or calibrated confidence probabilities in this workspace.

## What is observed

| Output | Operational meaning | Units / limitations |
| --- | --- | --- |
| `gyro_peak_v1` | Local maximum of filtered device angular-speed magnitude | rad/s; placement dependent; not swing apex or impact |
| `wrist_speed_peak_v1` | Local maximum of torso-relative, aspect-corrected image wrist speed | torso lengths/s in image coordinates; perspective and camera dependent |
| `multimodal_association_v1` | An angular-speed peak with a one-to-one temporally associated visual wrist-speed peak | Timestamp remains the IMU anchor; both times and disagreement are retained |
| `swing_apex_v1` human reference | Greatest visible dominant-wrist extension during an independently identified forward movement | Image-space operational label; not impact |
| `synthetic_reference` | Known generator centers in a deterministic fixture | Software verification only; not independent athlete evidence |

The Step 1 proposal to average IMU and visual timestamps was rejected: the two peaks are different observations, so their midpoint has no established physical interpretation. Association is a defensible baseline for testing co-occurrence, not a learned fusion model. A user must declare paired observations and document alignment evidence. Mixed unrelated sources are rejected for fusion.

## Numerical audit of the MVP

The audit read the actual ingestion, signal, pose, timing, storage, worker, API, replay, tests and migration code. SI conversions (g × 9.80665, deg/s × pi/180), retained raw bytes/origins, first-timestamp normalization, median sample-rate estimation, finite/null handling and positive-offset convention were sound. `session_us = sensor_us + offset_us`; video presentation time is the session clock. Independent CSVs retain independent clocks. No axis rotation, gravity subtraction or world-frame reconstruction is inferred. A magnitude is invariant to rigid coordinate-axis rotation, not sensor placement.

The legacy filter splits gaps over three measured median intervals, interpolates only within segments, uses fourth-order Butterworth SOS forward/backward filtering, and excludes short segments and 250 ms boundaries. It globally suppresses peaks by actual time, strongest first. This behavior remains available as `imu_gyro_peak@1.0.0`. Its fixed guard is an engineering assumption, not a proof of filter settling.

Step 2 display primitives normalize each frame independently and attach backward-difference speed to the later frame. They remain version-compatible display data. The new scientific video detector recomputes from stored landmarks, uses a fixed median valid torso scale within each track, and locates each velocity observation at the midpoint of its actual two-frame interval. This avoids introducing a changing denominator's derivative and avoids systematic half-interval timestamp delay. The new method has separate versioned semantics.

## Video baseline: `video_wrist_speed@1.0.0`

For valid frames, transform image coordinates to `(aspect*x, y)`. Let `h(t)` be the hip midpoint and `s(t)` the shoulder midpoint. The scale is `L = median(||s(t)-h(t)||)` over visible valid frames with scale at least 0.02 image heights. The dominant wrist position relative to the hips is `r(t) = wrist(t)-h(t)`.

Velocity observation: `v((t_i+t_(i-1))/2) = ||r(t_i)-r(t_(i-1))|| / (L*(t_i-t_(i-1)))`.

Require both shoulders, both hips and dominant wrist visibility >=0.5 by default. Any invalid frame breaks the derivative chain. Gaps >150 ms split it. Segments need at least five velocity observations. A centered median over a 150 ms time window uses actual timestamps, not assumed frame indices. Height is `max(1 torso/s, median + 3*1.4826*MAD)`; prominence defaults to 0.5 torso/s; minimum event separation is 0.3 s. Boundaries exclude at least the largest adjacent sampling interval and half the smoothing window. Half-prominence widths are measured on the smoothed signal with interpolation in actual time. These are engineering defaults, not learned tennis constants.

Return event timestamps, strength, prominence, candidate windows, source sampling intervals, visible fraction, cadence, gaps, eligible intervals and a bounded display signal. No-person/occluded frames never become zero velocity. Inadequate input fails explicitly; a usable flat signal successfully returns no events.

The optional 30 Hz extraction target plays the source at half speed, maintaining one inference in flight. The default 10 Hz remains available. Both use actual presentation timestamps and the installed MediaPipe 1.2.0 CPU worker; initialization failure selects the explicit main-thread fallback. Achieved cadence is measured. Neither target promises exhaustive decoding, sub-frame event recovery or impact precision. See [Google's web guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js) for the synchronous API and worker rationale.

The challenge exposes the adaptive multiplier `k`. The official integration clip initially returned an adequate-input empty result at `k=3`: its median plus the MAD threshold exceeded its observed maxima. An explicitly exploratory configuration (`k=1`, height 0.1 torso/s, prominence 0.05 torso/s) produces actual wrist-speed events without labels or accuracy metrics. This is configuration sensitivity on a development/integration input, not held-out validation or a learned threshold.

Playback-driven extraction can produce different sampled tracks and event counts on repeated runs because cadence and tracker input history vary. Deterministic event inference and rerun comparisons apply to a frozen pose artifact/configuration. Each extraction has its own timestamps, quality and artifact fingerprint; a common raw video alone does not imply identical observations.

## Inertial research baseline: `imu_motion_window@1.0.0`

Reuse the validated v1 angular-speed processing and peak definition, then apply a conservative boundary guard `max(0.25 s, 2/cutoff_hz)` for this research adapter. A segment that cannot survive this guard is excluded. The guard reduces risk but does not prove zero edge bias. Legacy v1 timestamps/default behavior remain compatible at 8 Hz.

At each retained peak, find the nearest valid measured gyro vector. Expand a connected window while raw magnitude exceeds `filtered_peak - prominence/2`, stopping at missing vectors or large gaps. Record start/end/duration and maximum available acceleration magnitude in that window. These raw crossings are descriptive movement windows, not validated swing segmentation. Acceleration can include gravity; it is not force or racket acceleration. Adding acceleration noise changes this diagnostic, not the gyro-only event rule.

Report valid sample counts, availability fraction, median interval, jitter p95, gaps and guard. Strength is rad/s, never probability. Unknown placement remains visible in the manifest and precludes interpreting the result as a specific body or racket motion. Forward/backward filtering is offline; a live causal implementation would require a new version and delay analysis. [SciPy SOS documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html)

## Fusion: `multimodal_temporal_association@1.0.0`

Run both independent baselines on immutable aligned inputs. Intersect their eligible intervals. Candidate anchors must lie inside common coverage. Associate one-to-one within a default 150 ms gate using the evaluator's cardinality-first/minimum-error ordered matcher. Output matched pairs only, at the IMU timestamp, with both source indices/times, visual strength and signed disagreement. Retain all unmatched candidate indices and component signals. No overlap fails explicitly; adequate overlapping observations with no associated pairs return a successful empty set.

This tests temporal co-occurrence. Unknown attachment, unrelated subjects, perspective, occlusion, low cadence, natural delays between body-part motions, bad alignment and changing motion patterns can defeat it. Fusion may reduce recall and is not presumed better. No biomechanical reconstruction, common physical apex or probability calibration follows from agreement.

## Evaluation

Freeze one annotation set revision and one event type, with operational definition, labeling procedure, labeler pseudonym, independence declaration, optional source-video hash and session clock. The snapshot copies only small event records; raw recordings are not duplicated. Subsequent edits/deletion of draft events do not change the snapshot. Stale set freezes and stale event edits return 409. Generated labels never become independent human labels.

Exact comparison requires identical event types and declared independent human labels. An explicit `proxy_hypothesis` may compare measured/associated peaks to `swing_apex_v1` or `movement_reference`; the hypothesis is stored and exported. This is a test of the proxy, not a relabeling of predictions. Generated references require `synthetic_fixture` comparison in a synthetic session. No reference means no precision/recall/F1. Independence and pairing are user attestations; the software cannot certify them.

In the declared inclusive session interval, sort events by timestamp/ID. Dynamic programming first maximizes the number of pairs with `|prediction-reference| <= tolerance`, then minimizes total absolute error. Equal objective ties prefer matching, then skipping a prediction, then skipping a reference. This deterministic rule handles duplicates without reuse. Lists are capped at 2,000 events each to bound O(n*m) time/memory. The adversarial `[0,80]` versus `[60,140]` ms at 70 ms tolerance correctly gives two matches; exhaustive small-list brute-force tests independently verify the objective.

`TP = matches`, `FP = unmatched predictions`, `FN = missed references`. Precision is TP/(TP+FP), recall TP/(TP+FN), F1 2TP/(2TP+FP+FN). Precision/recall are null when their denominators are zero; F1 is null only when both lists are empty. Nonempty all-miss comparisons have F1=0. Timing error is prediction minus reference; absolute per-pair errors and mean/median absolute error are retained. Timing summaries are conditional on matching and must be read beside recall. No true negatives or timestamp-event confusion matrix is invented.

Full declared intervals are scored: missing modality coverage does not delete references. Eligible duration/fraction and excluded out-of-interval event counts are reported separately. No usable interval fails rather than reporting accuracy. A separate common-coverage evaluation, participant aggregation, bootstrap uncertainty and held-out generalization study are not implemented or claimed.

## Controlled robustness

Every recipe records a seed. Derived in-memory copies implement random sample dropout, selected inertial-channel Gaussian noise in SI units, timestamp jitter bounded by each sample's local neighbor spacing, contiguous IMU gaps, landmark visibility masking in a selected video window, and an additive IMU synchronization error. The original source timestamps/channels/landmarks and frozen references remain intact. Independent RNG streams keep dropout/noise/jitter comparable when unrelated settings change. Jitter preserves order; missing windows are not interpolated across large gaps.

Jitter's maximum shift is floored to an integer microsecond before random shifts are rounded. This preserves strict ordering even for 1-3 microsecond spacings, where independently rounding opposite sub-microsecond shifts could otherwise cause a collision. An explicit multi-seed regression covers this edge case.

The UI runs one selected corruption at a time; the typed API supports combinations. Compare clean and degraded experiments with the same declared interval and references. Complete occlusion may produce explicit insufficient-data failure, not a flattering accuracy number. Actual source degradation and artificial interventions are labeled separately. No frame-rate decimation without anti-aliasing, automatic drift fitting, or learned correction is claimed.

## Evidence policy

The original five-pulse demo and new two-pulse paired fixture are synthetic. The paired fixture renders a generated stick figure and persists the same analytical landmarks; it is explicitly **not MediaPipe output**. Its generated IMU pulses share the fixture clock. This verifies fusion code without pretending the signals are a physical racket model. Real MediaPipe integration is separately exercised on the official clip's documented seekable derivative, with no independent tennis labels. That clip's unrelated synthetic IMU remains mixed and ineligible for fusion.

Half-prominence widths follow [SciPy's definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_widths.html). They are descriptive signal intervals, not physiological confidence intervals.
