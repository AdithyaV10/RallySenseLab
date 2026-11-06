# Step 3 implementation report

Date: 2026-11-05, America/New_York. Authorized scope: Step 3 only, including the explicit recovery request after the usage-limit interruption. No Step 4 work, deployment, cloud provisioning, remote publication or push is authorized or performed.

Final verification status is recorded below and in [PROJECT_STATUS.md](PROJECT_STATUS.md). The source specification is preserved verbatim in [STEP3_SPECIFICATION.md](STEP3_SPECIFICATION.md).

## A. Implemented functionality

| Requirement | Concrete implementation / evidence |
| --- | --- |
| Preserve the MVP | Same Next.js/FastAPI/PostgreSQL stack, durable worker, storage and ordinary session/video/CSV/replay/annotation paths; regression tests retain the original workflows |
| Scientific audit | Inspected actual SI conversion, time normalization, sampling/gaps, filtering, guards, event suppression, source frames, offset signs, pose visibility and derivative timestamps; see [RESEARCH.md](RESEARCH.md) |
| Video-only inference | Stored-landmark wrist-speed pipeline using real presentation times, visibility/gap gates, fixed torso scale, smoothing, adaptive threshold and prominence; analytic fixture tests and actual MediaPipe integration |
| Improved inertial inference | Preserved legacy `gyro_peak_v1`; added cutoff-scaled guards, measured movement windows, acceleration diagnostics, missing-sample/cadence/jitter/gap quality and explicit strength units |
| Real multimodal processing | Both independent numerical pipelines feed one-to-one temporal association inside continuous common eligible intervals; both source times, disagreement and unmatched observations retained |
| Versioned references | Human annotation-set creation, current set/event revisions, stale-edit/freeze rejection, immutable small snapshots with definition, procedure, labeler, provenance and optional source-video hash |
| Event evaluation | Cardinality-first/minimum-error matching, deterministic ties, configurable inclusive tolerance, TP/FP/FN, precision/recall/F1, signed/absolute per-event errors, mean/median timing error, misses and null rules |
| Reproducible experiments | Durable jobs, frozen input/config/sync/reference fingerprints, artifact checksum verification, versions/runtime identity, results, latency, errors, reuse and forced reruns; old results preserved |
| Challenge and dashboard | Three input-aware modes, actual job states, controls, side-by-side stored results, component signals, prediction/reference lanes, quality/coverage, errors, configuration/provenance and replay seeking |
| Robustness | Seeded sample dropout, SI channel noise, bounded timestamp jitter, contiguous IMU gaps, landmark visibility masking, controlled sync error; derived copies preserve sources |
| Export | Markdown and JSON containing actual manifests/results, question, source/label procedure, configuration, failures, latency, limitations and reproduction request |
| Hardware-free paired lab | Separate synthetic video/analytical landmarks/IMU fixture with shared generator clock and two generated references; explicitly not athlete footage or MediaPipe extraction |
| Denser pose option | Retained 10 Hz extraction and added a 30 Hz target at half-speed playback, with achieved cadence/gaps/executor recorded |
| Reliability | Transaction commits precede HTTP acknowledgement; expired leases/cancellation fence publication; insufficient input differs from successful empty detection; no source bind mounts in production verification |

No required Step 3 software feature is substituted with mocked successful inference. Unavailable real-world data limits experimental validity, not the implemented processing framework.

## B. Algorithms and event semantics

**Video: `video_wrist_speed@1.0.0`.** Convert normalized landmarks to aspect-corrected image coordinates, subtract hip midpoint, and divide displacement velocity by a median valid torso scale. Use actual adjacent times and place velocity at the interval midpoint. Missing/low-visibility observations break the chain. Time-window median smoothing, adaptive MAD height, prominence and actual-time event separation produce `wrist_speed_peak_v1` events. Candidate windows and sampling intervals accompany them. Default thresholds are engineering settings; the exposed adaptive multiplier supports exploratory sensitivity checks.

**IMU: `imu_motion_window@1.0.0`.** Reuse the v1 offline gyro-magnitude/SOS Butterworth peak calculation. Add a conservative `max(0.25 s, 2/cutoff_hz)` boundary guard, connected raw half-prominence windows, duration, peak available acceleration magnitude, and valid-sample/jitter/gap diagnostics. Preserve the original `imu_gyro_peak@1.0.0` endpoint and its measured-event meaning. Magnitude does not identify attachment, world frame, impact or athletic skill.

**Fusion: `multimodal_temporal_association@1.0.0`.** Intersect eligible coverage, then pair gyro and visual candidates one-to-one within the configured agreement gate using the deterministic event matcher. Never associate across missing common-coverage intervals. Emit `multimodal_association_v1` at the IMU anchor, retaining both observed times and signed disagreement. Unlike maxima are not averaged into an unsupported physical timestamp. This is an explicit association baseline, not trained biomechanical reconstruction.

**Evaluation: `ordered_cardinality_error_dp@1.0.0`.** Maximize valid pair count, then minimize total absolute timing error, then apply documented stable tie priorities. One reference cannot be reused. Precision/recall are null with empty denominators; F1 is null only when both lists are empty; timing is null without matched pairs. Full declared intervals retain misses when observations are unavailable. No usable interval fails. Matching is limited to 2,000 events per list; no true-negative or timestamp-only confusion matrix is invented.

Full equations, thresholds, coordinate assumptions, width definitions and edge rules are in [RESEARCH.md](RESEARCH.md).

## C. Scientific validity

The repository has **no independently labeled paired tennis study, validated impact timestamps, cross-player generalization result, or calibrated model confidence**. Strength, visibility, availability and empirical accuracy remain distinct.

The original 1,801-row demonstration and the new 801-row paired lab are deterministic synthetic fixtures. Their metrics test software against known generator centers; they do not measure tennis performance. The paired lab's 241 stored landmark observations are analytical, not MediaPipe estimates. Its rendered clip is a stick figure, not an athlete recording. One legacy descriptive coverage note was corrected accordingly without changing raw/pose artifacts or historical experiment manifests.

The official MediaPipe clip's documented seekable derivative is a separate real-video integration input. Actual browser inference and subsequent stored-pose processing run on it. Its unrelated synthetic IMU source remains mixed and ineligible for paired fusion. No independent tennis reference exists for that clip, so its evaluation is null. An exploratory adaptive threshold produces real wrist-speed events; this is not held-out threshold selection or accuracy validation.

Human independence, source placement and pairing are explicit user attestations. Exact scoring refuses unlike event definitions. A supported proxy-to-human-reference comparison requires an explicit frozen hypothesis. A declared visual reference cannot score a different video. Recording/label collection and blinded procedures are documented; no collection is claimed to have occurred.

## D. Actual experiment workflows and results

The challenge supports inference-only runs, independent-reference evaluation, generated fixture verification, historical sync selection, forced reruns, parameter comparison, and clean/degraded comparisons. References/configurations are frozen per experiment. The UI warns when evaluation protocols differ and sends actual markers back to the existing replay clock.

The local smoke workflow executes 11 conditions through the actual API/worker and writes [step3-local-verification.json](evidence/step3-local-verification.json). Its full per-event results, run IDs/fingerprints and measured processing times are retained there. These are **synthetic software observations only**:

| Condition | Computed events | TP / FP / FN | Fixture F1 | Interpretation |
| --- | ---: | --- | ---: | --- |
| Clean IMU | 2 | 2 / 0 / 0 | 1 | Known generated pulses recovered |
| Clean video | 2 | 2 / 0 / 0 | 1 | Analytical wrist-speed maxima recovered; matched timing error about 16.7 ms |
| Clean association | 2 | 2 / 0 / 0 | 1 | Both source observations contribute; timestamp remains IMU anchor |
| 20% seeded IMU dropout | 2 | 2 / 0 / 0 | 1 | This fixture/seed retained both events; no general robustness claim |
| Gyro noise SD 0.3 rad/s | 2 | 2 / 0 / 0 | 1 | This controlled perturbation retained both fixture events |
| Acceleration noise SD 1 m/s² | 2 | 2 / 0 / 0 | 1 | Expected negative control for a gyro-only event rule; acceleration diagnostics change |
| Timestamp jitter fraction 0.4 | 2 | 2 / 0 / 0 | 1 | Order-preserving irregularity on this fixture |
| Missing IMU window, 1.5–2.5 s | 1 | 1 / 0 / 1 | 0.667 | Missing coverage retains the missed reference |
| Wrist occlusion, 1.5–2.5 s | 1 | 1 / 0 / 1 | 0.667 | One visual association lost |
| IMU sync error +1 s | 0 | 0 / 0 / 2 | 0 | No agreement is manufactured; precision/timing are undefined |
| Full video occlusion | unavailable | not scored | null | Explicit insufficient-observation failure |

These conditions use seed 42. Short numerical processing times on an eight-second fixture exclude queue wait, browser extraction and ingestion; they are recorded observations, not a throughput/SLA benchmark. Reports preserve the complete configuration and data provenance needed to interpret them.

## E. Testing and verification

Final command outcomes are recorded in [TESTING.md](TESTING.md) and machine-readable browser/local evidence: **36 backend tests passed** in the final production API image (zero failures/skips, six deprecation warnings, 18.99 s); native **34 passed / 2 expected FFmpeg skips**; **9 frontend tests passed**; strict TypeScript, lint, Ruff, generated contracts and migration consistency passed; production builds passed; **5 browser tests passed**, zero failures/skips/flaky tests, **60.3 s**. The local application smoke and all 11 actual synthetic conditions passed their assertions, including preservation of existing Step 2 data. Six backend deprecations, the existing Vite advisory and Playwright color-environment warning remain documented. No new security advisory scan or remote CI result is claimed.

The final real-clip run measured 87 worker frames at an achieved 14.53 Hz against a 30 Hz target, with a 400 ms maximum gap, and 48 main-thread fallback frames at the standard target. Actual stored-pose processing produced nine wrist-speed events under the recorded exploratory configuration; accuracy remained unavailable. Achieved rate and events are specific to this integration run, not real-world performance claims.

The meaningful new coverage includes analytical feature/event expectations, exhaustive brute-force checks of matching objectives, duplicates/empty/tolerance/timing cases, no derivatives or association across gaps, cutoff guards, deterministic corruption/source preservation, true PostgreSQL ownership/frozen revisions/reruns/evaluation/deletion, expired-lease/cancel fencing, actual upgrade/downgrade/re-upgrade preservation, and transaction visibility at HTTP-header time with rollback failure handling. Browser tests use real processing and actual MediaPipe; only worker initialization is deliberately failed to test the actual fallback.

The original interrupted work was not blindly accepted. Recovery found and fixed ambiguous accessible locators, a real tab overflow, a stale annotation-freeze refresh race, two encoding-damaged strings, inapplicable corruption controls, visual-source mismatch, association across missing common coverage, and a directly observed response/commit race. Tests were strengthened rather than weakened. No remote CI run is claimed.

## F. Local application verification

Docker Desktop must run with Linux containers. From PowerShell:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open `http://127.0.0.1:3000`. API docs are at `http://127.0.0.1:8000/docs`; PostgreSQL binds locally on port 5433. Existing named volumes are preserved; startup automatically upgrades the additive migration. No `.env` is required for the documented local defaults.

Open the original demo to verify MVP replay, then **Sensor Fusion Challenge → Open paired synthetic lab**. Freeze its generated reference revision, select it, run all three modes, then introduce a one-second sync error. Inspect matched/missed events, quality, both component signals, exported reports and replay markers. For a real clip, extract MediaPipe pose, select Video only, and inspect the actual signal/threshold settings without claiming accuracy when labels are absent.

Detailed commands, input acquisition, API usage and safe paired-recording collection are in [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md), [EXPERIMENTS.md](EXPERIMENTS.md), [API.md](API.md), and [TESTING.md](TESTING.md). Screenshots/traces remain local ignored artifacts under `docs/evidence` and `apps/web/test-results`. The original Step 2 demo UUID and its 1,801 samples remain accessible.

## G. Outstanding limitations

- No independent paired tennis data, impact reference, trained movement classifier, calibrated probability, held-out cohort evaluation or demonstrated fusion improvement on athletes.
- Browser pose samples presented frames. Achieved cadence can be substantially below target; gaps, occlusion, camera motion and projection limit event localization. Physical mobile devices and non-Chromium browsers remain unverified.
- Repeating browser extraction can produce different sampled tracks and event counts. Numerical reproducibility applies to the same frozen landmark artifact/configuration, not an assumption that playback-driven extraction recreates identical observations.
- Offset-only synchronization; no automatic cue fitting or clock-drift correction. Pairing/independence/placement are documented user declarations. Quantitative inter-rater uncertainty and bootstrap/cohort summaries are not implemented; ambiguity can be recorded in notes.
- Descriptive raw crossing windows are not validated swing segmentation. Acceleration may include gravity. Torso-normalized image motion is not metric body/racket motion.
- Per-session bounded research rather than a large-study system: 2,000-event matching cap, latest-50 default experiment history (API max 200), one local worker, no batch cohort analytics or general job-retry UI. Sources and small results are referenced, not large duplicated datasets.
- Replay's initial pose response is capped at 10,000 frames. Very long densely sampled tracks can lack a late overlay in that initial view; numerical inference reads the full stored track. Windowed replay fetching remains a targeted later performance improvement.
- No automatic video transcoding or guaranteed random-access validation. The integration clip derivative is explicitly documented; portrait/rotated/VFR/nonzero-origin/max-size real recordings are not fully exercised.
- Local single-user access only; no public identity/deployment hardening. Existing development-tool advisories and deprecation warnings are documented separately from runtime capability. No new dependency was added for Step 3.

## H. Step 4 recommendations and stage gate

After separate authorization, prioritize physical phone/browser collection tests, capture ergonomics, wider codec/device coverage, targeted accessibility/performance work and clearer collection/annotation guidance. A consenting, placement-controlled paired pilot with independent blinded labels is needed before any empirical tennis accuracy or generalization claim. Add cue/drift analysis only with explicit uncertainty and test evidence. Keep future product feedback within validated evidence.

No Step 4 implementation, deployment, GitHub push or cloud provisioning occurred. The Step 3 local checkpoint contains this report; obtain its identity with `git log -1 --format=%h`. The application services remain running locally with the retained volumes. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the final stage gate.
