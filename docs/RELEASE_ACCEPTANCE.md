# Step 5.5 release acceptance

2026-11-08. **SOFTWARE ACCEPTANCE PASSED; PUBLIC DEPLOYMENT ACCEPTANCE PENDING.** A01–A05 are corrected; A06 is retained. A07 development-tool maintenance and external operational gates remain. Read the [implementation report](STEP5_5_REMEDIATION_REPORT.md) and [deployment execution plan](DEPLOYMENT_EXECUTION_PLAN.md).

## Recorded verification

| Check | Actual outcome | Evidence |
| --- | --- | --- |
| Ordinary packaged backend | **65 passed**, zero failed/skipped, six deprecation warnings, 38.04 s | [backend](evidence/step5_5/backend-acceptance.json) |
| Original runtime audit gate | **2 passed**, zero failed/skipped | [runtime](evidence/step5_5/runtime-acceptance.json) |
| Frontend units | **15 passed**, five files | [units](evidence/step5_5/frontend.json) |
| Standard production browser | **9 passed**, zero failed/skipped/flaky; includes new replay-window regression, isolated annotation edits and actual MediaPipe | [browser](evidence/step5_5/browser-final-report.json) |
| Final annotation-test isolation guard | **1 targeted test passed** after adding explicit set reselection on reload; original rows still match | [workflow](evidence/step5_5/annotation-isolation-final.json), [preservation](evidence/step5_5/research-preservation-final-guard.json) |
| Original upload audit gate | **2 passed**, zero failed/skipped | [upload](evidence/step5_5/upload-acceptance-report.json) |
| Large upload/resource adversarial probe | **14 cases passed**, including actual 50/500 MiB files, hashes, unknown lengths, 413, abort, idle timeout and concurrency | [results](evidence/step5_5/upload-boundaries-results.json) |
| Types, ESLint, Ruff, OpenAPI contracts | Passed | [types](evidence/step5_5/final-types.json), [lint](evidence/step5_5/final-eslint.json), [Ruff](evidence/step5_5/operations-ruff.json), [contracts](evidence/step5_5/contracts.json) |
| Alembic consistency | `0003_collection_readiness (head)`; no new operations | [head](evidence/step5_5/migration-current.json), [check](evidence/step5_5/migration-check.json) |
| Production image builds | API and web builds succeeded, including final failed-write cleanup | [packaging](evidence/step5_5/final-image-build.json), [API cleanup build](evidence/step5_5/final-api-cleanup-build.json) |
| Scientific synthetic pipeline | Eleven expected conditions; full occlusion is an expected explicit inference failure | [results](evidence/step5_5/synthetic-experiments-results.json) |
| Auth/readonly/private-session checks | 401 unauthenticated including spoofed headers; approved 200; private 404; mutation 403; invalid Origin/Host denied; caller token overridden | [access](evidence/step5_5/access-final.json), [command](evidence/step5_5/access-verified-command.json) |
| Actual nonroot readiness/storage | Unwritable directory 503; writable ready; probe removed; **139 final files matched**, zero missing/mismatched | [storage](evidence/step5_5/storage-final.json) |
| Paired backup/isolated restore | 17 table digests and 116 files matched; no ports published; original data retained | [backup](evidence/step5_5/paired-backup.json), [restore](evidence/step5_5/isolated-restore-verified.json) |
| Original research rows | All 12 baseline model inventories matched, including legacy runs, annotation values/set revisions, frozen references and experiments | [preservation](evidence/step5_5/research-preservation-acceptance.json) |
| Fresh curated demo mode | Two fresh synthetic sessions, three precomputed results; RO artifact mount, readable readiness, denied mutations and idle worker | [fresh demo](evidence/step5_5/fresh-readonly-demo.json) |
| Release configuration | Both modes render; only gateway publishes ports; private backend, identical API/worker image, auth and memory budgets asserted | [configuration](evidence/step5_5/release-config-results.json) |
| Pinned Caddy configuration validation | Valid configuration in a disposable container, no listener published | [Caddy](evidence/step5_5/caddy-validation.json) |
| npm production advisories | 0 | [runtime audit](evidence/step5_5/npm-runtime-audit.json) |
| npm full advisories | **10 moderate development findings; command exits 1** | [full audit](evidence/step5_5/npm-full-audit.json) |
| Container OS vulnerability scan | **Unverified: Docker Scout requires Docker authentication; command exits 1** | [scan attempt](evidence/step5_5/image-scan-api.json) |

Original failing evidence under `step5/` remains historical evidence of real defects. The four application audit cases under `step5_5/` now pass without skip/xfail or weakened assertions. Scan/advisory exit codes above are not counted as passing tests.

## Repeat application checks locally

From `C:\RallySenseLab` in PowerShell, with Docker Desktop running:

```powershell
docker compose up -d --build --wait --wait-timeout 60
docker compose exec -T api pytest -q --tb=short --basetemp=/tmp/step55-review -o cache_dir=/tmp/step55-cache
npm.cmd --prefix apps/web test
npm.cmd --prefix apps/web run typecheck
npm.cmd --prefix apps/web run lint
uv run --project apps/api ruff check apps/api/src apps/api/tests apps/api/migrations apps/api/audit
node scripts/check-contracts.mjs
docker compose exec -T api alembic current
docker compose exec -T api alembic check
npm.cmd --prefix apps/web run test:e2e
docker cp apps/api/audit/test_runtime_contract.py rallysense-api-1:/tmp/test_runtime_contract.py
docker compose exec -T -e PYTHONPATH=/app/tests:/app/src api pytest -q /tmp/test_runtime_contract.py --basetemp=/tmp/step55-runtime-review -o cache_dir=/tmp/step55-cache
docker compose exec -T api ffmpeg -v error -f lavfi -i color=c=black:s=160x120:r=25 -t 1 -c:v libx264 -y /tmp/step55-small.mp4
docker cp rallysense-api-1:/tmp/step55-small.mp4 storage/step5-small.mp4
npm.cmd --prefix apps/web run test:e2e -- --config audit.config.ts
uv run --project apps/api python scripts/verify-upload-boundaries.py
uv run --project apps/api python scripts/audit-access.py --output docs/evidence/step5_5/review-access.json
uv run --project apps/api python scripts/check-release-config.py
uv run --project apps/api python scripts/check-preservation.py verify --baseline storage/step5_5-preservation.json
uv run --project apps/api python scripts/check-research-preservation.py verify
```

Create a fresh baseline before new work on another checkout; never overwrite the retained one. Run browser checks serially. The real vision test requires the existing permitted private verification clip and pinned model assets; an optional skip on another machine does not reproduce this evidence. Camera tests still write a historical evidence filename: preserve it before reruns and store the new output separately.

## Mode-specific release decision

**Mode A, curated read-only:** application path verified on fresh synthetic-only volumes with a read-only mount and precomputed results. Public release remains conditional on content/license review, reviewed final domain/TLS/secrets/firewall, final image scan, off-host backups and host monitoring. Keep the workspace gate enabled, explicit fixture IDs, and science workers idle.

**Mode B, authenticated research:** upload, processing, annotations, synchronization and research gates pass locally. Use identical API/worker images, strong workspace access and private ports; complete the same operational gates. Validate physical capture before advertising phone compatibility. No open anonymous uploads or tenant isolation are provided.

Only a separately authorized deployment stage may start the public gateway. None was started here.
