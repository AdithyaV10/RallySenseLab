# Project status

## Public Cloudflare acceptance — 2026-11-09

**NOT READY to share.** The user deployed the separate static showcase to https://lucky-band-a550.adithya-v1833.workers.dev/. Actual-public Chromium acceptance returned **9 passed / 5 failed** across 14 cases. Three confirmed defects: video seeking resets to zero because the served MP4 has no usable byte-range seeking; hero accessible-name mismatch; comparison scroll region cannot receive keyboard focus. Public data, all 28 approved file hashes, ten scenarios, report exports, scientific labels, basic playback and responsive layouts verified.

A static-only replacement fixes all three defects and passes local build/types/lint, 7 units, 8 browser workflows, 10 repeated seeks and 18 accessibility/layout checks. **Replacement is not deployed; no public pass is claimed for these fixes.** Upload the complete checked replacement output to the existing Worker and rerun public acceptance. No full-stack algorithms, databases, private research artifacts, AWS resources or other Cloudflare resources changed. [Acceptance report, unresolved live status, package and exact handoff](LIVE_PRODUCTION_ACCEPTANCE.md). Earlier AWS/local-only status below is historical.

## Current final delivery ? static showcase (AWS action required)

**Static application complete and locally verified; not publicly deployed.** Separate `apps/showcase` Vite/React/TypeScript app includes the premium landing, synchronized generated video/IMU/analytical-pose replay, ten stored scenarios, comparisons, failure navigation, provenance and accurate report exports. Build output is 28 files / 2,507,048 bytes; local checked ZIP is in ignored `storage/static-showcase/`. [Release notes, actual tests and AWS GUI handoff](STATIC_SHOWCASE_RELEASE.md).

Production build, types, lint, 7 units and 9 final production-browser cases passed. All runtime requests stayed on same-origin static GET paths; no backend/model/credential/native assets. Original 85 full-stack source/release fingerprints, 12 research row inventories and 139 artifact hashes are unchanged. No research algorithm was modified. Original image/Mode B security findings remain preserved; this delivery excludes those server/model components.

AWS resource creation is paused at the user's $0 gate: `rallysense-showcase` CLI authentication is now verified (root identity), but actual new-distribution CloudFront Free $0 plan availability and S3 request-cost/credit coverage remain unverified. Read-only queries returned zero existing flat-rate subscriptions and no S3 allowance records; neither proves new-plan eligibility or zero total cost. No AWS resources were created, no PrintMatch resources were changed, no DNS/custom domain/paid service/push occurred, and no live URL is claimed. Continue only after the user confirms the account/plan/cost gate. Historical stage reports follow unchanged.

## Current Step 6.6 checkpoint ? 2026-11-09

**Mode A local security/preflight review delivered: CONDITIONAL GO for human review, NOT security-approved or authorized for public deployment. Mode B remains NO-GO and out of public scope.** Starting checkpoint `6ec8a92ea03e9a58f4987d7a6f67309eefa4ac96` was clean. Final local commit contains the decision package; retrieve with `git log -1 --format=%H`. No cloud/DNS/public listener/registry/GitHub action occurred.

Read [Mode A review](STEP6_6_MODE_A_REVIEW.md), [deployment checklist](MODE_A_DEPLOYMENT_CHECKLIST.md), [release decision](MODE_A_RELEASE_DECISION.md) and the separate [Mode A manifest](../infrastructure/mode-a-release-manifest.json). The original Step 6.5 manifest/images/evidence are preserved. Historical two-domain deployment commands must not expose Mode B.

Docker Desktop connectivity was recovered non-destructively. Four original Mode A archive hashes matched. New readonly API removes unused pip/vendor/bootstrap code. A supported PostgreSQL 17.11 Alpine variant with the same stable helper rebuilt on Go 1.27.3 is for fresh generated Mode A volumes only. Scientific app source, locks and algorithms are unchanged. Final Mode A raw scans: **0 critical / 94 high instances (12 unique CVEs)**, plus **seven manual unresolved XML advisories missing from Alpine's feed**. Zero PostgreSQL scanner highs does not resolve that manual review. Caddy JOSE v3 and API/web OS findings require explicit human dispositions; none approved. Model-weight/content/branding/access sign-offs and public operational checks remain pending.

Fresh standalone Mode A rehearsal: five healthy services; 8 live HTTP groups, all 22 registered mutations denied, hidden/private-source requests denied, 1 browser workflow and 1 private-CA release smoke passed. Targeted backend initial 25 passed/3 failed on TestClient Host; corrected test-only setup yielded 1 readonly worker + 2 trusted fixture guard passes. All failures are retained/explained; no new full-suite run is claimed. Eleven deterministic scientific conditions were identical. A generated paired backup/restore matched 17 table digests and 6 artifact hashes. Original 12 research row inventories and all 139 original artifact hashes remained intact.

Initial Mode A sizing recommendation is 2 vCPU/4 GiB/80 GiB, about $24/month compute plus extras, based on small local readonly measurements; target Linux capacity/public DNS/CA/firewall/reboot/off-host recovery/alerts are unverified. Mandatory human decisions and explicit deployment authorization precede external work. No next stage started.

## Current Step 6.5 checkpoint — 2026-11-09

**Targeted container remediation and review delivered. No image/public release is security-approved. Mode A is ready for human residual-risk review; Mode B remains blocked by native-media findings.** Starting checkpoint: `208e96dbe52d1a36670f16ae05656b6a5a700a23`. New frozen local RC aliases and OCI/archive identities are in [release manifest](../infrastructure/release-manifest.json); rollback images/manifests remain retained.

The four-component scan comparison is **4 critical/371 high → 1 critical/163 high** package instances. Full API:0/52; readonly API variant:0/52; final web:0/46; PostgreSQL:1/64; Caddy:0/1. No broad ignore or security exception was approved. Custom static FFmpeg is reviewed separately from OS package counts: the actual MOV/PSSH path confirms bounded resource exhaustion (CVE-2026-107678), and HDR metadata serialization (CVE-2026-107676) remains unresolved. **Mode B must not be released merely because its package scan improved.** Mode A omits native media tools entirely.

Verification:68 backend +15 frontend units,9 final standard browser cases,2 original upload +2 original runtime audit cases,14 large/adversarial probes,9 HTTPS groups,2 actual release-browser workflows and11 deterministic scientific equivalence conditions passed. A new hardened-workspace restore matched17 tables/14 artifacts. All original12 research inventories and139 artifact hashes were preserved. Scientific algorithms, numerical versions, locks and schema head remain unchanged. No public listeners/cloud/DNS/publication/push occurred.

Read [remediation report](STEP6_5_SECURITY_REMEDIATION.md), [final image security review](FINAL_IMAGE_SECURITY_REVIEW.md), [final release candidate](FINAL_RELEASE_CANDIDATE.md) and [updated controlled deployment handoff](DEPLOYMENT_HANDOFF.md). Explicit shared PostgreSQL XML/Caddy JWK/OS/SBOM dispositions, content/model/access approval and external deployment verification remain pending. No next stage is started.

Final post-interruption Docker Engine enumeration is unavailable: Desktop reports starting/already running but requests fail. Prior completed tests, preservation/recovery and successful stop evidence are retained; all five candidate archives were rehashed offline. Current live container/volume status is not freshly verified. No reset/prune/volume deletion was used. See [final local state](evidence/step6_5/final-local-state.json).

## Current Step 6 checkpoint — 2026-11-09

**Local release preparation/rehearsal delivered; PUBLIC RELEASE BLOCKED pending image-security disposition and external acceptance. No deployment authorization was exercised.** Approved application checkpoint remains `ac75d818a168bfcf1b7f23a609121b18b0933e8e`. Existing application images were reused; scientific code, dependency locks, migrations and historical research records were not changed.

Two isolated fresh projects and one loopback-only HTTPS gateway verified the synthetic readonly demonstration and protected research workspace simultaneously. Real TLS chain/name checks, Host/SNI/Origin/auth enforcement, private backend isolation, readonly mutation/allowlist/worker behavior, replay/comparison/failure exploration/exports and actual workspace ingestion/MediaPipe/sync/annotations/experiments passed. The generated MediaPipe clip processed 79 frames with zero person detections; no accuracy claim follows. A fresh paired backup/restore matched 17 tables and six generated artifacts.

Auth-free pinned Trivy scanning completed for all four images, replacing the earlier Scout-login limitation. It found **4 critical and 371 high package instances** (including duplicates/tooling). Raw findings and per-instance triage are retained; **the image security gate did not pass**. API media/XML parser advisories, gateway dependencies, OS updates and residual applicability decisions remain release blockers. Readonly mode mitigates uploads but does not clear public-facing image findings.

Read [Step 6 report](STEP6_RELEASE_REPORT.md), [deployment handoff and exact controlled commands](DEPLOYMENT_HANDOFF.md), [vulnerability review](VULNERABILITY_REVIEW.md), and [fixture inventory](FIXTURE_RELEASE_INVENTORY.md). The single-host recommendation is two independent application projects plus one shared Caddy gateway on a 16 GiB Linux/amd64 host. Viewer demo and research workspace retain distinct passwords. Real DNS/ACME/firewall/capacity, off-host recovery, alert delivery and owner content/model approval remain unverified. Do not provision, publish, change DNS or start public listeners without explicit authorization.

## Historical Step 5.5 checkpoint

Updated: 2026-11-08, America/New_York.

**Step 5.5 remediation complete. SOFTWARE ACCEPTANCE PASSED; PUBLIC DEPLOYMENT ACCEPTANCE PENDING.**

Authorization: [Step 5.5 specification](STEP5_5_SPECIFICATION.md). Starting checkpoint: `be725ae5cb474c74c84a3d2357565facd0f6d997`. The final local checkpoint contains corrections, original regression gates, new tests, evidence and release preparation. Obtain its ID with `git log -1 --format=%H`. No deployment, cloud provisioning or remote push occurred.

## Confirmed outcomes

- A01: independently authenticated bounded streaming uploads; actual 50 MiB CSV and 500 MiB MP4 passed through the web path with worker success and identical stored hashes. No large Next Proxy clone buffer.
- A02: frozen dependency/Python/numerical runtime enforcement for research and legacy inference; actual executor identity recorded; historical completed results unchanged.
- A03: bounded byte/count batching and total observation cap; 18,000 observations passed ordinary staged ingestion, with retry/conflict/completion checks.
- A04: writable write/read/fsync/remove/free-space readiness and read-only approved-fixture readability. Actual unwritable storage returns generic 503.
- A05: synchronization revision/offset participate in replay cache identity; browser verifies positive/negative offsets, partial and empty coverage without reload.
- A06 terminal-state repair remains covered. A07 remains ten moderate development-tool advisories; npm runtime scan reports zero.

## Actual verification

- Backend: **65 passed**, zero failed/skipped, six deprecation warnings.
- Frontend units: **15 passed**.
- Standard production browser: **9 passed**, zero failed/skipped/flaky, including actual MediaPipe worker/seek/fallback.
- Original audit gates: **2 upload + 2 runtime cases passed**, no weakened assertions or skip/xfail.
- Real upload boundary/adversarial probe: **14 cases passed**, including chunked limits, hashes, aborts, idle timeout, concurrency, invalid Origin/Host and malformed requests.
- Types, ESLint, Ruff, contracts, migration consistency and production image builds passed. Head remains `0003_collection_readiness`; no schema migration was added.
- Eleven synthetic scientific conditions had expected software outcomes; no real-world tennis accuracy was claimed.
- Production-image access checks, both release configuration modes, fresh synthetic-only read-only fixtures, restart and ordinary smoke passed.
- A paired backup/isolated restore matched **17 table digests and 116 then-current artifacts**. Original and test recovery volumes were retained.
- Full original-row preservation passed across 12 model inventories. Baseline includes 134 experiments, 19 frozen references, 116 artifacts, 43 active sessions and original annotations/legacy runs/poses/syncs. The final complete artifact scan checked **139 files: zero missing/mismatched**.

The browser annotation test now uses a dedicated new set. Its earlier three revision-counter increments on an existing synthetic set were restored using the isolated pre-test backup and an exact baseline hash guard; no annotation values or frozen records changed. Historical Step 5 failure evidence and Step 4 camera evidence are preserved.

## Release handoff

- [Implementation report](STEP5_5_REMEDIATION_REPORT.md)
- [Release acceptance and exact checks](RELEASE_ACCEPTANCE.md)
- [Deployment execution plan](DEPLOYMENT_EXECUTION_PLAN.md)
- [Current readiness](DEPLOYMENT_READINESS.md) and [known limitations](KNOWN_LIMITATIONS.md)

Mode A is a fresh curated read-only workspace with approved generated fixtures and precomputed results; it was verified locally with read-only artifact mounts and no exposed ports. Mode B is an authenticated shared research workspace with functioning uploads and scientific workflows. Neither is a public anonymous multiuser service.

Before public deployment: authenticate and review OS/FFmpeg/base-image scans (Docker Scout was blocked by missing Docker login), approve fixture/licenses/content, configure and verify actual host/domain/TLS/firewall/secrets, establish off-host backup retention/monitoring, and validate resource budgets on the target host. Physical phones and independent paired-tennis validation remain unverified. No clean OS scan or deployment result is invented.

Local startup from `C:\RallySenseLab`: `docker compose up -d --build --wait --wait-timeout 60`; open http://127.0.0.1:3000. Existing volumes are retained. Private backup and stopped isolated restore/demo projects remain local; do not reset or remove them as part of startup.

**STEP 5.5 COMPLETE - REMEDIATION AND RELEASE ACCEPTANCE DELIVERED. AWAITING DEPLOYMENT AUTHORIZATION.**
