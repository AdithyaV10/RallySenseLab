# Step 2 implementation report

Date: 2026-11-03, America/New_York. Local-only implementation of the approved full-stack foundation. This report distinguishes functioning software from unvalidated scientific hypotheses. Final checkpoint and production verification details are recorded in PROJECT_STATUS after verification.

## Implemented inventory

| Capability | Implementation and evidence |
| --- | --- |
| Full stack | Next.js 16.4.4 / React 19.3.1 / strict TypeScript; FastAPI 0.162.0 / Python; actual PostgreSQL 17.11; frozen Alembic migration; Docker Compose with API, worker, database and standalone web image |
| Session library | Create/list/load/delete, declared recorded/synthetic/mixed origin, handedness, capture metadata; immediate tombstone and durable file cleanup |
| CSV ingestion | Canonical and explicit-column UTF-8 CSV mapping, separate source clocks, SI unit normalization, finite-value/time checks, missing channels/values, rate/jitter/gap summaries including per-stream cadence, compressed Parquet and raw-byte retention |
| Signal processing | Real vector magnitude, segment/gap handling, resampling, fourth-order Butterworth SOS forward/backward filtering, configurable adaptive height/prominence, global time-based peak separation, actual event timestamps and strengths |
| Event semantics | `gyro_peak_v1` identifies a measured angular-speed maximum. The UI, stored output and documentation explicitly say its tennis interpretation is unvalidated. No automatic confirmed swing/impact label |
| Video ingestion | Bounded private upload, actual FFprobe validation of codec/container/dimensions/duration, safe generated keys, HTTP Range delivery, browser decoding errors |
| Actual pose extraction | Installed MediaPipe 1.2.0 API inspected; pinned Lite model/WASM served locally; classic worker with transferable ImageBitmap; actual presentation timestamps and missing detections; explicit CPU main-thread initialization fallback |
| Pose persistence/features | Idempotent typed batches, monotonic-time/source-duration checks, compressed Parquet, coverage summaries, no-person frames; actual torso-normalized image wrist radius/velocity and 2D elbow-angle features with visibility/gap gates |
| Synchronized replay | Shared media/synthetic clock, timeline and plot scrubbing, event/reference markers, speed controls, nearest-valid pose overlay, contained-image/letterbox geometry, xyz toggles and missing-data gaps |
| Synchronization | Immutable manual offset revisions, clear sign convention, persisted mapping, stale-alignment notice, rerun for new results; old runs remain tied to old mappings |
| Annotations | Independent human add/edit/delete workflows and categories; revision conflicts; immutable generated references; blinded mode hides signals/predictions/navigation |
| Synthetic demo | Deterministic 1,801-row, 100 Hz, 18-second input; real import/inference jobs; five computed gyro peaks and generated reference markers; labeled programmatic animation, not MediaPipe output or athlete validation |
| Reliability/security foundation | PostgreSQL leases, heartbeat/reclaim, stale-worker fencing, cancellation/deletion checks, same-session composite FKs, safe errors, bounds, local token proxy, Host/Origin checks, no-store private responses, orphan/abandoned-track maintenance |
| Developer handoff | npm/uv locks, generated OpenAPI/TypeScript contract and drift checker, pinned base images/model hashes, meaningful tests, local screenshots, CI definition and startup documentation |

## Verification

Verified backend: **17 tests passed in the Linux API container**, including FFprobe and range delivery. Native Windows: **16 passed, 1 expected skip** because no native FFmpeg binary exists on PATH. The equivalent video check passes in the supported container path. Backend lint passes; `alembic check` reports no new upgrade operations.

Verified frontend: **6 unit tests passed**, strict type checking and lint passed, and the generated API contract matches Pydantic OpenAPI. Browser tests cover the complete synthetic workflow, fresh CSV session ingestion/deletion, and actual MediaPipe video processing with both worker and fallback. The final production-mode Chromium suite passed all 3 tests in 37.6 seconds, including 0 skips. Both pinned container builds and the local readiness/demo smoke check passed; PROJECT_STATUS records restart/persistence verification. [TESTING.md](TESTING.md) contains reproducible commands and test scope.

The official MediaPipe documentation clip and its explicitly generated seekable H.264 derivative are only integration inputs. One observed run processed 48 sampled frames in the worker and 48 in the forced-fallback path; frame counts vary with browser scheduling and are stored per track. These observations establish software execution, not tennis accuracy or exhaustive decoding. The model checksum is `59929e1d1ee95287735ddd833b19cf4ac46d29bc7afddbbf6753c459690d574a`.

The combined-source browser workflow uses a recorded documentation clip and an explicitly declared synthetic sensor stream in a **mixed** session. It verifies a +0.1-second mapping by seeking the visible video to the computed signal time. It does not claim these independent inputs were physically synchronized recordings.

## Technical choices and changes from the blueprint

The approved architecture is preserved. PostgreSQL stores metadata/small events; immutable raw files and dense Parquet reside in the local volume. A single durable Python worker supplies real processing states without a broker. Browser CPU pose extraction is the primary path.

The installed MediaPipe package exposes a classic `Vision` IIFE bundle. A classic worker avoids module-worker/importScripts compatibility problems. Worker initialization failure selects a clearly reported main-thread fallback; mid-track failure does not splice tracker state. Both execution paths have processed actual video locally.

Mapping confirmation uses a local header preview and one server submission, followed by a durable validation/normalization job. The proposed separate server preview/commit resource is deferred. Browser pose batches use JSONB only as bounded temporary staging; finalized dense tracks are Parquet. Detailed decisions are recorded in [DECISIONS.md](DECISIONS.md).

The user's explicit measured-event requirement supersedes the blueprint's provisional automatic swing-apex output. Research reference definitions remain unchanged, but comparison to gyro peaks requires an explicit tested hypothesis in Step 3.

## Setup problems and corrections

Docker was reachable at Step 2 start; actual PostgreSQL and container health checks replaced the earlier unverified environment state. FFprobe is provided by the API container, resolving native binary absence for the supported workflow. The sandbox shell setup failure still required elevated local execution; Git uses a repository-scoped ownership exception without changing global trust settings.

Tests exposed and corrected a vector-magnitude expectation, Windows pytest temp permissions, test ORM lifetime/import errors, a generated migration type qualification, incomplete blinded-mode hiding, unreliable tooltip-based chart seeking, and an upstream verification clip that decoded sequentially but failed random access. Served full/ranged bytes matched the source; FFmpeg confirmed bad reference frames. The original is preserved and an explicitly identified seekable derivative is used for final playback verification. Browser assertions now check actual post-seek advancement and absence of media errors. Chart navigation now maps actual SVG plot coordinates through the installed inverse-scale hook. See TESTING for the distinction between harness fixes and application fixes.

## Known limitations and remaining work

- No tennis validation cohort or independent tennis event labels. Gyro peaks are signal observations; no swing-classification or impact-detection claim is supported.
- Pose extraction samples visible browser presentation frames at a target 10 Hz; it is not exhaustive decoding. Background throttling, occlusion, model error and browser capability affect coverage. Interrupted extraction requires a new track.
- Browser verification is Chromium on this Windows host. Physical iOS/Android capture and other browsers are unverified. Live phone recording is Step 4; CSV import works now.
- Manual offset only. Automated cue alignment and drift estimation remain Step 3. Arbitrary sensor/camera coordinate-frame calibration is not implemented.
- World landmarks are model estimates. Image-space features are not calibrated 3D biomechanics or professional coaching measurements.
- Human labels are editable drafts. Frozen label sets, experimental splits/manifests, event matching, metrics, video-event inference, fusion, challenge and scientific reporting remain Step 3.
- CSV requires explicit mapping and decimal-point numeric text. ZIPs, automatic locale repair, video transcoding and exhaustive phyphox format recognition are not implemented. Source video limits are enforced; codec support still depends on the active browser.
- Library list is capped at 100 latest sessions; viewport/data-window performance for much larger studies is not benchmarked. Large recordings and UI accessibility need broader Step 4 verification. Real portrait/rotated, variable-frame-rate and nonzero-origin clips were not directly exercised; contained-image geometry has a mathematical unit test.
- Failed imports retain raw sources until session deletion. General job-retry UI is not implemented; investigate errors and submit corrected inputs/new configurations. Maintenance uses a 24-hour grace period and runs at startup/hourly.
- Single-user loopback runtime. Public identity, multiuser ownership, quotas, deployment hardening and final security audit are future work. No deployment or image publication is authorized.
- npm reports 17 moderate development-tooling advisories and indirect lint peer warnings; runtime-only audit reported zero advisories. Starlette/httpx and Vite config warnings are recorded in TESTING. No blanket security/readiness claim is made.

## Files and continuation

`apps/api/src/rallysense` separates HTTP routers, models/schemas, storage, jobs/worker, CSV/signal numerics, provenance and pose features. `apps/api/migrations` contains the explicit initial schema, and `apps/api/tests` exercises the actual database and numerical behavior. `apps/web/src/features` separates ingestion, replay, events, pose extraction and media; `src/lib/schema.d.ts` is generated. `packages/shared-contracts` holds OpenAPI. `data/fixtures` and `data/assets.lock.json` preserve the software fixture and asset identities. `scripts`, `infrastructure` and `.github/workflows` provide verification/build workflows.

Start with [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md), [API.md](API.md), and [PROJECT_STATUS.md](PROJECT_STATUS.md). Step 3 must review the real numerical implementation and proxy/reference assumptions before adding video-event inference, fusion and evaluation. It requires explicit authorization. Nothing has been pushed or deployed.
