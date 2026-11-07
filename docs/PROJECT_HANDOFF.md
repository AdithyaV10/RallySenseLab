# Local project handoff

RallySense Lab remains a single-user local research application. Step 4 adds Collection studio, explicit source capture metadata, synchronization evidence, replay controls, a failure explorer, print-ready reports, readiness diagnostics and read-only policy. It preserves FastAPI/PostgreSQL/worker, Next.js and immutable experiments. Current acceptance status and exact evidence belong to [PROJECT_STATUS](PROJECT_STATUS.md) and [STEP4_REPORT](STEP4_REPORT.md).

## Start and inspect

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
docker compose ps
```

Open `http://127.0.0.1:3000`. The API is loopback `:8000`; PostgreSQL is loopback `:5433`. Do not remove named volumes. No private video, CSV, artifact, secret, certificate or backup belongs in Git.

Start with **Explore the demo**, then **Explore the paired research demo**. Open **Collection studio** for actual capture/import and **System readiness** for live DB/worker/job state. [INTERVIEW_WALKTHROUGH](INTERVIEW_WALKTHROUGH.md) gives a short review route. [DATA_COLLECTION](DATA_COLLECTION.md) and [REAL_WORLD_PILOT](REAL_WORLD_PILOT.md) distinguish implemented software from unperformed physical collection.

## Ownership and extension points

`apps/api/src/rallysense/research.py` holds numerical research baselines; `experiments.py` applies frozen input/configuration and deterministic corruption. `api/research.py` creates and exposes immutable experiments; `jobs.py` publishes only under valid leases. `signals.py`, `pose_features.py`, `media.py` validate measured sources and derived observations. Do not change event meanings to make scores look better. Label sets freeze revision/provenance; later annotation edits do not rewrite snapshots.

`apps/web/src/features/capture` handles explicit device measurements, camera encoding and paired setup. `features/replay` owns session-clock replay and MediaPipe worker/fallback sampling. `features/research` presents actual results and frozen contracts. The server-only Next proxy attaches credentials, exact host/origin guards and optional workspace gate. Generated contracts live in `packages/shared-contracts/openapi.json` and `apps/web/src/lib/schema.d.ts`; regenerate with the repository checker and review intentional drift.

Changes should run meaningful numerical/integration tests, frontend checks, contract/migration checks and real production browser workflows. Existing tests use disposable PostgreSQL schemas and temporary artifacts. Live source preservation can be checked with `scripts/check-preservation.py verify` when the ignored baseline exists; it refuses to replace the baseline automatically.

## Gate and boundaries

No physical iOS/Android sensor, paired tennis study, calibrated biomechanics, trained swing/impact classifier, multiuser identity, object-store adapter or public deployment is established. Trusted local phone HTTPS is opt-in and remains separately unverified on hardware. See [DEPLOYMENT](DEPLOYMENT.md) for isolation and review barriers. Step 5, cloud provisioning, publication and pushing require explicit later authorization.
