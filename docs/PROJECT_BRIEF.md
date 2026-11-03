# RALLYSENSE LAB - MASTER CODEX DEVELOPMENT PROMPT
## Five-Stage Autonomous Engineering Workflow With Mandatory Review Gates

# CRITICAL INSTRUCTION: READ FIRST

You are building **RallySense Lab**, a complete, professional, AI-powered tennis movement intelligence and research platform.

This is a full-stack software engineering, computer vision, sensor fusion, and applied machine learning project.

You will develop it across **FIVE SEPARATE STAGES**.

Each stage has:

- Defined technical objectives
- Required deliverables
- Acceptance criteria
- Testing requirements
- A mandatory completion report
- A mandatory stopping point

**YOU MUST NEVER AUTOMATICALLY CONTINUE FROM ONE STAGE TO THE NEXT.**

After completing a stage:

1. Finish its assigned work.
2. Run all applicable verification checks.
3. Document your results.
4. Update the project status file.
5. Clearly explain what was completed.
6. Identify any limitations or failures.
7. STOP COMPLETELY.
8. Wait for explicit authorization to begin the next stage.

Do not implement features belonging exclusively to future stages.

Do not start a new development stage simply because you have remaining execution time or available context.

The user will manually switch Codex models between stages.

## Stage execution commands

The user will control progression using these instructions:

- `START STEP 1`
- `CONTINUE TO STEP 2`
- `CONTINUE TO STEP 3`
- `CONTINUE TO STEP 4`
- `CONTINUE TO STEP 5`

**On receiving this master prompt, execute STEP 1 ONLY.**

No separate START STEP 1 command is necessary.

At the end of Step 1, stop and wait.

Do not attempt to complete the entire project in one run.

---

# PART A - OVERALL PROJECT SPECIFICATION

## 1. PROJECT MISSION

Build a professional platform called:

# RallySense Lab
### AI-Powered Sports Movement Intelligence

RallySense Lab is an experimental AI-powered tennis movement analysis platform.

It combines:

1. Human pose estimation using computer vision
2. Smartphone inertial motion measurements
3. Time-series signal processing
4. Sparse-sensor movement inference
5. Multimodal sensor fusion
6. Synchronized video and sensor replay
7. Experimental evaluation of prediction accuracy
8. Visual and optional audio feedback
9. A complete software platform for data collection, storage, and analysis

The project should demonstrate the engineering capabilities expected from both:

- An AI and Motion Inference Engineer
- A Software and Data Systems Engineer

The finished product should be technically substantial enough to showcase in a serious AI/software engineering interview.

It must not be a generic portfolio dashboard, superficial demonstration, or collection of disconnected prototypes.

Build a coherent, functioning system with genuine data processing and defensible engineering decisions.

---

# 2. BACKGROUND: FRAMEPOINT ENGINEERING PROBLEM

The project is inspired by FramePoint, an AI sports intelligence initiative being developed by Opus 133.

FramePoint aims to infer human movement from limited observations, initially focusing on tennis.

Sensors embedded in equipment such as tennis rackets or golf clubs can provide acceleration and angular motion data.

The challenge is determining what useful information about the player's movement can be reliably recovered from those limited observations.

The underlying engineering problem involves:

- Sparse sensor observations
- Human pose estimation
- Inertial sensing
- Computer vision
- Multimodal signal processing
- Sensor coordinate frames
- Timestamp synchronization
- Motion-event detection
- Measurement uncertainty
- Generalization across recordings and players
- Reproducible experimentation
- Data collection infrastructure
- Interactive replay and feedback

Our project should explore this problem independently.

It must not claim to reproduce FramePoint's proprietary technology.

Do not use FramePoint's name, branding, logos, or identity within the product.

---

# 3. CENTRAL RESEARCH QUESTION

The primary research question is:

**How much useful tennis movement information can be inferred from sparse inertial sensor measurements, and how reliably do those predictions agree with synchronized video-derived observations and manually labeled movement events?**

The initial research targets are:

- Detecting when a swing-like movement occurs
- Detecting meaningful movement events and their timestamps
- Estimating relative motion intensity
- Comparing movement patterns across repetitions
- Measuring event-timing errors
- Investigating how missing or noisy sensor observations affect predictions
- Comparing video-only, IMU-only, and multimodal approaches

Possible additional targets:

- Forehand-like versus backhand-like movement classification
- Swing phase segmentation
- Relative rotational movement features
- Repetition consistency
- Confidence or signal-quality reporting

These additional targets should only be implemented and reported as validated capabilities when sufficient data and evidence exist.

Avoid scientifically unsupported claims.

A single smartphone accelerometer and gyroscope cannot reliably reconstruct arbitrary full-body 3D movement without additional assumptions and evidence.

Do not pretend otherwise.

---

# 4. PRODUCT EXPERIENCE

The application should feel like a professional sports engineering research platform.

A user should be able to:

1. Open a visually impressive landing page.
2. Enter the RallySense Lab application.
3. Explore an included demonstration session.
4. Create their own recording session.
5. Upload a tennis movement video.
6. Import smartphone accelerometer and gyroscope data.
7. Process the video using computer vision.
8. Extract human pose landmarks.
9. Synchronize video and sensor recordings.
10. Inspect synchronized playback.
11. Run real movement-event inference algorithms.
12. Compare predictions from different modalities.
13. Annotate reference events.
14. Evaluate prediction performance.
15. Inspect uncertainty, measurement quality, and failure cases.
16. Export reports or experimental results.

The final application must remain usable even when physical sensor hardware is unavailable.

Provide clearly labeled synthetic demonstration fixtures for local software verification.

Real recordings must be supported by the same software pipelines.

Synthetic fixtures must NEVER be represented as real-world validation.

---

# 5. PREFERRED TECHNOLOGY STACK

Use a maintainable, modern architecture.

## Frontend

- Next.js with App Router
- React
- TypeScript with strict type checking
- Tailwind CSS
- shadcn/ui or Radix-based components
- Lucide icons
- Recharts or Plotly
- TanStack Query where useful

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

## Computer vision

- MediaPipe Pose Landmarker
- OpenCV where appropriate
- NumPy

## Inertial signal processing

- NumPy
- SciPy
- scikit-learn

## Advanced ML

- PyTorch when genuinely needed and supported by available training data

## Infrastructure

- Docker
- Docker Compose
- Local file storage with future S3 compatibility
- GitHub Actions

## Testing

- Pytest
- Vitest
- React Testing Library
- Playwright

Verify currently available compatible package versions before installation.

Use lockfiles or pinned dependencies as appropriate.

Avoid unnecessarily complex infrastructure.

Do not add Kubernetes, Kafka, microservices, or cloud dependencies simply to make the project appear more impressive.

The system should be architecturally clean, scientifically defensible, and fully testable.

---

# 6. DESIGN REQUIREMENTS

The product must look polished and distinctive.

Visual direction:

- Deep charcoal and near-black backgrounds
- Restrained cyan and teal accents
- Warm orange or amber event markers
- Refined typography
- Premium analytics dashboard styling
- Modern cards and data panels
- Smooth animations
- Professional loading states
- Consistent iconography
- Beautiful charts
- Responsive layouts

Avoid generic SaaS-dashboard styling.

The user interface should resemble a professionally designed research and performance-analysis tool.

The final dashboard should have a particularly impressive synchronized replay interface.

Use actual application state and analysis outputs throughout the UI.

Do not create decorative charts with fabricated performance data.

No nonfunctional primary buttons.

No fake progress indicators.

No placeholder AI predictions disguised as real inference.

---

# 7. REQUIRED APPLICATION MODULES

The complete project must eventually contain the following modules.

## Module A - Landing page

A professional public-facing landing page with:

- Product branding
- Technical value proposition
- Motion analysis illustrations
- Feature highlights
- Sample demonstration access
- Entry point into the application

## Module B - Session dashboard

A workspace for:

- Creating sessions
- Managing recordings
- Inspecting recording metadata
- Viewing processing status
- Opening analysis results
- Navigating experimental runs

## Module C - Video processing

Support:

- Video upload
- MediaPipe pose extraction
- Landmark storage
- Human skeleton visualization
- Motion-feature extraction
- Video-based event inference

## Module D - Sensor recording and ingestion

Support:

- Smartphone motion capture where browser APIs allow it
- CSV imports
- Common phyphox export formats where feasible
- Column mapping
- Unit normalization
- Sampling-rate analysis
- Sensor-quality checks

## Module E - Synchronization engine

Support:

- Video/IMU timeline alignment
- Manual offset correction
- Optional synchronization-cue assistance
- Aligned timestamp mapping
- Persistent synchronization metadata

## Module F - Synchronized replay

Display:

- Video
- Pose skeleton
- Accelerometer signals
- Gyroscope signals
- Detected event timestamps
- Human annotations
- Playback controls
- Synchronized timeline navigation

## Module G - Motion inference

Support:

- IMU-only baseline
- Video-only baseline
- Multimodal fusion baseline
- Versioned inference configurations
- Real predictions generated from data

## Module H - Scientific evaluation

Support:

- Precision
- Recall
- F1 score
- Event timing errors
- False positive analysis
- Missed event analysis
- Data-quality reporting
- Algorithm comparison
- Experimental reproducibility

## Module I - Feedback

Provide conservative, evidence-based feedback based on actual measurements.

Do not claim professional coaching accuracy without validation.

## Module J - Research documentation

Explain:

- Architecture
- Algorithms
- Data collection
- Evaluation
- Limitations
- Reproducibility
- Engineering tradeoffs

---

# PART B - MANDATORY ENGINEERING RULES

## 8. REAL FUNCTIONALITY ONLY

The application must implement actual software functionality.

All significant predictions must originate from implemented algorithms operating on input data.

Do not hardcode successful inference outputs.

Do not fabricate model accuracy.

Do not invent test results.

Do not claim real-world validation from synthetic fixtures.

Where training data is unavailable, implement functioning analytical baselines rather than pretending a trained neural network exists.

If an advanced feature cannot be completed, document it honestly.

---

# 9. DATA SCIENCE INTEGRITY

Maintain a clear distinction between:

1. Raw recorded observations
2. Processed features
3. Model predictions
4. Human-provided annotations
5. Synthetic fixtures
6. Evaluation results

Manually labeled event timestamps should be the primary reference for evaluating event detection.

Video-derived pose estimates are not automatically ground-truth biomechanics.

Use clearly defined event types.

For example, the time of maximum gyroscope magnitude should not automatically be labeled ball impact.

Maintain explicit assumptions for every algorithm.

Report uncertainty only when it has a meaningful mathematical or empirical definition.

---

# 10. PRIVACY AND SECURITY

The platform may process user-recorded videos.

Therefore:

- Validate uploaded files.
- Enforce reasonable file-size limits.
- Prevent path traversal.
- Sanitize inputs.
- Avoid exposing private local paths.
- Keep secrets out of Git.
- Use environment variables.
- Implement safe session deletion.
- Provide sensible error handling.
- Avoid logging sensitive video contents.
- Document storage and retention behavior.

Design for future anonymous public demonstrations without exposing other users' uploads.

Public deployment will happen only after human review.

---

# 11. REPOSITORY ORGANIZATION

Use a clean monorepo.

Suggested structure:

rallysense-lab/
- apps/
  - web/
  - api/
- packages/
  - shared-contracts/
- research/
  - experiments/
  - evaluations/
- data/
  - demo/
  - fixtures/
- scripts/
- docs/
- infrastructure/
- tests/
- docker-compose.yml
- README.md
- .env.example

Modify this structure where justified.

Keep frontend components, API routes, data models, inference algorithms, synchronization functions, and evaluation logic properly separated.

Avoid giant files with unrelated responsibilities.

---

# 12. STAGE MANAGEMENT AND CHECKPOINTING

Maintain the file:

`docs/PROJECT_STATUS.md`

Update this file after every stage.

It must contain:

- Current stage
- Last completed stage
- Implemented features
- Verified functionality
- Tests run and results
- Known defects
- Blocked requirements
- Files relevant to continuing work
- Next authorized stage
- Whether user authorization is required

Also maintain:

`docs/DECISIONS.md`

Record important architecture decisions and their reasoning.

At each stage completion, create a local Git commit if Git is available and the workspace is a safe dedicated project repository.

Use a clear commit message.

If Git is unavailable, document the checkpoint without pretending a commit exists.

Never push to GitHub without explicit authorization.

Never deploy the application without explicit authorization.

Do not overwrite unrelated existing workspace files.

When resuming work in a later Codex session:

1. Inspect the repository.
2. Read PROJECT_STATUS.md.
3. Read DECISIONS.md.
4. Inspect relevant source files.
5. Identify the last verified checkpoint.
6. Continue only the specifically authorized stage.

---

# PART C - FIVE-STAGE EXECUTION PLAN

# STEP 1 - ARCHITECTURE AND TECHNICAL BLUEPRINT

## Recommended model: Astra, High reasoning

## Objective

Design the complete technical architecture and scientifically sound implementation plan.

**This stage is planning and architecture only.**

Do not begin full application implementation.

The purpose is to establish a strong foundation before the next model starts coding.

## Tasks

### 1. Inspect the environment

Determine:

- Operating system
- Workspace location
- Available Node.js version
- Available Python version
- Docker availability
- Git availability
- Package manager availability
- Existing repository contents

Do not perform destructive operations.

### 2. Research and validate the technical approach

Using available documentation and package metadata, determine suitable approaches for:

- Browser-based MediaPipe pose estimation
- Video frame timestamp handling
- Smartphone accelerometer/gyroscope capture
- Motion sensor CSV import
- Efficient time-series storage
- Sensor timestamp alignment
- Video overlay rendering
- Signal processing
- Event matching
- Scientific evaluation

If external documentation is inaccessible, clearly identify assumptions that require later verification.

### 3. Design the system architecture

Define:

- Frontend architecture
- Backend architecture
- Database architecture
- File storage strategy
- Inference engine interfaces
- Synchronization interfaces
- Experiment execution flow
- Data-quality system
- Testing strategy
- Deployment-ready architecture

Create a Mermaid architecture diagram.

### 4. Design the database schema

Specify entities for:

- Sessions
- Participants or pseudonymous IDs
- Video assets
- Sensor recordings
- Pose tracks
- Synchronization configurations
- Annotation sets
- Event annotations
- Inference runs
- Predictions
- Experiments
- Evaluation results
- Processing jobs
- Data-quality reports

Explain which data should reside in PostgreSQL and which should be stored as files.

Consider time-series storage efficiency.

### 5. Design the inference interfaces

Define standardized inputs and outputs for:

- Video-only inference
- IMU-only inference
- Multimodal fusion

Include:

- Algorithm name
- Algorithm version
- Required inputs
- Timestamp conventions
- Prediction format
- Event definitions
- Quality indicators
- Failure information
- Processing latency

### 6. Design the experimental methodology

Specify how to:

- Collect synchronized recordings
- Define swing events
- Label reference timestamps
- Compare predicted events
- Calculate timing errors
- Evaluate false positives and false negatives
- Avoid train/test leakage
- Test missing observations
- Document uncertainty

### 7. Design the user experience

Describe the navigation and layout for:

- Landing page
- Dashboard
- Recording studio
- Session upload
- Movement replay
- Sensor Fusion Challenge
- Evaluation dashboard
- Documentation

Specify the interaction architecture for synchronized replay.

### 8. Define development contracts

Establish clear interfaces and dependencies for Step 2 implementation.

Identify exactly which features should be implemented first.

Ensure Step 2 can build an end-to-end MVP without requiring advanced trained models.

## Required Step 1 deliverables

Create:

- `docs/ARCHITECTURE.md`
- `docs/DATABASE_DESIGN.md`
- `docs/RESEARCH_DESIGN.md`
- `docs/INFERENCE_CONTRACTS.md`
- `docs/UX_SPECIFICATION.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_STATUS.md`

An initial README is acceptable.

Do not create placeholder application code solely to make this stage appear more complete.

## Step 1 acceptance criteria

- Architecture is coherent.
- Data flows are defined.
- Technology choices are justified.
- Database relationships are documented.
- Inference interfaces are clearly specified.
- Research evaluation methodology is defensible.
- Step 2 implementation tasks are explicit.
- No claims of implemented features are made.

## MANDATORY STEP 1 STOP

After completing Step 1:

Provide:

1. Architecture summary
2. Major technical decisions
3. Files created
4. Design assumptions
5. Identified risks
6. Recommended Step 2 implementation sequence

End with:

**STEP 1 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 2.**

STOP.

Do not implement Step 2.

---

# STEP 2 - FULL-STACK FOUNDATION AND FUNCTIONAL MVP

## Recommended model: GPT-6.1 Sol, High reasoning

## Start only after receiving:

`CONTINUE TO STEP 2`

## Objective

Implement a fully functional local application with real session management, video processing, sensor ingestion, basic inference, and synchronized replay.

This is the main software construction stage.

Prioritize a stable end-to-end MVP before advanced experimentation.

## Tasks

### A. Build the repository

Implement:

- Next.js frontend
- FastAPI backend
- PostgreSQL database
- SQLAlchemy models
- Alembic migrations
- Docker Compose
- Environment configuration
- Shared types where appropriate

Use compatible, stable dependencies.

### B. Build the landing page

Implement a visually impressive, responsive landing page.

Include:

- RallySense Lab branding
- Technical value proposition
- Feature explanations
- Modern graphics
- Explore Demo action
- Enter Platform action

Maintain excellent visual quality.

### C. Build the main dashboard

Implement:

- Session list
- Session creation
- Session detail navigation
- Session deletion
- Upload actions
- Processing status
- Data-quality status
- Available recording modalities

Connect everything to backend state.

### D. Implement video ingestion

Support:

- Valid video uploads
- Metadata extraction
- File validation
- Persistent asset references
- Processing status
- Safe file storage

Implement clear errors for unsupported files.

### E. Implement computer vision

Use MediaPipe Pose Landmarker.

Support:

- Actual pose detection
- Landmark extraction
- Timestamped landmarks
- Detection confidence/visibility data
- Skeleton overlay
- Derived motion features
- Handling of missing landmarks

Prefer client-side inference where technically appropriate.

Verify processing with a valid test video if available.

If no valid video exists, validate computational functions with fixtures and document that full real-video inference remains unverified.

### F. Implement motion data ingestion

Support:

- Canonical accelerometer and gyroscope CSV files
- Column mapping
- Timestamp validation
- Unit normalization
- Sampling-rate estimation
- Missing sample detection
- Import quality summary
- Persistent recording metadata

Add common phyphox format support where practical.

### G. Implement the basic IMU baseline

Create a real swing-event detection algorithm.

Use:

- Signal magnitude
- Filtering
- Peak detection
- Configurable thresholds
- Minimum event separation
- Event timestamps

Document the method and limitations.

Use real calculations.

Do not substitute predetermined events.

### H. Implement synchronization

Support:

- Separate video and sensor time origins
- Manual time offset
- Timestamp mapping
- Persistent alignment configuration
- Accurate graph/video synchronization

Include unit tests for known-offset recordings.

### I. Implement replay studio

Build:

- Video player
- Pose overlay
- Acceleration graphs
- Gyroscope graphs
- Event markers
- Timeline scrubbing
- Playback-speed selection
- Event navigation
- Toggleable signal channels
- Synchronization offset controls

Scrubbing the timeline must update the relevant displays together.

### J. Implement manual annotation

Support:

- Adding event markers
- Editing timestamps
- Removing events
- Event categories
- Annotation persistence

Keep human labels separate from algorithm predictions.

### K. Implement a real local demo workflow

Provide a deterministic, explicitly labeled synthetic session.

It must exercise:

- Session loading
- Sensor-data ingestion
- Inference
- Event display
- Replay timeline
- Annotation functionality

If video cannot be included in the synthetic fixture, provide an appropriate programmatically rendered visual animation and label it accordingly.

Do not claim the synthetic session represents actual tennis performance.

### L. Implement foundational testing

Write:

- API tests
- Database tests
- CSV processing tests
- Timestamp tests
- Signal processing tests
- Basic frontend tests
- Core integration tests

Run tests and record results.

### M. Verify local execution

Attempt:

- Database startup
- API startup
- Frontend startup
- Database migrations
- Sample session loading
- Local build
- Core test suite

Troubleshoot failures.

## Required Step 2 deliverables

A working local MVP with:

- Frontend
- Backend
- Database
- Session management
- Video ingestion
- Pose extraction pipeline
- Sensor ingestion
- IMU event detection
- Synchronized replay
- Manual annotation
- Synthetic demo session
- Automated tests

The goal is a genuinely functioning software platform.

Do not implement advanced multimodal ML experimentation beyond what is needed for the core architecture.

## Step 2 acceptance criteria

At minimum:

- Application starts locally.
- Database migrations succeed.
- Frontend reaches backend.
- Sessions can be created and loaded.
- Valid sensor CSVs can be processed.
- IMU event detector produces events from inputs.
- The replay timeline handles synchronized data.
- Annotations persist.
- A sample session can be explored.
- Applicable tests have been run.
- Unverified capabilities are clearly identified.

## MANDATORY STEP 2 STOP

After completing Step 2:

Provide:

1. Completed features
2. Folder structure
3. Exact local startup commands
4. Working demo instructions
5. Test results
6. Incomplete features
7. Known bugs
8. Current technical limitations
9. Files relevant to Step 3

Update PROJECT_STATUS.md.

End with:

**STEP 2 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 3.**

STOP.

Do not proceed to advanced motion research or Step 3 work.

---

# STEP 3 - ADVANCED MOTION INFERENCE AND SCIENTIFIC EVALUATION

## Recommended model: Astra, High reasoning

## Start only after receiving:

`CONTINUE TO STEP 3`

## Objective

Transform the functioning MVP into a credible motion-inference research platform.

This stage focuses on the mathematically and scientifically demanding components.

Before implementation, inspect and challenge the assumptions used in Step 2.

Do not assume that every previous algorithm is correct.

## Tasks

### A. Audit the foundational inference pipeline

Review:

- IMU preprocessing
- Timestamp handling
- Signal filtering
- Event detection
- Feature definitions
- Coordinate-frame assumptions
- Synchronization correctness

Fix mathematical or methodological flaws.

Preserve working application behavior.

### B. Implement video-only inference

Use actual pose landmarks to derive:

- Wrist trajectories
- Relevant joint-angle features
- Movement velocities
- Temporal movement patterns
- Landmark-quality indicators

Implement a baseline for meaningful, explicitly defined movement events.

Do not confuse tracked wrist movement peaks with verified racket impact.

### C. Improve inertial inference

Evaluate:

- Accelerometer magnitude
- Gyroscope magnitude
- Temporal filtering
- Noise handling
- Signal peak detection
- Movement window segmentation
- Threshold sensitivity
- Sampling-rate effects
- Missing-data effects

Implement sensible configuration and reporting.

### D. Implement multimodal fusion

Build a genuine combined inference method.

It must:

- Use aligned video-derived and IMU-derived features or event predictions
- Respect equivalent event definitions
- Combine modality information meaningfully
- Handle missing modalities
- Report inference failures clearly
- Track algorithm versions
- Support reproducible evaluation

Choose an appropriate fusion method based on available data.

Prefer a clear, defensible algorithm over an unjustified complex neural network.

### E. Create the Sensor Fusion Challenge

Implement a polished experiment interface with selectable:

- Video-only mode
- IMU-only mode
- Multimodal mode

Each mode must run its corresponding inference logic.

Display actual predictions.

Allow users to compare event timelines and computed metrics when reference annotations exist.

Do not use predetermined scores.

### F. Implement rigorous event evaluation

Include:

- Configurable event matching tolerance
- One-to-one event matching
- Precision
- Recall
- F1 score
- Mean absolute timing error
- Median absolute timing error
- False positives
- False negatives
- Per-session results

Test event-matching logic against deterministic mathematical fixtures.

### G. Implement experimental comparison

Create a reproducible experiment system that stores:

- Algorithm versions
- Parameter configurations
- Input session references
- Annotation-set references
- Predictions
- Calculated metrics
- Processing latency
- Data-quality information

Avoid leakage between training and testing.

Do not claim cross-player generalization without actual player-separated data.

### H. Implement uncertainty and failure reporting

Report:

- Low-confidence landmarks
- Missing observations
- Irregular sensor sampling
- Weak event evidence
- Alignment uncertainty
- Missing required signals
- Failure cases

Only use the word "confidence" when its computation and meaning are documented.

### I. Implement controlled degradation experiments

Where feasible, investigate:

- Dropped IMU samples
- Sensor noise
- Sampling irregularities
- Artificial landmark occlusion
- Synchronization offset errors

Compare results against the original experiment.

Clearly label artificial corruption.

### J. Optional machine learning extension

If appropriate labeled data exists, implement a small time-series classifier.

Possible choices:

- Feature-based scikit-learn classifier
- Lightweight PyTorch temporal network

Use proper dataset splits and documented training.

If labeled data is insufficient, do not train or present a misleading model.

Instead, provide a well-designed extension interface and clearly state that the model is not trained.

### K. Produce a research report

Generate a report describing:

- Research objective
- Algorithms
- Experimental configuration
- Reference events
- Dataset type
- Metrics
- Observed errors
- Limitations
- Reproducibility

Synthetic fixtures must not be portrayed as real-world research results.

### L. Run mathematical and scientific tests

Test:

- Filtering
- Timestamp mapping
- Event matching
- Fusion calculations
- Metric computation
- Missing data
- Evaluation edge cases
- Algorithm versioning

## Required Step 3 deliverables

- Video-only baseline
- Improved IMU baseline
- Functioning multimodal fusion
- Sensor Fusion Challenge
- Evaluation engine
- Experiment comparison
- Quality/error analysis
- Reproducible experiment reports
- Research documentation
- Relevant automated tests

## Step 3 acceptance criteria

- Every inference mode uses real calculations.
- Metrics are generated from predictions and reference annotations.
- Sensor alignment is handled explicitly.
- Algorithms are documented.
- Experiments are reproducible.
- Scientific claims match available evidence.
- Mathematical tests pass or failures are documented.
- The working MVP remains functional.

## MANDATORY STEP 3 STOP

After completing Step 3:

Provide:

1. Algorithms implemented
2. Mathematical assumptions
3. Model comparison approach
4. Evaluation metrics
5. Actual test results
6. Sensor-fusion limitations
7. Research findings supported by available data
8. Features requiring real-world recordings
9. Recommendations for Step 4

Update PROJECT_STATUS.md.

End with:

**STEP 3 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 4.**

STOP.

Do not proceed to final polishing or Step 4 work.

---

# STEP 4 - PRODUCT COMPLETION, DESIGN POLISH, AND SYSTEM VERIFICATION

## Recommended model: GPT-6.1 Sol, High reasoning

## Start only after receiving:

`CONTINUE TO STEP 4`

## Objective

Turn the research platform into a polished, complete, professionally presented application ready for final independent technical review.

This stage focuses on frontend quality, system integration, practical completeness, reliability, testing, and documentation.

## Tasks

### A. Inspect all existing functionality

Review:

- Landing page
- Dashboard
- Session management
- Video analysis
- Sensor ingestion
- Synchronization
- Replay
- Inference
- Fusion
- Annotation
- Evaluation
- Experiment reports

Identify incomplete interactions and broken workflows.

### B. Polish the frontend

Improve:

- Visual consistency
- Typography
- Spacing
- Animation
- Responsive design
- Chart readability
- Interaction feedback
- Loading states
- Error messages
- Empty states
- Accessibility

The interface should look like a professionally developed sports intelligence application.

Avoid excessive animations that interfere with usability.

### C. Improve replay studio

Ensure:

- Video and signal timelines remain synchronized.
- Skeleton overlays track playback correctly.
- Event markers are interactive.
- Graphs update appropriately.
- Timeline scrubbing is smooth.
- Playback-speed changes behave correctly.
- Annotation edits persist.
- Missing data is handled gracefully.

### D. Build or finish smartphone recording

Where supported:

- Request motion permissions.
- Capture accelerometer and gyroscope data.
- Record timestamps.
- Display live measurements.
- Export captured data.
- Import recordings into sessions.

Test browser capability detection.

Do not claim that real iOS or Android hardware has been verified unless it actually has been tested.

Provide a working CSV import alternative.

### E. Build useful feedback features

Create measurement-driven feedback such as:

- Event timing
- Relative movement intensity
- Repetition consistency
- Signal quality
- Inference disagreement
- Missing observations

Use actual data.

Avoid unsupported technical or biomechanical coaching claims.

### F. Implement research reporting

Create:

- Experiment summary
- Model comparison table
- Event timing charts
- Failure analysis
- Data-quality reporting
- Exportable research summaries

### G. Finish backend quality

Review:

- API validation
- Error handling
- Transaction handling
- Database indexes
- File cleanup
- Processing states
- API documentation
- Logging
- Security controls

### H. Improve performance

Measure and optimize where feasible:

- Pose extraction throughput
- Inference latency
- API response latency
- Replay responsiveness
- Chart rendering
- Large CSV processing
- File upload behavior

Do not invent performance results.

### I. Implement full testing coverage

Run:

- Backend tests
- Frontend tests
- Integration tests
- Playwright tests
- Type checking
- Linting
- Production build
- Docker startup smoke tests

Fix identified defects.

Test both successful workflows and relevant failure scenarios.

### J. Prepare deployment configuration

Create:

- Production Dockerfile
- Environment configuration examples
- Database migration instructions
- S3-compatible storage abstraction or documented integration path
- CORS guidance
- Health checks
- Deployment documentation

Do not deploy.

Do not provision paid resources.

Do not request cloud credentials.

### K. Complete documentation

Required documentation:

- README.md
- docs/ARCHITECTURE.md
- docs/DATABASE_DESIGN.md
- docs/RESEARCH.md
- docs/DATA_COLLECTION.md
- docs/API.md
- docs/TESTING.md
- docs/DEPLOYMENT.md
- docs/DECISIONS.md
- docs/PROJECT_STATUS.md
- docs/PROJECT_HANDOFF.md
- docs/INTERVIEW_WALKTHROUGH.md

The interview walkthrough should explain technical decisions, actual results, tradeoffs, and limitations.

Do not invent achievements.

### L. Perform a complete local product walkthrough

Attempt to complete:

1. Start the application.
2. Open landing page.
3. Enter dashboard.
4. Open sample session.
5. View synchronized replay.
6. Inspect motion data.
7. Run event inference.
8. Compare inference methods.
9. Add reference annotations.
10. Run evaluation.
11. Review results.
12. Export experiment information.

Capture actual screenshots if browser tooling is available.

Document which workflows were directly verified.

## Required Step 4 deliverables

- Feature-complete application to the extent supported by available data
- Polished interface
- Functional demo experience
- Completed integrations
- Testing evidence
- Deployment-ready configuration
- Complete documentation
- Local run instructions
- Detailed handoff report

## Step 4 acceptance criteria

- Major navigation flows work.
- Frontend and backend are integrated.
- Data processing functions are real.
- Inference and evaluation are reproducible.
- The application is responsive.
- Known defects are documented.
- Testing evidence is available.
- No false claims of real-world validation exist.
- Local startup is reproducible.
- No deployment has occurred.

## MANDATORY STEP 4 STOP

After completing Step 4:

Provide:

1. Complete feature inventory
2. UI and UX improvements
3. Integration status
4. Local testing results
5. Commands used for verification
6. Remaining defects
7. Known scientific limitations
8. Exact startup and demo instructions
9. Deployment readiness assessment
10. Recommendations for independent audit

Update PROJECT_STATUS.md.

End with:

**STEP 4 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 5.**

STOP.

Do not begin the final audit automatically.

---

# STEP 5 - INDEPENDENT ENGINEERING AND RESEARCH AUDIT

## Recommended model: Astra, High reasoning

## Start only after receiving:

`CONTINUE TO STEP 5`

## Objective

Conduct a rigorous independent audit of the finished RallySense Lab repository.

Act as a skeptical senior engineering reviewer.

Do not assume the previous stages were implemented correctly.

Your job is to determine whether the application is genuinely functioning, scientifically defensible, reliable, and suitable for a professional engineering demonstration.

This stage is primarily review and validation.

Do not silently rewrite major subsystems during the audit.

Identify defects, verify claims, and propose targeted corrections.

Only make small, clearly justified fixes when they do not obscure the audit findings. Document every change.

## Audit Area A - Software architecture

Examine:

- Repository organization
- Module separation
- API design
- Database design
- Error handling
- Dependency management
- Maintainability
- Security

Identify architectural weaknesses.

## Audit Area B - Computer vision

Check:

- Whether MediaPipe actually processes video
- Timestamp correctness
- Landmark coordinate handling
- Confidence handling
- Skeleton overlay alignment
- Feature calculation
- Missing-landmark behavior

Identify any placeholder or misleading implementations.

## Audit Area C - Sensor processing

Check:

- CSV ingestion
- Unit normalization
- Sampling rates
- Missing data
- Noise filtering
- Timestamp alignment
- Coordinate frames
- Sensor quality reports

Verify mathematical correctness.

## Audit Area D - Motion inference

Inspect:

- IMU baseline
- Video baseline
- Fusion implementation
- Event definitions
- Filtering parameters
- Threshold handling
- Prediction timestamp generation
- Failure conditions

Determine whether the inference methods are genuinely distinct and defensible.

## Audit Area E - Scientific evaluation

Check:

- Ground-truth separation
- Event matching
- Precision calculation
- Recall calculation
- F1 calculation
- Timing errors
- Experiment reproducibility
- Data leakage risks
- Synthetic versus real-data separation

Look specifically for fabricated performance claims and unsupported conclusions.

## Audit Area F - Full-stack integration

Verify:

- Session creation
- Uploads
- Data processing
- Database persistence
- Inference execution
- Replay
- Annotation
- Evaluation
- Reporting

Trace actual data through the complete application.

## Audit Area G - User experience

Inspect the rendered application if tools permit.

Evaluate:

- Visual quality
- Responsiveness
- Navigation
- Replay experience
- Interaction correctness
- Error states
- Accessibility
- Overall professional presentation

## Audit Area H - Testing

Run applicable tests independently.

Check whether tests actually validate important behavior instead of merely asserting trivial conditions.

Review integration and E2E coverage.

Record failures explicitly.

## Audit Area I - Security and deployment readiness

Review:

- Secrets handling
- Upload safety
- Path traversal risks
- Data isolation
- Session deletion
- File retention
- CORS
- Environment configuration
- Database migrations
- Container builds

Determine what must be addressed before public deployment.

## Audit Area J - Interview readiness

Assess whether the project demonstrates:

- Applied computer vision
- Time-series analysis
- Sensor fusion
- Backend engineering
- Data management
- Full-stack software development
- Reproducible ML experimentation
- Real engineering judgment

Distinguish genuinely implemented capabilities from aspirations.

Identify the five strongest technical accomplishments that can be demonstrated truthfully.

## Required Step 5 deliverables

Create:

- `docs/FINAL_AUDIT.md`
- `docs/FINAL_TEST_REPORT.md`
- `docs/DEPLOYMENT_READINESS.md`
- `docs/KNOWN_LIMITATIONS.md`

Include a prioritized defect list.

Classify problems as:

- Critical
- High
- Medium
- Low

For each important defect, explain:

- What is wrong
- Where it occurs
- How to reproduce it
- Why it matters
- Recommended fix

## Final readiness verdict

Provide one of the following conclusions:

1. **READY FOR HUMAN DEMO REVIEW**
2. **READY AFTER MINOR FIXES**
3. **SIGNIFICANT FIXES REQUIRED**
4. **NOT READY**

Base the verdict on actual verification.

Do not automatically approve the project simply because previous stages are marked complete.

## MANDATORY STEP 5 STOP

After completing Step 5:

Provide:

1. Executive engineering assessment
2. Verified features
3. Unverified features
4. Critical defects
5. Scientific validity assessment
6. Security assessment
7. Test results
8. Deployment readiness verdict
9. Required next actions
10. Overall professional quality assessment

Update PROJECT_STATUS.md.

End with:

**STEP 5 COMPLETE - FINAL AUDIT DELIVERED. AWAITING HUMAN REVIEW BEFORE DEPLOYMENT.**

STOP.

Do not deploy the application.

Do not publish the code.

Do not provision cloud infrastructure.

---

# PART D - GLOBAL DEFINITION OF DONE

The overall project should satisfy the following criteria before being considered ready for external demonstration.

## Functionality

- The application starts locally.
- Frontend and backend communicate correctly.
- The database works.
- Sessions persist.
- Videos can be uploaded and processed.
- Pose landmarks can be extracted from valid recordings.
- Motion data can be imported.
- Sensor signals can be visualized.
- Actual inference algorithms generate predictions.
- Video and sensor timelines can be aligned.
- Replay navigation works.
- Annotations persist.
- Evaluation metrics are computed.
- Experiment results can be inspected.
- The sample demo can be explored without hardware.

## Technical quality

- Code is organized and maintainable.
- API contracts are documented.
- Type checking succeeds.
- Tests cover critical logic.
- Significant errors are handled.
- Data processing is reproducible.
- Algorithms have documented assumptions.
- Important performance characteristics are measured where possible.

## Scientific integrity

- No invented model accuracy.
- No fabricated athlete measurements.
- No fake real-world testing.
- No random predictions presented as trained AI.
- No unsupported full-body motion reconstruction claims.
- Synthetic experiments are clearly labeled.
- Metrics are linked to actual predictions and reference labels.
- Limitations are clearly explained.

## Presentation quality

- Professional landing page.
- Beautiful research dashboard.
- Functional synchronized replay.
- Clear model comparison interface.
- Meaningful evaluation charts.
- Readable technical documentation.
- Working demo access.
- Responsive user interface.

## Deployment readiness

- Environment variables documented.
- Production build succeeds.
- Container configuration exists.
- Database migrations documented.
- File storage strategy is defined.
- Security risks have been reviewed.
- Deployment instructions are available.
- No deployment has been performed without authorization.

---

# PART E - AUTONOMOUS WORKING PRINCIPLES

During each authorized stage:

1. Work independently on tasks within that stage.
2. Make routine technical decisions without asking for confirmation.
3. Inspect existing code before modifying it.
4. Build incrementally.
5. Run relevant checks throughout implementation.
6. Debug failures rather than ignoring them.
7. Document assumptions and limitations.
8. Preserve stable checkpoints.
9. Avoid fabricated results.
10. Keep the application coherent.
11. Prioritize functioning engineering over unnecessary complexity.
12. Respect the boundary of the currently authorized stage.

If you encounter an environmental blocker:

- Attempt reasonable troubleshooting.
- Document the issue.
- Complete independent tasks that remain possible.
- Report what could not be verified.

Do not claim a blocked feature is working.

If a stage is too large to finish within one execution:

- Preserve completed work.
- Update PROJECT_STATUS.md.
- Describe exactly what remains.
- Stop safely if necessary.
- Resume the same stage when the user instructs you to continue.

Do not mark that stage complete until its acceptance criteria have been reasonably assessed.

Do not advance to the next stage merely because execution time is limited.

---

# PART F - FINAL USER HANDOFF REQUIREMENTS

At every mandatory stopping point, provide an informative completion report.

The report must contain:

**1. What was built or reviewed**

Describe the actual work completed.

**2. Important technical decisions**

Explain meaningful choices and tradeoffs.

**3. Verification**

Show the commands executed and relevant results.

**4. Problems encountered**

Include errors, blockers, and unresolved issues.

**5. Files changed**

Identify important files and modules.

**6. Local execution**

Give startup commands when applicable.

**7. Next stage**

Explain what the next authorized stage will accomplish.

**8. Completion status**

Clearly indicate whether the current stage is complete, partially complete, or blocked.

Never invent test results.

Never claim an application is production-ready without evidence.

---

# FINAL EXECUTION COMMAND

You have received the complete RallySense Lab project specification.

**BEGIN STEP 1 ONLY.**

Use the Step 1 instructions to design the architecture, validate the approach, and create the required planning documents.

Do not implement the full application yet.

Do not begin Step 2.

After Step 1 is complete, present your results and stop with the exact message:

**STEP 1 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 2.**

Wait for the user's next instruction.
