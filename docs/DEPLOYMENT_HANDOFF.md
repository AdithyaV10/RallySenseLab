# Step 6 deployment handoff — authorization required

## Current Step 6.6 Mode A-only handoff ? 2026-11-09

**The current controlled procedure is [MODE_A_DEPLOYMENT_CHECKLIST](MODE_A_DEPLOYMENT_CHECKLIST.md), with [release decision](MODE_A_RELEASE_DECISION.md) and [review](STEP6_6_MODE_A_REVIEW.md). CONDITIONAL GO for human review; no security/content/model approval or public deployment authorization.** Use the separate four-image [Mode A manifest](../infrastructure/mode-a-release-manifest.json) and standalone `compose.mode-a.yml`. New PostgreSQL variant is for fresh synthetic volumes only. Do not apply old two-domain commands below or expose Mode B. All historical instructions/evidence are retained for provenance, not current authorization.

## Current Step 6.5 handoff — 2026-11-09

**Only a scoped Mode A deployment may proceed to human security review. Mode B is blocked; no public deployment is authorized.** Read [FINAL_RELEASE_CANDIDATE](FINAL_RELEASE_CANDIDATE.md), [FINAL_IMAGE_SECURITY_REVIEW](FINAL_IMAGE_SECURITY_REVIEW.md) and [remediation report](STEP6_5_SECURITY_REMEDIATION.md). Shared PostgreSQL XML/Caddy JWK/OS/SBOM exceptions, model/content/access approval and external operational acceptance remain pending. Native MOV/PSSH DoS and HDR serialization block the upload-enabled workspace. The historical two-domain start commands below must not be used to expose Mode B.

Current immutable local aliases are `rallysense-{api,api-readonly,web,postgres,caddy}:release-step6_5-rc1`. The [manifest](../infrastructure/release-manifest.json) is authoritative for exact image IDs, OCI configuration/platform digests, archive hashes, build ID and source fingerprint. Rollback identities are retained in [previous manifest](evidence/step6_5/previous-release-manifest.json). Final archives: `storage/step6_5/scanner-inputs/caddy.tar` and `storage/step6_5/scanner-inputs/final/{api,api_readonly,web,postgres}.tar`. Root-level intermediate web/PostgreSQL archives are not final.

After human security/content approval and **separate explicit cloud/DNS/transfer/public-listener authorization**, a Linux operator can load privately transferred archives without a public registry. Use the verified source archive and compare checksums first; do not transfer development DBs, artifacts, env files or private verification media. Example controlled loader, not executed here:

```bash
cd /opt/rallysense
umask 077
python3 - <<'PY'
import hashlib,json,pathlib,subprocess
manifest=json.loads(pathlib.Path('infrastructure/release-manifest.json').read_text())
for image in manifest['images']:
    archive=pathlib.Path('/secure-transfer')/(image['name']+'.tar')
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==image['archive_sha256']
    subprocess.run(['docker','load','-i',str(archive)],check=True)
    actual=json.loads(subprocess.check_output(['docker','image','inspect',image['image']]))[0]
    assert actual['Id'] in {image['image_id'],image['config_digest'],image['platform_manifest_digest']}
    subprocess.run(['docker','tag',actual['Id'],image['release_tag']],check=True)
PY
uv run --frozen --project apps/api python scripts/prepare-release-config.py \
  --demo-host demo.YOUR-DOMAIN --workspace-host research.YOUR-DOMAIN
# Use actual lowercase domain names. Generator starts nothing, refuses existing secrets,
# and reads all current image/build identities from the reviewed manifest.
```

For an initial **Mode A only** release, use the existing single-domain gateway chain, omitting `compose.application.yml` and `compose.gateway.yml`. This keeps the unreleased workspace out of gateway routing entirely. Independent later workspace data/secrets must remain separate. The generated workspace env may remain unused; a second public DNS record is unnecessary until that scope is approved. Review the actual single-domain Caddy configuration, target-host HTTPS monitoring and final cloud firewall before public start.

```bash
demo_seed() {
  docker compose --project-directory "$PWD" --env-file storage/release/demo.env \
    -p rallysense-release-demo -f docker-compose.yml -f infrastructure/compose.release.yml "$@"
}
demo_view() { demo_seed -f infrastructure/compose.readonly.yml "$@"; }
# First creation only: STOP if this project has existing containers/volumes/data.
docker volume ls --filter label=com.docker.compose.project=rallysense-release-demo
demo_seed config --quiet
# API_IMAGE initially points at the full reviewed image for trusted offline generation.
# APP_MODE=local; no web/gateway or published DB/API port is started during seeding.
demo_seed up -d --no-build --wait db
demo_seed run --rm --no-deps -T \
  -v "$PWD/scripts/prepare-demo-fixtures.py:/tmp/prepare-demo-fixtures.py:ro" \
  -v "$PWD/scripts/prepare-curated-fixtures.py:/tmp/prepare-curated-fixtures.py:ro" \
  api sh -c 'alembic upgrade head && python /tmp/prepare-curated-fixtures.py'
# Inspect the generated content and final two session_ids. Edit demo.env privately:
# APP_MODE=demo_readonly
# DEMO_SESSION_IDS=<exact comma-separated inspected DEMO IDs>
# API_IMAGE=rallysense-api-readonly:release-step6_5-rc1
demo_view config --quiet
demo_view up -d --no-build --wait --wait-timeout 120 db api worker web
# STOP: verify all applicable human/external gates and explicit deployment authorization.
# Only this next authorized command opens the reviewed public gateway:
demo_view up -d --no-build gateway
```

This single-domain command path reuses the existing supported release configuration; **it has not been started publicly or newly rehearsed as a single-domain live stack in Step 6.5**. The final-image two-role HTTPS topology was rehearsed only on loopback, including strict certificate/auth/Host/Origin/readonly checks. The public single-domain smoke and monitoring are therefore explicit final-host verification gates, not invented evidence. Use `scripts/smoke-release.py --env-directory storage/release --role demo` after real public DNS/CA is ready; browser-check replay/research/report exports and denial of mutations. Do not start an upload-enabled workspace as part of this smoke.

For future approved two-mode operation, the shared-gateway topology below remains the architectural plan, but update any historical tags/paths to the current manifest and remove the Mode B block only after its native findings are resolved and reviewed. On Linux, separate secret generation remains0700directory/0600files. Never regenerate a database password against an existing volume as an implicit credential rotation.

For a Mode A paired backup, use the same single-domain runtime chain (omit `compose.application.yml`):

```bash
uv run --frozen --project apps/api python scripts/backup-workspace.py backup \
  --project rallysense-release-demo --env-file storage/release/demo.env \
  --file docker-compose.yml --file infrastructure/compose.release.yml \
  --file infrastructure/compose.readonly.yml --directory storage/backups/demo-YYYYMMDD-HHMM
```

Use the unchanged fresh `rallysense-restore-*` recovery guard, matching paired archives and retained previous image/env identities for rollback. No live DB overwrite, `down -v`, pruning or private database import is authorized. The hardened workspace recovery rehearsal passed17tables/14files after an isolated timeout-headroom correction; off-host encryption/restore/retention still requires external verification. Host sizing, budget, DNS/firewall, monitoring and owner-account prerequisites below remain recommendations, not provisioned resources.

## Historical Step 6 two-environment plan — Mode B start remains blocked

2026-11-09. **Local preparation delivered. Public deployment NOT authorized and NOT complete.** Image security acceptance is blocked; see [vulnerability review](VULNERABILITY_REVIEW.md). Finish that local work, content/model approval and external gates before starting the public gateway. No cloud resources, DNS changes, public listeners, registry pushes or GitHub pushes were made during this stage.

## Recommendation and budget

Use one maintained **Linux x86-64 Docker host, DigitalOcean Basic 16 GiB / 8 vCPU / 320 GiB SSD** for the two isolated application projects and one Caddy gateway. Each project contains Next.js, FastAPI, the durable worker, its own PostgreSQL and artifacts. Only web joins its own edge network. API/worker/DB stay on that project's internal backend network; the shared gateway joins both edge networks. Demo and workspace have distinct credentials, DBs and volumes. This is logical isolation on one host, not a separate-host security boundary or HA design.

Current memory caps total 8.25 GiB for both full stacks; 16 GiB leaves OS, Docker and filesystem-cache headroom. Shared CPU is adequate as a starting candidate for low concurrency, not a completed load benchmark. MediaPipe runs in the client browser; no GPU server is required. The disk must hold originals, normalized artifacts, PostgreSQL, upload spools, paired backups and a restoration copy. Establish quotas/retention before sustained ingestion. A single 8 GiB / 4 vCPU host at $48/month is only a possible one-environment starting point; it does not fit the sum of both configured caps plus host overhead.

Pricing checked 2026-11-09: the proposed server is **$96/month**; an optional private Spaces bucket starts **$5/month**, so $101/month before tax/domain/overage. Optional basic weekly VM backup adds 20% ($19.20), making $120.20/month with the bucket. Daily adds 30% instead. VM snapshots do not replace paired quiesced database/artifact backups. Prices/availability must be reconfirmed at purchase. Sources: [Droplet pricing](https://www.digitalocean.com/pricing/droplets), [Spaces pricing](https://www.digitalocean.com/pricing/spaces-object-storage), [backup pricing](https://docs.digitalocean.com/products/backups/details/pricing/).

The owner needs a cloud account with billing, MFA, a project, an SSH public key, budget alerts, chosen region and recovery contact. For off-host recovery, configure a private encrypted backup destination and narrowly scoped credentials. No cloud API token is needed merely to review this handoff. Do not send credentials in chat.

Use two hostnames on an owned domain, for example `demo.<owned-domain>` and `research.<owned-domain>`. No separate domain purchase is necessary if one is already owned. Otherwise register a domain and verify its actual renewal price. DNS A records must target the approved IPv4; publish AAAA only after IPv6 routing/firewall is configured. Check CAA permits the selected Caddy ACME issuer. The owner must approve whether the viewer-password-gated demo access policy is suitable. Research uploads must remain protected; anonymous multiuser service is not supported.

## Release candidates and configuration

[release-manifest.json](../infrastructure/release-manifest.json) pins the reviewed source checkpoint, Linux/amd64 local image IDs, local tags and archive hashes. These are **candidate images with a failed security gate**, not approved final release images. After image hardening, issue new immutable tags, regenerate the manifest and rescan. Do not silently reuse an old tag or mark the existing manifest clean.

Use the base Compose file followed by `compose.release.yml` and **`compose.application.yml`** for each project. Add `compose.readonly.yml` last for demo runtime. Use **one** `compose.gateway.yml` project for both domains. Do not start the original standalone gateway twice: ports 80/443 would collide. The old single-environment instructions are historical; this two-environment procedure supersedes them.

Docker Compose must support `!reset` and `!override` (>=2.24.4; locally tested 5.1.4). Use the official supported Docker Engine/Compose installation for the chosen Linux distribution, plus Python/uv for the provided helpers. Keep Docker administration private. The application images were reused without rebuild; API image source matched all 31 Python files at approved checkpoint `ac75d818a168bfcf1b7f23a609121b18b0933e8e`. No algorithm/lock/migration changes were made.

Environment checklist per project:

| Variable | Required value |
| --- | --- |
| `POSTGRES_PASSWORD` | Independent random 32-byte hex secret; never development default |
| `LOCAL_TOKEN` | Independent random internal secret; API/worker/web agree only within a project |
| `SITE_ACCESS_PASSWORD` | Different strong viewer/workspace passwords, shared only with intended users |
| `BUILD_ID`, `API_IMAGE`, `WEB_IMAGE` | Actual reviewed application identity; API and worker identical image |
| `APP_MODE` | `local` for protected workspace; `demo_readonly` for final demo runtime |
| `DEMO_SESSION_IDS` | Only IDs generated and inspected in the fresh demo database |
| `RALLYSENSE_DOMAIN`, `WEB_ALLOWED_HOSTS` | One exact hostname, no wildcard |
| `WEB_ALLOWED_ORIGINS` | Exactly `https://<same-hostname>`, no cross-project origin |
| `EDGE_WEB_ALIAS`, `EDGE_NETWORK` | `demo-web`/`workspace-web` and different role-specific network names |

Gateway `DEMO_HOST`, `WORKSPACE_HOST` and edge network names must agree with the two projects. **Production `TLS_POLICY` is empty**, enabling public ACME. `compose.gateway.local-test.yml`, `.test` hosts and the local private CA must never be used as the public configuration. Generated files stay in ignored `storage/release/`, directory 0700/files 0600 on Linux. Docker administrators can inspect environment secrets; this is not a secrets-vault implementation.

## Controlled future commands

**Do not execute provisioning, transfer to a public host, DNS changes or the gateway start until explicit owner authorization.** The commands below are a reviewable operator procedure, not actions already taken. Resolve the security gate first. Use an empty project/volume namespace; never point these commands at the development project. Run from the repository root.

Transfer can use private SSH and `docker load`; a public registry is unnecessary. A source bundle must include only reviewed tracked files, excluding `storage/`, private recordings, `.env*`, `data/private/`, `.git`, screenshots and developer dependencies. `git archive <final-approved-commit>` provides the tracked source boundary; inspect `git ls-tree` for any accidentally tracked private files first. Candidate tar archives currently reside in ignored `storage/step6/scanner-inputs/`; compare their SHA-256 values with the manifest before loading. Once replacement images are approved, transfer only those replacement archives and revised manifest. On the authorized host:

```bash
# AFTER authorization, source transfer, reviewed image hardening and checksum verification:
cd /opt/rallysense
umask 077
sha256sum /secure-transfer/{api,web,postgres,caddy}.tar
# Compare all four values to infrastructure/release-manifest.json; STOP on any mismatch.
for image in api web postgres caddy; do docker load -i "/secure-transfer/$image.tar"; done
# docker save/load may omit registry RepoDigests. Resolve the pinned PUBLIC upstream
# PostgreSQL/Caddy references if Docker cannot match them locally; no custom registry is needed.
# Use the exact approved digest references from the revised Compose/manifest, never floating tags.
# Current archive tags require these local aliases; substitute revised reviewed tags after hardening.
docker tag rallysense-api:local rallysense-api:release-ac75d818
docker tag rallysense-web:latest rallysense-web:release-ac75d818
docker image inspect rallysense-api:release-ac75d818 rallysense-web:release-ac75d818
# Check immutable IDs and linux/amd64 against the APPROVED revised manifest.

uv run --frozen --project apps/api python scripts/prepare-release-config.py \
  --demo-host demo.YOUR-DOMAIN --workspace-host research.YOUR-DOMAIN
# Use real lowercase hostnames above. Generator refuses an existing destination;
# it generates new independent secrets, but starts nothing. Inspect env privately.
```

The generator deliberately initializes demo `APP_MODE=local` solely for private preparation. It does not override the security review, create volumes or start services. Before runtime, replace mode/allowlist as shown below. If the approved images change, edit `API_IMAGE`, `WEB_IMAGE` and `BUILD_ID` to the new reviewed values before validation. Never rotate DB passwords by regenerating an env file against an existing PostgreSQL volume; use a planned database credential rotation.

```bash
app() {
  role="$1"; shift
  docker compose --project-directory "$PWD" --env-file "storage/release/$role.env" \
    -p "rallysense-release-$role" -f docker-compose.yml \
    -f infrastructure/compose.release.yml -f infrastructure/compose.application.yml "$@"
}
demo() { app demo -f infrastructure/compose.readonly.yml "$@"; }
edge() {
  docker compose --project-directory "$PWD" --env-file storage/release/edge.env \
    -p rallysense-release-edge -f infrastructure/compose.gateway.yml "$@"
}

# Verify no pre-existing release projects/volumes before first creation. Do not delete any.
docker volume ls --filter label=com.docker.compose.project=rallysense-release-demo
docker volume ls --filter label=com.docker.compose.project=rallysense-release-workspace
# STOP if either target already has data; use the recovery/update procedure instead.
app demo config --quiet
app workspace config --quiet
for role in demo workspace; do
  app "$role" up -d --no-build --wait db
  app "$role" run --rm --no-deps -T \
    -v "$PWD/scripts/prepare-demo-fixtures.py:/tmp/prepare-demo-fixtures.py:ro" \
    -v "$PWD/scripts/prepare-curated-fixtures.py:/tmp/prepare-curated-fixtures.py:ro" \
    api sh -c 'alembic upgrade head && python /tmp/prepare-curated-fixtures.py'
done
# Inspect generated content and final JSON. In storage/release/demo.env set:
# APP_MODE=demo_readonly
# DEMO_SESSION_IDS=<exact comma-separated two session_ids from DEMO output only>
# Do not copy workspace IDs or use any private database dump.
demo config --quiet
demo up -d --no-build --wait --wait-timeout 120 db api worker web
app workspace up -d --no-build --wait --wait-timeout 120 db api worker web
# No application ports are published by either project.
edge config --quiet
# STOP HERE until security/content approval, DNS/firewall review and explicit deployment authorization.
# This next command is the public exposure boundary:
edge up -d --no-build --wait --wait-timeout 120

# After real DNS/ACME is ready, from an authorized host with private env files:
uv run --frozen --project apps/api python scripts/smoke-release.py --env-directory storage/release
```

The final smoke validates public CA chain/hostname by default, Basic auth, readiness, exact Host/Origin rejection, readonly fixture allowlist and report access. Its `--local-step6` option was executed here only against loopback and a verified private CA. Do not use certificate verification bypasses for production. After authorized start, additionally perform browser video/graph/research/report checks and a small **new generated workspace** CSV/video upload, actual MediaPipe, sync, annotation edit and experiment export. Do not edit an existing research session to run a smoke test. Existing Step 5.5 evidence covers exact 50 MiB CSV / 500 MiB MP4 boundaries through Next; Step 6 gateway checks used small generated uploads. Final host throughput, full-size upload timing and OOM behavior are still external gates.

## DNS, firewall, monitoring and acceptance

Allow inbound TCP 80/443 only to Caddy, SSH22 only from approved administrator IPs (or reviewed private administration path). API8000, Next3000, PostgreSQL5432/5433, health8081, Docker2375/2376 and Caddy admin2019 must not be public. The Caddy admin API is disabled and health binds loopback. Current configuration publishes TCP only; HTTP/3 availability is not verified. Apply both cloud firewall and Docker-aware host rules; UFW alone is insufficient because Docker port publishing can bypass its normal filtering. Verify externally for IPv4 and any enabled IPv6. [Docker firewall behavior](https://docs.docker.com/engine/network/packet-filtering-firewalls/).

Target-host checklist:

- Validate merged Compose privately and confirm all nine containers healthy, restart policies, memory/CPU/PID caps, bounded logs and RO demo artifact mounts.
- Confirm only gateway published ports, independent databases/volumes/secrets, backend-network connection isolation and inaccessible Docker administration.
- Confirm real certificate issuance/renewal, HTTP-to-HTTPS redirect, exact Host/SNI rejection, Origin policy, no caller internal-token/middleware bypass and no development credentials.
- Inspect the two demo sessions, generated privacy inventory, stored comparisons/failure cases/report exports, all denied mutations and worker `readonly_idle`. Approve fixture/model terms and public presentation.
- Monitor CPU/memory/OOM/restarts, free disk/inodes, DB/storage readiness, worker heartbeat/job backlog/stuck jobs, failed uploads, repeated401/403/429/5xx, certificate expiry, backup freshness and restore outcomes.
- Proposed initial alerts: disk <20% or <20 GiB, unhealthy container >2 minutes, backup older than 26 hours, worker heartbeat failure, sustained queue delay >5 minutes, certificate <14 days. Tune on measured traffic; these are operational targets, not proven SLAs.
- Configure private off-host encryption/retention and an alert receiver, then prove restore on a disposable target. A reasonable starting policy is daily paired backups, 7 daily/4 weekly retention, RPO 24h; measure and approve RTO rather than promise one. Logs/archives must exclude passwords/tokens/request bodies and respect recording retention policy.

## Paired backups and rollback

Use the same role/env/Compose chain as runtime. The helper quiesces writers, waits for running/queued jobs, stops the worker, captures PostgreSQL plus artifacts and a table/hash manifest, then restarts the prior writers. Plan a maintenance window: the fresh demo rehearsal took about179 seconds, largely shutdown grace. For a research workspace, ensure no active browser upload/inference before starting; do not back up live files independently of DB state.

```bash
uv run --frozen --project apps/api python scripts/backup-workspace.py backup \
  --project rallysense-release-demo --env-file storage/release/demo.env \
  --file docker-compose.yml --file infrastructure/compose.release.yml \
  --file infrastructure/compose.application.yml --file infrastructure/compose.readonly.yml \
  --directory storage/backups/demo-YYYYMMDD-HHMM
# Repeat with workspace project/env and omit readonly override.
# Encrypt and transfer the complete matching dump/tar/manifest off-host with approved tooling.
# Verify destination checksums/decryption/access controls and apply retention only to verified backups.

uv run --frozen --project apps/api python scripts/backup-workspace.py restore \
  --project rallysense-restore-YYYYMMDD-hhmm --env-file storage/release/demo.env \
  --file docker-compose.yml --file infrastructure/compose.release.yml \
  --file infrastructure/compose.application.yml --file infrastructure/compose.readonly.yml \
  --directory storage/backups/demo-YYYYMMDD-HHMM
```

Restore requires a new `rallysense-restore-*` namespace and refuses existing containers/volumes/networks; it resets ports, verifies all table/artifact hashes/readiness, and retains restored volumes with DB stopped. It is a **recovery rehearsal**, not an automatic live-volume switch. Do not run `down -v`, volume prune, `pg_restore --clean`, or overwrite the existing research database.

For an image-only compatible rollback, save previous env files securely, retain previous image IDs, quiesce writers with a paired backup, change only `API_IMAGE`/`WEB_IMAGE`/matching `BUILD_ID` to the prior approved release, then use `demo up ...` / `app workspace up ...` and repeat smoke. For schema/data incompatibility, stop the affected writers, restore into a fresh namespace, verify it, then explicitly review routing/volume/environment changes before cutover. Current schema remains `0003_collection_readiness`; no migration was added in Step 6. Never downgrade scientific dependencies against historical manifests merely to force startup.

## Remaining gates and next authorization

1. Local image patch/minimization and residual critical/high CVE applicability decisions; new scan/manifest and affected targeted regressions. Both modes remain blocked on this security decision.
2. Owner approval of generated public content, exact model redistribution terms, viewer-password access policy and chosen budget/region/domain.
3. Explicit authorization for paid provisioning, approved DNS/firewall changes, private source/image transfer and public listener start. These have not occurred.
4. Actual Linux host capacity/permissions, cloud/Docker firewall scan, real public ACME/renewal, end-to-end final-host uploads, off-host encrypted restore and monitoring/alert delivery.

The recommended next action is **local image security remediation and review**, followed by a separate deployment approval. This document does not authorize or start another stage.
