# RallySense Lab

**AI-Powered Sports Movement Intelligence**

An experimental tennis movement analysis platform investigating what sparse inertial measurements can reveal when compared with synchronized video observations and human annotations.

**Status: Step 4 collection and research product.** The Next.js/FastAPI/PostgreSQL MVP now includes stored-pose video inference, enhanced IMU observations, explicit multimodal association, frozen references, event evaluation, reproducible experiments, controlled corruption and the Sensor Fusion Challenge. See [project status](docs/PROJECT_STATUS.md), [research methods](docs/RESEARCH.md) and [experiment walkthrough](docs/EXPERIMENTS.md) for verified scope and limits. No real-world tennis accuracy is claimed.

## Start locally

Docker Desktop must be running with Linux containers. From PowerShell:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open **http://127.0.0.1:3000** and select **Explore the demo**. The first build installs locked dependencies and downloads checksum-verified official MediaPipe assets. No cloud account or sensor hardware is required. [Exact startup, native-development options, and troubleshooting](docs/LOCAL_DEVELOPMENT.md).

```powershell
docker compose exec api pytest -q
npm.cmd --prefix apps/web test
npm.cmd --prefix apps/web run test:e2e
```

Host frontend tests need `npm.cmd ci --prefix apps/web`; browser tests also need Chromium and the optional external verification clip. [Testing instructions and actual evidence](docs/TESTING.md).

## What works

- Create, load and delete local sessions with recorded/synthetic/mixed provenance.
- Upload validated video and import explicitly mapped accelerometer/gyroscope CSVs into immutable raw/Parquet storage.
- Run real offline filtering/peak detection. `gyro_peak_v1` events are measured angular-speed maxima, with an unvalidated relationship to tennis swings.
- Extract actual timestamped MediaPipe landmarks, retain no-person frames and coverage, and derive image-space feature primitives.
- Replay video, pose and signals together; scrub plots/timeline, change playback speed, save alignment revisions, and add/edit independent human references.
- Explore a deterministic synthetic fixture with computed events and a clearly labeled programmatic animation.
- Compare video, IMU and temporal-association experiments using actual stored predictions, frozen labels, quality, timing errors and processing latency.
- Run seeded missing-data, noise, timestamp, occlusion and synchronization experiments; export stored Markdown/JSON reports.
- Open the separate paired synthetic lab to exercise all three modes without claiming its generated landmarks are MediaPipe output.

The application is loopback-only and single-user. Physical phone capture and broader product hardening remain later-stage work requiring authorization. Independent paired tennis recordings, impact validation and cross-player generalization evidence are unavailable. Deployment and remote publication are prohibited.

## Blueprint

- [Project status and verification](docs/PROJECT_STATUS.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Database and artifact design](docs/DATABASE_DESIGN.md)
- [Inference, ingestion, synchronization, and API contracts](docs/INFERENCE_CONTRACTS.md)
- [Research methodology](docs/RESEARCH_DESIGN.md)
- [User experience](docs/UX_SPECIFICATION.md)
- [Stage boundaries and implementation sequence](docs/IMPLEMENTATION_PLAN.md)
- [Architecture decisions](docs/DECISIONS.md)
- [Environment and primary-source research](docs/TECHNICAL_VALIDATION.md)

The implemented stack is Next.js/React/TypeScript, browser MediaPipe, FastAPI/Python, PostgreSQL, and local artifact storage. Analytical event detectors precede any optional trained movement classifier. Synthetic fixtures verify software behavior; they do not establish real-world accuracy. Pose estimates are observations, not ground-truth biomechanics. No affiliation with another sports technology product is claimed.

No publishing, pushing, cloud provisioning, or deployment is authorized. The project remains local until a separate human review and explicit authorization.

## Step 4 collection and review experience

Open **Collection studio** at `/record` for pseudonymous session metadata, actual browser motion/camera capture, CSV/video import, quality inspection and start/end cue alignment. Browser measurements keep missing channels, raw device axes and explicit acceleration type; physical iOS/Android validation remains unperformed. Synthetic software inputs require explicit source provenance.

Replay supports bounded pose windows, signal zoom, clock readouts, time stepping and view preferences. The paired synthetic Challenge computes real stored results, failure navigation and print-ready reports. System readiness shows database, worker heartbeat and source-validation retries. `APP_MODE=demo_readonly` is a fail-closed fixture allowlist, not multiuser authentication. Default services remain loopback. No deployment or public push occurred.

See [Step 4 report](docs/STEP4_REPORT.md), [collection conventions](docs/DATA_COLLECTION.md), [physical pilot playbook](docs/REAL_WORLD_PILOT.md), [deployment preparation](docs/DEPLOYMENT.md), [handoff](docs/PROJECT_HANDOFF.md) and [interview walkthrough](docs/INTERVIEW_WALKTHROUGH.md). Final status/checks are recorded in the report; no physical-study metrics are claimed.
