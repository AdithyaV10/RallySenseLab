# Step 5 final test report

**Historical Step 5 results.** The four failed application cases recorded below were corrected in Step 5.5 and now pass unchanged. Current counts and remaining scan/advisory outcomes are in [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md). Original evidence is preserved.

Date: 2026-11-07. All verification was local. Starting checkpoint: `e80cd99`. Existing Step 4 claims were not treated as current passes. The interrupted Step 5 evidence is retained alongside the resumed final runs.

Finalization review: 2026-11-08, America/New_York. The completed audit was already committed as `1063eba`. Only documentation/evidence consistency checks were needed: saved pass/fail outcomes, tracked unweakened regression tests, local report links, and retained preservation counts/hash results. No application or test source changed and no expensive suite was repeated. [Finalization evidence](evidence/step5/finalization-review.json) records these checks; the execution dates and results below remain those of the original runs.

## Outcomes

| Check | Actual result | Evidence |
| --- | --- | --- |
| Original packaged backend baseline | 42 passed, six warnings, 16.58 s | `evidence/step5/backend-baseline.txt` |
| Final packaged backend, including ten independent audit tests | **52 passed, 0 failed, 0 skipped**, six warnings, 14.24 s | [backend-final](evidence/step5/backend-final.json) |
| Independent numerical subset, resumed native run | 5 passed, 4 deselected at that point; 13.72 s | [audit-numerical](evidence/step5/audit-numerical.json); also included in final 52 |
| Frontend units | **15 passed**, five files; final run 3.64 s | [frontend-final](evidence/step5/frontend-final.json) |
| TypeScript/Next route types, ESLint, Ruff | PASS | [types](evidence/step5/typecheck-final.json), [ESLint](evidence/step5/eslint-final.json), [Ruff](evidence/step5/ruff-final.json) |
| OpenAPI/TypeScript contract drift | PASS | [contracts-final](evidence/step5/contracts-final.json) |
| Migration head and model consistency | `0003_collection_readiness`; no new operations | [current](evidence/step5/migration-current.json), [check](evidence/step5/migration-check.json) |
| Production Docker API and web build | PASS, underlying Docker exit 0, 27.096 s | [production-build-final](evidence/step5/production-build-final.json) |
| Final standard production browser suite | **8 passed, 0 failed, 0 skipped, 0 flaky** | [browser-final-report](evidence/step5/browser-final-report.json), [command](evidence/step5/browser-final.json) |
| Additional upload audit gate | **2 FAILED**, 0 skipped: valid CSV and MP4 rejected by web proxy | [upload-regressions-report](evidence/step5/upload-regressions-report.json) |
| Additional frozen-runtime audit gate | **2 FAILED**, 0 skipped: lock/runtime mismatches not rejected | [runtime-regressions](evidence/step5/runtime-regressions.json) |
| Eleven synthetic conditions | All expected software outcomes verified; full occlusion intentionally produces failed inference | [results](evidence/step5/synthetic-experiments-results.json) |
| Actual MediaPipe + decoded presentation-time comparison | Three real extraction paths; strictly increasing stored times, zero distance to source PTS on tested clip | [frame-timestamps](evidence/step5/frame-timestamps.json) |
| Production workspace gate/read-only | PASS: 401 unauthorized, 200 approved access, private 404, mutation 403; direct API covered | [access](evidence/step5/access.json) |
| UI navigation and response sizes | 16 desktop/mobile route checks, no overflow/page errors; real screenshots | [browser-review](evidence/step5/browser-review.json) |
| Storage/readiness adversarial probe | Initial 104 and final 116 then-current artifact files matched SHA-256; confirmed read-only directory falsely reports ready | [initial](evidence/step5/storage-readiness.json), [final](evidence/step5/storage-final.json) |
| Replay alignment-cache probe | Confirmed no refetch after offset save; reload fetches corrected window | [replay-cache](evidence/step5/replay-cache.json) |
| Startup/restart and source preservation | Stack recovered/recreated on retained volumes; baseline 113 experiments, 16 references, 93 artifact identities, 35 active sessions preserved | [final preservation](evidence/step5/preservation-final.json) |
| Ordinary application smoke | PASS; original 1,801-row source still readable, landing/library/readiness 200 | [smoke](evidence/step5/smoke-results.json) |
| Dependency advisories | npm production 0; full npm ten moderate development findings; 35 pinned Python packages 0 known findings | `npm-runtime-audit.json`, `npm-full-audit.json`, `python-advisories.json` under `evidence/step5` |

**The complete audit gates are not green.** The standard regression suites pass while four added defect regressions fail. Their separate configuration makes the unresolved acceptance requirements explicit; they are not marked skipped or xfail and must be run during remediation. Do not report “all tests pass” by omitting them.

## Reproduce the ordinary checks

From `C:\RallySenseLab` in PowerShell:

```powershell
docker compose up -d --build
docker compose exec -T api pytest -q --tb=short --basetemp=/tmp/step5-review -o cache_dir=/tmp/step5-cache
npm.cmd --prefix apps/web test
npm.cmd --prefix apps/web run typecheck
npm.cmd --prefix apps/web run lint
uv run --project apps/api ruff check apps/api/src apps/api/tests apps/api/migrations apps/api/audit
node scripts/check-contracts.mjs
docker compose exec -T api alembic current
docker compose exec -T api alembic check
npm.cmd --prefix apps/web run test:e2e
uv run --project apps/api python scripts/verify-research.py --output docs/evidence/step5/review-synthetic.json
uv run --project apps/api python scripts/verify-local.py --output docs/evidence/step5/review-smoke.json
uv run --project apps/api python scripts/check-preservation.py verify --baseline storage/step5-preservation.json
```

The preservation baseline is private/ignored and retained locally; the public report contains counts, not the underlying private records. On a fresh checkout create a **new** baseline before work rather than overwriting the existing one. Backend integration tests create/drop only unique disposable PostgreSQL schemas and use temporary artifacts. Browser tests create their own sessions and may add immutable test runs/references to built-in synthetic demos. They do not delete user recordings. Run Playwright serially because its standard artifact directory is shared.

The real MediaPipe test needs the already present permitted `data/private/pose-sample.mp4` and pinned model assets. In this audit the test actually ran; on another machine its optional skip is **not** equivalent evidence. Acquisition/licensing is documented in TESTING. The existing camera test writes a historical Step 4 evidence filename; this audit copied its new outputs into the Step 5 folder and restored the old tracked evidence exactly.

## Reproduce the failing upload acceptance gate

```powershell
docker compose exec -T api ffmpeg -v error -f lavfi -i color=c=black:s=160x120:r=25 -t 1 -c:v libx264 -y /tmp/step5-small.mp4
docker cp rallysense-api-1:/tmp/step5-small.mp4 storage/step5-small.mp4
npm.cmd --prefix apps/web run test:e2e -- --config audit.config.ts
```

`apps/web/audit/uploads.spec.ts` constructs a finite, valid 450,001-row CSV and a valid one-second MP4 padded with a legal `free` box. It verifies real backend normalization/probing succeeds before asserting equivalent frontend behavior. Both frontend assertions currently fail: expected 202, actual 422. Each fixture session is cleaned up in `finally`; no pre-existing session ID is used for deletion. Traces are local under ignored `apps/web/audit-results`; machine results are retained in the evidence folder. The direct API test uses the local development token or an explicitly supplied LOCAL_TOKEN, never publishes it to browser code, and is intended only for loopback testing.

## Reproduce the failing runtime acceptance gate

```powershell
docker cp apps/api/audit/test_runtime_contract.py rallysense-api-1:/tmp/test_runtime_contract.py
docker compose exec -T -e PYTHONPATH=/app/tests:/app/src api pytest -q /tmp/test_runtime_contract.py --tb=short --basetemp=/tmp/step5-runtime-review -o cache_dir=/tmp/step5-cache
```

Both parameterized cases currently fail: expected failed experiment, actual succeeded. The test changes only a newly created disposable-schema queued manifest to represent a different enqueuing environment. It does not modify real frozen records or runtime libraries. It validates an execution contract, not a claim that previously computed numerical values were inaccurate.

## Supplemental reproducible probes

```powershell
uv run --project apps/api python scripts/audit-access.py
node scripts/audit-browser.mjs
node scripts/audit-replay-cache.mjs
docker cp scripts/audit-storage-readiness.py rallysense-api-1:/tmp/audit-storage-readiness.py
docker compose exec -T api python /tmp/audit-storage-readiness.py
docker cp scripts/audit-presentation-times.py rallysense-api-1:/tmp/audit-presentation-times.py
docker cp docs/evidence/step5/browser-final-report.json rallysense-api-1:/tmp/step5-browser.json
docker compose exec -T api python /tmp/audit-presentation-times.py
```

Access verification starts only temporary loopback containers with exact test names and removes them afterward, without removing volumes. It assumes the default local development API token. The readiness probe changes permissions only on its own temporary directory. The replay-cache script characterizes the **current defect**; its successful exit does not mean the cache is correct. Likewise, pose-capacity characterization confirms the cap rather than claiming long extraction succeeds.

## What the tests establish

Ten added ordinary backend tests cover independent metrics, 120 brute-force matcher cases, analytical aspect-corrected velocity/midpoint timing, inclusive fusion gates and coverage, seeded corruption/channel preservation, exhausted retries, queued and claimed-job cancellation/retry, hidden-resource access/export paths, and the 10,000-observation batch boundary. Existing tests cover source ownership, numerical units/gaps, frozen reference revisions, transaction visibility, stale lease fencing, tombstone publication rejection, migrations, browser WebM repair and late pose-window retrieval.

The production browser suite verifies actual CSV ingestion, synthetic DeviceMotion transport, permission fallbacks, actual MediaRecorder encoding/probing, replay seeking, annotations, saved synchronization, three research modes, corruption, reference freezing, reports, actual MediaPipe worker processing, seek sampling and forced worker-init failure followed by actual main-thread inference. It does not mock a successful backend computation or count generated analytical landmarks as MediaPipe output.

Screenshot paths retained locally: `docs/evidence/step5-{landing,library,collection,replay,challenge,method,diagnostics,report}-{desktop,mobile}.png`. The desktop replay and mobile Challenge screenshots were visually inspected. Existing Step 4 tablet and other screenshots are historical supplementary evidence, not a fresh comprehensive accessibility test.

## Failure history and limitations

- The first independent source-state checks produced two real failures. A06 was fixed and both now pass, alongside running-cancel and retry protection.
- Initial resumed Docker requests failed with engine HTTP 500 while Desktop was stalled at “starting.” A forced application stop/start recovered the engine; no volume reset, distribution deletion or database restore occurred. Application tests were run after healthy startup.
- Two temporary access-harness attempts queried before the API was ready; one also needed the temporary upstream hostname explicitly allowlisted. The final harness waits for an authenticated API response and passes. These were setup failures, not proven access-control bypasses.
- The command evidence writer saved the successful Docker exit/output, then encountered a Windows console Unicode-printing error. Its UTF-8 console handling was corrected. The recorded build command itself returned zero; this is not a failed build relabeled as success.
- A formatting command initially used the wrong working directory and matched no files; the final check uses explicit paths. No test assertion was relaxed.
- Starlette TestClient and Alembic path-separator deprecations, the Vite config advisory and NO_COLOR/FORCE_COLOR warning remain visible.
- No physical phones, held-out tennis labels, participant statistics, arbitrary-codec/VFR/rotation matrix, maximum concurrent uploads, denial-of-service exercise, full screen-reader/contrast audit, OS-image scan, destructive disaster-recovery drill or external CI execution was claimed.
