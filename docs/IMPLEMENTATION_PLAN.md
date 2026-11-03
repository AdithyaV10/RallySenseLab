# Implementation plan and stage gates

This is the approved Step 1 plan. The user subsequently authorized Step 2; see [current project status](PROJECT_STATUS.md) for the implemented checkpoint and authorization boundary. The full [original project brief](PROJECT_BRIEF.md) remains authoritative. Never infer permission for the next stage from available time or context.

## Stage ownership

| Stage | Trigger | Deliverable and boundary |
| --- | --- | --- |
| 1 Architecture | Initial master prompt | Documents, validated approach, environment findings, local checkpoint; no application code |
| 2 Foundation/MVP | `CONTINUE TO STEP 2` | Running local full-stack ingestion, pose, IMU events, alignment, replay, annotations, synthetic demo and tests |
| 3 Research | `CONTINUE TO STEP 3` | Video-event and improved IMU baselines, fusion, challenge, evaluation, reproducible experiments/report; optional ML only if data supports it |
| 4 Completion | `CONTINUE TO STEP 4` | Product polish, phone recording, feedback, exports, performance measurements, full system testing and deployment configuration; no deployment |
| 5 Audit | `CONTINUE TO STEP 5` | Independent architecture/science/security/UX audit, reproducible findings, severity-ranked defects, readiness verdict; no publishing |

At each stage: complete assigned work, run applicable checks, update status/decisions, make a local Git checkpoint when safe, provide an honest report, and stop. A model recommendation in the brief is not a requirement to spawn agents or change runtime settings.

## Step 2 prerequisite checks

Read PROJECT_STATUS, DECISIONS, this plan, and the exact Step 2 section of the brief before edits. Inspect the actual Git working tree; preserve any intervening user changes.

1. Resolve local Docker Desktop/engine availability. `docker info` currently cannot reach the engine. No database has started. If unavailable, a real local PostgreSQL installation is a possible explicitly documented substitute; do not silently replace PostgreSQL with SQLite and claim integration passed.
2. Use `npm.cmd` under Windows PowerShell: `npm.ps1` is blocked by execution policy. Use the working `python` executable or `uv`, since `py` reported no installed runtime.
3. Refresh registry metadata, check all dependency/peer ranges, resolve exact locks, inspect security advisories, and verify a minimal build/import before broad implementation. The [metadata snapshot](TECHNICAL_VALIDATION.md) is not a resolved lockfile. Do not pin a package solely because it was latest during planning.
4. Install/provision FFprobe/FFmpeg for bounded metadata inspection, preferably in the API/worker container. Verify local binary path or container invocation and supported formats. Do not shell-interpolate filenames.
5. Acquire and checksum an appropriately licensed MediaPipe model plus matching WASM/runtime. Verify actual browser worker initialization and a valid real clip when available. If no clip exists, explicitly distinguish fixture tests from unverified real-video inference.

## Step 2 ordered work packages

| Order | Work and dependencies | Concrete completion evidence |
| --- | --- | --- |
| 1 | Create monorepo, package/uv locks, strict TS, API config, Compose DB/API/worker/web definitions, `.env.example`, minimal CI | Clean install/import, API liveness, web build, actual PostgreSQL ready |
| 2 | Implement SQLAlchemy models/migrations, storage abstraction, bounded upload validation, durable jobs, session CRUD and deletion | Empty DB migrates; create/read/delete survives restart; file traversal/size rejection; cancellation cleanup |
| 3 | Implement canonical sensor import and explicit mapping; raw/normalized artifacts and quality | Equivalent unit inputs agree; separate sensor clocks retained; invalid rows, gaps, absent channels handled |
| 4 | Implement versioned synchronization and pure IMU baseline modules | Known positive/negative offsets, inverse mapping, minimum separation, flat/noisy/gapped signals pass meaningful tests |
| 5 | Seed deterministic synthetic inputs through real import/inference; add explicitly labeled animation if no demo video | Session reload has computed events; changing signal amplitude/config changes actual outputs; annotations persist |
| 6 | Implement real video upload/probe/stream, browser pose worker, batch finalization, pose feature primitives | Valid video metadata; ordered actual media timestamps; missing pose and interrupted extraction behavior; real-clip result only if directly tested |
| 7 | Build connected landing/dashboard/data screens and synchronized replay using shared clock; annotation CRUD, quality states | Core user journey, saved alignment, event navigation, speed/seek behavior, no fake primary actions |
| 8 | Integrate failure paths, docs and CI; run full MVP checks and record limits | Test/build commands and exit results; reproducible startup/demo instructions; Step 2 completion report and stop |

The first useful vertical slice is sensor CSV -> normalization -> IMU inference -> persisted events -> signal-only replay -> annotation. Add actual video/pose to the same data contracts next. This sequence yields useful incremental verification but does not waive any Step 2 deliverable.

No trained neural network, automated drift fitting, scientific evaluation UI, fusion algorithm, or challenge implementation belongs to Step 2. Schema and type extension points may exist without advertised inactive primary actions. Browser recording completion is Step 4; CSV import must already work in Step 2.

## Contract acceptance fixtures

| Area | Required check and expected behavior |
| --- | --- |
| Units | 180 deg/s -> pi rad/s; 1 g -> 9.80665 m/s²; including-gravity stays explicitly distinct |
| Import | Canonical and mapped equivalent files produce equivalent normalized streams; decreasing times rejected; separate stream rates preserved; null != zero |
| Mapping | Sensor 2 s -> video 3.5 s with +1.5 s; inverse 5 s -> 3.5 s; negative offsets, boundaries, rounding ties, and nonzero origins agree across TS/Python |
| Signals | Constant input yields no events; isolated known pulses are recovered within sampling/filter tolerance; minimum spacing respected; short/gapped data excludes intervals |
| Pose | Actual media timestamp propagation, no-person frames, batch retries/conflicts, stale frames hidden, rotation/letterboxing correct |
| Jobs/storage | Restart with expired lease, idempotent retry, session delete during processing, no stale-worker publication, staging orphan recovery |
| Database | Actual PostgreSQL migration/restart persistence, same-session FK constraints, annotation revision conflicts, safe cleanup |
| Browser | Create session, import fixture, run detector, scrub/select event, edit annotation, save alignment, reload; no false success on API failure |
| Security | Oversized upload, forged MIME, malformed CSV, traversal/symlink escape, foreign-session asset ID, origin rejection, bounded probe timeout |
| Later evaluation | Adversarial matching, no events/references, undefined metrics, label version isolation, time-shift invariance, paired corruption reproducibility |

Write meaningful tests for implemented computational and persistence behavior, not tests that merely mirror constants or assert mocked success. Fixture-derived expected results must be independently calculated; no snapshots of an incorrect algorithm as truth.

## Planned commands, not executed application checks

The exact manifests/paths below must be created and confirmed during Step 2. These are a proposed interface for the implementation, **not currently runnable startup instructions**:

```powershell
docker compose up -d db
uv sync --project apps/api --frozen
npm.cmd ci --prefix apps/web
docker compose run --rm api alembic upgrade head
docker compose up --build web api worker
uv run --project apps/api pytest
npm.cmd --prefix apps/web run typecheck
npm.cmd --prefix apps/web run lint
npm.cmd --prefix apps/web run test -- --run
npm.cmd --prefix apps/web run build
npm.cmd --prefix apps/web run test:e2e
```

Do not use `--frozen`/`ci` until actual lockfiles exist. Docker/native configuration should use the same schema and settings; maintain one documented default path and test it end-to-end. Step 2 must replace the proposal with exact verified commands, including seeding/demo instructions.

## Later handoffs

Step 3 starts by challenging foundational numerical assumptions. Add independent video features, robust sensor processing, explicit late fusion, one-to-one evaluation, frozen experiment manifests, missing-data challenge, and reproducible reports. Deliver real findings only for data actually available; an untrained extension interface is preferable to a fabricated model.

Step 4 completes phone capture where supported, conservative measurement feedback, report exports, visual/accessibility polish, API/storage/performance hardening, full browser/Compose verification, and all documentation requested by the brief, including handoff and interview walkthrough. Do not claim actual device testing from simulated events.

Step 5 independently executes the checks and traces data. Produce FINAL_AUDIT, FINAL_TEST_REPORT, DEPLOYMENT_READINESS, and KNOWN_LIMITATIONS; record every small fix. Choose an evidence-based readiness verdict. A passing prior stage never substitutes for audit evidence.

## Risk register

| Risk | Mitigation / point of verification |
| --- | --- |
| Docker engine unavailable | Resolve at Step 2 start; document actual DB startup failures |
| New package versions introduce compatibility gaps | Resolve locks, build/import smoke tests, versioned dependencies; metadata alone is insufficient |
| Browser misses frames or fails worker delegate | Track coverage, bounded slow extraction, explicit CPU fallback only if verified; no exhaustive-frame claim |
| No real recording/model asset | Test numerical contracts with synthetic fixtures; clearly retain real-video validation gap |
| Sensor placement differs from hypothesis | Record placement and stratify; require declared experimental override for unsupported cases |
| Variable frame rate, drift, async sensor streams | Actual presentation times, preserved stream clocks, cue-based alignment and revisioned mappings |
| Manual event has annotation ambiguity | Operational definition, blinded dual labels, uncertainty interval and protocol revision |
| Fusion reduces recall or appears better through missing-data exclusion | Paired full-task and common-coverage results; retain failures and denominators |
| Local files and DB diverge on crash/deletion | Staging publication, manifests, durable cleanup, job lease enforcement |
| Public demo exposes recordings | Keep loopback-only; implement/audit ownership and isolated demo data before any deployment |

## Step 1 verification scope

Check all required documents exist and contain nonempty substantive content, local links resolve, required schema entities and stage gates are present, and no application scaffold appears. Inspect Git whitespace and diff contents, then commit only project documentation and ignore rules. Markdown/Mermaid rendering and application tests are not implied by text consistency checks. Actual check results belong in PROJECT_STATUS.
