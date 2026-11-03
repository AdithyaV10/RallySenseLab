# Project status

Updated: 2026-11-03, America/New_York.

## Authorization and checkpoint

- Current stage: **Step 1 — architecture and technical blueprint**.
- Stage state: **complete; stopped at the mandatory Step 1 review gate**.
- Last completed stage: **Step 1**.
- Authorized work: Step 1 only, as explicitly requested by the master prompt.
- Next authorized stage: **none**. Step 2 requires `CONTINUE TO STEP 2`.
- User authorization required to advance: **yes**.
- No application code, dependency installation, deployment, remote repository, push, or cloud provisioning has occurred.

## Delivered design

The blueprint defines a Next.js browser application, MediaPipe pose worker, modular FastAPI backend, durable PostgreSQL-backed processing jobs, PostgreSQL metadata, immutable local/Parquet artifacts, and a future storage adapter boundary. It specifies source clocks/units, ingestion and inference contracts, an IMU-first MVP, replay state, annotation provenance, event matching, evaluation methodology, and subsequent stage gates.

Implemented application features: **none; this stage is architecture only**. No scientific findings, model accuracy, throughput, or real-world device/video validation are claimed.

## Verification evidence

Environment probes and 23 public package metadata checks completed; see [technical validation](TECHNICAL_VALIDATION.md) for commands, actual versions, failures, and primary sources.

Actual documentation verification used an inline Python script (`@' ... '@ | python -`) checking file presence/size, Markdown local targets, code-fence pairing, schema entity names, stage commands, source-file hashes, and the project file inventory. Results:

- **PASS:** 8/8 required documents have substantive content; 11 Markdown files inspected.
- **PASS:** 25 local Markdown links resolve; code fences balanced.
- **PASS:** 14/14 required database entity names documented; all four later authorization commands present.
- **PASS:** preserved PROJECT_BRIEF is byte-identical to the supplied attachment (SHA-256 comparison).
- **PASS:** 12 project files comprise documentation and `.gitignore` only; no application scaffold.
- **PASS:** repository initialized on `main`; `git remote -v` returns no remote.
- **PASS:** `git -c safe.directory=C:/RallySenseLab diff --cached --check` found no whitespace errors; staged inventory contains exactly the 12 intended files. Git emitted expected Windows line-ending conversion notices.

Manual design review mapped all Step 1 acceptance criteria to their deliverables: component/data-flow coherence (ARCHITECTURE), justified stack (DECISIONS and TECHNICAL_VALIDATION), relationships (DATABASE_DESIGN), common interfaces (INFERENCE_CONTRACTS), defensible evaluation (RESEARCH_DESIGN), actionable MVP ordering (IMPLEMENTATION_PLAN), and clear nonimplementation status (all design documents and README).

Local checkpoint message: `docs: complete Step 1 architecture and technical blueprint`. Resolve the checkpoint ID with `git log -1 --format=%h`; the final user report includes the actual ID after commit. No remote or push is part of this checkpoint.

Application unit/integration/E2E tests, typecheck, lint, production build, database migrations, Docker startup, and real-video/device inference: **not run, because application code does not exist at this stage**. Mermaid syntax/visual rendering is not yet verified with a renderer.

## Known defects, limits, and blocked requirements

No application defect assessment is possible before implementation. The following are observed setup limitations or design risks:

- Docker CLI/Compose exist, but the engine named pipe is unavailable; Docker config reads also warn access denied. Database/container startup remains unverified.
- FFprobe, FFmpeg, and psql were not found on PATH. FFprobe documentation timed out twice; exact invocation remains a Step 2 check.
- PowerShell blocks npm.ps1; use the successfully verified `npm.cmd`. The `py` launcher does not discover Python; `python` works.
- Registry network reads required an elevated read-only tool call; that retry succeeded. Dependency resolution, native wheels, browser binaries, model assets, and compatibility builds remain untested.
- After repository initialization, sandboxed shell creation failed with `setup refresh had errors`; read-only verification succeeded using elevated execution. Git then detected the sandbox/elevated user ownership difference. A per-command `-c safe.directory=C:/RallySenseLab` exception was used for this known newly created repository; no global trust configuration changed.
- No real recordings, independent annotations, tested phones, or pose model artifact exist in this workspace.
- Browser sampling coverage, unknown sensor placement, ambiguous manual event times, and small datasets limit eventual scientific conclusions.

These do not block architecture completion. They may block Step 2 runtime acceptance until resolved. Public access remains out of scope and requires authentication/isolation review plus explicit authorization.

## Handoff files

| File | Purpose |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, data flows, worker/storage lifecycle, security, testing |
| [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | All required entities, constraints, artifacts, indexes, retention |
| [INFERENCE_CONTRACTS.md](INFERENCE_CONTRACTS.md) | Clocks/units, import/pose contracts, algorithms, failures, API |
| [RESEARCH_DESIGN.md](RESEARCH_DESIGN.md) | Collection, reference labels, matching, metrics, leakage prevention, challenge |
| [UX_SPECIFICATION.md](UX_SPECIFICATION.md) | Routes, interaction design, replay clock and states |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Exact stage boundaries, Step 2 sequence, acceptance fixtures |
| [DECISIONS.md](DECISIONS.md) | Accepted decisions and tradeoffs |
| [TECHNICAL_VALIDATION.md](TECHNICAL_VALIDATION.md) | Environment and primary-source evidence |
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Unmodified full user specification and stage reports/gates |
| [README.md](../README.md) | Entry point and honest current state |

## Next action after authorization

Step 2 should resolve runtime prerequisites, lock compatible dependencies, implement persistence/ingestion and the IMU vertical slice, then add actual video/pose, synchronized replay, annotation workflows, and a clearly labeled synthetic demo. Run all MVP checks, document actual startup commands and remaining limitations, create a local checkpoint, and stop before Step 3.

Local execution at this checkpoint: read the documents; there is no application startup command. Planned future commands are explicitly marked as unexecuted in IMPLEMENTATION_PLAN.

**STEP 1 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 2.**
