# Deployment preparation — no deployment performed

Step 4 prepares configurations and identifies barriers. It does not authorize public exposure, hosting, provisioning, publication or a remote push. Step 5 requires independent review and explicit authorization.

## Recommended first demonstration architecture

Use the existing packaged Next.js, FastAPI, durable worker and PostgreSQL on a small container-capable server with a private persistent artifact volume, behind a reviewed TLS/access layer. Keep database and API ports private. This is an engineering recommendation based on the implemented filesystem interface and durable worker lifecycle, not a measured cost forecast. A single server reduces integration/operations overhead for a modest demonstration but remains a single failure domain. [Docker documents the single-server Compose pattern and production overrides](https://docs.docker.com/compose/how-tos/production/).

| Approach | Fit and remaining work |
| --- | --- |
| Single VM/container host + persistent disk + PostgreSQL | Closest to tested local architecture; bounded jobs and video artifacts persist across container restarts. Requires backups, disk monitoring, TLS, access controls and patching. Operational cost depends on selected CPU/disk/egress and uptime; no quoted price or purchase recommendation. |
| Next.js on Vercel + container API/worker + managed PostgreSQL + object storage | More independently managed services, suitable after storage/auth adapters and direct upload are implemented. Current Next API route proxies uploads up to 500 MiB; Vercel's documented function request/response payload limit is 4.5 MB, so this path cannot simply be hosted unchanged. [Function limits](https://vercel.com/docs/functions/limitations). Long processing should remain a durable worker rather than assuming request duration is sufficient. |
| AWS compute + private disk/object storage + managed PostgreSQL | Credible later architecture with networking/IAM/monitoring choices; greater configuration and audit burden for this stage. S3-compatible storage and signed multipart upload are **not implemented**. Do not configure an S3 bucket URL as though the filesystem adapter supported it. |

Provider details were checked against primary documentation on 2026-11-06. Pricing, quotas and service features can change. No paid API or cloud account was used.

## Configuration and readiness

The base Compose setup remains loopback-only, packaged source, retained volumes, restart policies and nonroot application processes. API readiness checks database/storage; worker health checks a real heartbeat. `/diagnostics` reports runtime/build/migration, FFprobe availability, free storage and the latest visible jobs. It does not expose service tokens, storage paths or request bodies. Production preparation is `infrastructure/compose.production-prep.yml`; it remains loopback-bound and is not a public TLS solution.

Prepare unique secrets outside Git: PostgreSQL password, internal LOCAL_TOKEN (at least 32 characters for ENVIRONMENT=production), workspace password (at least 20), exact hosts/origins, BUILD_ID reviewed commit and explicit demo session IDs. The server-only Next proxy forwards the internal token; the browser never receives it. The optional Basic workspace gate uses username `lab`; it requires TLS when used over a network. It is single-workspace access, not user accounts or object-level multiuser authorization. [Docker secrets](https://docs.docker.com/compose/how-tos/use-secrets/) are an option for a future reviewed secret-injection layer; the app currently consumes environment variables, not `_FILE` conventions. Do not claim secrets-file support merely by mounting files.

Do not expose a Next development server publicly. Trusted local phone development has separate opt-in instructions. Production should use reviewed TLS termination, strict host/origin configuration, proxy upload/time limits appropriate for media, and access logs with redaction/retention. Check dependencies/container OS packages, resource quotas, abuse controls and backup restore before public access. The per-process source-upload burst limit is only a basic local guard, not distributed quota enforcement or DDoS protection.

## Read-only demonstration isolation

Set APP_MODE=demo_readonly and DEMO_SESSION_IDS to an explicit allowlist. Visible sessions must also be synthetic built-in fixtures with recognized demo keys. Empty allowlists expose no sessions. API mutation methods are blocked; direct private IDs, source data, jobs, experiments and exports pass the same session visibility guard. Visitors inspect actual stored fixture experiments; new computations remain disabled in this mode.

**Use a fresh dedicated Compose project and dedicated fresh database/artifact volumes for any future public demo. Never mount private recording volumes.** Before enabling read-only mode, locally seed only built-in fixtures, create transparently synthetic demonstration experiments, inspect all notes/labels/artifacts, then capture the exact IDs. Existing data marked synthetic is an attestation and is not a privacy scrubber. Allowlisting an old personally modified demo is unsafe. Read-only mode does not remove previously stored private text or media from an allowlisted object. The default project contains private-capable local records and must remain private.

The app has no disposable multiuser mutation sandbox, account management, public upload isolation, production object store, distributed quotas or public penetration-test evidence. These are review barriers, not completed public security features.

## Migrations, backup and recovery

Back up PostgreSQL and artifacts together before applying schema changes. Stop new writes and wait/cancel active jobs for a consistent maintenance window; do not interrupt source publication halfway through a backup. Use `pg_dump -Fc` inside the database container and copy the dump to restricted storage. In Windows PowerShell 5.1, do not pipe binary pg_dump output through text redirection: write it inside the container with `-f`, then `docker cp` the exact file. Archive the actual named artifact volume through a temporary read-only mount to restricted backup storage. Include the reviewed commit, migration revision, configuration without plaintext secrets, artifact hashes and an encrypted separately retained secret recovery plan. Retention/deletion must match participant permission. Never commit backups.

Restore into a **separate** local project/database/volume first. Restore the dump, restore corresponding artifacts, verify hashes/counts, run `alembic current`/`alembic check`, readiness, original source reads, immutable experiment/export checks and application smoke. A database-only restore cannot recover video/Parquet content. This playbook is documented; a destructive restore of the user's live project has not been attempted.

The API startup runs additive `alembic upgrade head` before accepting requests. Independently run migration preservation tests before rollout. Do not downgrade populated production schemas casually: the Step 4 downgrade removes collection/evidence data. Prepare recovery from the paired backup rather than treating schema rollback as nondestructive.
