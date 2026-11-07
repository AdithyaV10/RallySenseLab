# Local application and research API

Version 0.2.0. The canonical, generated contract is [OpenAPI JSON](../packages/shared-contracts/openapi.json), with generated [TypeScript types](../apps/web/src/lib/schema.d.ts). Interactive API documentation is available locally at `http://127.0.0.1:8000/docs` after startup. Its Try-it-out requests require `x-lab-token`; ordinary web users go through the local Next.js proxy, which supplies that credential server-side.

## Step 3 research routes

All paths use `/api/v1`, the existing local credential/origin rules, safe errors and same-session checks.

| Method / path | Behavior |
| --- | --- |
| `POST /research-demo-sessions` | Idempotently queue the separate paired synthetic fixture; returns session metadata |
| `POST/GET /sessions/{id}/annotation-sets` | Create a named human draft set; list source sets with current revision/provenance |
| `POST /sessions/{id}/annotations?set_id=UUID` | Add a typed human event to the chosen draft; increments set revision |
| `POST /annotation-sets/{id}/freeze` | Copy one event type at a checked set revision with operational definition, labeler, procedure, independence and optional source-video ID/hash; 409 if stale |
| `GET /sessions/{id}/references` | Latest 100 immutable reference snapshots with event records and fingerprint |
| `POST /sessions/{id}/experiments` | Queue/reuse real `imu`, `video` or `fusion` processing with typed parameters, explicit sources/alignment, interval, reference and corruption recipe |
| `GET /sessions/{id}/experiments?limit=N` | Latest research history; default 50, maximum 200 |
| `GET /experiments/{id}` | Frozen manifest, durable state, predictions, component observations, quality, coverage, metrics, timing errors, latency and failure details |
| `POST /experiments/{id}/evaluate` | Create/reuse a new experiment with a chosen frozen reference, tolerance and comparison hypothesis; does not patch old results |
| `GET /sessions/{id}/experiment-comparison?ids=UUID&ids=UUID` | Up to three same-session stored experiments |
| `GET /experiments/{id}/report` | Download Markdown reflecting actual manifest/results/failure and reproduction request |

JSON export uses the same typed `GET /experiments/{id}` response; the browser downloads that stored representation. There is no independent source-data regeneration or hypothetical result in exports. Empty queued/failed results have typed empty collections and null evaluation until computation succeeds.

`ExperimentCreate` requires sensor and sync IDs for IMU, a ready pose ID for video, and both for fusion. Fusion requires `pairing` and documented `alignment_note`; mixed unrelated sources return `UNPAIRED_INPUT`. `comparison=exact` requires identical definitions and independent human labels. `proxy_hypothesis` requires explicit text for a supported human movement reference; `synthetic_fixture` requires synthetic session/reference provenance. No reference is a valid inference-only run with evaluation null. Source-video mismatch is refused. Invalid semantic settings return 422; stale revisions return 409; missing resources return 404.

Every experiment persists expanded algorithm settings, artifact identities, source provenance, sync/reference revisions, implementation/dependency/runtime identity, interval, seed and corruption parameters. It evaluates the full inclusive session interval with a one-to-one cardinality/error matcher. Old results remain unchanged after labels, alignment or settings change. `force_rerun=true` creates a new experiment; an identical ordinary request reuses queued/running/succeeded work. Numerical processing uses immutable Parquet, not downsampled chart windows. Lists are bounded, and event matching caps each list at 2,000 events.

Pose start accepts `sample_target_hz` 10 or 30 and `playback_rate` 1 or 0.5; the web selects half-speed playback for the denser target. Finalized quality records achieved cadence, gaps and executor/source provenance. These targets do not guarantee every frame.

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

The legacy detector produces `gyro_peak_v1`: filtered angular-speed maxima with rad/s magnitude and prominence. These are measured signal events and unvalidated movement proxies. Step 3 research adapters add image wrist-speed events, temporal association and explicit reference-based evaluation. No output establishes swing occurrence, ball contact, force or skill without an independently validated hypothesis.

Pose output contains normalized image landmarks, separate model world estimates, visibility/presence when available, actual media timestamps, and per-frame image-space features. Torso-normalized wrist radius/velocity and a 2D elbow angle are geometric observations; they are not calibrated biomechanics. Gaps and low visibility suppress derived values.

Source metadata and dense samples are separate: PostgreSQL holds metadata/events/configurations; raw files and compressed sensor/pose Parquet live in the artifact volume. API responses exclude private storage keys. Generated references are immutable; human drafts remain editable, and Step 3 frozen snapshots preserve prior reference revisions independently.

Errors use safe messages and typed codes. Declared and received request limits, bounded upload reads, finite numeric validation, UUID validation, Host/Origin checks, same-session composite foreign keys, generated storage keys, and fenced jobs protect the local workflow. This is a foundation, not a final security audit. Failed imports retain their private source/error metadata until session deletion; orphan files and abandoned pose batches are reconciled after a 24-hour grace period.

## Contract verification

From the repository root after dependency installation:

```powershell
node scripts/check-contracts.mjs
```

The script exports Pydantic OpenAPI, generates and formats TypeScript, and exits nonzero when it finds drift. Review and commit intentional changes, then rerun it. Do not maintain a second handwritten copy of the API DTOs.

## Step 4 endpoints and additions

- `GET /capabilities`: local/read-only mode, mutation availability, build and environment.
- `GET /diagnostics`: real DB check, worker heartbeat age/state, Python/FFprobe/storage/migration and latest visible job counts/records; no credentials or paths.
- `GET /demonstrations`: visible builtin synthetic sessions.
- `PATCH /sessions/{id}/collection`: `{revision, profile}` optimistic revision update (409 on stale input). Session creation also accepts collection_profile.
- Sensor multipart mapping optionally includes typed capture metadata; video multipart `metadata` carries explicit provenance/capture. Original uploads are retained; a streamed browser WebM repair records derived-container provenance.
- `POST /sessions/{id}/sync-configurations`: optional video_id/evidence with pairing note, paired attestation, up to two ordered source-clock cue pairs and timing uncertainty. Offset stays explicit; end residual is computed without drift fitting.
- `POST /jobs/{id}/retry`: failed/cancelled source normalize/video_probe only; creates/reuses a pending new validation job and retains the failed record. Experiments rerun as new immutable runs.
- Pose frames accept bounded `start_us`, `end_us`, `max_frames` (1..5000, default2000), returning filtered source_count and truncated. PoseStart adds sampling_method playback/seek_backpressure.
- Experiment list optional `summaries=true` omits dense results in a response-only projection. Full detail/report endpoints preserve stored results.

In demo_readonly mode all API mutation methods are rejected; session-owned GETs require explicit approved builtin synthetic IDs. Empty allowlist fails closed. Full generated OpenAPI remains the exact schema contract. Web `/experiments/{id}/report` is an actual-result print view, not a separate scientific computation.
