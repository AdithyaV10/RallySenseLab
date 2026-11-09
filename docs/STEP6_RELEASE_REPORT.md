# Step 6 local release preparation report

2026-11-09. **Local release configuration and functional rehearsal delivered. PUBLIC RELEASE BLOCKED: image-security acceptance and external gates remain unresolved.** This report does not certify that every release gate passed. No paid services, public listener, DNS change, image/code publication or remote push occurred. Stop here for human review.

## Starting point and scope

The repository started clean at approved checkpoint `ac75d818a168bfcf1b7f23a609121b18b0933e8e`. The requested release plans, acceptance/remediation/readiness documents and Docker/Caddy/env configuration were reviewed. Docker Desktop was stopped and was started; the original retained development services resumed on loopback. Existing images were inspected, tagged locally and reused; all 31 API source Python files matched the approved workspace after newline normalization. No application/scientific code, dependency lockfile or migration was changed. Historical Step 5/5.5 evidence is preserved.

Two fresh projects were created, `rallysense-step6-demo` and `rallysense-step6-workspace`, with new independent secrets, networks, PostgreSQL and artifact volumes. They received only in-repository generated synthetic fixtures. A shared Caddy project served two `.test` names on **127.0.0.1:18443 and 127.0.0.1:18080 only**. No OS hosts/DNS records changed. Process-local resolver overrides preserved TLS hostname/SNI checks. The demo is viewer-password gated and readonly; the research workspace uses a different password and retains full workflows.

## Delivered artifacts

- [Deployment handoff](DEPLOYMENT_HANDOFF.md): proposed host/budget, account/domain prerequisites, exact future commands, env/secret checklist, DNS/firewall, smoke, backups/rollback, monitoring and release checklist.
- [Vulnerability review](VULNERABILITY_REVIEW.md): all four scans, critical/high triage, exact runtime/tooling distinctions and unresolved security gate.
- [Fixture/privacy/license inventory](FIXTURE_RELEASE_INVENTORY.md): two generated demo sessions, six artifact hashes, ten stored paired experiments and approval exclusions.
- [Immutable candidate manifest](../infrastructure/release-manifest.json): source identity, image IDs/local tags, archive SHA-256 values and explicit failed security gate.
- [Application topology override](../infrastructure/compose.application.yml), [shared gateway](../infrastructure/compose.gateway.yml), [Caddy routing](../infrastructure/Caddyfile.release), and [loopback-only test override](../infrastructure/compose.gateway.local-test.yml).
- [Secret/config generator](../scripts/prepare-release-config.py), [isolated local orchestration](../scripts/prepare-step6-local.py), [fixture preparation](../scripts/prepare-curated-fixtures.py), [production renderer](../scripts/verify-production-config.py), [operator smoke](../scripts/smoke-release.py), and actual HTTP/browser/scanner verification scripts.

The shared gateway avoids two standalone projects competing for ports 80/443. Each web app joins only its own backend/edge; gateway joins only the two edges. DB/API/worker have no host ports. Actual cross-backend connections were denied. Every application service has an enforced memory/CPU/PID budget and a meaningful health check; new web health uses the credentialed proxied readiness route without putting passwords in command arguments. Demo API/worker artifacts are mounted RO. Gateway admin is off; its health listener explicitly binds loopback; caller internal-token/middleware headers are stripped. Logs are bounded.

## Actual new verification

| Area | Exact outcome | Evidence |
| --- | --- | --- |
| Isolated production-shaped configuration | Both roles passed, independent credentials, no application host ports, internal backends, health checks and limits | [isolated config](evidence/step6/isolated-config.json) |
| Final production rendering / offline Caddy | Both exact production Host/Origin configurations, random credentials, private ports/networks, readonly mounts and public-ACME configuration passed; no app/public listener started by this check | [final rendering](evidence/step6/production-config-final.json) |
| Real HTTPS HTTP acceptance | **9 grouped checks passed**, covering eight app containers and both roles; verified private CA chain/hostname, unauth 401/spoof defenses, wrong Host 421, foreign / cross Origin 403, wrong-role password 401, cross-project ID 404 | [command](evidence/step6/http-acceptance.json), [detailed results](evidence/step6/release-http.json) |
| Demo visibility/replay/research/export | Exactly 2 generated sessions; video Range 206; sensor graph/pose window; ten paired experiments; clean generated references TP 2; offset failure FN 2; comparison 200; Markdown export 200 | [HTTP details](evidence/step6/release-http.json), [fixtures](evidence/step6/demo-fixtures.json) |
| Readonly privacy/mutations/worker | **12 mutation families 403**; real extra generated row hidden/404 and then removed; diagnostic/list allowlisting; worker `readonly_idle`; RO artifacts | [HTTP details](evidence/step6/release-http.json) |
| Protected workspace actual writes | Generated new session, CSV 202 and video 202 with successful worker jobs; sync 201; annotation create/edit 200; experiment succeeded with approved executor identity; report export 200 | [HTTP details](evidence/step6/release-http.json) |
| Actual Chromium | **2 complete role workflows passed**: decoded video play, synchronized seek, graph, stored comparison, missed-reference navigation, report, desktop/mobile with no overflow or page errors | [successful browser command](evidence/step6/browser-verified-command.json), [results](evidence/step6/browser-release.json) |
| Actual workspace MediaPipe | Browser worker completed track 200 / ready; **79 processed frames, 0 detected person frames**, on generated MP4; no model-accuracy claim | [browser results](evidence/step6/browser-release.json) |
| Operator smoke after final gateway changes | Both roles passed TLS/auth/readiness/Host/Origin and demo allowlist/report checks, using strict private-CA verification | [final smoke](evidence/step6/operator-smoke-final.json) |
| Fresh demo paired backup/restore | Backup passed; restored **17 table digests + 6 artifact hashes** into a new private recovery namespace; migration `0003_collection_readiness (head)` | [backup](evidence/step6/backup-command.json), [restore](evidence/step6/restore-command.json) |
| Original research preservation | All original rows in **12 inventories** unchanged, including108 sessions,155 experiments,22 frozen references,139 artifacts and annotations/legacy results | [baseline](evidence/step6/baseline.json), [final verification](evidence/step6/preservation-final.json) |
| Actual original storage | **139 files checked; 0 missing / 0 mismatched**; nonroot unwritable 503; writable ready; 0 leftover probes | [final storage](evidence/step6/storage-final.json) |
| Fixture/vendor checks | Demo 2 generated sessions, 6 matching artifact hashes; locked model and Google LICENSE hashes match; JS package declares Apache-2.0 | [inventory](evidence/step6/fixture-inventory.json) |
| Targeted static checks | Ruff passed for eight new Python helpers; Node syntax passed for browser helper | [Ruff](evidence/step6/lint-release-final.json), [Node](evidence/step6/node-syntax.json) |
| Image scanning | **4 / 4 analyses completed** using pinned Trivy 0.76.2; **security gate FAILED/review pending: 4 critical + 371 high package instances** | [scanner](evidence/step6/scanner-version.json), [scans](evidence/step6/scan-progress.json), [triage](evidence/step6/vulnerability-triage.json) |

Private screenshots of actual desktop/mobile reports/research views were inspected locally and remain ignored; no additional UI polish or redesign was undertaken. All displayed perfect synthetic scores arise from analytical generated references and are explicitly labeled software verification. No real athlete metrics or experimental outcomes were fabricated.

## Preserved unsuccessful checks and corrections

These results remain recorded and must not be counted as successful runs:

- [Initial configuration check](evidence/step6/config-initial.json), exit1: the harness assumed a disabled-profile gateway would remain in rendered services. Compose omits it. Assertion corrected; both final role configurations passed.
- [Initial HTTP check](evidence/step6/http-verification.json), exit1: mismatched Host with valid SNI returned Caddy's empty default200 response. It did not disclose fixture data, but failed the intended reject policy. `strict_sni_host on` was added to both Caddyfiles; actual mismatch now returns421. This is a verified configuration correction, not an app algorithm change. [Caddy's documented behavior](https://caddyserver.com/docs/caddyfile/options#strict-sni-host).
- [Second HTTP check](evidence/step6/http-verified.json), exit1: harness used comma-separated experiment IDs; actual endpoint requires repeated `ids=` parameters. Harness corrected; comparisons passed without server changes.
- [First browser run](evidence/step6/browser-command.json), exit1: harness called `toBeDisabled` for both roles via an unsupported option. Demo had already passed; workspace correctly allowed execution. Explicit role assertions corrected it; both complete workflows passed.
- [First final lint](evidence/step6/lint-final.json), exit1: operational helper omitted explicit `check=False`. Corrected; final lint passed.
- Scanner exits were0, but advisory security gate is still **false**. No scan findings, intentionally failed occlusion experiment or prior Step 5 application-defect regressions were converted into fabricated pass results.

## Reused evidence and limits

Application source and lockfiles are unchanged from approved Step 5.5; its **65 backend,15 frontend,9 standard browser and4 original audit regression cases passed**, plus14 adversarial/upload probes including exact50 MiB CSV / 500 MiB video and hashes. These counts are retained evidence, **not new Step 6 full-suite executions**. Final-host full-size uploads/load/OOM/slow-client timing, physical phones and independent real-tennis validation were not repeated or claimed. Step 6 used actual small generated uploads through Caddy. Browser private-CA trust bypass was used only for functional Chromium tests; separate Python checks validated the real chain and hostname strictly.

Remaining blocks: native media/XML image advisories and residual OS/gateway/tooling applicability/patch decisions; exact model redistribution/content approval; real cloud Linux capacity/permissions, DNS/public ACME renewal, IPv4/IPv6 firewall verification, off-host encrypted backup/restore and monitoring/alert delivery. The general OS CVE review is preliminary, with no approved exceptions. See the detailed review and handoff before deciding whether a final release is acceptable.

The retained worker can take its 150-second Docker stop grace before termination when idle; the fresh backup took178.548seconds and restore28.702seconds. Current worker code does not provide an explicit graceful-drain signal handler. Backup explicitly quiesces HTTP writers and drains queued/running jobs first; use that maintenance procedure rather than claiming seamless live rollback. No active research job was interrupted in these isolated checks. Target-host recovery time is unmeasured.

## Local state and next gate

Private env files, local CA, candidate image tar archives, generated demo/workspace volumes and the recovery volumes remain ignored/retained. No existing database, recording or volume was deleted/reset. Step 6 test containers are stopped at the end of verification to release resources; the original development project remains available on its original loopback ports. To inspect the retained isolated stacks again, run `uv run --project apps/api python scripts/prepare-step6-local.py start`; use `stop` afterward. `init` refuses existing state/volumes and will not overwrite secrets. Do not use local-test config as public deployment config.

Recommended sequence: **targeted image security remediation/review → renewed scan and affected regressions → owner content/access/model approval → explicit hosting/DNS/public-exposure authorization → controlled deployment → external smoke/firewall/backup/monitoring acceptance**. No subsequent stage was started.
