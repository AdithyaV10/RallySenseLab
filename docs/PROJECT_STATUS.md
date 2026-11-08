# Project status

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
