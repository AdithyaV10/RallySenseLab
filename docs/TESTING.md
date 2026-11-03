# Step 2 verification

All results below refer to local software checks, not a tennis accuracy study. The repository has no evaluated real-world classifier, fusion model, F1 score, or coaching validation.

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
