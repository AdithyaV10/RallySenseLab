# Final independent engineering audit

**2026-11-08 remediation update:** this document preserves the original Step 5 findings and verdict below. Step 5.5 corrects A01–A05 and retains A06; the four original defect regressions now pass. A07 development tooling and external release gates remain. Current implementation/evidence: [STEP5_5_REMEDIATION_REPORT](STEP5_5_REMEDIATION_REPORT.md), [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md). Historical OPEN labels below describe the audited checkpoint, not the remediated application. No deployment has been authorized or performed.

Audit date: 2026-11-07, America/New_York. Scope: local checkpoint `e80cd99`, preserved interrupted Step 5 work, and the narrowly scoped fixes below. Authorization: [original specification](STEP5_SPECIFICATION.md) and [resume specification](STEP5_RESUME_SPECIFICATION.md). This is an independent pass over the implementation and fresh tests, performed by the same coding agent; it is not third-party certification.

**Final verdict: SIGNIFICANT FIXES REQUIRED.**

The application is a credible local observation/research demonstrator. The core numerical methods, persistence, real pose integration, and ordinary browser workflows execute. It is not ready for general upload-enabled deployment: large uploads fail through the frontend and a worker can publish under mismatched frozen runtime metadata. Several recoverable reliability defects also remain. A fixture-only read-only demonstration has a materially smaller remediation scope; approval still requires the operational and privacy gates in [DEPLOYMENT_READINESS](DEPLOYMENT_READINESS.md).

No deployment, public listener, cloud provisioning, repository publication or remote push occurred. Existing recordings and research records were retained. Only fixtures created by audit tests were removed. The Docker engine was recovered from a stalled startup without resetting volumes.

## Verified and unverified scope

Fresh verification includes 52 backend tests, 15 frontend units, eight production Chromium tests, strict types/lint, contracts, migrations, production image builds, 11 synthetic experiment conditions, actual MediaPipe worker/fallback/seek extraction, direct read-only access checks, restart preservation and artifact hashes. **Four additional audit regression cases fail**: two upload and two runtime-contract cases. These are actual unresolved defects, not skips or successful tests. Exact commands, failures and evidence are in [FINAL_TEST_REPORT](FINAL_TEST_REPORT.md).

Physical iOS/Android capture, a consented paired tennis study, exhaustive media-format compatibility, maximum-size concurrent load, backup restoration, container OS vulnerability scanning and formal accessibility assessment remain unverified. The audit is complete within this declared local evidence boundary; these are release/research gates, not implied successes.

## Confirmed findings

### A01 — Large multipart requests are truncated before reaching the API

**HIGH · OPEN · upload-enabled deployment blocker**

- **Files:** `apps/web/src/proxy.ts`, `apps/web/next.config.ts`, `apps/web/src/app/api/v1/[...path]/route.ts`; installed Next `dist/server/body-streams.js`; CSV/video API routers.
- **Root cause:** the global Next Proxy executes even with the optional password unset. The installed Next 16.4.4 clones/buffers request bodies with `DEFAULT_BODY_CLONE_SIZE_LIMIT = 10 * 1024 * 1024`. Once a chunk crosses the limit it ends both cloned streams and drops subsequent chunks. The route handler's `duplex: "half"` does not recover already discarded bytes. No override is configured.
- **Reproduction:** prepare the one-second synthetic MP4 as described in FINAL_TEST_REPORT; run `npm.cmd --prefix apps/web run test:e2e -- --config audit.config.ts`. The CSV is 11,590,089 bytes and within the 450,001-row/450-second limits; the MP4 contains a legal padding box and is over 12 MiB. Both first pass through direct loopback FastAPI and finish their actual worker validation, then fail through the web proxy.
- **Expected:** intact in-limit multipart import, HTTP 202, successful source processing. **Actual:** frontend HTTP 422, missing `file`; web logs explicitly report the 10 MB truncation. Direct API returns 202 and both jobs succeed. [Initial evidence](evidence/step5/large-upload.json), [failing regressions](evidence/step5/upload-regressions-report.json).
- **Impact:** external CSV/video uploads and saved browser motion/camera buffers share this path. Small demos pass while normal larger recordings fail. JSON pose batches are bounded below 2 MiB and are not affected by this particular limit.
- **Correction:** implement one authenticated, size-bounded streaming ingress, preserving token secrecy, exact Host/Origin rules and read-only enforcement. Prefer an edge reverse proxy routing `/api/v1` directly to private FastAPI after shared access checks, or relocate API-route authentication so uploads avoid the global Next body clone. Do not simply exclude uploads from authentication. See the concrete repair acceptance criteria in REMEDIATION_PLAN.
- **Memory implications:** increasing the clone to approximately 501 MiB allows roughly that much retained body payload per concurrent upload, plus parser/application/browser overhead. Four such uploads imply about 2 GiB of body buffering alone; this is arithmetic, not a measured memory benchmark. An explicit lower cap can be an interim product decision, but must replace advertised limits and reject early with 413. A large untested buffer increase was not made.

| Layer | Current bound |
| --- | --- |
| Browser camera buffer | Approximately 100 MiB, checked on arriving chunks; ten minutes |
| Browser motion buffer | 120,000 observations, twenty minutes |
| Next global proxy | 10 MiB total body; may retain less because the crossing chunk is discarded |
| API multipart request | 51 MiB CSV / 501 MiB video, including multipart overhead |
| API file | 50 MiB CSV / 500 MiB video |
| Normalization/probe | 1,000,000 rows / twenty minutes; video ten minutes / 1920×1080 pixels |
| Pose JSON | 2 MiB request / 300 frames per batch; client currently flushes 100 |

The [official Next documentation](https://nextjs.org/docs/app/api-reference/config/next-config-js/proxyClientMaxBodySize) also describes buffering/truncation. The installed code and actual regression results establish this finding independently of documentation.

### A02 — Worker does not verify the frozen dependency/runtime environment

**HIGH · OPEN · research execution/release blocker**

- **Files:** `apps/api/src/rallysense/experiments.py`, `api/research.py`, `provenance.py`.
- **Evidence:** enqueue records `dependency_lock_sha256` and numerical-library versions. `compute_experiment` verifies implementation source and input artifact hashes, but never compares the frozen dependency lock or runtime with the executing worker. Both adversarial cases in [runtime-regressions](evidence/step5/runtime-regressions.json) publish `succeeded` despite a mismatched frozen environment.
- **Reproduction:** run `apps/api/audit/test_runtime_contract.py` in the API container as documented in FINAL_TEST_REPORT. The disposable fixture changes only the queued manifest's environment descriptor to simulate an API/worker environment difference. No installed dependency or existing record is modified.
- **Expected:** fail with a typed environment mismatch, or execute the exact retained environment and record it. **Actual:** successful output remains attached to the old environment claim.
- **Impact:** rolling updates or separated API/worker releases can violate reproducibility metadata without changing numerical source code. This does **not** establish that existing same-image results are wrong; it establishes a missing enforcement boundary.
- **Correction:** compare the actual worker lock and numerical runtime before inference, record executor identity, and test matching/mismatching environments. Drain or explicitly reject queued old-environment jobs during upgrades. Review the legacy inference path too, which records provenance but has no equivalent execution-time environment guard. Deferred rather than changing scientific execution semantics during the audit.

### A03 — Browser extraction exhausts batch indices after 10,000 observations

**MEDIUM · OPEN**

- **Files:** `features/replay/pose-extraction.ts`, API `api/pose.py`, `schemas.py`.
- **Evidence/reproduction:** `test_audit_pose_batch_capacity_characterization` successfully submits 100 batches of 100 frames, then receives 409 `INVALID_STATE` for batch 100. Client `flush()` emits every 100 observations; API permits only indices 0–99.
- **Expected:** supported source duration/sampling settings should fit the upload contract or be rejected clearly before extraction. **Actual:** the next flush fails after substantial browser work and the track is marked failed. At an achieved 30 observations/s, 10,000 observations span about 333 seconds; at 25/s, about 400 seconds. Targets do not guarantee those achieved rates.
- **Impact:** ten-minute dense tracks can fail although the media upload/probe accepts them. Step 4's late-window test bypassed batch ingestion by finalizing frames directly; it did not validate long browser uploads.
- **Correction:** align client batching, total frame cap, batch count and byte bound; test the full staged ingestion path with at least 18,000 observations and partial retries. Do not merely increase unbounded resource use. Pre-extracted short read-only fixtures are unaffected.

### A04 — Readiness can report writable processing storage as healthy when writes fail

**MEDIUM · OPEN**

- **File:** `apps/api/src/rallysense/main.py:ready`.
- **Evidence/reproduction:** `scripts/audit-storage-readiness.py`, executed as the nonroot API user, points the readiness check at a disposable mode-0555 directory. A real write raises PermissionError while readiness returns `{"status":"ready"}`. [Evidence](evidence/step5/storage-readiness.json).
- **Expected:** local/upload processing readiness should reject unwritable storage. **Actual:** `mkdir(exist_ok=True)` succeeds for an existing directory regardless of its writability.
- **Impact/correction:** uploads and publication can fail behind a green health check. Use a bounded temporary write/read/remove probe in writable mode; verify readable known fixture storage in deliberately read-only mode. Add disk-space monitoring and distinguish readiness from worker health. No live volume permissions were changed.

### A05 — Alignment changes reuse a stale zoomed sensor window

**MEDIUM · OPEN**

- **File:** `apps/web/src/features/replay/workbench.tsx`, samples query.
- **Root cause:** query function depends on `offsetUs`; cache key omits it and `staleTime` is infinite. Saving alignment invalidates the session query, not this cached sample window.
- **Reproduction:** `node scripts/audit-replay-cache.mjs` creates a disposable synthetic session. View session [4,6] seconds at zero offset, then save +1 second. **Expected:** fetch source [3,5] seconds. **Actual:** no sample request; reloading then seeking the same window fetches [3,5]. [Actual request evidence](evidence/step5/replay-cache.json).
- **Impact:** clipped/stale waveform content can mislead interactive alignment until reload. Saved experiment inference reads full source artifacts and is not affected by this display cache.
- **Correction:** include immutable sync identity/offset in the query key or invalidate affected windows, with a browser regression. Reload is the verified interim workaround. Deferred as a small, well-defined remediation item.

### A06 — Cancelled/exhausted source jobs left nonterminal source state

**MEDIUM · FIXED DURING AUDIT**

- **Files:** API `jobs.py`, `api/sessions.py`; tests `tests/test_audit.py`.
- **Original reproduction:** queue an import, cancel it, or expire a running job after attempt three. The job became cancelled/failed while its source remained queued. The initial independent run had five numerical passes and two failing state assertions.
- **Expected/correction:** terminal job and source states agree. Added a small shared terminal-state helper for sensor/video/inference/experiment targets, preserving ready/succeeded output. Cancellation locks the job and leaves already terminal jobs unchanged. Both worker cancellation publication paths and retry exhaustion update the target.
- **Verification:** queued cancellation, claimed-job cancellation without artifact publication, retry recovery, completed-job no-op cancellation and exhausted retry are covered; the full packaged backend suite passes 52 tests. No migration, historical-row rewrite or numerical algorithm change was made.

### A07 — Development-tool dependency advisories remain

**LOW for the deployed runtime · OPEN maintenance item**

- **Files:** `apps/web/package-lock.json` and development lint dependency graph.
- **Evidence/reproduction:** fresh `npm audit --json` reports ten moderate dependency findings propagating minimatch advisory GHSA-g3hv-75wg-m249. Runtime-only npm scan reports zero; 35 pinned Python packages report no known advisories. Evidence: `npm-full-audit.json`, `npm-runtime-audit.json`, `python-advisories.json` under `evidence/step5`.
- **Expected/correction:** review a compatible patched tooling graph and rerun lint/build/contracts. No blind major downgrade or forced audit fix was applied. The current evidence does not demonstrate a runtime exploit. Container OS packages remain unscanned and require a separate release scan.

No CRITICAL private-data exposure or primary numerical-invalidity defect was confirmed in the tested scope. This is not a claim that all vulnerabilities have been excluded.

## Scientific and computer-vision assessment

IMU normalization retains raw bytes, subtracts the first source timestamp before integer microsecond conversion, converts g by 9.80665 and degrees/s by pi/180, and retains absent channels as missing. DeviceMotion beta/gamma/alpha map to device x/y/z angular rates; linear and gravity-inclusive acceleration are explicit alternatives. No gravity subtraction, world-frame reconstruction, physical placement correction or racket velocity is inferred.

The offline detector filters angular-speed magnitude using fourth-order Butterworth SOS forward/backward filtering, a measured median sampling interval, gap segmentation and boundary guards. Small within-segment irregularities are interpolated; large gaps split. The research guard scales with cutoff. These are engineering choices, not learned tennis constants, and do not guarantee freedom from aliasing, edge bias or sensor-placement effects.

Video features use aspect-corrected normalized x/y and a median visible torso scale, hip-relative wrist differences and actual interval midpoint timestamps. Visibility failures break derivative chains; large gaps are excluded. The older replay feature strip has per-frame normalization/later-frame derivative semantics, while research inference recomputes its separately defined baseline. These should not be interpreted as identical curves. World landmarks and visibility are model outputs, not calibrated biomechanics or probability of correctness.

Actual pinned MediaPipe CPU integration ran on the permitted clip: playback worker 117 observations, seek/backpressure 149, forced main-thread fallback 49. FFprobe found 149 source frames; every stored observation timestamp in all three tracks matched a decoded presentation timestamp exactly in microseconds. Strict ordering was verified. This checks one clip's timing grid, not pixel identity, exhaustive VFR support, arbitrary PTS origins or frame-perfect detection. Playback cadence varied from Step 4; frozen-track inference, not repeated browser extraction, is the deterministic comparison boundary. [Timing evidence](evidence/step5/frame-timestamps.json).

Fusion genuinely requires both modality event lists, intersects common coverage, and uses cardinality-first/minimum-error one-to-one matching within a fixed tolerance. It retains the IMU timestamp, both source timestamps and disagreement; it does not average unlike observations into artificial agreement. Unmatched indices remain available. Incorrect +1-second alignment removed both generated associations; complete occlusion failed explicitly. This is **temporal event association**, not learned biomechanical reconstruction. Agreement can reduce recall and is not assumed to improve accuracy.

Evaluation counts and timing were checked analytically: TP=3, FP=1, FN=2 yields precision .75, recall .6, F1 2/3; absolute errors 10/20/30 yield mean/median 20. A separate 120-case enumeration covers unsorted duplicates and the matching objective. Undefined denominators remain null. Full declared evaluation intervals retain missed references despite coverage loss. Frozen reference revisions and same-session/video restrictions pass integration tests. No automatic ground-truth generation from predictions or independent real tennis evidence was found. Pairing and label independence remain operator attestations; A02 limits runtime reproducibility enforcement.

All six corruption families actually alter derived inputs or alignment, use seeded streams, preserve original measurements, rerun inference and evaluate its output. Fresh 11-condition verification includes clean modes, dropout, gyro/acceleration noise, jitter, missing IMU window, wrist occlusion, synchronization error and full occlusion. Acceleration noise affects the descriptive acceleration statistic, not the gyro-only event rule. Synthetic perfect scores establish plumbing/numerical agreement with a generator, not real-world model accuracy.

## Architecture, security, performance and UX

The modular FastAPI routers, pure numerical core, PostgreSQL ownership constraints and separate durable worker are appropriate for a single workspace. Function-scoped transactions publish only after commit; lease tokens fence stale workers and deletion tombstones block active reads. Atomic file replacement plus delayed orphan reconciliation acknowledges the filesystem/database transaction boundary. Storage is filesystem-specific, not a completed object-store abstraction. Long computation reads whole artifacts; histories and session detail can still grow substantially.

Security verification covered exact Host/Origin checks, missing/wrong internal token, traversal and ownership checks in the ordinary suites; plus twelve hidden-resource read paths, reports, Range media, pose/sensor data, comparisons and job access in the new suite. Production images challenged unauthenticated page/API routes with 401, including a spoofed middleware-subrequest header; authenticated approved fixtures were visible, private IDs returned 404 and direct API mutations returned 403 in read-only mode. Temporary test containers were removed. No allowlist bypass was confirmed. Shared workspace credentials are not multiuser authorization, and allowlisting an old synthetic session does not sanitize its notes or media.

Upload bounds, subprocess argument arrays/timeouts, restricted FFmpeg protocols and nonroot app containers reduce risk. They are not a hardened hostile-file sandbox or distributed quota system. Source-upload throttling is process-local; it does not limit all reads, experiments, disk growth or concurrent memory. Do not expose the default development token, DB password or direct backend ports. TLS, upstream abuse controls, backup restoration and OS-image scanning are outstanding deployment gates.

Same-current-history measurement: 50 full results transferred 3,255,565 bytes; summaries plus selected failed-result detail transferred 222,471 bytes. This confirms a response-size benefit; the selected detail is small, so it is not a like-for-like reproduction of Step 4's percentage. The server still materializes full JSONB results before projecting summaries. No database-speed improvement is established. Sixteen navigation checks ranged roughly .57–1.22 seconds through network idle under concurrent local workload; these are observations, not capacity/SLA benchmarks. Maximum-size concurrency was not stress-tested.

Eight route families were visited at desktop/mobile sizes with zero horizontal overflow and no page errors. Screenshot inspection confirms a consistent hierarchy, explicit synthetic labels, usable replay controls and legible failure states. Reference workflow, event seeking, graph seeking, exports and print report are exercised by browser tests. Basic DOM checks found an h1 and no unnamed buttons on those views; screen-reader, keyboard-only, contrast, focus-order and WCAG conformance were not comprehensively audited. The mobile Challenge is very long and information dense. The application is understandable with a short guided technical demo, but a first-time recruiter should be directed to a curated successful run before deliberate failure examples. Physical capture permissions/interruptions remain device-specific and in-memory route navigation can discard unsaved buffers.

## Technical-interview readiness

The defensible presentation is an observation/reproducibility platform with transparent analytical baselines:

- IMU measures device acceleration/angular rate. A gyro maximum does not establish a swing or impact; fixed placement and independent labels are required to test that proxy.
- Video events are peaks in torso-normalized image wrist speed, not maximal extension or ball contact.
- Fusion adds a temporal agreement constraint with retained disagreement and coverage; it does not infer hidden biomechanics.
- Clocks use `session_us = sensor_us + offset_us`; two cues expose residual inconsistency but no drift is corrected.
- Association and evaluation each default to 150 ms, serve different purposes and must be fixed before held-out scoring.
- Reference snapshots freeze operator-declared human observations; independence cannot be certified by a checkbox. Blind labeling and a separate protocol reduce circularity.
- Perfect synthetic F1 verifies the constructed software fixture. Real paired recordings, negatives, inter-rater consistency and participant-separated evaluation are still required for tennis claims.
- Missing data can remove coverage/events or force explicit failure; references in the declared task interval remain misses.
- Recording conditions, subject identity, camera geometry, placement, sampling cadence and threshold choice can change outcomes. No cohort/generalization result exists.

Present A01–A05 candidly with their evidence and remediation gates. Use recorded successful short fixtures, then a controlled failure, and distinguish analytical landmarks from actual MediaPipe output. Do not describe this as a validated swing classifier, production multiuser system or completed deployment.

## Handoff

[REMEDIATION_PLAN](REMEDIATION_PLAN.md) orders concrete fixes and exit tests. [DEPLOYMENT_READINESS](DEPLOYMENT_READINESS.md) separates fixture-only public-demo requirements from upload-enabled operation. [KNOWN_LIMITATIONS](KNOWN_LIMITATIONS.md) records scope gaps. Step 5 stops here; remediation and deployment require separate authorization.
