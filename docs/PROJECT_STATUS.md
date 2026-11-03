# Project status

Updated: 2026-11-03, America/New_York.

## Authorization and checkpoint

- Current stage: **Step 2 ? full-stack foundation and functional MVP**.
- Stage state: **complete; stopped at the mandatory Step 2 review gate**.
- Last completed stage: **Step 2**.
- Authorized work completed: the user's explicit `CONTINUE TO STEP 2` instruction and implementation priorities.
- Next authorized stage: **none**. Step 3 requires `CONTINUE TO STEP 3`.
- User authorization required to advance: **yes**.
- No deployment, publication, Git remote, push, or cloud provisioning occurred.
- Step 1 checkpoint: `7316393`. Step 2 checkpoint message: `feat: complete Step 2 local movement analysis MVP`; obtain its ID with `git log -1 --format=%h` after the local commit.

## Implemented and verified

The local application connects Next.js 16.4.4/React 19.3.1/TypeScript to FastAPI 0.162.0 and real PostgreSQL 17.11. It implements session creation/loading/deletion, declared source provenance, actual video validation/streaming, CSV mapping and SI normalization, compressed raw/derived storage, durable jobs, gyro signal processing, immutable offset revisions, replay, independent annotation editing, and the synthetic demonstration.

Browser MediaPipe 1.2.0 processes actual video using the pinned Pose Landmarker Lite model in a classic CPU worker. The explicitly forced initialization-failure path also processed video using the main-thread CPU fallback. Final production browser evidence recorded 48 sampled frames in the worker and 48 in the fallback. Stored pose includes no-person observations, visibility, quality/coverage, actual presentation times, and real image-space feature primitives. Frame counts are scheduling-dependent and do not establish tennis accuracy.

`gyro_peak_v1` denotes filtered angular-speed maxima. These measured signal events are explicitly unvalidated proxies, never automatically confirmed swings or ball impacts. Human annotations, generated references, raw measurements, pose estimates, and computed events remain separate.

See [STEP2_REPORT.md](STEP2_REPORT.md) for the full inventory, implementation decisions, problems resolved and known limitations.

## Actual verification results

| Check / command | Result |
| --- | --- |
| `docker compose build api web` plus final cached image rebuilds | PASS: pinned API/FFprobe image and production Next.js standalone image built |
| `docker compose up -d --no-build` | PASS: actual packaged API/web/worker/PostgreSQL; API mount inspection confirmed no source bind mounts |
| `docker compose exec api pytest -q --tb=short --basetemp=/tmp/rallysense-pytest` | PASS: **17 tests**, including real PostgreSQL, FFprobe, Range, pose persistence and lifecycle checks |
| Native `uv run pytest ... --basetemp=../../storage/pytest-native` from apps/api | **16 pass, 1 expected skip** for absent native FFmpeg; equivalent test passes in the API container |
| `uv run ruff check src tests migrations` from apps/api | PASS |
| `docker compose exec api alembic check` | PASS: no new upgrade operations detected |
| `npm.cmd --prefix apps/web run typecheck` | PASS: strict TypeScript |
| `npm.cmd --prefix apps/web run lint` | PASS |
| `npm.cmd --prefix apps/web test` | PASS: **6 tests** across 2 files |
| `node scripts/check-contracts.mjs` | PASS: generated types match Pydantic OpenAPI |
| `npm.cmd --prefix apps/web run test:e2e` against production containers | PASS: **3 tests**, 0 skips, 37.6 seconds; synthetic workflow, fresh CSV flow, real pose/combined-source flow and forced fallback |
| `uv run --project apps/api python scripts/verify-local.py` | PASS: web pages HTTP 200, proxied API ready, stored 1,801-sample synthetic session accessible |
| Full `docker compose restart` followed by smoke verification | PASS: same demo UUID and persisted observations survived; all services recovered |
| `npm audit --omit=dev --json` | 0 runtime advisories in that dependency scan |
| Full npm advisory scan | 17 moderate development-tooling advisories; no high/critical advisories reported |

Raw local evidence: [browser summary](evidence/browser-verification.json), [readiness/persistence summary](evidence/local-verification.json), and [scoped dependency audit](evidence/dependency-audit.json). Screenshots in `docs/evidence` show the landing page, desktop/mobile replay, and real pose overlay. Browser traces/report remain under `apps/web/test-results`; screenshots/traces are local artifacts, not committed private recordings.

[TESTING.md](TESTING.md) explains commands, meaningful coverage, corrected failures and warning details. Git whitespace/document checks and the final clean checkpoint are recorded in the user-facing completion report. No remote CI execution is claimed; only the CI definition exists.

## Known defects, verification limits, and blocked requirements

No unresolved failure blocks the Step 2 MVP acceptance paths. Remaining limits are explicit:

- No independent tennis recordings/labels or real-world accuracy study. The external official video's seekable derivative is an integration input, and the combined sensor/video test uses explicitly mixed, unrelated sources.
- Browser pose extraction samples frames at a target 10 Hz and can be throttled or interrupted. It does not guarantee every decoded frame. Main-thread fallback can reduce responsiveness.
- Physical iOS/Android capture and non-Chromium browsers remain unverified. Live browser recording belongs to Step 4; CSV import is functional.
- Real rotated/portrait, variable-frame-rate/nonzero-origin and maximum-size recordings were not directly exercised. Contained-image geometry has a mathematical test. Large-study performance and full accessibility review remain Step 4.
- Offset only; no drift fit or automatic cue alignment. Unknown placement/frame/gravity handling must be declared rather than inferred.
- No video event classifier, fusion, evaluation metrics, frozen experimental label sets or challenge. Those are Step 3, currently unauthorized.
- FFprobe metadata validation does not guarantee random-access decodability. The original upstream verification clip had bad H.264 seek references; its preserved, explicitly re-encoded test derivative passes post-seek playback checks. Automatic transcoding is not an application feature.
- UTF-8 explicit-column CSV with decimal-point numerics; no ZIP import, automatic locale repair or automatic transcoding. Library listing is capped at 100 latest sessions.
- General job-retry UI is not implemented. Failed sources remain private until session deletion. Orphans/abandoned tracks use a 24-hour grace period, reconciled at startup/hourly.
- Single-user loopback access only. Public identity, isolation, quotas and deployment hardening are incomplete and deployment remains prohibited.
- Development dependency advisories, indirect lint peer warnings, Starlette's httpx TestClient deprecation and the future Vite config-loader advisory remain documented maintenance items. Current checks/builds pass.
- The shell sandbox setup error required elevated local execution. Git operations use a per-command safe.directory setting for this known project; global trust settings were not changed.

## Files relevant to continuation

- [Implementation report](STEP2_REPORT.md), [local startup](LOCAL_DEVELOPMENT.md), [API contract](API.md), [testing](TESTING.md), [decisions](DECISIONS.md), [research protocol](RESEARCH_DESIGN.md), and the [original master brief](PROJECT_BRIEF.md).
- `apps/api/src/rallysense/{api,models.py,schemas.py,signals.py,pose_features.py,provenance.py,jobs.py,worker.py,storage.py,maintenance.py}`.
- `apps/api/migrations/versions/0001_mvp.py` and `apps/api/tests`.
- `apps/web/src/features/{ingestion,replay}`, `src/lib`, `src/app`, `tests/workflow.spec.ts`, and the generated contract.
- `docker-compose.yml`, `infrastructure`, `scripts`, `data/fixtures`, `data/assets.lock.json`, and both dependency lockfiles.

## Local execution and next stage

Services are stopped after final verification; named database/artifact volumes and all source/evidence files are preserved. Restart from PowerShell:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open `http://127.0.0.1:3000` and choose Explore the demo. Exact instructions are in LOCAL_DEVELOPMENT.

After explicit Step 3 authorization, audit the real timing/filtering/placement assumptions, define any proxy-to-reference comparison explicitly, then implement video-event inference, improved baselines, fusion, leakage-safe evaluation, reproducible experiments and the corruption challenge. Preserve the functioning MVP and stop at the next stage gate.

**STEP 2 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 3.**
