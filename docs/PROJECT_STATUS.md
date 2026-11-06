# Project status

Updated: 2026-11-05, America/New_York.

## Authorization and stage gate

- Current and last completed stage: **Step 3 - advanced inference, sensor association, and scientific evaluation**.
- State: **complete; stopped at the mandatory Step 3 review gate**.
- Authorization: the preserved [Step 3 specification](STEP3_SPECIFICATION.md), the explicit November 5 recovery request, and the instruction to continue after Docker startup.
- Next authorized stage: **none**. Step 4 requires separate user authorization.
- No Step 4 implementation, deployment, publication, remote push, GitHub synchronization or cloud provisioning occurred.
- Step 2 checkpoint: `7ce77c6`. The Step 3 checkpoint is the local commit containing this status/report; obtain its ID with `git log -1 --format=%h`.

## Implemented

The working Next.js/FastAPI/PostgreSQL MVP is preserved. Step 3 adds actual stored-pose wrist-speed inference, enhanced measured IMU windows/quality, explicit temporal association using both modalities, frozen reference revisions, mathematically defined event evaluation, durable reproducible experiments, controlled corruption, the Sensor Fusion Challenge/results dashboard, and actual-result Markdown/JSON export.

Algorithms are `imu_motion_window@1.0.0`, `video_wrist_speed@1.0.0`, and `multimodal_temporal_association@1.0.0`. Output meanings remain distinct: `gyro_peak_v1`, `wrist_speed_peak_v1`, and `multimodal_association_v1`. None is automatically a confirmed tennis swing or ball impact. Unlike reference definitions require an explicit proxy hypothesis. Missing references give no accuracy metrics. Mixed unrelated inputs cannot run paired fusion.

Reference snapshots freeze one set revision/event definition with provenance and labeling metadata. Later edits do not rewrite experiments. Manifests preserve input identities/hashes, parameters, alignment/reference revisions, algorithm/code/dependency/runtime identity, seed and evaluation interval. Results preserve events, quality/coverage, per-event errors, metrics, measured latency and failures. Dense sources are referenced rather than duplicated.

The paired synthetic lab renders a stick figure and persists analytical landmarks plus generated IMU pulses on a shared clock. It is explicitly not athlete footage or MediaPipe output. Actual MediaPipe remains separately verified on the official clip's seekable derivative. Extraction supports the original 10 Hz path and a denser 30 Hz target with slower playback, recording achieved cadence/gaps.

## Recovery audit and integration fixes

All uncommitted work from the interrupted session was inspected and preserved. Docker was restored without deleting volumes. The additive migration `a496e751b8a9` is valid and applied; a real migration test preserves an MVP row across upgrade, checks consistency and exercises downgrade/re-upgrade.

Recovery corrected mobile tab overflow, annotation refresh/freeze racing, two damaged text encodings, inapplicable corruption controls, visual-reference source mismatch, cross-gap event association, legacy generated-source wording and a directly observed response/commit race. Database transactions now commit before HTTP success headers; a separate PostgreSQL connection verifies visibility at the ASGI send boundary, and injected persistence failure returns an error with no persisted row. Numerical semantics and raw observations remain preserved.

## Final verification

| Check | Actual result |
| --- | --- |
| Production API/worker and Next.js builds | PASS; final packaged sources, no API source bind mounts |
| Container backend suite | **36 passed, 0 failed, 0 skipped**, 18.99 s; six deprecation warnings |
| Native backend suite | **34 passed, 2 expected native-FFmpeg skips**; equivalent tests pass in container |
| Frontend unit tests | **9 passed**, 3 files |
| Strict TypeScript and installed Next route types | PASS |
| ESLint and Ruff | PASS |
| Generated OpenAPI/TypeScript contract consistency | PASS |
| Alembic head / consistency | `a496e751b8a9`; no new upgrade operations |
| Production Chromium browser suite | **5 passed, 0 failed, 0 skipped, 0 flaky**, 60.3 s |
| Ordinary local application smoke | PASS: HTTP 200/readiness and preserved Step 2 demo |
| Real synthetic research smoke | PASS: 11 conditions, strict read-after-create, source preservation, original Parquet read and actual report export |

The original Step 2 demo remains `3a29c800-519d-437e-85b0-5c7d712253f0`, with 1,801 samples read from its retained Parquet. The new paired fixture is `d4eb12ca-ad5c-453a-b8ff-fc59ec5f6472`, with 801 generated IMU rows and 241 analytical landmark observations. Existing sessions and original source volumes were retained.

Final actual real-clip evidence: 87 worker frames, achieved 14.53 Hz against a 30 Hz target, maximum gap 400 ms; 48 main-thread fallback frames at the standard target. The recorded exploratory video configuration produces nine wrist-speed events, with evaluation null. These values describe this integration run and do not establish tennis accuracy.

Synthetic clean modes recover two generator events. Missing-window and occlusion conditions retain missed references; +1 second sync error removes both associations; full occlusion explicitly fails without metrics. All values come from stored computations. See [local conditions](evidence/step3-local-verification.json), [browser summary](evidence/step3-browser-verification.json), and [readiness](evidence/local-verification.json). Screenshots and traces are local ignored artifacts. No remote CI result is claimed.

## Known limits

- No independently labeled paired tennis study, impact validation, calibrated confidence, trained movement classifier, held-out player evaluation or demonstrated real-world fusion improvement.
- Sampling targets are not exhaustive decoding guarantees. Visibility, gaps, camera geometry, device/browser scheduling and perspective limit localization. Physical iOS/Android and non-Chromium runs remain unverified.
- Offset-only alignment; no automatic drift fitting. Pairing, placement and label independence are user attestations. No cohort/bootstrap summaries or structured inter-rater uncertainty computation.
- Matching caps each list at 2,000 events. Default experiment history returns the latest 50 (API maximum 200). Initial replay pose fetching caps at 10,000 frames; long dense tracks can lack late overlays while inference still reads the full artifact.
- No automatic transcoding; full rotated/portrait/VFR/nonzero-origin/max-size real-recording coverage is not established. Existing CSV locale/ZIP and general job-retry limits remain.
- Single-user loopback application. Public identity/security/deployment readiness is not claimed. Existing deprecation/tooling warnings and the historical dependency-advisory scan are documented in TESTING.

## Review locally and next stage

Services are left running locally with retained database/artifact volumes. If stopped, use:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open `http://127.0.0.1:3000`, enter a session and select **Sensor Fusion Challenge**. Choose **Open paired synthetic lab**, freeze the generated references, run/compare the modes and try a controlled sync error. The full report is [STEP3_REPORT.md](STEP3_REPORT.md); methods are in [RESEARCH.md](RESEARCH.md); the practical workflow and real paired-collection guide are in [EXPERIMENTS.md](EXPERIMENTS.md). Exact tests/startup/API details are in [TESTING.md](TESTING.md), [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md), and [API.md](API.md).

Step 4 recommendations are recorded, but no Step 4 work is authorized or begun. Stop after this Step 3 handoff and await the user's explicit instruction.

**STEP 3 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 4.**
