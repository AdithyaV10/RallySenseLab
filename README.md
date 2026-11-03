# RallySense Lab

**AI-Powered Sports Movement Intelligence**

An experimental tennis movement analysis platform investigating what sparse inertial measurements can reveal when compared with synchronized video observations and human annotations.

**Status: Step 1 architecture complete. No application has been implemented.** Step 2 requires the explicit instruction `CONTINUE TO STEP 2`. There are no startup commands, installed project dependencies, test results for application code, or deployment at this checkpoint.

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

The planned stack is Next.js/React/TypeScript, browser MediaPipe, FastAPI/Python, PostgreSQL, and local artifact storage. Analytical event detectors precede any optional trained movement classifier. Synthetic fixtures verify software behavior; they do not establish real-world accuracy. Pose estimates are observations, not ground-truth biomechanics. No affiliation with another sports technology product is claimed.

No publishing, pushing, cloud provisioning, or deployment is authorized. The project remains local until a separate human review and explicit authorization.
