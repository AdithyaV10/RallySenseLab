# Step 6 curated fixture and privacy inventory

2026-11-09. Fresh `rallysense-step6-demo` volumes contain exactly two built-in generated sessions. No development database dump, recording directory, physical-device data or third-party video was imported. The independent workspace project has its own generated fixtures plus a generated acceptance session. Its IDs and credentials differ. Neither environment mounts the development volumes.

[Fixture inventory](evidence/step6/fixture-inventory.json) records the two demo IDs and all six artifact SHA-256 hashes. [Generation evidence](evidence/step6/demo-fixtures.json) records seven scored clean/failure experiments in addition to three precomputed unscored modes. The paired fixture has ten experiments total; full occlusion intentionally produces one explicit inference failure. These generated pulse references are frozen with `independent=false`. Report metrics verify software behavior only. Raw angular-speed events remain measured signal events/unvalidated proxies; no confirmed tennis swing or calibrated confidence claim was added.

| Item | Provenance / intended inclusion | License or approval status |
| --- | --- | --- |
| Synthetic CSV, pulse references, analytical landmarks | Existing in-repository generators; known generated clock, no real participants | Safe privacy scope verified; owner must approve final public fixture content. Analytical landmarks are not represented as MediaPipe output. |
| Synthetic MP4 | Programmatic rendering generated inside the fresh project; no athlete/source clip | No third-party footage imported. MP4 replay verified in Chromium. Encoding libraries retain their packaged licensing requirements. |
| Precomputed experiments and exported reports | Actual existing algorithms applied to generated observations | Clearly labeled synthetic; clean 2/2 reference matches and failure-case misses are not real-world accuracy. |
| MediaPipe JS/WASM | Installed `@mediapipe/tasks-vision 1.2.0`, package declares Apache-2.0 | Package metadata checked. Keep the shipped Google license/required notices. |
| Pose Landmarker Lite model | Official Google model URL/version and SHA-256 pinned in `data/assets.lock.json` | Model and Google LICENSE hashes checked. **Public redistribution approval for the exact model artifact/terms remains an owner gate**; package code license/page footer alone is not proof of model-weight licensing. |
| Optional official MediaPipe source clip / prior camera evidence | Earlier ignored/private validation assets and historical local evidence | Excluded from fresh demo and release bundle. No redistribution rights inferred. |
| Debian/FFmpeg/container components | Pinned release images, scanner package inventories and upstream copyright files | Preserve notices; external binary distribution/license review remains required if images are published. This run publishes none. |
| Private development database, backups, artifacts, env files, certificates/private keys | Ignored `storage/`, Docker named volumes, `data/private/` | Excluded from source bundle and public fixture data. Never copy the existing development database into the demo. |

The readonly demo enforces an explicit session allowlist and RO artifact mounts. A real extra generated guard row was temporarily inserted only into the fresh demo database, was absent from lists/diagnostics and returned 404, and was removed after the check. All twelve tested mutation families returned 403; retained worker state was `readonly_idle`. Cross-environment credentials and session IDs were rejected. An allowlist is defense in depth; the stronger privacy boundary here is a database that never contained private records.

The demo remains **viewer-password gated**, as required by the existing release access policy; the research workspace has a different strong password. Anonymous demo access is not enabled by this preparation. Shared workspace authentication is not per-user authorization or tenant isolation.

Actual workspace MediaPipe ran on the generated MP4 through the browser worker: 79 processed frames, zero detected person frames. This proves runtime/ingestion execution, not athlete tracking quality. Prior real-clip worker/fallback evidence remains in Step 5.5 and was not relabeled as new Step 6 evidence.

Sources: [locked assets](../data/assets.lock.json), [fixture generators](../scripts/prepare-curated-fixtures.py), [MediaPipe upstream license](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE), [official Pose Landmarker model documentation](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker). Public content, branding and exact model redistribution approval must precede internet release.
