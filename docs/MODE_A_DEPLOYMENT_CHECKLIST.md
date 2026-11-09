# Mode A controlled deployment checklist

**Prepared, not authorized or deployed.** Use only the standalone [Mode A configuration](../infrastructure/compose.mode-a.yml) and [frozen Mode A manifest](../infrastructure/mode-a-release-manifest.json). Do not use historical two-domain commands, the development Compose file, the upload-enabled API image, private research volumes or old DB physical files. [Review](STEP6_6_MODE_A_REVIEW.md) and [decision](MODE_A_RELEASE_DECISION.md) define the outstanding gates.

## Mandatory sign-offs before external actions

- [ ] Named security reviewer resolves **94 raw high instances / 12 unique CVEs**, seven additional manual XML advisories and other retained scan findings. Record exact images/config, evidence, accept/reject/patch decision, owner, expiry and revalidation triggers. No accepted exception exists yet.
- [ ] Owner approves generated fixture/video/report content, synthetic claims, branding and ownership. No private recording or independently validated tennis accuracy is included.
- [ ] Owner/legal reviewer approves exact model-weight hosting/redistribution and required component notices. Current web image **still includes** MediaPipe model/JS/WASM; disabled extraction does not remove distribution concerns. If rejected, authorize a separate asset-removal rebuild/scan/retest rather than waive the requirement.
- [ ] Owner approves password-gated viewer access and credential distribution. Username is `lab`; this is a shared viewer gate, not multiuser identity/tenant isolation. Anonymous access is not prepared.
- [ ] User explicitly authorizes provider/account/size/budget, private transfer, DNS changes, firewall opening and public listener. This document is not that authorization.
- [ ] Agree operator, monitoring recipient, maintenance window, backup destination/retention, RPO/RTO and rollback owner. Provisional objectives: recover within one maintenance window; retain immutable approved demo pair and take paired backups before any release/config/data change. Owner must set actual service objectives.

## Host, account, DNS and network prerequisites

Recommend DigitalOcean Basic regular **2 vCPU/4 GiB/80 GiB SSD**, Linux **amd64** Ubuntu 24.04 LTS, for small gated Mode A traffic. Compute listing is $24/month; optional basic weekly snapshots $4.80/month additional; separate backup/domain/tax/traffic costs apply. Local evidence supports a starting assumption, not a target-host capacity guarantee. See pricing and measured limits in the review. No GPU, managed database, registry, orchestration cluster or public workspace is needed. Use 8 GiB if capacity checks warrant it.

Owner must configure account billing/MFA, an SSH key, chosen region, a restricted administrator and a cloud firewall. Use an existing owned subdomain (for example `demo.<owned-domain>`); buy a domain only if none is owned and the user separately approves. Domain pricing is registrar dependent, not included in the server price.

- [ ] Install maintained Docker Engine/Compose plugin from [official Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/), plus Python 3.13 and reviewed `uv` 0.12.23 or equivalent compatible runner. Local testing used Docker 29.5.2/Compose 5.1.4. Compose must support `!reset`/`!override`; validate with the actual installed version. Do not build/scanner-load the full stack on this small production host.
- [ ] SSH 22 only from approved operator addresses; public TCP 80/443 only after authorization. No 3000/8000/5432/5433/18080/18443/8081 or Caddy admin port. No Docker daemon/socket TCP exposure. No Mode B hostname, network, image or container.
- [ ] Cover IPv4 **and** IPv6 in provider/host rules. Do not assume UFW alone blocks Docker published ports: [Docker firewall guidance](https://docs.docker.com/engine/network/packet-filtering-firewalls/). Verify externally after authorized start; leave backend ports unpublished.
- [ ] Approved exact domain A record points to the host. Set AAAA only when IPv6 routing/firewall is verified; otherwise leave it absent. Review CAA and any DNS proxy settings for Caddy's public CA validation. Allow outbound DNS, time synchronization and CA HTTPS; application backend network remains internal.
- [ ] Time synchronized; host security updates configured; Docker/data filesystem durable; >=20% disk headroom. Allocate/monitor logs and paired backup storage without deleting retained recovery volumes. Host/domain/CA/firewall checks are **not yet executed**.

## Local artifact preparation (no network action)

Run from the final clean Step 6.6 checkout on the existing development machine. Commands are shell-neutral except filesystem navigation. Do not copy all of `storage/`, the working directory, Docker volumes or Git history.

```text
uv run --project apps/api python scripts/mode-a-images.py verify
uv run --project apps/api python scripts/prepare-mode-a-transfer.py
```

The packager requires a clean Git checkpoint and refuses an existing output directory. It creates ignored `storage/step6_6/mode-a-transfer/` with:

- `mode-a-source.tar`: **tracked allowlist only** — needed app/lock fingerprints, Mode A config/scripts, restore overlay, notices and the three decision documents. No historical evidence/private data/Git metadata.
- Four exact reviewed image archives at their manifest-relative paths; **no full API/FFmpeg image**.
- Only `storage/step6_6/generated-demo-pair/{manifest.json,database.dump,artifacts.tar}`: fresh generated pair, six artifacts, two sessions. Never the private development backup.
- `SHA256SUMS` for all bundle files. Keep this checksum and the Git commit identity in a trusted separate record. A checksum without a trusted reference does not authenticate a transfer.

No environment secrets, private keys or local test CA are copied. The source bundle contains the Mode A local override for optional loopback rehearsal; it must not be applied to the production public gateway. `prepare-mode-a-local.py`/seed scripts are for the original private machine, not required on the public host; the host restores the precomputed generated pair without native processing.

**STOP here until security/content/model decisions and explicit external-action authorization are recorded.** Thereafter privately transfer only this allowlisted bundle over approved SSH/SFTP. The following Linux commands are prepared instructions, not commands executed during Step 6.6.

## Authorized host preparation and restore — public gateway still closed

Unpack into a private operator-owned release directory, conventionally `/opt/rallysense`. Restrict it to the operator; do not serve this directory directly. Retain the received `SHA256SUMS`/source tar for provenance. The final Git checkpoint hash must match the approved handoff.

```bash
cd /opt/rallysense
umask 077
sha256sum -c SHA256SUMS
tar -xf mode-a-source.tar
uv run --project apps/api python scripts/mode-a-images.py load
uv run --project apps/api python scripts/mode-a-images.py verify
```

The loader verifies **all** four archive/config/rootfs/platform identities and generated-pair hashes **before** loading. It accepts Docker's image-store ID representation only when it matches the expected image/config digest, then assigns frozen aliases. `pull_policy: never` prevents surprise pulls. Do not retag an unreviewed image over those aliases. Image IDs are exact in the manifest; aliases alone are not an integrity guarantee.

Generate new **host-specific** secrets. Replace the domain argument with the separately approved exact lowercase hostname. No scheme, port, wildcard or list. Do not use the private test domain/CA or development passwords. The helper refuses an existing file and writes mode 0600 before its content.

```bash
uv run --project apps/api python scripts/prepare-mode-a-env.py --domain demo.YOUR-OWNED-DOMAIN.example --output storage/release/demo.env
chmod 600 storage/release/demo.env
uv run --project apps/api python scripts/check-mode-a-production.py --env-file storage/release/demo.env
```

The example domain is a placeholder; replace it. Do not print the env file or rendered `docker compose config` into tickets/logs. The helper sets three distinct 64-hex secrets and the frozen fixture IDs. Required keys:

| Key | Required value |
| --- | --- |
| `POSTGRES_IMAGE`, `READONLY_API_IMAGE`, `WEB_IMAGE`, `CADDY_IMAGE` | Four frozen aliases verified against the Mode A manifest; no full API fallback |
| `POSTGRES_PASSWORD` | Unique 64 hex characters, also used internally in the DB URL |
| `LOCAL_TOKEN` | Separate unique 64-hex internal credential; never sent to the browser |
| `SITE_ACCESS_PASSWORD` | Separate unique 64-hex viewer password; distribute through an approved secure channel |
| `RALLYSENSE_DOMAIN`, `WEB_ALLOWED_HOSTS` | Same one exact approved hostname |
| `WEB_ALLOWED_ORIGINS` | Exactly `https://<that-hostname>`, standard port 443, no wildcard |
| `BUILD_ID`, `DEMO_SESSION_IDS` | Frozen build ID and two inspected generated session UUIDs from manifest |

`APP_MODE=demo_readonly`, authenticated gate, readonly mounts and private network are hardcoded in Mode A Compose. Production `TLS_POLICY` is unset; Caddy uses public HTTPS automatically after authorized start. An internal CA is only for local rehearsal. Docker host administrators can read container environments; restrict SSH/Docker access and keep backups encrypted. The current DB bootstrap/application account is a superuser inside this isolated synthetic-only DB; HTTP readonly is not SQL-role readonly. A compromised API/DB credential could mutate this generated DB. This is part of the scoped residual-risk decision, not multiuser hardening.

Choose a **new** release project, e.g. `rallysense-restore-mode-a-release-20261109`. The restore helper requires the `rallysense-restore-*` prefix, refuses an existing project/volumes/networks, checks the paired archive hashes, starts only private DB/temporary extraction containers, verifies all 17 tables/six files and readiness, then stops DB. It does not start web/gateway. A temporary RW artifact mount is confined to that fresh restore target.

```bash
uv run --project apps/api python scripts/backup-workspace.py restore \
  --directory storage/step6_6/generated-demo-pair \
  --project rallysense-restore-mode-a-release-20261109 \
  --env-file storage/release/demo.env \
  --file infrastructure/compose.mode-a.yml
```

- [ ] Record matching 17-table/six-artifact restore result and migration head; do not proceed on any difference.
- [ ] Confirm project volumes are newly created and source is exactly the generated pair; **never** attach old glibc/private volumes to the Alpine database.
- [ ] Confirm only four reviewed images are needed and no full API/FFmpeg image/Mode B service exists on the public host.
- [ ] Complete security/content approvals and explicit public listener/DNS/firewall authorization before the next command.

## Authorized cutover and acceptance

Use the **same project/env** as the successful restore. Production config has five services, only gateway publishes TCP 80/443, no workspace domain. No development/local-test overlays.

```bash
docker compose -p rallysense-restore-mode-a-release-20261109 \
  --env-file storage/release/demo.env -f infrastructure/compose.mode-a.yml \
  up -d --no-build --wait --wait-timeout 180

uv run --project apps/api python scripts/smoke-release.py \
  --env-directory storage/release --role demo

docker compose -p rallysense-restore-mode-a-release-20261109 \
  --env-file storage/release/demo.env -f infrastructure/compose.mode-a.yml ps
```

The smoke defaults to **real DNS/system public CA**, validates auth, exact Host/Origin, readiness, synthetic allowlist, mutation denial and report. Do not use `--local-stage`, disable certificate verification or accept a private CA for production. Store actual output securely; never claim success from prepared commands.

- [ ] Validate public certificate chain/name/expiry, HTTP→HTTPS redirect, DNS A/AAAA/CAA and ACME issuance/renewal logs. Local private-CA evidence did not test these.
- [ ] From an independent external machine, inspect approved host IP ports: only 80/443 publicly reachable; 22 only from operator IPs; API/DB/admin/health ports closed over both address families. Check Docker network/mount/image/health details without dumping secrets.
- [ ] Verify password challenge/bad password, foreign Origin denied, wrong Host/SNI denied, readonly uploads/edits denied, expected two synthetic sessions, video/graphs/pose, all ten experiments (one expected failed), comparisons/failure explorer and report downloads in an ordinary browser.
- [ ] Verify `readonly_idle` heartbeat and no queued/running processing jobs; no FFmpeg/FFprobe/installers in API/worker. No native media job is expected or enabled.
- [ ] Measure CPU/memory/OOM/disk and latency on this actual host under expected visitor concurrency. Reboot host once in an agreed window, confirm restart/readiness and paired data persistence. Docker healthchecks **report**, but do not automatically restart an unhealthy live process; arrange alerts/operator response.
- [ ] Configure and verify external uptime/auth-safe readiness, certificate-expiry, disk <20% free, memory pressure/OOM, unhealthy/restart-loop, stale heartbeat, elevated 5xx and backup-age alerts. Keep credentials out of monitoring URLs/logs. No recipient/service was configured in this stage.
- [ ] Deliver actual monitoring alert and restore an off-host copy before final operational acceptance. Record human acceptance; public deployment remains unverified until these actions actually run.

## Paired backup, recovery and rollback

Retain the original immutable generated pair and exact images/manifests. Before any change, quiesce and back up this **Mode A project**, not the development workspace. Use a new timestamped directory each time (helper refuses overwrite):

```bash
uv run --project apps/api python scripts/backup-workspace.py backup \
  --directory storage/backups/mode-a-YYYYMMDD-HHMMSS \
  --project rallysense-restore-mode-a-release-20261109 \
  --env-file storage/release/demo.env --file infrastructure/compose.mode-a.yml
```

This stops HTTP application services, drains queue, stops idle worker, inventories all tables/files, takes a PG custom logical dump and artifact tar together, then restarts stopped app services. Gateway may return 502/503 during the maintenance window. Preserve `manifest.json` and both files as one unit. A readonly demo should have no queued work; investigate rather than process unexpected native jobs. Encrypt and transfer to separately authorized off-host storage, with restricted retention (proposed seven daily/four weekly plus immutable release pair; owner must approve), verify transport hashes and schedule isolated restore drills. Do not rely solely on a crash-consistent whole-disk snapshot.

For immediate exposure containment or failed acceptance, stop the gateway (no data deletion):

```bash
docker compose -p rallysense-restore-mode-a-release-20261109 \
  --env-file storage/release/demo.env -f infrastructure/compose.mode-a.yml stop gateway
```

For recovery, restore the chosen matching pair into a **different new** `rallysense-restore-*` project using the same helper/Mode A file and the previously approved exact images/config. Validate privately with `compose.mode-a.local.yml` on loopback or via an approved SSH tunnel before cutover. Stop old gateway before assigning 80/443 to the recovered project; point the cutover command at that new project. Keep old project/volumes stopped and retained. Never `down -v`, prune, replace DB files in place, or mix DB/artifact snapshots. Step 6.5's old PostgreSQL image has known critical XML risk; it is not an automatic security-approved rollback. If no approved prior release exists, keep the public gateway closed and recover the exact reviewed Mode A pair/config pending approval.

Local Step 6.6 evidence demonstrates backup/isolated restore, not a cloud recovery/SLA. Cloud account, host, domain, firewall, public CA, off-host backup and monitoring decisions remain external prerequisites.
