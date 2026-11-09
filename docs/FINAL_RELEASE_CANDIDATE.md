# Final release candidate — Step 6.5

2026-11-09. **Review candidate only. No image or public deployment is approved.**

| Scope | Software result | Release decision |
| --- | --- | --- |
| Mode A: curated viewer-password-gated readonly demo | Passed with fresh generated-only volumes, precomputed clean/failure experiments, replay/graphs/comparison/exports, allowlisting, rejected mutations and idle worker. Native tools absent. | **Ready for human security review**, conditional on explicit shared-image residual decisions, fixture/model/content/access approval and external deployment acceptance. |
| Mode B: authenticated shared research workspace | Passed recording/CSV ingestion, real MediaPipe, synchronization, annotations, inference/evaluation/export, large uploads and paired recovery. | **Blocked; not ready for release approval.** Reachable native MOV/PSSH DoS and unresolved HDR serialization require a supported fix or separately reviewed processing isolation/applicability decision. Shared residual and external gates also apply. |

Authentication remains a shared-workspace control, not per-user/tenant authorization. Synthetic metrics are software demonstrations, never validated tennis accuracy. No experimental algorithm or historical result was altered.

## Frozen local candidates

All are Linux/amd64. Full hashes, OCI configuration/platform digests, source fingerprint, scan paths, archive hashes and rollback identity are in the [release manifest](../infrastructure/release-manifest.json). The suffix is an immutable local review alias; it does not grant security approval.

| Component | Local frozen alias | Docker-reported image ID prefix |
| --- | --- | --- |
| Full API/worker | `rallysense-api:release-step6_5-rc1` | `519c277ba95d` |
| Readonly API/worker | `rallysense-api-readonly:release-step6_5-rc1` | `729f07e91dfb` |
| Next.js | `rallysense-web:release-step6_5-rc1` | `aa451a1a778c` |
| PostgreSQL 17.11 | `rallysense-postgres:release-step6_5-rc1` | `c0ac57594a88` |
| Caddy 2.11.9 + x/net 0.62.0 | `rallysense-caddy:release-step6_5-rc1` | `f7fa280c0954` |

Application executor `BUILD_ID=step6_5-rc1-208e96d` identifies the reviewed patch candidate based on checkpoint208e96d; it is not represented as an unmodified historical commit. Scientific versions and dependency-lock hash match rollback. Final local Git records the source changes and manifest; no images were pushed. Docker image ID representation can differ between image-store modes; retain archive SHA-256 plus the manifest's OCI config/platform digests during transfer verification.

## Remaining decisions

1. **Mode B native blocker:** CVE-2026-107678's required MOV/PSSH path is confirmed to exhaust the 20-second child timeout on a small generated file. CVE-2026-107676's Matroska HDR serialization path is unresolved. Custom static FFmpeg coverage was reviewed separately from Trivy package counts; it was not declared clean because package names disappeared.
2. **Shared image acceptance:** PostgreSQL stable libxml2 remains genuinely affected, including one critical scanner match. Caddy go-jose/v3 has no compatible upstream patch; the current proxy exposes no JWK/JWT/admin/ACME-server endpoint. Remaining local-helper/SQLite/CLI/SBOM matches require explicit per-scope human disposition. VEX is affected/under-investigation, not a suppression.
3. **Owner content/access/legal:** approve the exact generated public fixtures, model redistribution terms, notices, branding and viewer-password policy. No private development DB/recordings may be copied into the demo.
4. **External operations:** choose host/budget/region/domain; explicitly authorize provisioning/DNS/public exposure; verify real Linux permissions/capacity, public ACME/firewall, off-host encrypted restore, monitoring/alerts and final-host upload behavior. These actions have not occurred.

Recommended next action: review **Mode A only** for an explicitly scoped release, keeping Mode B private/unreleased until its native blockers are resolved. A positive Mode A review is not permission to start Mode B or an anonymous multiuser service. Deployment requires separate explicit authorization after applicable conditions are satisfied.

## Reproduce local review

Docker Engine was unavailable at the final post-interruption state check, despite Desktop reporting starting/already running. The successful verification and stop records are retained, but current container/volume enumeration is unverified. All five image archives were rehashed offline and match the manifest. See [final local state](evidence/step6_5/final-local-state.json). A functioning local Engine is a prerequisite for the commands below; no reset or volume deletion was performed to recover it.

Existing private development startup remains `docker compose up -d --no-build`; its old local images/data were not replaced. To inspect the retained isolated candidate stacks:

```powershell
uv run --project apps/api python scripts/prepare-step6-local.py start --stage step6_5
uv run --project apps/api python scripts/smoke-release.py --local-stage step6_5
uv run --project apps/api python scripts/prepare-step6-local.py stop --stage step6_5
```

This starts only loopback18080/18443 with local `.test` hosts/private CA; the two app stacks have no published API/DB ports. Credentials remain in ignored `storage/step6_5/*.env`; do not paste them into reports/chat. The smoke helper resolves these names within its own process, with strict private-CA verification. Browser navigation needs a deliberate local resolver setup; no public DNS was configured here.

Fresh reproduction uses `init --stage step6_5`, then `seed`, then `start`, but **init refuses existing state/volumes**. Retain current data and use a separately reviewed fresh namespace for another independent rehearsal. The regression-only `compose.security-test.yml` publishes loopback test ports and uses development access; it must never be part of a release deployment.

Candidate archives stay in ignored `storage/step6_5/scanner-inputs/`: Caddy at the root; API, readonly API, final web and final PostgreSQL under `final/`. Intermediate root web/PostgreSQL archives are not final. [Deployment handoff](DEPLOYMENT_HANDOFF.md) gives exact controlled loading/configuration, backup/rollback and verification commands; those commands do not authorize cloud or public actions.

Full verification and failure history: [remediation report](STEP6_5_SECURITY_REMEDIATION.md). Exact vulnerability applicability: [final security review](FINAL_IMAGE_SECURITY_REVIEW.md). **Stop for human review; no subsequent stage has started.**
