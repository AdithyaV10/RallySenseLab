# Verification

All results refer to local software checks, not a tennis accuracy study. Synthetic fixture scores are explicitly software verification. No independent paired tennis or coaching validation is claimed.

## Step 3 final acceptance, 2026-11-05

| Actual command / scope | Result |
| --- | --- |
| `docker compose build api web`, followed by final `docker compose build api` / `docker compose build web` after fixes | PASS: production API/worker and standalone Next.js images |
| `docker compose up -d --no-build` and final API/worker recreation | PASS: retained real PostgreSQL and artifact volumes; production API has only its artifact-volume mount, no source bind mounts |
| `docker compose exec api pytest -q --tb=short --basetemp=/tmp/rallysense-step3-acceptance-final` | **36 passed, 0 failed, 0 skipped**, 18.99 s; six deprecation warnings |
| From `apps/api`: `uv run pytest -q --tb=short --basetemp=../../storage/pytest-step3-final-native` | **34 passed, 2 skipped**, 18.19 s; native FFmpeg absent; both equivalent tests pass in the container |
| `uv run --project apps/api ruff check apps/api/src apps/api/tests apps/api/migrations` | PASS |
| `npm.cmd --prefix apps/web run typecheck` | PASS: installed Next route generation plus strict TypeScript |
| `npm.cmd --prefix apps/web run lint` | PASS |
| `npm.cmd --prefix apps/web test` | **9 passed**, 3 files |
| `node scripts/check-contracts.mjs` | PASS: generated OpenAPI/TypeScript match Pydantic |
| `docker compose exec api alembic current` / `alembic check` | `a496e751b8a9` head; no new upgrade operations |
| `npm.cmd --prefix apps/web run test:e2e` | **5 passed, 0 failed, 0 skipped, 0 flaky**, 60.3 s, production Chromium |
| `uv run --project apps/api python scripts/verify-local.py` | PASS: HTTP 200, ready API and preserved original 1,801-row demo |
| `uv run --project apps/api python scripts/verify-research.py` | PASS: 11 actual synthetic conditions, strict read-after-create, source preservation and actual report export |

Machine-readable final evidence: [browser verification](evidence/step3-browser-verification.json), [research conditions](evidence/step3-local-verification.json), and [ordinary readiness](evidence/local-verification.json). The browser run's timestamp is UTC; the user-facing verification date above is America/New_York. Remote CI is configured but has not been run or claimed.

New numerical checks independently verify analytical wrist speed/event times, no derivatives or association across missing intervals, stronger filter guards, measured windows/quality, deterministic noise/dropout/jitter/occlusion, source preservation, empty/duplicate/tolerance matching, timing and undefined metrics. Exhaustive small-list brute-force enumeration checks both matching objectives rather than copying implementation results.

Real PostgreSQL integration exercises frozen source revisions after edits, stale freeze/edit rejection, forced reruns/immutability, incompatible event/video references, cross-session rejection, failure/cancellation/expired-lease publication, actual evaluation/comparison/report endpoints, and safe cleanup. A separate Alembic test upgrades an actual MVP schema with a preserved row, checks model consistency and performs downgrade/re-upgrade. A real ASGI test reads through a separate database connection when HTTP headers are sent, proving commit visibility; injected persistence failure returns an error and leaves no row.

Browser flows cover all original Step 2 paths plus paired synthetic mode execution/scoring/comparison, generated/human snapshot eligibility, artificial synchronization failure, exported results, responsive containment and prediction-to-replay seeking. The real-video test uses actual installed MediaPipe in a CPU worker, forces initialization failure to verify actual main-thread fallback, validates seeking/playback, and runs real stored-pose event processing. No successful analysis response is mocked.

Final measured real-clip evidence: **87 worker frames** at a 30 Hz target, achieved average **14.53 Hz**, maximum sampled gap **400 ms**; **48 fallback frames** at the 10 Hz target. These counts vary with scheduling. With recorded exploratory `k=1`, height 0.1 torso/s and prominence 0.05 torso/s, stored-pose processing produced **nine wrist-speed events**, with evaluation null. The conservative `k=3` configuration previously returned a valid empty result; neither outcome measures tennis accuracy.

The paired software fixture recovers two generated events in clean modes. A missing IMU window or wrist occlusion leaves one event/reference miss; +1 s synchronization error leaves zero associations and two misses; full occlusion explicitly fails without metrics. The retained JSON records every actual result and latency. Those expected scientific failures are not failed automated tests.

Recovery corrected genuine mobile tab overflow, annotation refresh/freeze racing, legacy generated-source wording, two encoding-damaged strings and a transient create/read transaction race. The last race was fixed by database dependency function scope, not by relaxing the strict smoke assertions or adding retries for 404 responses. The test locator was made exact after adding an accessible reference timeline.

Warnings: one Starlette httpx TestClient deprecation and five Alembic legacy `prepend_sys_path` splitting warnings in the backend run; the existing future Vite native-config-loader advisory; Playwright's NO_COLOR/FORCE_COLOR warning. They do not fail the checks. No Step 3 dependency was added. The Step 2 dependency-advisory scan remains historical evidence (17 moderate development-tool advisories, zero runtime advisories at that scan); a new dependency security audit is not claimed.

## Step 2 verification history

## Commands

Run the default Docker application first as described in [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md). From `C:\RallySenseLab`:

```powershell
docker compose exec api pytest -q --tb=short --basetemp=/tmp/rallysense-pytest
docker compose exec api alembic check
uv run --project apps/api ruff check apps/api/src apps/api/tests apps/api/migrations
npm.cmd --prefix apps/web run typecheck
npm.cmd --prefix apps/web run lint
npm.cmd --prefix apps/web test
node scripts/check-contracts.mjs
```

The host commands require the locked dependencies (`uv sync --project apps/api --frozen`, `npm.cmd ci --prefix apps/web`). All backend tests can run inside the container without a host Python installation. Tests create and drop uniquely named PostgreSQL schemas and use temporary artifact storage; they do not reset the normal application tables.

Frontend type checking runs `next typegen` before `tsc`, so a clean checkout does not depend on leftover development-server route types. The framework-generated `next-env.d.ts` is ignored, as recommended by the installed Next.js CLI documentation.

For native backend tests where FFprobe is absent:

```powershell
New-Item -ItemType Directory -Force storage | Out-Null
uv run --project apps/api pytest apps/api/tests -q --basetemp=storage/pytest-native
```

This environment required a workspace-local temporary directory because the user-profile pytest temp directory had a Windows permission conflict. One video integration test skips natively without FFmpeg; it is required and passes in the API container.

For browser verification:

```powershell
node scripts/fetch-assets.mjs
python scripts/fetch-verification-video.py
Set-Location apps/web
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

The optional external clip comes from the official MediaPipe documentation and is retained only in ignored `data/private`. The helper preserves the original as `pose-upstream.mp4` and uses the built API image's FFmpeg to create a seekable H.264 derivative, `pose-sample.mp4`. The upstream file has invalid random-access references in Chromium; sequential extraction alone did not reveal this. It is an existing demonstration with rendered annotations, not an independently collected tennis recording. It verifies actual browser inference/transport/overlay behavior. The test explicitly skips with a reason when the clip is absent; a skipped clip is not evidence of pose verification. The clip is not redistributed in the repository. Fixture CSV origin is explicitly synthetic, and the combined-source browser test declares its session mixed.

## Scope and observed checks

| Area | Verification |
| --- | --- |
| Numerical backend | Known pulse recovery, flat streams, missing gyro, finite-value rejection, exact unit conversion, time-origin normalization, duplicate-time rejection, offset sign, cutoff validation, gap handling, global peak separation |
| Pose features | Independently calculated 2D elbow angle and torso-normalized wrist radius/velocity; no differentiation across missing frames or large gaps |
| PostgreSQL/API | Real import -> Parquet -> event run -> persisted predictions; idempotent run identity; saved sync revision; annotation stale-edit conflict; same-session database constraints; safe source ownership |
| Worker/storage | Expired lease reclamation, stale-worker fencing, deletion before publication, cleanup and immediate tombstone access blocking, retention of referenced/unrelated files during orphan reconciliation |
| Video/pose API | Actual FFmpeg-generated video -> FFprobe -> ranged media response; pose-batch idempotency/conflict; no-person frame persistence and typed retrieval |
| Browser | Landing/demo, source import and mapping, computed events, timeline/event/plot seeking, annotation edits/deletion, saved offsets and reload, blind-mode controls, mobile overflow check |
| Actual MediaPipe | Official video upload, classic-worker CPU inference, persisted landmarks and overlay; forced initialization failure followed by actual main-thread CPU fallback; combined synthetic signal/video replay and offset check; actual post-seek playback advancement and no media error |
| Build/contracts | Strict TypeScript, lint, generated OpenAPI type agreement, maintained locks, frozen migration consistency, Next standalone/container build |

Current verified unit/integration totals: **17 backend tests pass in the Linux API container; 16 pass and 1 expected FFmpeg-dependent skip natively; 6 frontend tests pass.** Typecheck, lint, contract drift check and `alembic check` pass. Final production browser/build evidence is recorded in [STEP2_REPORT.md](STEP2_REPORT.md).

## Evidence and actual fixes

- [Browser tests](../apps/web/tests/workflow.spec.ts) execute real HTTP/database/worker/browser paths. They do not mock successful pose inference or event outputs.
- The initial numerical test mistakenly expected a y-axis threshold to exclude a pulse whose full vector magnitude exceeded it. Its analytical expectation was corrected; the detector was not changed to match an arbitrary fixture.
- Integration test setup initially hit a Windows temp-directory permission conflict; using workspace-local temp storage resolved it. A detached ORM fixture ID and a missing test import were corrected.
- The generated migration required qualifying its SQLAlchemy `Text` type; the explicit frozen migration now applies and matches the model metadata.
- Browser testing found that relying on Recharts tooltip `activeLabel` did not reliably implement click-to-seek. Scrubbing now uses the installed library's plot-area and inverse-x-scale hooks plus actual SVG screen coordinates; the targeted test passes.
- Screenshot review exposed a genuine upstream H.264 seek failure despite successful sequential inference. Full and ranged served bytes matched the original. FFmpeg reported invalid random-access references. The verification helper now preserves the original and creates an explicitly identified seekable derivative; browser assertions require playback to advance after seeking and reject any media error. Error overlays no longer change image geometry and hide pose output on a decoder failure.
- Blinded mode now removes prediction navigation as well as chart/marker output. A dedicated component test covers this behavior.
- Starlette emits a deprecation warning for its current `httpx` TestClient compatibility path. The tests actually run and pass; migrating that test client dependency is a maintenance item.
- Vitest emits an advisory about a future Vite native config loader and the current config's module mode. It does not invalidate current checks.
- npm reports moderate advisories in development tooling and indirect ESLint peer warnings. The runtime-only audit reported zero advisories; do not interpret that limited scan as a full security audit. The final dependency-audit counts are recorded in the implementation report.

Screenshots and browser traces are local artifacts; screenshots are in ignored `docs/evidence/*.png`, traces/reports in ignored `apps/web/test-results`. CI configuration runs the checks and uploads evidence when the repository is eventually connected to GitHub; no remote CI execution or Git push occurred during Step 2.

## Step 4 acceptance and advisory scope (2026-11-06)

Current packaged container backend acceptance: **42 passed, 0 failed, 0 skipped**, 13.10 s with six existing deprecation warnings. Command: `docker compose exec api pytest -q --tb=short --basetemp=/tmp/step4-final-source -o cache_dir=/tmp/step4-pytest-cache`. Actual schema is `0003_collection_readiness` head; `alembic check` reports no new upgrade operations. Frontend units/types/lint/contracts pass. Serialized production Chromium: 8 passed, 0 failed/skipped/flaky, 96.996 s. A final focused ingestion/lifecycle run after source-panel polish passed 4 tests in 33.5 s. Eight routes at desktop/tablet/mobile passed containment checks and actual screenshot inspection. Exact commands/evidence are in STEP4_REPORT.

New meaningful checks cover capture metadata/revision conflicts, real PostgreSQL cue evidence and residuals, fail-closed readonly access including direct IDs/sources/jobs, fresh safe source-validation retries, actual/stale heartbeat, source-upload throttling, late dense pose windows, summary projection without stored-result mutation, and streamed WebM repair with original retained. The original remux test fixture accidentally contained duration metadata and was corrected to explicit `-live 1`; its first failure was a fixture precondition error, not a reason to weaken retention assertions. Browser fixtures explicitly identify synthetic DeviceMotion/camera input. The positive motion fixture filters Chromium's trusted initial all-null event to isolate its injected clock; it does not claim physical hardware or mock backend processing.

Frontend acceptance currently passes **15 tests / 5 files**. These check normalization/axis conversion/missing values/timestamp ordering, timeline/geometry, distinct immutable generated labels, blind mode, compatible comparison deltas, failure-window seeking and optional workspace-gate credentials. Strict type checking and lint pass.

Advisory commands: `npm.cmd --prefix apps/web audit --omit=dev --json` and full `npm.cmd --prefix apps/web audit --json`; Python locked requirements exported with `uv export --project apps/api --frozen --no-hashes --no-emit-project --format requirements-txt`, then `uvx --cache-dir storage/uv-audit-cache --from pip-audit pip-audit --no-deps --disable-pip -r storage/step4-python-requirements.txt -f json`. Exact machine summary is `evidence/step4-dependency-audit.json`. Runtime npm reports zero advisories. Full npm reports **10 moderate development-tool dependency findings**, originating from minimatch glob amplification [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249), propagated through ESLint/typescript-eslint/config packages. No high/critical finding. The suggested automatic fix changes major framework/lint versions; it was not applied blindly. This remains a review limitation. The pinned Python package scan reports no known vulnerabilities; it is not a container OS scan, physical security audit or Step 5 independent review. No dependency version was changed for these features.

Warnings retained: Starlette TestClient httpx deprecation, five Alembic path-separator notices, Vite future native-config-loader advisory, Playwright NO_COLOR/FORCE_COLOR warning. A transient overlapping Playwright run collided with its shared artifact directory; final browser acceptance must run alone. Earlier failures and their fixes belong in the report rather than being counted as passing evidence.
