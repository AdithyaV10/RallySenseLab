# Deployment execution plan — authorization required

**Step 6 update, 2026-11-09:** use [DEPLOYMENT_HANDOFF.md](DEPLOYMENT_HANDOFF.md) for the current **two isolated environments / one shared gateway** procedure, image manifest, secrets, DNS/firewall, recovery and smoke commands. The single-project examples below remain historical context. Do not start two standalone gateways on the same ports. Local dual-project rehearsal passed; image-security acceptance is blocked by [actual Trivy findings](VULNERABILITY_REVIEW.md). No deployment/provisioning/public exposure/push is authorized by this document.

2026-11-08. These are historical reviewable instructions for a future authorized single-environment deployment. **Do not start the public gateway without authorization.** Local preparation, configuration validation and isolated recovery tests have run; no server/domain/cloud account has been provisioned. Complete [RELEASE_ACCEPTANCE](RELEASE_ACCEPTANCE.md) first.

## Topology and prerequisites

Use one maintained Linux Docker host, persistent PostgreSQL and artifact volumes, identical API/worker images, the existing Next app and a pinned Caddy HTTPS gateway. Only Caddy publishes ports 80/443. DB/API have an internal network; web bridges that network and the gateway network. API routes independently enforce the shared workspace gate before bounded streaming. No object-store or serverless adapter is required.

Install Docker Engine/Compose with `!reset` support (Compose ≥2.24.4) and Python ≥3.11 for the standard-library operational helpers. Host firewall should expose only reviewed SSH and HTTPS/HTTP; Docker published-port rules must be reviewed too. Initial memory budgets total about 4.25 GiB across services before host/cache overhead; an 8 GiB class host is a starting capacity candidate, not a verified minimum. Choose disk capacity for database, originals, derived files, upload spools, paired backup and at least one recovery copy, with ample headroom and disk alerts.

Configuration sources: [release Compose](../infrastructure/compose.release.yml), [read-only override](../infrastructure/compose.readonly.yml), [Caddyfile](../infrastructure/Caddyfile), [release environment](../infrastructure/release.env.example). Caddy configuration was validated against its pinned image without exposing ports. Actual public certificate issuance, DNS, firewall and Linux-host permissions remain unverified. The topology follows [Docker's production Compose guidance](https://docs.docker.com/compose/how-tos/production/); [Compose merge/reset](https://docs.docker.com/reference/compose-file/merge/) and [Caddy timeouts](https://caddyserver.com/docs/caddyfile/options) explain the relevant configuration controls.

## Prepare secrets and images

The following examples assume the repository root on Linux and an authorized future operator. Keep the private local project's volumes separate.

```bash
cp infrastructure/release.env.example .env.release
chmod 600 .env.release
# Edit the file locally. Generate separate random values, e.g. openssl rand -hex 32.
# Never reuse the example database password or development API token.
```

Set a unique database password, internal token ≥32 characters and workspace password ≥20 characters; use generated 32-byte secrets rather than merely satisfying a length test. Set exact `WEB_ALLOWED_HOSTS`, exact HTTPS `WEB_ALLOWED_ORIGINS`, the reviewed `RALLYSENSE_DOMAIN`, and reviewed commit `BUILD_ID`. `API_IMAGE` and `WEB_IMAGE` must identify retained release tags/digests; the worker uses the identical API image. Do not leave `CHANGE_ME` values. Production API rejects default/short/template tokens and the web gate rejects missing/short/template access passwords. Environment variables are not a secrets vault and `_FILE` support is not implemented.

Select a fresh project name and desired initial mode:

```bash
export RELEASE_PROJECT=rallysense-demo
dc() {
  docker compose --env-file .env.release -p "$RELEASE_PROJECT" \
    -f docker-compose.yml -f infrastructure/compose.release.yml "$@"
}
dc config --quiet
dc build api web
python3 scripts/check-release-config.py
# Inspect the final merged config locally; it contains secrets. Do not paste it into tickets/logs.
```

The config assertion helper uses disposable values and starts no services. Separately inspect the actual operator values, image identities, mount paths and project name. Save image IDs/digests and a previous-release rollback tag before updates. Do not push images or publish the repository without separate authorization.

## Mode A: fresh curated read-only demonstration

Create **new empty volumes**, not a filtered copy of private workspace volumes. Temporarily set `APP_MODE=local` only for offline preparation, with the gateway and web stopped. Do not import local recordings. The preparation script refuses a nonempty session database or nonempty artifact directory.

```bash
dc up -d --wait --wait-timeout 60 db
dc run --rm --no-deps -T \
  --volume "$PWD/scripts/prepare-demo-fixtures.py:/tmp/prepare-demo-fixtures.py:ro" \
  api sh -c 'alembic upgrade head && python /tmp/prepare-demo-fixtures.py'
```

This seeds two built-in generated synthetic sessions and computes three research modes under the pinned worker environment. Its output supplies the exact fixture IDs. Inspect all media, text, reports and provenance; these generated results carry no tennis accuracy claim. Set those IDs in `DEMO_SESSION_IDS` and set `APP_MODE=demo_readonly` in `.env.release`.

```bash
dcdemo() {
  docker compose --env-file .env.release -p "$RELEASE_PROJECT" \
    -f docker-compose.yml -f infrastructure/compose.release.yml \
    -f infrastructure/compose.readonly.yml "$@"
}
dcdemo config --quiet
# After deployment authorization and the release gates, start the public stack:
# dcdemo up -d --no-build --wait --wait-timeout 120
```

The override mounts artifact storage read-only for API and worker. Backend allowlisting is fail-closed. Worker polling publishes only an idle heartbeat and does not execute jobs or reconcile/delete files. API readiness checks approved content readability rather than write access. HTTP read-only is not a read-only PostgreSQL role: migrations and operational heartbeats can still write the database. Protect database credentials and private networks.

The complete fresh fixture/precompute/read-only transition was locally tested in a separate project with **no published ports**, distinct from the public startup command above. The two local restore projects and the synthetic demo preparation project retain their volumes with stopped DB containers. Do not mistake these for deployed services or delete them as part of routine startup.

## Mode B: authenticated research workspace

Set `APP_MODE=local` deliberately, retain required workspace authentication and use release Compose without the read-only override. `local` is the internal name for writable controlled-workspace mode; it does not authorize public anonymous access. Leave API/DB ports private. No per-user identities, tenant isolation, anonymous upload service or hardened hostile-codec sandbox is provided.

Prepare/migrate privately before starting writers:

```bash
dc up -d --wait --wait-timeout 60 db
dc run --rm --no-deps -T api alembic current
dc run --rm --no-deps -T api alembic upgrade head
dc run --rm --no-deps -T api alembic check
# Only after separate deployment authorization:
# dc up -d --no-build --wait --wait-timeout 120
```

Step 5.5 adds no schema migration; head remains `0003_collection_readiness`. Existing API startup also applies pending Alembic migrations. Always backup/rehearse a future migration before an image upgrade. Changing `POSTGRES_PASSWORD` in an environment file does not rotate the password of an initialized database. Release DB health now performs an authenticated TCP SELECT 1, avoiding both this credential mismatch and PostgreSQL's transient initialization socket.

Keep the two-upload limit and explicit 50/500 MiB file plus 51/501 MiB multipart bounds. Unknown-length requests are counted; extra multipart files/fields are rejected. Do not enable proxy body buffering or raise all bounds to resolve a single failed test. The Caddy body ceiling is a total ingress bound; app/API enforce per-route/file and metadata limits. Rate budgets are per single process/shared workspace. Additional replicas require a shared admission/quota design.

## Upgrade and queue policy

1. Stop web ingress writers (and gateway if necessary), preserve project/volume identity, and let the **old** worker drain queued/running jobs.
2. Inspect queue state privately: `dc exec -T db psql -U rallysense -d rallysense -Atc "SELECT state,count(*) FROM processing_jobs GROUP BY state"`.
3. Stop the old worker after the queue drains; take a paired backup. Record current images, migration head and allowlist.
4. Build/validate the new release, rehearse any migration and update API/worker to the exact same image. Use the reviewed mode configuration.
5. If old queued work cannot drain, preserve it. The new worker must fail typed environment/source mismatches; create new experiments under the new release instead of rewriting manifests or completed results.
6. Run private smoke/security/upload checks, then obtain/perform the authorized public switch. Keep rollback images and the pre-upgrade paired backup.

New frozen runtime identity includes Python. Old queued manifests without it fail closed. Completed results remain readable. Runtime rejection is a scientific provenance boundary, not evidence that old numerical values were inaccurate.

## Paired backup and isolated restore

Run backups under an operational account with restricted storage permissions. Artifacts and PostgreSQL form one recovery unit. The helper stops HTTP writers, waits for queue drain, stops the worker, computes a table/artifact inventory and writes binary pg_dump/tar streams without PowerShell text conversion. It restarts only the services that were running. No database or volume is deleted.

```bash
python3 scripts/backup-workspace.py backup --project "$RELEASE_PROJECT" \
  --env-file .env.release --file docker-compose.yml \
  --file infrastructure/compose.release.yml \
  --directory storage/backup-REPLACE_WITH_UNIQUE_TIMESTAMP
# For Mode A add: --file infrastructure/compose.readonly.yml
```

The backup path must remain under ignored `storage/` and must not already exist. Linux backup files receive owner-only permissions. On Windows, protect the containing folder with appropriate ACLs. If the queue cannot drain or an archive step fails, the backup remains incomplete and must not be used as a successful recovery point. Do not overwrite it silently. Off-host encrypted copies, retention and restore ownership are still operator tasks.

```bash
python3 scripts/backup-workspace.py restore \
  --directory storage/backup-REPLACE_WITH_UNIQUE_TIMESTAMP \
  --project rallysense-restore-REPLACE_WITH_UNIQUE_SUFFIX
```

That example uses locally available base images and a fresh local recovery environment. For retained release images/credentials, pass the reviewed `--env-file` and `--file` arguments too. The helper refuses any existing target containers/volumes/networks and any project outside the `rallysense-restore-*` prefix. Its final recovery override removes published service ports and temporarily uses writable mode/artifact mounts for extraction in the fresh isolated project, including backups from Mode A. It verifies archive hashes, restores without destructive `--clean`, compares all table-content digests and artifact hashes, checks migration/readiness, then stops the isolated DB. It retains the recovered volumes. It never restores over the live project.

The executed rehearsal matched 17 tables and 116 artifacts. This proves local binary backup/restore compatibility, not off-host/cloud disaster recovery. Keep the current private backup out of any public fixture preparation.

## Rollback

Remove writers and drain/stop the worker. If schema-compatible, restore the previous reviewed API/worker/web image references together, retaining volumes and the same access mode; restart privately and verify contracts, readiness and source reads. New-release queued jobs must not run silently on an old environment. If a future migration is incompatible, restore the paired backup into a **new** project, verify it and switch the reviewed entry point only after human acceptance. Do not use a blind Alembic downgrade, volume reset or live `pg_restore --clean`.

## Scan, smoke and monitoring gates

Before public release, authenticate to an approved image scanner and review API/FFmpeg, frontend, PostgreSQL and Caddy images. The local Docker Scout attempt was blocked by missing Docker login; no OS-clean result exists.

```bash
docker scout cves --only-severity critical,high local://REVIEWED_API_IMAGE
docker scout cves --only-severity critical,high local://REVIEWED_WEB_IMAGE
docker scout cves --only-severity critical,high REVIEWED_POSTGRES_IMAGE
docker scout cves --only-severity critical,high REVIEWED_CADDY_IMAGE
```

Use retained image digests and save scan dates/results; a successful scanner command without an exit-policy check is not automatically a clean report. Review/fix exploitable or applicable findings before release. npm runtime audit has zero known findings; ten moderate development-tool advisories remain separately documented.

After authorized staging, verify valid TLS and exact-host routing, unauthorized page/API 401 even with spoofed internal headers, valid credentials, rejected foreign Origin/Host, direct API/DB port isolation, Range media, reports and fixture exports. In Mode A check every mutation family returns 403 and private/unknown IDs return 404. In Mode B rerun valid/invalid uploads and actual worker completion, annotation/sync/research workflows and a restart. `curl --user lab https://REVIEWED_DOMAIN/...` prompts for the password; do not put it in shell history or process arguments.

Monitor `dc ps`, database/API readiness, diagnostics and worker heartbeat separately. Alert on stale worker age (>45 s), sustained queue age, repeated 5xx/413/429, disk utilization/headroom, container restarts/OOMs and backup age. Keep bounded container logs; application logs use route templates and never uploaded body values. Add host-specific alerts and off-host backup schedules before accepting valuable recordings. Do not claim throughput or size the host solely from the observed local process peaks.

Human acceptance includes fixture/license/privacy review, key-browser accessibility/error paths and physical phones if capture compatibility is advertised. A consented independent paired-tennis study remains necessary for any tennis accuracy claim. **Deployment still requires explicit authorization.**
