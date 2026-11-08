# Architecture decision record

## Step 3 accepted implementation decisions (2026-11-05)

- **ADR-023 - preserve observation semantics:** gyro magnitude and image wrist-speed maxima are distinct observable events. Video inference recomputes interval-midpoint wrist velocity using actual stored landmarks and a fixed median torso scale. Legacy Step 2 primitives/results remain available.
- **ADR-024 - association with an IMU anchor:** replace the planned timestamp midpoint fusion with explicitly named temporal association. Pair one-to-one inside continuous common eligible intervals; keep both timestamps, source indices, disagreement and unmatched candidates. Agreement does not establish a common physical apex or impact.
- **ADR-025 - frozen small research records:** use additive PostgreSQL snapshot/experiment tables and immutable JSONB manifests/results while referencing dense input artifacts by ID/hash. Use the existing durable worker; no extra infrastructure. Draft edits advance set revision, and frozen references remain unchanged.
- **ADR-026 - explicit evaluation eligibility:** identical definitions for exact scoring, declared proxy hypothesis for supported human movement references, and separately labeled synthetic fixture verification. Missing references never produce accuracy metrics. Pairing/independence declarations are attestations; source-video mismatch is refused.
- **ADR-027 - deterministic matching:** implement ordered maximum-cardinality, minimum-absolute-error dynamic programming with stable tie handling and inclusive tolerance. Cap each list at 2,000 events. Full declared intervals retain misses caused by unavailable observations; report eligible coverage separately.
- **ADR-028 - derived perturbations:** apply seeded dropout, SI noise, bounded timestamp jitter, missing windows, landmark visibility masks and sync error to in-memory copies. Persist recipe and rerun actual algorithms. Inapplicable modality settings are rejected.
- **ADR-029 - actual browser cadence:** retain the verified 10 Hz path and offer a 30 Hz target with half-speed playback, recording achieved cadence and gaps. Neither promises exhaustive decoding or impact timing.
- **ADR-030 - separate paired software fixture:** add a generated stick-figure clip, analytical landmarks and paired Gaussian IMU pulses on a shared clock. Explicit provenance prevents confusing these landmarks with MediaPipe output. The unrelated official clip/synthetic IMU test remains mixed and ineligible for fusion.
- **ADR-031 - commit before acknowledgement:** set database dependency lifetime to FastAPI function scope. A local smoke run directly exposed a transient 404 after successful experiment creation because request-scope teardown could commit after response delivery. The corrected boundary commits before response headers and surfaces commit failures as errors. PostgreSQL/ASGI regression coverage verifies the actual ordering, not only immediate reads after a test client returns.

The following earlier planning and Step 2 records are retained as history. Where they describe planned averaging or unavailable Step 3 features, the decisions above and [RESEARCH.md](RESEARCH.md) supersede them.

Accepted for planning on 2026-11-03. None implies implemented or benchmarked functionality. Change decisions explicitly when implementation evidence warrants it.

| ID | Decision | Reason and tradeoff | Revisit when |
| --- | --- | --- | --- |
| ADR-001 | Next.js + FastAPI modular monorepo | Matches requested stack and separates interactive browser work from numerical Python; two runtimes add setup cost | Actual integration/build evidence exposes incompatibility |
| ADR-002 | Browser MediaPipe worker is primary pose path | Reduces server inference load and fits client-side preference; browser/session interruption and frame coverage require explicit handling | Long clips or reproducible exhaustive decoding require a server pipeline |
| ADR-003 | Source clocks plus revisioned microsecond mapping | Prevents silent origin/unit confusion and preserves historical run reproducibility; revisions complicate cache/UI state | Precision/range requirements change |
| ADR-004 | PostgreSQL metadata, immutable Parquet/files for dense data | Avoids SQL sample-row explosion while retaining relational constraints and efficient column/time reads; filesystem/DB recovery must be designed | Measured scale exceeds single-host storage |
| ADR-005 | One durable PostgreSQL job worker | Retry/restart/cancel state without Redis or distributed infrastructure; moderate polling/lease complexity | Measured concurrency needs exceed this design |
| ADR-006 | IMU analytical baseline before trained models | Real calculable behavior without unavailable training data; fixed parameters have limited generalization | Labeled data with adequate grouped splits exists |
| ADR-007 | Blinded human event references, explicit proxy hypotheses | Gyro peaks and pose estimates are not impact or biomechanical truth; annotation uncertainty limits conclusions | Pilot shows the selected reference cannot be labeled reliably |
| ADR-008 | Cardinality-first, minimum-error event matching | Avoids greedy matching errors and one prediction matching multiple labels; evaluator needs adversarial tests | Event definition changes to intervals or multi-class structure |
| ADR-009 | Manual offset first; drift/fusion/evaluation in Step 3 | Keeps MVP end-to-end while preserving scientific extensions | Step 3 authorization and alignment evidence |
| ADR-010 | Loopback-only single-user MVP | Avoids pretending local UUIDs provide multiuser isolation; public demo requires auth/ownership/retention review | Explicit public deployment design and authorization |
| ADR-011 | Versioned provenance for observations/features/predictions/labels/fixtures/results | Enables honest synthetic demonstration and reproducible comparisons; adds manifest/schema work | Never remove the separation; evolve schemas as needed |
| ADR-012 | npm + uv; no dependencies installed in Step 1 | Available tools, conventional locks, architecture-only scope; full compatibility remains an implementation check | Resolver/build evidence warrants versions or manager changes |
| ADR-013 | PostgreSQL 17 target with maintained patch selected later | Supported conservative baseline; pin digest after checking registry and runtime | Step 2 dependency resolution or support policy changes |
| ADR-014 | Synthetic demo uses ordinary pipelines and optionally programmatic animation | Hardware-free reproducibility; no real-video inference validation from artificial skeletons | Licensed real demo recording available |
| ADR-015 | Local requested repository, no Sites registration/hosting | User mandates Next.js/Python/PostgreSQL and no publication; hosting workflow is not needed for planning | A separately authorized deployment task chooses hosting |

The Sites skill was inspected for applicability; its implementation/publishing workflow was not invoked because the authorized stage is documentation-only. No Site was created, registered, synchronized, or published.

## Step 2 implementation decisions

- **ADR-016 — measured event semantics:** per the user's explicit Step 2 instruction, the baseline emits `gyro_peak_v1`, described as filtered angular-speed maxima and unvalidated movement proxies. It never assigns a confirmed swing/impact label. Human `swing_apex_v1` annotations remain separate.
- **ADR-017 — verified classic worker:** inspected installed `@mediapipe/tasks-vision` 1.2.0 type signatures and its `Vision` IIFE bundle. A classic worker uses `importScripts`, local WASM, the pinned Lite model, and CPU execution. Initialization failure explicitly selects a main-thread CPU fallback. No tracker states are spliced mid-extraction.
- **ADR-018 — direct confirmed import:** the UI previews headers/column/unit/provenance mapping before one import submission. Full parsing/normalization is a durable worker job. The proposed separate server preview/commit resource is deferred; validation failures are visible jobs, not successful imports.
- **ADR-019 — runtime local proxy:** a Next.js route handler injects the server-held local credential, forwards streaming media/Range requests, and rejects foreign Host/Origin values. FastAPI also checks credentials/origins and resource ownership. This is single-user local access, not public authentication.
- **ADR-020 — staged pose batches:** bounded, hashed, idempotent JSONB batches provide upload staging; completion validates ordered times, derives image-space features, writes compressed Parquet, and deletes staging rows. Abandoned tracks expire after a 24-hour grace period during maintenance.
- **ADR-021 — concrete source provenance:** sessions expose recorded/synthetic/mixed types; sensor mappings retain recorded/synthetic origin. Generated fixture references are immutable and visibly distinct from editable human observations. User declarations are recorded, not independently authenticated.
- **ADR-022 — implementation fingerprints:** inference identities include source artifact hash, alignment revision, expanded configuration, signal implementation hash, dependency-lock hash, and numerical library versions. Old completed runs retain their manifests.

The earlier decision table describes the accepted architecture; source-level details and known limits are recorded in STEP2_REPORT. No advanced event classifier, fusion, or evaluation engine has been implemented.

## Invariants retained at the Step 2 checkpoint

- Positive IMU offset moves sensor events later relative to video; inverse mapping subtracts the offset.
- Changing alignment/configuration/labels creates a new revision and never silently changes old experimental results.
- Nonfinite/missing samples never become zero and never cross large gaps through implicit interpolation.
- Missing input is distinguishable from a successful detector returning no events.
- A score, quality indicator, confidence interval, and annotation uncertainty are different concepts.
- No metric or user-facing claim may imply a real experiment when only synthetic fixtures have run.
- A completed stage always stops at its mandatory gate. Publication and Git push remain unauthorized.

## Step 4 decisions, 2026-11-06

- Preserve the local Next/FastAPI/PostgreSQL/durable-worker architecture and scientific event semantics. Use an additive collection/evidence/heartbeat migration and preserve old manifests/results.
- Use explicit browser quantities and per-source recorded/synthetic provenance; never silently replace missing linear acceleration with gravity-inclusive acceleration or treat angular rate as attitude. Unsaved capture is bounded memory, with explicit save/export and interruption states; no background recording promise.
- Repair a directly observed streamed WebM duration problem with bounded encoded-frame container copying, retaining the original artifact/hash. Do not introduce general automatic transcoding.
- Add optional seek/backpressure, retain actual presentation timestamps and existing playback/fallback. Keep achieved cadence separate from target frequency.
- Load cursor-local pose windows and summary experiment history; full scientific artifacts/results remain available. Use deterministic stored-result explanations, not an external LLM.
- Public preparation uses fail-closed builtin synthetic allowlists and requires fresh isolated volumes. A shared local token/workspace password is not multiuser security. Prepare private trusted phone HTTPS without actually opening a LAN listener.
- Recommend the implemented filesystem-compatible container topology for an initial demonstration. Split serverless/object-store architecture needs adapters and upload changes. No deployment, paid service or push in Step 4.

## Step 5 audit decisions, 2026-11-07

- Preserve numerical algorithms, scientific event semantics, frozen results and user data. The only application repair during this audit propagates terminal source/run status on cancellation or exhausted retries and makes terminal cancellation a no-op under a job lock. No schema migration or historical-row rewrite was added.
- Retain four explicit failing audit regressions: valid large CSV/video uploads and mismatched frozen worker lock/runtime. Ordinary suites passing does not override these release failures. Separate runnable audit gates are described in FINAL_TEST_REPORT and must remain part of remediation acceptance.
- Do not raise Next's 10 MiB clone limit to 501 MiB without a bounded-memory ingress design. Prefer authenticated streaming through the existing single-host topology; architectural implementation is deferred to separate authorization.
- Distinguish a fresh fixture-only precomputed read-only demonstration from upload-enabled research and open multiuser service. The audit verdict is SIGNIFICANT FIXES REQUIRED. Deployment remains unauthorized. See FINAL_AUDIT, DEPLOYMENT_READINESS and REMEDIATION_PLAN.

## Step 5.5 remediation decisions, 2026-11-08

- Use the existing authenticated API route as a bounded streaming gateway and exclude it from global Next Proxy cloning. Share the workspace gate explicitly; do not increase large in-memory clone limits or forward caller credentials. A separate pinned Caddy layer terminates future TLS and only forwards to private web.
- Enforce frozen lock/Python/numerical runtime before new research/legacy computations; record actual executor metadata in result JSON without migrations or historical manifest rewriting. Old incompatible queued work fails typed; upgrades drain the old worker first.
- Keep detector mathematics/event labels unchanged. Reconcile pose ingestion through bounded count/byte batching and a total observation cap, with expected completion count. Readiness is mode-aware; replay query identity includes synchronization revision/offset.
- Read-only workers never compute or reconcile files; Mode A uses fresh generated/precomputed fixture volumes and read-only artifact mounts. Mode B remains a single authenticated shared workspace. No public multiuser/anonymous-upload claim is introduced.
- Preserve baseline data through full-row/hash checks. Isolate browser annotation edits in new sets; guarded cleanup restored only the test-induced synthetic label-set counter from the pre-test backup. Paired backups restore only into new isolated projects; never reset live volumes.
- Retain ten moderate development advisories pending compatible maintenance. OS scanning requires unavailable Docker authentication; public TLS/host/content/monitoring/off-host recovery remain human release gates. No deployment, provisioning or remote push in this stage.
