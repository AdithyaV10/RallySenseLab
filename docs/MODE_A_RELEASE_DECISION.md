# Mode A release decision — Step 6.6

2026-11-09. Baseline `6ec8a92ea03e9a58f4987d7a6f67309eefa4ac96`. Final local checkpoint is the commit containing this document (`git log -1 --format=%H`); its hash is provided in the handoff.

**Recommendation: CONDITIONAL GO for the scoped, password-gated interactive readonly demonstration. This is NOT release approval or deployment authorization.** Local software/preflight preparation is complete. Public exposure must wait for explicit security/content/model decisions and external operational acceptance. If those decisions are rejected or cannot be made, the disposition is **NO-GO** until patched/repackaged/retested.

**Mode B remains NO-GO and is excluded from public deployment.** MOV/PSSH DoS and Matroska HDR serialization blockers are unchanged. No native processing route, full API image, research workspace host, private database or private recording may be added to this release.

## What is ready

- Standalone Linux Docker Mode A topology: Caddy HTTPS → Next.js → readonly FastAPI + idle durable worker → private PostgreSQL, separate persistent generated artifacts. Actual loopback rehearsal: five healthy containers, all 22 registered mutations denied, backend fixture allowlisting, real video/replay, graphs, stored pose, ten precomputed clean/corrupt experiments, failure explorer, comparison and exports.
- Supported fresh-volume PostgreSQL variant avoids the old reverted-libxml2 critical and uses the maintained Go toolchain for the same entrypoint helper. Readonly pip/bootstrap component removed. No algorithm, app source or dependency lock changed. Eleven generated scientific cases stayed numerically identical.
- Exact four-image archives/config/rootfs identities and generated paired bundle frozen in [Mode A manifest](../infrastructure/mode-a-release-manifest.json). Original Step 6.5 manifest/images/evidence remain intact. No registry/push/public action occurred.
- Generated backup restored with 17 matching table digests and six artifact hashes. Original private rows across 12 inventories and all 139 original artifact hashes preserved.
- Exact render-only preflight, secret generation, transport allowlist/checksums, restore, cutover, smoke, monitoring, backup and rollback instructions prepared in [deployment checklist](MODE_A_DEPLOYMENT_CHECKLIST.md). This package does not transfer secrets or the full API image.

## Mandatory human decisions — all still pending

| Gate | Required decision / evidence | Status |
| --- | --- | --- |
| Security A: PostgreSQL XML | SQL/XML positively reachable to SQL users. Installed 2.13.9-r2 is newer than the 2.11.0 fix for historical CVE-2026-6653, but six later 2.15.4 advisories plus Python SAX advisory lack Alpine backport proof. Accept a named/time-bounded exact-configuration exception or require vendor evidence/supported patch. No scanner-feed absence waiver. | **PENDING** |
| Security B: gateway JOSE | go-jose/v3 3.0.5 high remains, no upstream v3 patch. Direct JWK features absent/admin off; public ACME/renewal indirect paths not fully established. Explicit scoped decision or supported upstream fix. | **PENDING** |
| Security C: API/web OS | 93 raw high package instances across 11 unique OS CVEs remain (47 API, 46 web): mount/nsenter/ACL/homed/infocmp/Perl/SQLite conditions. Per-instance provenance/reachability documented; not blanket excluded. Scope includes synthetic-only DB role/host privilege limits. | **PENDING** |
| Public fixture/branding | Approve generated content, ownership, labels, report presentation and RallySense Lab name/branding. No athlete/real-world accuracy validation is claimed. | **PENDING OWNER** |
| Model/component terms | Exact Lite model weights and code/WASM/bundled notices; model remains in web image even when unused. Owner/legal clearance or authorize a separately tested asset-removal rebuild. | **PENDING OWNER/LEGAL** |
| Access/operations | Approve shared viewer-password policy, selected provider/host/budget/domain, security maintenance, monitoring recipient, off-host backup retention and recovery objectives. | **PENDING OWNER/OPERATOR** |
| External actions | Explicit authorization before paid provisioning/private transfer/DNS/firewall/public listener. | **NOT GRANTED** |

Suggested exception template (proposal only): affected CVEs/images/config hashes; rationale and exposure category; required controls; reviewer/owner; approval or rejection date; expiry no later than an owner-chosen short review window (suggest 30 days); patch/watch cadence; invalidation on image/config/auth/network/new-input changes; rollback/closure trigger. Blank fields are not consent. No exception has been signed by the agent.

## Verification result and practical limits

Final raw scanner result: **0 critical / 94 high instances**, 12 unique high CVEs, **plus seven manual XML advisories** not in the Alpine scan. PostgreSQL's raw 0/0 does not override manual XML risk. All lower/UNKNOWN results remain available. The [review](STEP6_6_MODE_A_REVIEW.md) and [per-finding JSON](evidence/step6_6/residual-security-dispositions.json) distinguish confirmed SQL capability, configuration-limited paths, plausible indirect exposure and insufficient evidence.

New executions: **8 live HTTP groups**, **22 mutation method/routes denied**, **1 browser scenario**, **1 release-smoke group**, **11 equivalent numerical conditions**, **17-table/six-artifact restore**, **four final archive integrity matches**, original **139-file preservation**, production/local config/Caddy checks. Backend initial **25 pass/3 fail** (test Host mismatch); then **1 readonly worker + 2 trusted fixture guards passed** with a test-only Host setup. New harness failures and corrections are retained and explained. No fresh full 68-test backend, nine-test standard browser or Mode B acceptance run is claimed; unchanged app/lock evidence from Step 6.5 is reused.

Recommend **DigitalOcean Basic 2 vCPU/4 GiB/80 GiB, $24/month compute** for initial small gated Mode A traffic, based on ~0.8 GB summed local container peak marks and 2.125 GiB configured memory caps. $30–45/month total budget is an assumption with backup/domain/tax/usage extras. [Provider compute pricing](https://www.digitalocean.com/pricing/droplets), [backup pricing](https://docs.digitalocean.com/products/backups/details/pricing/). 8 GiB/$48 compute is the conservative alternative if actual host/concurrency checks require it. Two GiB is below configured caps. No target-host/WAN capacity guarantee.

External release acceptance still requires actual Linux host/reboot/persistence/load checks, owned exact domain/DNS/CAA, public certificate issuance/renewal, external IPv4/IPv6 port verification, off-host encrypted backup restore and alert delivery. These checks require authorized infrastructure and are **unexecuted**, not passed. Source/image/bundle hashes must be rechecked after transfer. Domain purchase is unnecessary if an owned suitable subdomain exists; otherwise purchase/configuration needs separate permission.

Next authorized sequence: human security dispositions → owner/legal content/model/access sign-off (or scoped patch/rebuild if rejected) → explicit provider/domain/transfer/listener authorization → host-only private restore and checks → authorized Caddy/public DNS cutover → actual public smoke/firewall/monitoring/restore acceptance. **Do not run the public cutover merely because this preparation stage is complete.**

**STEP 6.6 COMPLETE - MODE A RELEASE DECISION DELIVERED. AWAITING EXPLICIT DEPLOYMENT AUTHORIZATION.**
