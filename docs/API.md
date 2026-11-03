# MVP API

Version 0.2.0. The canonical, generated contract is [OpenAPI JSON](../packages/shared-contracts/openapi.json), with generated [TypeScript types](../apps/web/src/lib/schema.d.ts). Interactive API documentation is available locally at `http://127.0.0.1:8000/docs` after startup. Its Try-it-out requests require `x-lab-token`; ordinary web users go through the local Next.js proxy, which supplies that credential server-side.

## Implemented routes

All domain paths below begin with `/api/v1`. Health endpoints are public local probes; the remaining routes require the local token. Foreign browser origins are rejected. No multiuser/public access is supported.

| Method / path | Behavior |
| --- | --- |
| `GET /health/live`, `/health/ready` | Process version; database/storage readiness |
| `GET /sessions`, `POST /sessions` | Latest 100 sessions; create a declared recorded/synthetic/mixed session with handedness and notes |
| `GET /sessions/{id}` | Session, sensors, videos, tracks, jobs, sync revisions, runs, measured events, and annotations |
| `DELETE /sessions/{id}` | Tombstone immediately, cancel work, enqueue safe cleanup; returns 202 job |
| `POST /demo-sessions` | Idempotently seed the deterministic synthetic session through import and inference jobs |
| `POST /sessions/{id}/sensor-imports` | Multipart `file` and JSON string `mapping`; confirmed mapping submission, returns normalization job |
| `GET /contracts/sensor-mapping` | Canonical mapping defaults/schema for column, unit, origin and placement declarations |
| `GET /sensor-recordings/{id}/samples` | Source-time window (`start_us`, `end_us`), bounded min/max chart sampling (`max_points` 20–5000); source/returned counts |
| `POST /sessions/{id}/videos` | Stream MP4/WebM to generated private key; queue actual FFprobe content validation |
| `GET /videos/{id}/content` | Validated media with HTTP Range support and no-store caching |
| `POST /videos/{id}/pose-tracks` | Start a new extraction with installed runtime version, model hash and executor |
| `PUT /pose-tracks/{id}/batches/{index}` | Bounded typed frames; same-content retries accepted, conflicting retries rejected |
| `POST /pose-tracks/{id}/complete` | Validate increasing media times, derive image features, publish Parquet and quality; remove staging |
| `POST /pose-tracks/{id}/fail` | Mark interrupted extraction failed and clear staging |
| `GET /pose-tracks/{id}/frames` | Bounded source-media window including landmarks, no-person frames, and derived feature values |
| `POST /sessions/{id}/sync-configurations` | Save a new sensor offset revision; positive means later in session/video time |
| `POST /sessions/{id}/inference-runs` | Run or reuse the exact IMU configuration/input/alignment fingerprint; queue actual numerical processing |
| `POST /sessions/{id}/annotations` | Add an independent human marker, category and note |
| `PATCH /annotations/{id}` | Edit with optimistic revision; stale edits return 409 |
| `DELETE /annotations/{id}?revision=N` | Remove an editable human annotation with matching revision |
| `GET /jobs/{id}`, `POST /jobs/{id}/cancel` | Real durable state and cancellation; deletion cleanup cannot be cancelled |

## Semantics

Movement timestamps are integer microseconds; public IDs have UUID semantics. Each sensor import normalizes its own first timestamp to zero while retaining original origin/unit metadata and raw bytes. Separate files are separate clocks. Step 2 supports offset only; no drift estimate is implied. A saved alignment does not rewrite an old run.

The detector produces `gyro_peak_v1`: filtered angular-speed maxima with rad/s magnitude and prominence. These are measured signal events and unvalidated movement proxies. They do not establish swing occurrence, ball contact, stroke category, force, or skill. There is no accuracy endpoint, classifier, fusion, event matcher, or scientific evaluation result in this stage.

Pose output contains normalized image landmarks, separate model world estimates, visibility/presence when available, actual media timestamps, and per-frame image-space features. Torso-normalized wrist radius/velocity and a 2D elbow angle are geometric observations; they are not calibrated biomechanics. Gaps and low visibility suppress derived values.

Source metadata and dense samples are separate: PostgreSQL holds metadata/events/configurations; raw files and compressed sensor/pose Parquet live in the artifact volume. API responses exclude private storage keys. Reference and measured-event tables are distinct. Generated references are immutable; human labels remain editable drafts until Step 3 adds frozen experimental snapshots.

Errors use safe messages and typed codes. Declared and received request limits, bounded upload reads, finite numeric validation, UUID validation, Host/Origin checks, same-session composite foreign keys, generated storage keys, and fenced jobs protect the local workflow. This is a foundation, not a final security audit. Failed imports retain their private source/error metadata until session deletion; orphan files and abandoned pose batches are reconciled after a 24-hour grace period.

## Contract verification

From the repository root after dependency installation:

```powershell
node scripts/check-contracts.mjs
```

The script exports Pydantic OpenAPI, generates and formats TypeScript, and exits nonzero when it finds drift. Review and commit intentional changes, then rerun it. Do not maintain a second handwritten copy of the API DTOs.
