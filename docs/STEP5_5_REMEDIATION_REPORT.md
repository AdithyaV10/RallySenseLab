# Step 5.5 engineering remediation

2026-11-08, America/New_York. Starting checkpoint: `be725ae5cb474c74c84a3d2357565facd0f6d997`. Scope is [the authorized specification](STEP5_5_SPECIFICATION.md). Step 5 findings and failure evidence remain intact; new evidence is under [evidence/step5_5](evidence/step5_5/).

**A01–A05 are corrected, A06 is preserved, and software acceptance passed: 65 backend, 15 frontend, nine standard browser and four original audit cases. Public deployment still requires the external/human gates in [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md).** No cloud resources, public listeners, deployment or remote push were created.

## Corrections and original reproductions

| Finding | Original behavior | Implemented correction and verification |
| --- | --- | --- |
| A01 HIGH, large uploads | Valid 11,590,089-byte CSV and >12 MiB MP4 succeeded directly but web returned 422 after Next's 10 MiB Proxy clone | Global Proxy excludes `/api/`; the API route independently applies the shared workspace gate, then forwards a bounded backpressured stream. Both original unmodified audit cases pass. Exact 50 MiB CSV and 500 MiB MP4 also passed with actual normalization/probing and matching stored SHA-256. |
| A02 HIGH, frozen environment | Two adversarial dependency/runtime manifests still published successful output | Worker checks dependency lock SHA-256 and Python/numpy/scipy/pyarrow versions before computation. Both original unmodified cases pass. Matching execution, deterministic event results, typed failures and completed-result immutability are tested. Legacy inference now checks environment, implementation and actual input bytes too. |
| A03 MEDIUM, pose capacity | 100 batches × 100 observations exhausted ingestion after 10,000 | Client stages at most 200 observations and less than 1,900,000 serialized bytes per batch, retaining only the current batch. Server permits 200 batch indices, 300 observations/request and 30,000 total observations, under the existing 2 MiB HTTP bound. A real staged 18,000-observation/33-landmark integration test finalizes and retrieves the late window. Retry, conflict, monotonicity, incomplete sequence/count and terminal idempotency are covered. |
| A04 MEDIUM, false readiness | Nonroot mode-0555 storage falsely returned ready | Writable readiness checks free space, bounded temporary write, fsync, readback and cleanup; failures return generic 503 without paths. Read-only readiness verifies approved fixture inventory and artifact readability without writing. Real nonroot and disposable-schema regressions pass. API readiness does not assert worker capacity. |
| A05 MEDIUM, stale replay window | Saving +1 s at session [4,6] s made no sample request; reload finally fetched [3,5] s | Sample identity includes immutable sync ID and offset. Fully uncovered windows return empty data; partial coverage clips the lower bound. A browser regression verifies positive/negative offsets, partial overlap and empty windows immediately after save. |
| A06 MEDIUM, already repaired | Cancelled/exhausted jobs previously left queued source state | Existing terminal-state propagation, completed-job no-op cancellation and retry/cancellation tests are retained and pass. |
| A07 LOW runtime relevance, open maintenance | Ten moderate development-tool advisories from minimatch | Current production npm audit is clean. Full npm audit still reports ten moderate development findings. npm proposes major downgrades of ESLint/Next configuration rather than a compatible declared fix; no forced downgrade or unreviewed major override was applied. Lockfiles remain reproducible. |

The detector equations and event meanings were preserved. Gyro peaks remain measured angular-speed signal events/unvalidated tennis proxies. Visual events remain image wrist-speed peaks; fusion remains temporal association. Synthetic outcomes are software checks, not athlete accuracy.

## Exact implementation

- Frontend: `src/lib/workspace-access.ts`, `src/proxy.ts`, `src/app/api/v1/[...path]/route.ts`, replay `pose-extraction.ts` and `workbench.tsx`.
- Backend: `provenance.py`, `experiments.py`, `jobs.py`, `api/pose.py`, `schemas.py`, `main.py`, `upload_route.py`, upload routers, `storage.py`, `policy.py`, `config.py`, `worker.py` under `apps/api/src/rallysense/`.
- Contracts: regenerated OpenAPI and TypeScript schema for optional completion observation count; no database schema change.
- Tests: `apps/api/tests/test_remediation.py`, the retained/repaired boundary characterization in `test_audit.py`, `apps/web/tests/replay-alignment.spec.ts`, and isolated annotation-set setup in the existing workflow test. Original upload/runtime acceptance assertions are unchanged.
- Operations: [release Compose](../infrastructure/compose.release.yml), [read-only override](../infrastructure/compose.readonly.yml), [Caddyfile](../infrastructure/Caddyfile), [environment template](../infrastructure/release.env.example), paired backup/restore, release-config assertions and empty-database fixture preparation scripts. Docker build context excludes environment files, credentials and browser traces.

## Upload/security/resource contract

The chosen design uses an isolated authenticated application route rather than adding another upload implementation at the edge. It fits the existing Next/FastAPI architecture and was verified with the real installed Next package. Native `fetch` receives a backpressured ReadableStream; no `formData()`, `arrayBuffer()` or whole-video Buffer is created in Next. No experimental large Proxy buffer was enabled.

Both pages and API routes use the same Basic workspace gate. `REQUIRE_WORKSPACE_AUTH=true` fails closed on missing/short/template credentials. Host and Origin checks precede forwarding; a client guard remains required for mutations. Only an explicit safe header allowlist reaches FastAPI, with a server-owned internal token replacing any caller credential. Backend auth, exact Origin checks, fixture visibility and mutation denial remain enforced. Release Compose publishes only the TLS gateway; API/DB ports are reset, with an internal backend network. Base development ports remain loopback-only for local work and original direct-API audit tests.

| Resource | Effective application contract |
| --- | --- |
| File limits | CSV 50 MiB; video 500 MiB |
| Multipart body | CSV 51 MiB; video 501 MiB including overhead; counted even without Content-Length |
| Other API body | 2 MiB |
| Parser resources | One file, one metadata field; metadata part ≤64 KiB; file spools to disk above 1 MiB |
| Active uploads | Two per web process and two per API process; excess 429 with retry guidance |
| Timeouts | 30 s idle receive and 300 s total frontend request; actual idle rejection observed at 32.74 s under local scheduling |
| Production requests | API-wide 600 authenticated requests/minute, 12 upload attempts/minute; single process/workspace budgets, not distributed per-user quotas |
| Pose | 200 batch indices, ≤300 frames/request, ≤30,000 frames/track, ≤2 MiB request; client byte/count flushing remains bounded |

Early and streamed oversize requests return 413. Multipart parse errors return 400/422. Abort/timeout cancels upstream transport, releases admission slots and closes parser temporary files. Raw CSV staging is removed on failed write/rename; video staging uses `finally`. The filesystem and PostgreSQL cannot share a transaction: an already-renamed file after a later DB commit failure remains subject to existing delayed orphan reconciliation. This limitation is retained explicitly.

The real boundary probe exercised exact limits, one byte over each file limit, unknown-length body over the CSV request limit, declared oversized body, malformed multipart, invalid Host/Origin, missing client guard, two aborted uploads, third-upload rejection and two concurrent successful uploads. Stored lengths/hashes and actual worker success were checked. [Results](evidence/step5_5/upload-boundaries-results.json).

Kernel-observed process lifetime peak RSS after the boundary run was **208,756 KiB (204 MiB) for Next** and **254,120 KiB (248 MiB) for Uvicorn**. Earlier checks contribute to those high-water marks. These are real process peaks, not aggregate container/cgroup/cache peaks, a two-concurrent-500-MiB benchmark or production sizing guarantees. The concurrent successful-file test uses small synthetic MP4s; separate saturation tests hold two streams open. Release resource limits are initial budgets requiring host-specific validation.

## Research execution and upgrades

New manifests include Python plus numerical versions. Results record actual executor dependency/runtime/build identity. Mismatches use `EXECUTION_ENVIRONMENT_MISMATCH`; implementation and input changes retain separate typed failures. Failed legacy runs retain their input manifest and executor/failure details. No historical manifest/result was rewritten to claim a new executor.

Old queued manifests without the newly required Python identity deliberately fail closed. Before an upgrade, remove HTTP writers, let the old worker drain, verify no queued/running work, then stop it and update API/worker to the identical reviewed image. If stale work remains, preserve it and create new runs under the new release; retries must not silently substitute metadata. Completed historical results remain readable. See the exact procedure in [DEPLOYMENT_EXECUTION_PLAN](DEPLOYMENT_EXECUTION_PLAN.md).

Read-only workers neither claim queued jobs nor run storage reconciliation. They publish an operational idle heartbeat. This prevents HTTP read-only mode from accidentally executing an existing research queue.

## Verification and preservation

See [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md) for commands, exact pass/fail results and evidence. Completed ordinary runs cover backend integration/numerical/migrations, frontend units, browser capture/replay/annotations/research, real MediaPipe worker/seek/fallback, and the four formerly failing cases. Eleven synthetic experiment conditions have the expected outcomes; full occlusion intentionally fails inference and +1-second misalignment removes associations.

Before app changes, a non-destructive baseline recorded 134 experiments, 19 references, 116 artifact identities and 43 active sessions. An additional full-row baseline covers all 82 session rows (including tombstones), 28 sensors, 22 videos, 33 pose tracks, 38 legacy runs, 110 predictions, 8 annotations, 45 annotation sets and 80 sync configurations. Final preservation checks compare every original row, not just counts. New test records may be appended.

The initial standard browser run added/edited/deleted its marker in an existing built-in synthetic human set, changing only its revision counter by three. The full-row check detected it. The old revision was read from the verified pre-test backup, candidate full-row hash matched the baseline, and absence of newer dependent frozen references was checked before restoring only that test counter. No annotation values or frozen records were replaced. The workflow now creates its own label set; the final preservation check must remain green. [Cleanup evidence](evidence/step5_5/browser-test-state-cleanup.json).

A paired pg_dump/artifact archive was created while writers were stopped and the queue drained. A second fresh isolated restore passed **17 table-content digests and 116 artifact hashes**, migration head and writable readiness. Original volumes were retained. The first restore attempt exposed PostgreSQL's transient initialization socket: pg_isready was insufficient. The helper and release health check now use actual TCP SELECT 1; the successful retry used another fresh project and left the first volume intact. Backups and both stopped restore projects remain local/private.

Fresh demo preparation was separately verified on empty isolated volumes: two generated synthetic sessions, three precomputed experiments, read-only artifact mount, 403 mutations, 404 unknown session, readable storage and no worker job claims. No private recording was copied. These test projects exposed no host ports and their DB containers were stopped with volumes retained.

## Failure history and remaining gates

- Initial native pytest hit Windows temp-directory permissions. Explicit workspace temp storage resolved that setup issue. Native FFmpeg fixture execution was unavailable; the required Linux suite ran with the packaged media tools.
- The first targeted native run found the streamed-limit 400 bug and a test assertion against a deliberately private DTO field. The application now preserves 413, and terminal idempotency compares the actual supported response.
- The first real boundary run found a keepalive closure race after streamed rejection. Error responses now explicitly close that HTTP/1 connection. A later idle test found cancellation awaited client close; cleanup now cancels without delaying the response. Final boundary verification passes.
- One expanded temporary access probe ran before its API became ready. It was reordered behind the authenticated readiness wait; final spoof/Origin/Host checks pass.
- Initial OpenAPI drift was expected from the new completion payload; regenerated files were reviewed and the consistency check passes.
- Historical Step 4 camera evidence was copied for new verification and restored exactly. Old Step 5 failed logs are retained; remediation evidence does not relabel them as passes.
- npm full audit still exits 1 for ten development advisories. Docker Scout exits 1 because Docker authentication is unavailable. **No clean OS/image scan is claimed.** Required application acceptance failures must be resolved; external scan/credentials and human release gates remain explicit.

Remaining release gates: final OS/FFmpeg/base-image scanning and exposure review; actual Linux host/DNS/TLS/secrets/firewall acceptance; off-host encrypted backup retention and recovery ownership; host-specific disk/queue/request monitoring and resource validation; fixture/license/human UI review. Physical iOS/Android capture and independent paired-tennis evaluation remain research/product limitations. This is a controlled shared workspace, not a public anonymous multiuser service.
