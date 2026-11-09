# Deployment readiness decision

## Current Step 6.5 decision, 2026-11-09

**Mode A: ready for human security review, conditional/unreleased. Mode B: blocked for release approval by native-media findings.** [Final security review](FINAL_IMAGE_SECURITY_REVIEW.md) supersedes the Step 6 image counts with1 critical/163 high package instances and a separate current native-component review. No image was declared clean/approved. [Final RC](FINAL_RELEASE_CANDIDATE.md) and [handoff](DEPLOYMENT_HANDOFF.md) identify frozen local artifacts, exact commands and pending human/external gates. All normal functional regressions and original data/hash preservation passed; none of this authorizes deployment.

## Current Step 6 decision, 2026-11-09

**Local dual-environment release rehearsal passed; image-security gate FAILED / disposition pending; public deployment NOT ready.** [Step 6 report](STEP6_RELEASE_REPORT.md) records new evidence. [Deployment handoff](DEPLOYMENT_HANDOFF.md) supersedes the historical single-project commands with two independent backend/database/artifact projects and one shared gateway.

Auth-free pinned Trivy scanning completed. Four critical and 371 high package instances were reported, including duplicated libraries, build/SBOM/CLI tooling and unproven runtime applicability. [Vulnerability review](VULNERABILITY_REVIEW.md) distinguishes vendor-supported false-positive candidates from unresolved media/XML/gateway/OS risks. No scan suppression or security acceptance was invented. Both curated demo and authenticated workspace require an approved image-security disposition; uploads add native media-parser exposure.

Fresh synthetic-only demo and separate protected workspace passed actual HTTPS/browser/worker workflows, auth/Host/Origin/isolation checks and paired recovery. Existing Step 5.5 software tests remain applicable because application source/locks were unchanged. Public ACME/DNS/firewall/target-host performance, encrypted off-host restore, monitoring and owner fixture/model approval are still external gates. No cloud resource or public listener was created. The earlier statement that image scanning requires Docker authentication is superseded by the successful Trivy execution, not by a clean security verdict.

## Current Step 5.5 decision, 2026-11-08

**Application remediation delivered; public release remains conditional on operational and human acceptance.** A01–A05 are repaired, A06 is retained, and all four original application audit regressions pass. [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md) records exact final results and unresolved scan/advisory outcomes.

Mode A has been verified on fresh synthetic-only volumes with two sessions, three precomputed results, a read-only artifact mount, denied mutations, unknown-session isolation and an idle worker. Mode B has verified authenticated streaming uploads through actual 50/500 MiB file limits, scientific processing, annotations and replay. Both are controlled shared workspaces; no anonymous multiuser upload service is provided.

Use [release Compose](../infrastructure/compose.release.yml), [read-only override](../infrastructure/compose.readonly.yml), [Caddyfile](../infrastructure/Caddyfile) and the [execution plan](DEPLOYMENT_EXECUTION_PLAN.md). Only gateway ports are published; backend networking is internal; API/worker use the same image; missing/template credentials fail closed. A local paired backup/restore verified 17 tables and 116 artifacts. Final OS/FFmpeg/base-image scans require Docker authentication, and actual public DNS/TLS/host/firewall, off-host recovery/retention, monitoring and human fixture review are still required. No public gateway was started.

## Historical Step 5 decision and acceptance matrix

The original decision below is retained as the pre-remediation baseline. Its application defects are resolved as described above; its external release gates still apply.

2026-11-07. **SIGNIFICANT FIXES REQUIRED** for the full application. Local controlled demonstration is viable with short verified fixtures and explicit limitations. Neither unrestricted public deployment nor deployment authorization follows from this audit.

## Simplest compatible topology

Use one container-capable Linux host with the existing Next.js, FastAPI, durable worker and PostgreSQL, private persistent artifact/database volumes, and one TLS/access reverse proxy. Publish only the reviewed HTTPS entry point. Keep API, PostgreSQL and Docker administration private. Pin the audited image/lock versions and retain a rollback image plus paired database/artifact backups. This follows the [documented single-server Compose pattern](https://docs.docker.com/compose/how-tos/production/) and matches the implemented filesystem paths; it is an engineering recommendation, not a deployment already performed.

For the first public read-only demo, use a fresh dedicated Compose project and fresh volumes containing **only** approved synthetic fixtures and precomputed results. Do not mount or copy the present private-capable workspace wholesale. Keep uploads and mutations disabled at both the edge and backend. Review whether a worker is needed at all after seeding; if retained, drain queued jobs and verify maintenance/heartbeat behavior. HTTP read-only mode does not turn the database into a read-only database or stop already queued worker jobs.

Avoid splitting the frontend onto a serverless platform for the initial release. The current shared-secret proxy, persistent filesystem access, long-lived worker and large media transport do not transfer unchanged. Object storage, signed/direct uploads and cross-service authentication would need implementation and review. No object-store adapter exists today.

## Required gates by release scope

| Gate | Public fixture-only read-only demo | Upload-enabled private/shared workspace | Open multiuser upload service |
| --- | --- | --- | --- |
| Fresh fixture-only DB/artifact volumes and manual content/license review | MUST | Separate private environment; explicit participant retention/permissions | MUST isolate tenants and public fixtures |
| TLS, unique secrets, exact hosts/origins, private API/DB ports, reviewed access policy | MUST | MUST | MUST plus per-user identity/authorization |
| Backend APP_MODE=demo_readonly and explicit built-in synthetic allowlist; direct-route negative tests | MUST | Use deliberate authenticated writable mode | Per-user/object policy required; local mode is insufficient |
| A01 streaming upload repair and two upload gates passing | Not required while mutations are unconditionally disabled | MUST | MUST |
| A02 executor environment enforcement / release queue policy | Precompute under one pinned image; do not execute research jobs during demo | MUST before accepting research jobs across releases | MUST |
| A03 supported extraction duration/count contract | Use inspected pre-extracted short tracks | MUST fix or explicitly cap accepted sampling/duration before extraction | MUST |
| A04 mode-appropriate artifact readiness | MUST verify readable fixture storage and actual media smoke | MUST verify writable storage and disk alarms | MUST |
| A05 alignment-dependent sample-cache invalidation | Editing disabled; fixed alignment snapshots avoid trigger | MUST before interactive alignment acceptance | MUST |
| A06 source terminal-state repair | Included, regression passed | Included, regression passed | Included, still requires wider concurrency validation |
| Backup + isolated restore, migration rehearsal, host/image patching and OS vulnerability scan | MUST before public release | MUST before retaining valuable recordings | MUST with tenant-aware restore/deletion policy |
| Bounded ingress, read/request limits, upload concurrency, disk/retention alarms | MUST bound read/media abuse and egress | MUST additionally bound all write/compute resources | Distributed quotas, fairness and hostile-file isolation required |
| Human demo review, key-browser accessibility and error-state review | MUST | MUST; physical capture test if advertised | MUST plus independent security review |

The read-only path can proceed through a smaller remediation/operational acceptance stage without implementing a new upload architecture first. Its success must not be used to approve writable operation. “Public read-only” may be gated for invited reviewers or deliberately anonymous; select that access policy explicitly and test it. The current Basic gate is a shared workspace gate and requires TLS over a network.

## Upload repair architecture

The recommended single-host repair is same-origin streaming `/api/v1` ingress at the TLS reverse proxy, protected before forwarding and mapped only to the private API. Preserve backend credential enforcement using a server-held injected token after successful edge authentication, discard spoofed client credential headers, retain exact Origin checks and reject mutations in read-only mode. The backend must trust only that gateway, not a publicly reachable direct port. If authentication remains in Next, refactor only the necessary API ingress to avoid body cloning while preserving equivalent authentication and CSRF checks. Test both paths; do not treat the `x-lab-client` header alone as authentication.

Set explicit body/file limits, timeouts and concurrency limits at every layer. Reject over-limit bodies with 413 before processing; enforce limits for streamed/chunked uploads too. Test byte/hash preservation, malformed multipart, aborted clients, midstream rejection, cleanup and concurrent RSS under a chosen budget. Increasing Next's experimental body buffer alone is an interim bounded-memory tradeoff, not the accepted default fix for 500 MiB media.

## Operations and resources

The base configuration already uses packaged source, pinned base images, restart policies, nonroot app users and retained volumes. API readiness has A04; worker heartbeat is separate and does not prove a job will finish. The production-preparation override requires explicit secrets and fixture IDs but is not a complete TLS/authentication/backup/abuse-control deployment. Verify rendered configuration without disclosing its secrets.

Maintain PostgreSQL and artifact backups as a consistent pair. Stop new writes and drain jobs for a backup window; restore into a separate local/staging project and verify hashes, frozen records, media reads and application smoke before claiming recovery. Changing POSTGRES_PASSWORD in Compose does not rotate credentials inside an existing initialized database; use a reviewed rotation procedure or a genuinely fresh database. Secrets are environment-driven; `_FILE` support is not implemented. Do not log or commit secrets/backups.

One local post-check snapshot showed approximately 136 MiB web, 300 MiB API, 226 MiB worker and 98 MiB PostgreSQL resident container usage. This is a momentary observation, not a production sizing minimum or peak. Browser MediaPipe uses the visitor's CPU; server memory also grows with artifact processing, result materialization and concurrent requests. Choose CPU/RAM/disk limits after a bounded representative workload and monitor free disk, queue age, worker age, request failures and backup age. A single host remains a single failure domain.

No cloud-price quote or monthly cost is established. Budget items are compute uptime, persistent disk, backup copies and media egress; public WASM/media downloads can dominate egress independently of inference CPU. No paid service is required for the proposed architecture, but hosting itself has provider-dependent costs. Do not buy infrastructure before the release scope and gates are agreed.

## Human release acceptance

1. Approve a curated fixture-only content inventory and license/provenance statement.
2. Review the short local demonstration and four failing audit regressions before choosing release scope.
3. Complete applicable remediation, then run ordinary **and** audit gates; preserve the failure history.
4. Rehearse isolated backup restore and migration/restart; scan final OS/application images.
5. Verify production-domain TLS, credentials, Host/Origin, direct-port isolation, readonly exports/media and denial of mutations in a separately authorized staging deployment.
6. If capture is promoted, test real iOS/Android and consented paired recordings. Do not market tennis accuracy without independent evaluation.
7. Obtain explicit deployment authorization. This audit created no cloud resources and authorizes none.
