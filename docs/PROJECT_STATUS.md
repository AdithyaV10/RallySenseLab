# Project status

Updated: 2026-11-06, America/New_York. Verification timestamps in JSON are UTC and can fall on November 7.

## Authorization and stage gate

- Completed stage: **Step 4 ? collection readiness, analytical product experience, reliability and deployment preparation**.
- State: **complete; stopped at the mandatory Step 4 review gate**.
- Authorization: [preserved Step 4 execution specification](STEP4_SPECIFICATION.md).
- Next authorized stage: **none**. Step 5 needs explicit user authorization.
- No deployment, publication, remote push, cloud provisioning or Step 5 independent audit occurred.
- Starting checkpoint: Step 3 `3ec36d8`; Step 2 `7ce77c6`. The Step 4 checkpoint is the local commit containing this status/report; obtain its ID with `git log -1 --format=%h`.

## Delivered

The Next.js/FastAPI/PostgreSQL/durable-worker architecture is preserved. Collection studio supports real browser DeviceMotion and optional MediaRecorder where APIs permit, explicit recorded/synthetic source provenance, raw/SI export, ordinary worker ingestion, revisioned collection metadata, actual source quality and start/end cue evidence. Streamed WebM repair retains original uploads and copies encoded video without re-encoding.

Replay adds cursor-local pose retrieval beyond the former initial cap, signal windows, time/observed-pose-frame stepping, short event-context playback, clock/evidence readouts and view preferences. Challenge adds actual-result failure navigation, compatible comparison deltas, efficient history summaries and print-ready reports. Independent annotations, blind labeling and immutable reference snapshots remain intact. Dismissible guidance, responsive polish, diagnostics/heartbeat, narrow safe retries, readonly fixture visibility and optional trusted local HTTPS preparation are implemented.

Scientific meanings are unchanged: `gyro_peak_v1` is an angular-speed signal event, `wrist_speed_peak_v1` an image wrist-speed event and `multimodal_association_v1` a temporal co-occurrence retaining both observation times. None automatically confirms a tennis swing, ball impact or biomechanical reconstruction. Unlike reference definitions need a declared proxy hypothesis. No eligible reference means no accuracy. Synthetic results verify software only.

## Actual verification

| Check | Result |
| --- | --- |
| Production API/worker and Next images / startup | PASS; retained volumes, packaged source, loopback web/API/DB, healthy API/DB/worker |
| Final container backend suite | **42 passed, 0 failed, 0 skipped**, 13.10 s; six documented deprecation warnings |
| Final frontend units | **15 passed**, 5 files, 4.63 s |
| Strict types / ESLint / Ruff / generated contracts | PASS |
| Migration head / consistency | `0003_collection_readiness`; no new upgrade operations |
| Full production Chromium suite | **8 passed, 0 failed/skipped/flaky**, 96.996 s |
| Focused final ingestion/permission/camera/CSV/lifecycle verification | **4 passed**, 33.5 s after source-panel polish |
| Optional workspace gate and read-only production integration | PASS: 401/200 authentication, approved fixtures only, private 404, mutation 403, capture/upload disabled |
| Desktop/tablet/mobile layout and actual screenshot inspection | PASS: eight routes, 24 viewport checks without page overflow; additional paired-collection screenshots |
| Original Step 3 data preservation | PASS: baseline 82 experiments, 11 references, 41 artifact identities/fields and 10 sessions retained; additions allowed |
| Ordinary smoke and 11-condition synthetic research smoke | PASS; original 1,801-row Parquet read, source preservation and actual reports |
| Package advisory scan | Runtime npm 0; pinned Python 35 packages / 0 known findings; 10 moderate development-tool findings remain |
| Phone helper / default and production-prep Compose configuration | Syntax/render checks PASS; no LAN listener/trust/firewall change performed |

The actual permitted clip produced 83 playback-worker observations at 13.85 Hz with 360 ms maximum gap, and 149 seek/backpressure observations at 24.67 Hz with 80 ms maximum gap, at a nominal 30 Hz target. The actual main-thread fallback completed 49 frames. These are source observation/cadence measurements, not throughput or tennis accuracy.

Same-history profiling measured 3,335,773 bytes for 50 full experiment results versus 281,249 bytes for summaries plus one selected full result. Current screenshot/navigation measurements and exact scope are retained; no production benchmark is claimed.

Evidence: [ordinary readiness](evidence/step4-readiness-verification.json), [full browser](evidence/step4-browser-verification.json), [focused final ingestion](evidence/step4-final-ingestion-verification.json), [access restrictions](evidence/step4-access-verification.json), [preservation](evidence/step4-preservation-verification.json), [synthetic conditions](evidence/step4-local-verification.json), [history profile](evidence/step4-history-profile.json), [final layout/performance](evidence/step4-final-performance.json), [advisories](evidence/step4-dependency-audit.json). Screenshots and the actual synthetic PDF are retained locally under ignored `docs/evidence/step4-*` paths. Historical Step 3 evidence remains separate.

## Known limits

Physical iOS/Android and a consented paired tennis pilot remain unverified. Capture is foreground/in-memory until save/export; browser support, missed channels, interruption, codec and clock limits remain. Offset-only alignment does not repair drift. Pairing/placement/consent are operator attestations. No independently labeled held-out tennis accuracy, trained movement classifier, calibrated confidence, racket orientation/trajectory or ball-impact validation is claimed.

Public multiuser identity, disposable mutation isolation, object storage/direct upload, distributed quotas and public security certification are not implemented. Readonly demos require fresh dedicated fixture-only volumes and independent review. The optional shared workspace gate is not multiuser authorization. Ten moderate development-only package findings and an unperformed container OS scan remain. Backup/restore is documented; the live project was not destructively restored.

## Review locally

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open `http://127.0.0.1:3000`. Explore the ordinary or paired synthetic demo, follow/dismiss guidance, run/compare modes, introduce a controlled failure and inspect its actual report. Collection studio handles actual capture/import, quality and cue alignment. System readiness shows live services and processing state.

The full implementation/checks/limits are in [STEP4_REPORT](STEP4_REPORT.md); startup in [LOCAL_DEVELOPMENT](LOCAL_DEVELOPMENT.md); collection in [DATA_COLLECTION](DATA_COLLECTION.md) and [REAL_WORLD_PILOT](REAL_WORLD_PILOT.md); handoff in [PROJECT_HANDOFF](PROJECT_HANDOFF.md); future hosting barriers in [DEPLOYMENT](DEPLOYMENT.md). The working tree is checked after the local checkpoint. No Step 5 work is authorized.

**STEP 4 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 5.**
