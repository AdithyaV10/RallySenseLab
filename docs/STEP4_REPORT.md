# Step 4 completion report

Local software acceptance is complete. This report distinguishes verified application behavior from physical-device and real-world research limitations. The staged review gate is recorded in PROJECT_STATUS.

## A. Executive summary

The existing research platform now has a real browser collection workflow, source-level provenance, collection metadata revisions and cue-based pairing evidence. Replay has bounded pose-window loading, signal zoom, time stepping, explicit clocks and view preferences. Challenge results add failure navigation, compatibility-guarded deterministic comparisons and print-friendly actual-result reports. Readiness diagnostics and fail-closed read-only visibility support safer operation while preserving the local architecture.

## B. Implemented source areas

| Area | Source |
| --- | --- |
| Device motion normalization, missing values, raw/SI export, permissions and interruption | `apps/web/src/features/capture/motion.ts`, `motion-capture.tsx` |
| Actual browser camera encoding and paired setup/import/metadata/cue UI | `features/capture/camera-capture.tsx`, `paired-workflow.tsx`, `sync-editor.tsx`, `/record` |
| Collection/evidence schema and additive migration | API `models.py`, `schemas.py`, `migrations/versions/0003_collection_readiness.py` |
| Browser streamed WebM metadata repair with original retained | API `media.py`, `jobs.py` |
| Windowed replay, controls, actual timestamps, optional seek/backpressure | `features/replay/workbench.tsx`, `pose-extraction.ts`, `signals-chart.tsx` |
| Independent sets, timestamp/note editing, blind labeling and existing freeze workflow | `features/replay/event-panel.tsx`, `features/research/reference-manager.tsx` |
| Failure explorer, compatible comparison deltas and actual-result print report | `features/research/failure-explorer.tsx`, `insights.ts`, `print-report.tsx`, `results.tsx` |
| Live diagnostics, safe source-job retry, worker heartbeat/health | API `api/diagnostics.py`, `api/sessions.py`, `worker.py`, `check_worker.py`; web `/diagnostics` |
| Read-only policy and workspace gate | API `policy.py`, session ownership guard/middleware; web `src/proxy.ts`, capabilities and proxy route |
| Opt-in trusted phone HTTPS and production preparation | `scripts/start-phone-https.ps1`, `infrastructure/compose.production-prep.yml` |

## C. User experience and local visual evidence

The charcoal/teal identity is retained. Landing has direct ordinary and paired-demo entry points. Dismissible guidance explains actual worker operations. Collection has four visible stages, explicit source provenance, metadata and live observations. Replay adds event-context playback, 100 ms seeks, observed-pose-frame stepping, signal zoom, source-clock readouts, prediction toggles and saved axes/marker/rate/window preferences. Exact decoded frame-by-frame stepping is not promised. Independent sets, editable timestamp/note, blind mode and the existing reference-freeze procedure remain available.

Failure explorer uses stored matched/unmatched/missed events and observation intervals. Expected failed robustness experiments remain in their result/history rather than appearing as an unrelated workspace-wide failure. Source processing history defaults to eight recent rows and can expand. Reports show actual stored values, expandable reproducibility metadata and full printed manifests.

Actual rendered evidence is local and ignored by Git:

- `docs/evidence/step4-after-{landing,library,capture,replay,research,method,diagnostics,report}-{desktop,tablet,mobile}.png`
- `step4-after-paired-collection-{desktop,mobile}.png`
- `step4-readonly-collection.png`
- `step4-synthetic-report.pdf` (generated from an actual synthetic experiment, not a physical study).

Desktop, tablet and mobile screenshots were inspected, including collection/replay/research/report views. The final layout check covers eight routes at 1440?1000, 834?1100 and 390?844, with no page overflow. Inspection corrected the collection heading hierarchy, reference-set spacing, excessive job-history height and report manifest presentation. Browser emulation is layout evidence, not physical-device validation. Machine-readable visual/performance evidence is `evidence/step4-final-performance.json`; baseline is retained separately.

A same-history local profile measured **3,335,773 bytes** for 50 full results versus **217,542 bytes** for the same 50 summaries, plus **63,707 bytes** for one selected full result (281,249 combined; approximately 91.6% fewer bytes). Three local requests per representation had median client request times 302.3 ms and 170.9 ms respectively. This includes serialization/network/client overhead and concurrent local workload; it is not an isolated database or production-throughput benchmark. See `evidence/step4-history-profile.json`. Browser research navigation resource bytes also fell from approximately 4.41 MB in the baseline to 1.03 MB, with different accumulated fixture histories; do not interpret that comparison as a controlled speed benchmark.

## D. Real-world collection readiness

Software supports actual incoming DeviceMotion events, user-gesture permission, explicit acceleration quantities/device axes/angular-rate conversion, duration/cadence/missing-channel inspection, raw CSV/metadata export and normal worker ingestion. Camera recording uses actual MediaRecorder and worker validation, with a bounded remux for streamed WebM lacking duration. Pseudonyms, placement/attachment/device/task/conditions and pairing evidence are operator declarations. The pilot playbook describes a safe controlled protocol; no physical recording or consented tennis dataset was collected here.

Physical iOS/Android, phone trust installation, background behavior across browser versions, and actual physical camera/sensor behavior remain unverified. In-memory unsaved buffers are not durable. CSV and external camera upload remain the fallback. See DATA_COLLECTION and REAL_WORLD_PILOT.

## E. Computer vision and inference

The final real permitted-clip browser run executed both paths with the actual pinned Tasks Vision 1.2.0 CPU runtime and the same uploaded video:

| Method at 30 Hz target | Processed frames | Achieved media cadence | Largest observed gap |
| --- | --- | --- | --- |
| Playback-driven worker | 83 | 13.85 Hz | 360 ms |
| Seek + processing backpressure | 149 | 24.67 Hz | 80 ms |

The same browser suite also forced worker initialization failure and completed **49** sampled frames using the actual main-thread fallback. Exact track identities/quality are in `evidence/step4-browser-verification.json`. An earlier separate seek run is retained in `step4-seek-pose.json`. Counts describe these runs and source presentation cadence, not analysis throughput, an exhaustive decode guarantee or tennis accuracy. Source cadence limits a nominal 30 Hz target. Local workload/scheduling affect results; cross-device generalization is unverified.

Seek/backpressure waits for processing before requesting the next observation and records the presented frame timestamp rather than the requested seek time. Duplicate/nonmonotonic observations are not invented or padded. Playback sampling remains available, with a clear retry instruction if paused seek callbacks are incompatible. The UI reuses stored tracks for replay/inference; new extraction is explicit. Quality includes achieved cadence, detections and gap warnings. Temporal coverage and landmark visibility are not calibrated confidence or ground-truth biomechanics.

Scientific algorithms/event meanings are unchanged: angular-speed maxima, image wrist-speed maxima, and explicit one-to-one temporal association. Unlike human event definitions need a proxy hypothesis; no eligible reference means no accuracy metrics. Synthetic clean/corrupted scores remain software verification. Collection profile, video binding and cue evidence are frozen into future manifests. Existing manifests/results are not rewritten.

## F. Engineering improvements

The additive migration preserves existing rows. Replay can fetch late dense frames beyond the former initial cap. Experiment history now uses a response-only summary projection and full detail for selected results rather than polling all dense signals. Safe retries create new source-validation jobs without modifying failed scientific results. Actual worker heartbeat differentiates ready/stale/unknown. API hides SQL parameter values, bounds uploads, provides request IDs and structured safe timing logs. Default ports remain loopback; trusted phone mode requires an explicit private IP, provided trusted cert/key and workspace password. No LAN listener or cloud service was started.

Read-only mode requires explicit builtin synthetic fixture IDs, hides unlisted session-owned objects and blocks mutations. It is not multiuser security or a privacy scrubber. Future public demos must use fresh dedicated fixture-only volumes and independent audit. See DEPLOYMENT.

## G. Tests and verification

All results are local; no remote CI or independent Step 5 audit is claimed.

| Exact command / scope | Actual result |
| --- | --- |
| `docker compose build api web` and final incremental API/web builds | PASS; packaged production sources, nonroot app processes |
| `docker compose up -d --no-build` | PASS; retained volumes, API/DB/worker healthy, web serving loopback |
| `docker compose exec api pytest -q --tb=short --basetemp=/tmp/step4-final-source -o cache_dir=/tmp/step4-pytest-cache` | **42 passed, 0 failed, 0 skipped**, 13.10 s; six existing deprecation warnings |
| `docker compose exec api alembic current` / `alembic check` | `0003_collection_readiness` head; no new upgrade operations |
| `uv run --project apps/api ruff check apps/api/src apps/api/tests apps/api/migrations` | PASS |
| `npm.cmd --prefix apps/web run typecheck` | PASS; installed Next route types and strict TypeScript |
| `npm.cmd --prefix apps/web run lint` | PASS |
| `npm.cmd --prefix apps/web test` | **15 passed / 5 files**, final run 4.63 s |
| `node scripts/check-contracts.mjs` | PASS; generated schema matches Pydantic OpenAPI |
| `npm.cmd --prefix apps/web run test:e2e` | **8 passed, 0 failed, 0 skipped, 0 flaky**, 96.996 s; production Chromium |
| Final focused ingestion: `npm.cmd --prefix apps/web run test:e2e -- capture.spec.ts workflow.spec.ts -g "browser motion|permission|browser camera|session creation"` | **4 passed**, 33.5 s after final source-panel polish; no skips/flaky failures |
| Local production workspace-gate/read-only integration | PASS: unauthenticated 401, authorized 200, two approved fixtures, private session 404, mutation 403 READ_ONLY_DEMO, capture and upload controls disabled |
| PowerShell phone-helper parser / Compose default and production-prep `config --quiet` | PASS; preparation only, no LAN listener or deployment |
| `uv run --project apps/api python scripts/verify-local.py --output docs/evidence/step4-readiness-verification.json` | PASS: HTTP 200/readiness, original 1,801-row Step 2 source |
| `uv run --project apps/api python scripts/verify-research.py` (Step 4 evidence retained separately) | PASS: 11 actual software conditions, original Parquet read, frozen result export and source preservation |
| `uv run --project apps/api python scripts/check-preservation.py verify` | PASS: original 82 experiments, 11 references, 41 artifacts and 10 sessions retain baseline hashes; additions allowed |
| Local Markdown links and Git whitespace | PASS at review; final checkpoint status recorded in PROJECT_STATUS |

The container suite includes real PostgreSQL ingestion/metadata/revision conflicts, cue residuals and ownership, safe retry idempotence, heartbeat readiness/staleness, source burst bounds, read-only direct-source/job/private-ID restrictions, late >10,000-frame window retrieval, summary projection immutability, streamed WebM remux/original retention, numerical research and migration preservation. Disposable schemas/temp artifacts do not reset live tables.

Browser flows include synthetic DeviceMotion transport/unit mapping/interruption/save/normalization/inference, denied/absent API fallback, actual synthetic camera encoding/probe/remux, CSV import and cue revision, ordinary replay/annotation/sync reload, three-mode/corruption comparisons/failure seeking/export/PDF, independent label-set eligibility, actual MediaPipe worker/seek/fallback and stored-pose inference. The positive motion fixture isolates Chromium's initial trusted all-null event and explicitly declares injected data synthetic. Backend successes are not mocked. No physical phone or camera verification is implied.

Earlier failures were resolved rather than hidden: a fixture incorrectly assumed streamed FFmpeg output lacked duration (fixed with explicit `-live 1`); browser test navigation/duplicate-locator assumptions were corrected; camera validation exposed a real missing-duration issue (fixed by retaining-original remux); an overlapping Playwright run collided with the artifact directory (acceptance serialized); initial test-fixture type fields were fixed. The temporary read-only check was rerun after its containers were ready. Native baseline post-migration regression was 34 passed / two expected FFmpeg skips; the complete final acceptance above uses the FFmpeg-equipped container and skips none.

Advisories: **zero runtime npm findings**, **10 moderate development-tool findings** propagated from minimatch glob amplification through lint tooling, no high/critical npm finding; **35 pinned Python packages checked, zero known vulnerabilities**. See `evidence/step4-dependency-audit.json` and TESTING for commands/advisory link. The automatic suggested fix changes major lint/framework versions and was not applied blindly. This is not a container OS vulnerability scan or proof of public security.

Warnings retained: Starlette TestClient/httpx deprecation, five Alembic path-separator notices, Vite future native-config-loader advisory, Playwright NO_COLOR/FORCE_COLOR warning. Historical Step 3 evidence is retained; both smoke scripts now accept `--output` to keep later evidence separate.

## H. Demonstration

Start with `docker compose up -d --build`, open `http://127.0.0.1:3000`, select the ordinary or paired synthetic demo, follow/dismiss guidance, freeze fixture references and run modes. Introduce a controlled failure, select compatible runs, inspect failure timestamps and open Print-ready report. For capture create a session in Collection studio, choose source quantities/origin, save or import observations, inspect quality, record cue alignment, then open replay/Challenge. See INTERVIEW_WALKTHROUGH for exact explanation.

## I. Deployment preparation

The recommended initial topology is the tested containers, durable worker, PostgreSQL and private persistent disk behind reviewed TLS/access. Split Vercel/API/managed DB/object storage requires a storage/direct-upload adapter; the present proxy is incompatible with Vercel function payload bounds. No public deployment, provisioning, push or publication has occurred.

## J. Known limitations and deferred optional work

- Physical iOS/Android, actual phone trust installation, sensor delivery under device/browser variants and a consented paired tennis pilot require participant hardware; none was fabricated.
- Capture is bounded in-memory foreground work. Unsaved data can be lost on SPA navigation/reload; there is no automatic durable draft/background recorder. Permission/API/channel/codec support varies. Use CSV/external camera import when necessary.
- Offset-only alignment, attested pairing/placement/consent, image-derived pose and unvalidated event proxies remain. There is no drift fit, calibrated orientation/racket trajectory, impact detector, trained tennis classifier or demonstrated real-world fusion benefit.
- Frame controls are explicit time seeks or stored observed-pose steps, not an exhaustive decoded-frame editor. Seek sampling was verified in Chromium on the permitted clip; other browsers, rotated/VFR/nonzero-origin/max-size source coverage remain unverified.
- No structured inter-rater/cohort confidence-interval analysis, public account system, disposable multiuser mutation sandbox, S3 adapter, distributed quotas or public security certification. Optional side-by-side session replay/sharing was not added.
- Public/demo preparation remains subject to Step 5 review and fresh isolated fixture-only volumes. The single workspace password and local token are not multiuser security. Backup/restore is documented; no destructive restore was performed against the user's live project.
- Ten moderate development-only dependency findings and unperformed container OS scanning remain explicit review items. Existing narrow source retries do not promise generic recovery for every processing/cleanup failure.

No important required Step 4 software feature remains unfinished. Physical verification and public readiness limits above are retained for review; optional enhancements were deferred. Step 5, deployment, publication and pushing remain unauthorized.

## K. Step 5 review focus

Review scientific proxy semantics, reference independence and matching; physical sensor compatibility and placement/timing uncertainty; capture interruption/loss; container remux/probe file boundaries; session allowlisting/privacy and single-workspace authentication limits; resource/retention/backup behavior; readonly exports; and immutable source/result preservation. Step 5 is not begun by this implementation or these developer checks.

**STEP 4 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 5.**
