# Prioritized remediation handoff

2026-11-07. This is a plan for the next explicitly authorized stage, not permission to deploy. Starting application checkpoint is `e80cd99`; the Step 5 local checkpoint adds audit reports/evidence, regression gates and the A06 terminal-state fix. Preserve existing databases, volumes, artifacts and immutable research results.

## P0 — Choose the smallest release scope

For fastest safe demonstration, select **fresh fixture-only, precomputed, read-only** operation on a single container host. Keep the current private workspace separate. That scope avoids exposing the unresolved upload and runtime-transition paths; it does not make them repaired. Use [DEPLOYMENT_READINESS](DEPLOYMENT_READINESS.md) as the acceptance matrix.

Before any public read-only release: inspect all fixture text/media/exports and licenses; enforce backend readonly plus allowlist; provide TLS, unique secrets, exact hosts/origins and private API/DB; set resource/read limits; verify actual fixture media readability; scan final images; perform an isolated restore; review the demonstration with a human. Drain queues and keep scientific execution disabled. Re-run access tests through the eventual ingress, not just localhost. These operational gates remain mandatory even if no additional product feature is built.

## P1 — Required before upload-enabled research operation

### A01: repair authenticated upload ingress

**Owner:** full-stack/infrastructure. **Affected:** global Next proxy, API route/edge topology and upload limits. Do not blindly set a 501 MiB in-memory clone limit or remove authentication from upload routes.

Implement bounded same-origin streaming to the private API with equivalent workspace authentication, Origin/Host validation and read-only rejection. Keep server credentials off the client. Align edge body limits and file limits, including multipart overhead. Enforce early 413 and streamed limits, concurrency and timeouts. Preserve original bytes and clean abandoned staging files.

**Exit tests:** both existing `audit/uploads.spec.ts` cases pass with actual worker success; near-limit and over-limit CSV/video, chunked and missing Content-Length, abort/malformed multipart, unauthorized/foreign-Origin requests and readonly mutations behave correctly. Verify hashes/file lengths at every hop. Measure peak RSS for the selected concurrent-upload budget. A temporary smaller advertised limit is acceptable only as an explicit product constraint with early rejection and updated tests/docs.

### A02: enforce frozen executor environment

**Owner:** backend/scientific infrastructure. Compare executing dependency lock and numerical runtime with the enqueued manifest before inference. Return a typed mismatch and retain the original frozen record. If exact environment execution is supported later, record the actual executor identity without overwriting history. Review the legacy inference path's weaker execution-time provenance checks as well.

**Exit tests:** both `apps/api/audit/test_runtime_contract.py` cases pass; a matching environment still produces identical deterministic events; stale queued jobs after dependency-only changes cannot succeed under false metadata. Test release queue draining/rejection. Do not change detector equations, old algorithm labels or completed results merely to implement this guard.

## P2 — Required for advertised collection/replay reliability

| Issue | Concrete repair | Acceptance |
| --- | --- | --- |
| A03 dense-track capacity | Reconcile client batch size/count, API frame/byte caps and supported duration; expose unsupported work before lengthy extraction | At least 18,000 observations pass ordinary staged ingestion or an explicitly lower duration/rate is rejected upfront; idempotent retry/conflict/incomplete-batch checks still pass |
| A04 artifact readiness | Mode-aware temporary write/read/remove check for writable storage; readable known fixture check for readonly storage; disk alarms | Read-only/full/missing storage states do not report writable readiness; probe cleans up; no private path disclosure |
| A05 zoom cache | Include sync ID/offset in sample query identity or invalidate all affected windows on save | At session [4,6]s, saving +1s requests source [3,5]s without reload; test positive/negative offsets and boundary-empty windows |
| Unsaved collection buffers | Add a clear route/session-change guard or durable draft strategy if uninterrupted collection is promised | Real navigation, cancellation and physical-device interruption do not silently violate the advertised retention behavior; larger persistence design needs separate scope |

For a fixed-alignment readonly demo, A03 and A05 may be deferred by using verified short pre-extracted tracks and disabled edits. A04 still needs an appropriate readable-storage acceptance probe. Keep A06's small repair and all 52 backend regressions; do not reset historical sources to “ready.”

## P3 — Release hardening and maintenance

- Review A07 tooling advisories with compatible versions; rerun types/lint/build/contracts and both audit gates. Scan OS/base-image/FFmpeg packages and patch according to exposure/severity. Runtime npm/Python clean scans are insufficient for that decision.
- Establish consistent paired backups, off-host retention, isolated restore, migration rehearsal and secret rotation. Render/review the final Compose configuration. Existing DB passwords require actual database rotation, not merely changing an environment variable.
- Bound all ingress/read/compute resources for the chosen audience; monitor storage, request failures, worker age and queue age. Benchmark representative loads before selecting hardware or making capacity claims.
- If growing histories matter, project experiment summaries in SQL and paginate heavy session detail; verify response equivalence and stored-result immutability before optimization. This is not a prerequisite for the small curated demo.
- Conduct human accessibility/browser review. Physical iOS/Android and a consented paired pilot are required before promoting capture compatibility or scientific tennis capabilities. No trained classifier or advanced fusion rewrite is needed for an honest technical demo.

## Release acceptance and stopping rule

Run ordinary backend/frontend/browser checks **and** the four currently failing audit cases. Report failures/skips separately; no weakening assertions, xfail conversion or omission from release evidence. Preserve raw audit evidence and label new remediation evidence separately. Repeat data-preservation hashes and source reads after restart. Create a local reviewable checkpoint with exact outcomes. Obtain explicit authorization before deployment, cloud provisioning, publication or remote push.
