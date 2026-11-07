# RALLYSENSE LAB - STEP 4 MASTER EXECUTION PROMPT
## Flagship Product Completion, Real-World Capture, Premium UX, Reliability, and Deployment Preparation

# AUTHORIZATION: STEP 4 ONLY

**CONTINUE TO STEP 4.**

You are now acting as a coordinated team of:

- Principal Full-Stack Engineer
- Senior Computer Vision Engineer
- Sensor Systems Engineer
- Senior Product Designer
- Frontend Performance Engineer
- Backend and Infrastructure Engineer
- QA Automation Lead
- Applied ML Product Engineer

Your mission is to transform RallySense Lab from a technically functioning research platform into an exceptionally polished, reliable, and professionally presented AI sports intelligence application.

This is not a routine cleanup stage.

**The goal is to produce a product that looks, behaves, and performs like a serious early-stage sports technology platform, supported by a scientifically rigorous research backend.**

You must implement working software, not merely propose changes.

Work autonomously within the authorized scope, inspect the existing implementation, resolve routine engineering problems, run meaningful tests, and deliver a fully documented handoff.

**Do not stop after planning. Do not begin Step 5. Do not deploy or publish anything.**

---

# 1. PROJECT BACKGROUND

RallySense Lab is an AI-powered tennis movement analysis and experimentation platform.

It investigates how much useful information about human movement can be inferred from limited inertial sensor observations and video-derived pose estimates.

The system is inspired by the engineering challenges of FramePoint, a sports intelligence initiative at Opus 133.

Its central research question is:

**What useful tennis movement information can be inferred from sparse sensor observations, how accurately can those inferences be evaluated, and what happens when observations become unreliable?**

The application should showcase engineering across:

- Computer vision
- Human pose estimation
- Inertial sensor processing
- Time-series analysis
- Multimodal sensor fusion
- Data collection and synchronization
- Experimental evaluation
- Full-stack software engineering
- Real-time-capable data capture
- Interactive visualization
- Reproducible experiments

The finished product must demonstrate both AI research engineering and professional software systems development.

---

# 2. EXISTING IMPLEMENTATION - DO NOT REBUILD

Steps 1, 2, and 3 have been completed.

The latest Step 3 checkpoint is:

`3ec36d8`

The application runs locally through Docker Compose at:

`http://127.0.0.1:3000`

The existing platform includes:

- Next.js / React / TypeScript frontend
- FastAPI backend
- PostgreSQL database
- Durable processing worker
- Video upload and validation
- MediaPipe Pose Landmarker integration
- Timestamped pose storage
- Accelerometer/gyroscope CSV ingestion
- Signal preprocessing and normalization
- Gyroscope-based motion-event inference
- Video wrist-speed inference
- Multimodal temporal association
- Immutable synchronization revisions
- Synchronized movement replay
- Manual annotations
- Frozen reference snapshots
- Reproducible experiment manifests
- Event-level evaluation metrics
- Sensor Fusion Challenge
- Robustness and corruption experiments
- Markdown/JSON report exports
- Synthetic paired research fixtures
- Extensive automated testing

Step 3 reportedly verified:

- 36 backend tests passing
- 9 frontend tests passing
- 5 production browser tests passing
- Production builds passing
- Type checking and linting passing
- Database migration consistency
- Original Step 2 data preserved

Treat these as previous reported results, not a substitute for current verification.

Preserve the existing functional architecture, database records, research methods, and application workflows.

Do not replace sophisticated working systems with simpler superficial implementations.

---

# 3. PRE-IMPLEMENTATION REVIEW

Before implementing Step 4, inspect:

- `docs/PROJECT_STATUS.md`
- `docs/STEP3_REPORT.md`
- `docs/RESEARCH.md`
- `docs/EXPERIMENTS.md`
- `docs/RESEARCH_DESIGN.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/IMPLEMENTATION_PLAN.md`
- Existing tests
- Current application screens
- Frontend and backend source code
- Docker and build configurations

Inspect Git status and preserve existing work.

Run the currently available baseline tests.

Identify:

1. Functionality already complete
2. Usability weaknesses
3. Performance limitations
4. Missing recording workflows
5. Data-quality risks
6. UI and visual inconsistencies
7. Scientific presentation weaknesses
8. Reliability and security limitations

Create a prioritized internal implementation checklist.

Then proceed directly with implementation.

Do not stop to ask for approval of routine decisions.

---

# 4. FLAGSHIP PRODUCT DESIGN

This is one of the most important Step 4 deliverables.

The existing RallySense Lab interface already uses a refined dark visual theme.

Preserve that identity and elevate it.

The final application should feel like a premium sports research product, not a generic SaaS template.

## Visual requirements

Use:

- Deep charcoal backgrounds
- Carefully restrained green/teal accents
- Clear scientific typography
- Professional data visualization
- Consistent spacing
- Purposeful micro-interactions
- Carefully designed controls
- Subtle motion and transitions
- Strong information hierarchy
- Excellent responsive layouts
- Accessible contrast and keyboard support

Avoid:

- Excessive glowing effects
- Unnecessary gradients
- Decorative visual clutter
- Generic AI-generated dashboard layouts
- Fake statistics
- Irrelevant animations
- Huge empty panels
- Inconsistent navigation
- Nonfunctional controls

The interface should communicate engineering precision, trust, and sophistication.

## Design process

Review every major screen at representative desktop, tablet, and mobile sizes.

Use browser automation and actual screenshots where available.

Inspect and fix:

- Overflow
- Truncated labels
- Inconsistent spacing
- Poor visual hierarchy
- Awkward panel proportions
- Difficult-to-read graphs
- Confusing controls
- Inaccessible interactions
- Loading and empty states

Use screenshots of actual rendered application states as verification evidence.

Do not merely assert that the UI looks professional.

---

# 5. BUILD AN EXCEPTIONAL FIRST-TIME DEMONSTRATION

A recruiter or engineer should understand the platform within one minute of opening it.

Create a carefully designed demonstration experience.

## Landing page

Improve the existing landing page while preserving its successful visual identity.

The page should communicate:

- What RallySense Lab investigates
- Why sparse motion sensing is difficult
- How video and inertial data work together
- What the application can actually demonstrate
- Why experimental validation matters

Include clear actions to:

- Explore the demonstration
- Open the research workspace
- Understand the methodology

Avoid overstating scientific capabilities.

## Guided demo mode

Implement a guided but nonintrusive demonstration experience.

A new visitor should be able to:

1. Open a sample movement session.
2. See synchronized movement replay.
3. Inspect actual sensor signals.
4. Run an inference baseline.
5. Compare video and inertial outputs.
6. Introduce missing observations or synchronization errors.
7. See how results change.
8. Inspect the underlying experiment methodology.

Add contextual explanations where useful.

The user must be able to dismiss guidance and navigate independently.

Do not build a scripted animation that pretends to execute models.

All displayed experiment results must come from the existing computation system.

## Synthetic demonstration transparency

The built-in demonstration must remain clearly labeled synthetic.

The demo should still be visually engaging and scientifically informative.

Do not present synthetic measurements as recorded athletic performance.

---

# 6. BUILD A PREMIUM MOVEMENT REPLAY STUDIO

The synchronized replay studio should become one of the most visually impressive components of the application.

The system should present video and sensor data like a professional motion-analysis workstation.

## Required features

Improve and verify:

- Video playback
- Pose skeleton overlay
- Acceleration visualization
- Gyroscope visualization
- Prediction markers
- Reference event markers
- Synchronized time cursor
- Timeline scrubbing
- Variable playback speed
- Event seeking
- Manual annotation
- Synchronization-offset controls
- Missing-data visualization
- Session metadata display

## Advanced replay improvements

Where practical, implement:

- Frame-by-frame navigation
- Precise event-centered replay
- Adjustable playback windows
- Zoomable time-series graphs
- Better high-density signal rendering
- Toggleable pose landmarks
- Toggleable detected events
- Clear reference-versus-prediction visual styling
- Keyboard shortcuts
- Event-detail inspection
- Persistent user view preferences within the session

Ensure all interactions remain tied to the actual session clock.

A user clicking a specific detected event must navigate to the correct timestamp.

## Alignment quality

Make it easy to inspect:

- Video time
- Sensor time
- Applied synchronization offset
- Current alignment revision
- Pairing evidence
- Potential timing uncertainty

Do not imply that a manually selected offset automatically corrects clock drift.

---

# 7. MAKE REAL-WORLD DATA COLLECTION PRACTICAL

This is a major priority.

The project currently demonstrates software correctness using synthetic fixtures.

We now need a practical workflow that can support real tennis-style recordings.

**Implement the complete software collection workflow, while acknowledging that actual physical recording requires the user or another participant.**

## A. Smartphone motion capture

Build or complete a mobile-friendly browser capture interface.

Where supported, allow users to:

- Request motion permissions
- Read accelerometer values
- Read gyroscope values
- Start recording
- Stop recording
- Observe live signal activity
- View recording duration
- Inspect sample count
- Estimate sampling frequency
- Detect missing channels
- Export sensor data
- Save recordings into the application

Handle differences between browser sensor APIs and native device capabilities.

Carefully distinguish:

- Acceleration including gravity
- Linear acceleration
- Rotation-rate measurements
- Orientation estimates
- Raw device coordinates

Do not silently substitute one quantity for another.

## B. Device compatibility

Investigate support for:

- Android Chrome
- iOS Safari
- Desktop browsers without sensors

Handle:

- Missing sensor APIs
- Denied permissions
- Insecure contexts
- Background-tab throttling
- Screen locking
- Interrupted recordings
- Missing measurement channels
- Unsupported sampling rates

Where full browser capture is unavailable, clearly guide users to supported CSV-based recording methods such as phyphox.

Use browser feature detection rather than assuming all smartphones work identically.

**Do not claim physical-device testing unless a physical device was actually used.**

## C. Secure local access

The existing application is designed for loopback access.

A phone on the same Wi-Fi network cannot simply use the computer's `127.0.0.1` address.

Investigate a safe local development workflow for testing the capture interface on a phone.

Document HTTPS and browser-permission requirements.

If practical, provide an opt-in development configuration using local trusted certificates and explicit LAN binding.

Do not weaken the default loopback security posture.

Do not expose the application or development credentials publicly.

## D. Recording metadata

Capture or request:

- Device model
- Sensor source
- Device placement
- Handedness
- Recording start time
- Timestamp basis
- Sensor-axis information
- Sampling characteristics
- Session notes
- Recording conditions

Unknown values must remain explicitly unknown.

Do not invent calibration data.

---

# 8. DESIGN A GUIDED PAIRED-RECORDING WORKFLOW

Build a dedicated workflow for capturing synchronized video and inertial measurements.

This is important because the platform's core research requires actual paired observations.

## Recording workflow

Guide the user through:

1. Creating a new participant/session identifier.
2. Selecting the movement to record.
3. Specifying camera placement.
4. Recording the sensor attachment location.
5. Capturing smartphone IMU measurements.
6. Capturing video.
7. Recording visible synchronization cues.
8. Importing or saving both sources.
9. Inspecting data quality.
10. Aligning recordings.
11. Confirming pairing evidence.
12. Saving the prepared session for inference.

## Safety

Never recommend swinging a racket while loosely holding a phone or using an insecure attachment.

Use conservative recording instructions.

For an initial pilot, support safe controlled shadow movements with a securely mounted sensor.

Do not confuse arm-mounted, pocket-mounted, torso-mounted, and racket-mounted measurements.

Their mechanical relationships differ.

## Synchronization

The existing system supports manual offset alignment.

Improve the workflow for documenting synchronization evidence.

If feasible, implement optional assisted synchronization using explicitly identifiable cues.

However:

- Do not assume two independent device clocks are synchronized.
- Do not optimize alignment against model predictions and then treat it as independent evidence of accuracy.
- Do not claim automatic drift compensation without validated implementation.
- Preserve manually entered alignment evidence.

Support start and end synchronization cues when useful for detecting possible drift.

If drift correction is implemented, document the model and uncertainty, and test it against known-clock fixtures.

Otherwise provide an explicit drift warning and manual inspection workflow.

---

# 9. IMPROVE COMPUTER VISION PROCESSING

Review the actual MediaPipe processing architecture.

Step 3 reported that a nominal 30 Hz extraction target achieved approximately 14.53 Hz on one real-video integration run, including a maximum sampled gap of 400 ms.

This is an important limitation for fast tennis movements.

Investigate whether the current browser playback-driven sampling can be improved.

## Objectives

- Improve frame sampling consistency where feasible.
- Preserve actual presentation timestamps.
- Avoid fabricating unobserved frames.
- Reduce unnecessary main-thread work.
- Keep pose extraction responsive.
- Avoid redundant extraction of unchanged assets.
- Record achieved rather than merely requested processing cadence.
- Provide clear warnings for insufficient temporal coverage.

Consider approaches such as:

- More reliable frame scheduling
- Efficient frame decoding
- Worker-based processing
- Frame extraction from supported decoded media
- Optional deterministic offline processing

Choose based on compatibility and actual verification.

Do not introduce a fragile new pipeline simply to advertise a higher frame rate.

Preserve the existing functioning MediaPipe worker and fallback behavior unless a replacement is demonstrably better.

## Pose quality

Improve presentation of:

- Landmark visibility
- Detection coverage
- Missing joints
- Large timestamp gaps
- Extractor/runtime metadata
- Source video properties
- Confidence-related observations

Do not describe monocular pose landmarks as calibrated biomechanical ground truth.

---

# 10. ELEVATE THE SENSOR FUSION CHALLENGE

The Sensor Fusion Challenge was implemented in Step 3.

Now turn it into an outstanding technical demonstration.

The experience must clearly communicate:

**What can the sensor observe? What can the algorithm infer? What remains uncertain?**

## Improve the three-mode comparison

Modes:

- IMU only
- Video only
- Multimodal fusion

For each method, present:

- Input observations
- Algorithm name and version
- Prediction definition
- Detected events
- Timing
- Data quality
- Evaluation eligibility
- Measured error when independent references exist
- Failure cases

Make it obvious which modality contributed to each prediction.

## Standout interaction: What happens when observations fail?

Create an intuitive research experience where the user can modify an experiment by introducing:

- Missing sensor samples
- IMU measurement noise
- Wrist occlusion
- Sampling irregularity
- Synchronization error

Then display actual changes in prediction and evaluation.

Use the existing reproducible experiment system.

Do not invent improved or degraded metrics.

## Experiment comparison

Allow a visitor to compare up to three runs with clear visual hierarchy.

Highlight:

- Events recovered
- Events missed
- Incorrect detections
- Timing disagreements
- Changes in coverage
- Processing latency
- Changes in methodology

Warn when comparisons use different reference definitions, alignment revisions, or evaluation protocols.

Make it clear that differences across incompatible configurations cannot establish an algorithmic performance improvement.

## Insight explanations

Implement concise explanations generated from stored experiment results.

For example:

- A detected event disappeared after wrist observations were removed.
- Two previously associated events no longer meet the association tolerance.
- Insufficient reference labels prevent accuracy evaluation.
- Sensor coverage is inadequate for the chosen interval.

These explanations must be computed from actual run differences, not fabricated by a chatbot.

Avoid making an external LLM API a dependency.

---

# 11. BUILD AN EXCELLENT FAILURE-CASE EXPLORER

A strong research platform should make incorrect or missing predictions easy to investigate.

Implement or improve a dedicated event and failure inspection experience.

Users should be able to inspect:

- Correctly matched events
- Unmatched predictions
- Missed references
- Large timing disagreements
- Missing sensor coverage
- Pose landmark occlusion
- Invalid or incomplete experiments

Clicking a failure should open the corresponding replay time window when data is available.

Show the relevant modality signals and event information.

Explain why the system classified the event as matched, unmatched, or unavailable.

Do not assign causal explanations that the observed data cannot establish.

Distinguish confirmed algorithmic conditions from possible hypotheses.

---

# 12. BUILD A RESEARCH-GRADE REPORTING EXPERIENCE

The existing Markdown and JSON exports are functional.

Improve the report presentation.

Each experiment report should clearly explain:

- Research question
- Recording provenance
- Data type
- Recording conditions
- Sensor placement
- Video processing configuration
- Inference algorithms
- Synchronization revision
- Evaluation method
- Reference annotations
- Results
- Timing errors
- Quality limitations
- Failure cases
- Reproduction steps

## Research dashboard

Provide professional:

- Event timeline visualizations
- Algorithm comparison charts
- Quality indicators
- Timing-error tables
- Per-event inspection
- Experiment history
- Reproducibility metadata

Avoid unnecessary visualizations that do not convey meaningful scientific information.

## Export

Retain Markdown/JSON.

Add a professional, print-friendly experiment summary or PDF export if this can be implemented reliably.

If PDF export would introduce disproportionate complexity, provide a polished print stylesheet and browser print workflow.

Do not allow report generation to block the main application.

---

# 13. IMPROVE DATA COLLECTION AND LABELING QUALITY

Refine annotation workflows.

Support:

- Clear operational definitions
- Manual event placement
- Timestamp editing
- Label-set selection
- Human versus generated labels
- Blinded labeling
- Frozen reference revisions
- Notes for ambiguous events
- Visible label provenance

Where practical, improve workflows for independent labelers and adjudication.

Do not merge annotations automatically and call the result objective ground truth.

Document disagreements and uncertainty.

Make it easy to distinguish:

- Raw measurements
- Video-derived estimates
- Algorithm predictions
- Human references
- Synthetic generated references

---

# 14. PRODUCTION-QUALITY BACKEND ENGINEERING

Inspect and improve backend reliability.

Areas to evaluate:

- Request validation
- Database transactions
- Data consistency
- File ownership
- Storage cleanup
- Upload bounds
- Processing job states
- Job cancellation
- Retry behavior
- Idempotency
- Failure visibility
- API documentation
- Structured logging
- Resource usage

The application already includes durable jobs and lease handling.

Preserve these mechanisms.

Improve user-facing error recovery where appropriate.

For example, a failed import should present a meaningful error and a clear recovery path.

Do not implement unsafe automatic retries for non-idempotent operations.

## Large-data handling

Review:

- Sensor-series query sizes
- Large Parquet artifacts
- Replay response limits
- Pose-track pagination/windowing
- Chart downsampling
- Experiment history limits
- Database index usage

Step 3 identified a replay pose-response cap that could omit late overlays for long tracks.

Consider implementing windowed replay fetching or another appropriate solution if feasible.

Profile first.

Avoid premature architectural complexity.

---

# 15. PERFORMANCE OPTIMIZATION

Measure actual bottlenecks before optimizing.

Evaluate:

- Frontend page loading
- Replay scrubbing
- Signal visualization
- Video frame processing
- Sensor CSV processing
- API response times
- Processing job execution
- Experiment comparisons
- Large session behavior

Implement performance improvements where useful.

Potential approaches:

- Chart windowing
- Largest-triangle or min/max-preserving visualization downsampling
- Memoization
- Batched API requests
- Artifact reuse
- Avoiding unnecessary rerenders
- Lazy-loaded heavyweight components
- Efficient pose-data retrieval

Do not remove scientifically meaningful peaks during chart downsampling.

Do not claim production throughput based on synthetic eight-second fixtures.

Record the conditions under which performance measurements were obtained.

---

# 16. ADD A PROFESSIONAL SYSTEM HEALTH EXPERIENCE

The application should be easy to inspect and troubleshoot.

Implement a suitable developer-facing diagnostics area or diagnostic workflow.

Show or make accessible:

- API readiness
- Worker readiness
- Database connectivity
- Processing job status
- Failed jobs
- Data-processing errors
- Environment mode
- Version/build identity
- Relevant runtime capability information

Do not expose credentials, database connection strings, private paths, or sensitive configuration values.

The health interface should distinguish real checks from unknown status.

---

# 17. SECURITY AND PRIVACY HARDENING

Prepare for a future public demonstration without deploying it yet.

The current application is designed for local single-user access.

Review:

- File upload validation
- Maximum request sizes
- Storage path safety
- Session ownership
- Deletion behavior
- API authentication assumptions
- Cross-origin rules
- Rate limits
- Resource exhaustion
- Public-demo isolation
- Browser security
- Sensitive data retention

## Public demo mode

Design and, where practical, implement a safe read-only demonstration mode.

In public-demo mode:

- Visitors may explore preloaded demonstration sessions.
- Visitors must not be able to delete shared demonstration artifacts.
- Visitors must not access private local recordings.
- Public mutation operations must be disabled unless separately isolated and secured.
- Internal service credentials must never be exposed.

If interactive experiments require mutation, consider an isolated disposable session model or precomputed, transparently identified experiment results with live read-only inspection.

Do not claim that a single-user local token provides multiuser security.

Document remaining barriers before public deployment.

---

# 18. PREPARE THE PROJECT FOR DEPLOYMENT

Do not deploy during Step 4.

Prepare a credible deployment architecture.

Evaluate the existing requirements and recommend an appropriate hosting approach.

Potential architecture:

- Vercel for Next.js
- Container hosting for FastAPI and the worker
- Managed PostgreSQL
- Private S3-compatible artifact storage

An AWS-based deployment is also acceptable if justified.

Compare options based on:

- Simplicity
- Reliability
- Video storage requirements
- CPU-intensive processing
- Worker lifecycle
- Database persistence
- Cost
- Security
- Ease of maintaining a recruiting demonstration

Do not assume serverless functions are suitable for long-running CPU video-processing tasks.

Provide production-ready configurations where feasible:

- Dockerfiles
- Environment variable templates
- Health checks
- Database migration procedures
- Storage settings
- Secret management guidance
- Logging configuration
- Safe backup strategy
- Public-demo access design

Do not provision cloud services.

Do not use paid APIs.

Do not push to a public GitHub repository.

Deployment remains subject to the Step 5 independent audit and human approval.

---

# 19. COMPREHENSIVE QUALITY ASSURANCE

Testing is mandatory.

Do not rely only on the previous Step 3 test report.

## Backend

Run existing tests and add relevant coverage for:

- New capture and import workflows
- Recording metadata
- File safety
- Session lifecycle
- Alignment state
- New processing logic
- Data validation
- Error handling
- Job recovery
- Export
- Public-demo restrictions
- Database migration preservation

## Frontend

Test:

- Navigation
- Recording permission states
- Unsupported devices
- Capture states
- Upload workflows
- Replay controls
- Timeline navigation
- Failure inspection
- Experiment comparison
- Report exports
- Responsive behavior
- Accessible controls

## End-to-end browser testing

Verify real browser workflows:

1. Landing page to demo.
2. Open synthetic paired lab.
3. Run inference.
4. Compare algorithms.
5. Introduce a controlled failure.
6. Inspect the changed results.
7. Navigate from prediction to replay.
8. Annotate a session.
9. Export results.
10. Import and process a valid recording.

Test negative and error cases.

Use actual backend processing rather than mocking successful responses.

## Real-video verification

Where a valid, permitted sample video exists, verify actual MediaPipe processing, video playback, pose overlay, and stored-pose inference.

Do not equate an unrelated demo video with validated tennis performance.

## Mobile verification

Use responsive browser emulation for layout testing.

Test actual motion capture on physical devices only when the hardware is available.

Record what was and was not physically verified.

## Build verification

Run:

- Backend tests
- Frontend tests
- TypeScript checks
- Lint checks
- API contract checks
- Migration checks
- Production builds
- Playwright tests
- Container startup checks
- Local smoke tests

Record exact outcomes.

---

# 20. DELIVER A COMPLETE REAL-DATA COLLECTION PLAYBOOK

Create:

`docs/REAL_WORLD_PILOT.md`

This should provide a realistic, safe protocol for collecting a small tennis movement research dataset.

Include:

- Equipment requirements
- Safe phone placement
- Camera setup
- Supported movement types
- Device metadata
- Sensor coordinate conventions
- Recording duration
- Start/end synchronization cues
- Negative examples
- Repeated sessions
- Rest intervals
- Import instructions
- Annotation procedure
- Evaluation procedure
- Known limitations

Design for a small controlled pilot rather than claiming a professional motion-capture experiment.

Include an operator-friendly checklist for collecting one usable paired session.

Clearly distinguish prerequisites requiring physical participation.

Do not claim collection has occurred.

---

# 21. FINAL DOCUMENTATION

Update or create:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/RESEARCH.md`
- `docs/EXPERIMENTS.md`
- `docs/RESEARCH_DESIGN.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_STATUS.md`
- `docs/API.md`
- `docs/TESTING.md`
- `docs/LOCAL_DEVELOPMENT.md`
- `docs/DATA_COLLECTION.md`
- `docs/REAL_WORLD_PILOT.md`
- `docs/DEPLOYMENT.md`
- `docs/PROJECT_HANDOFF.md`
- `docs/INTERVIEW_WALKTHROUGH.md`
- `docs/STEP4_REPORT.md`

The interview walkthrough should explain:

- The engineering problem
- The platform architecture
- Why the system uses sparse sensors
- How the IMU baseline works
- How pose-based inference works
- How multimodal association works
- How synchronization is handled
- How evaluation metrics are computed
- What the robustness experiments demonstrate
- What the system cannot yet infer
- What would be required for real-world validation
- What architectural decisions make the software extensible

Use accurate descriptions of implemented features.

Do not describe the association baseline as a trained biomechanical reconstruction model.

Do not fabricate research results.

---

# 22. OPTIONAL HIGH-IMPACT ENHANCEMENTS

Only consider the following after the core Step 4 requirements work.

Choose enhancements based on actual product value, not novelty alone.

## A. Intelligent experiment insights

Generate data-grounded comparisons between experiments.

Explain improvements and failures using actual stored results.

No external LLM is required.

## B. Racket-motion visualization

Where sufficient measured orientation information exists, render an appropriately labeled representation of equipment motion.

If orientation cannot be recovered reliably, do not invent a physically accurate racket trajectory.

## C. Live sensor visualization

Where the device supports motion capture, show actual incoming measurements in a responsive live dashboard.

Clearly distinguish live capture from offline inference.

## D. Side-by-side replay

Allow a user to compare two recording sessions or experiments using synchronized timelines when meaningful alignment exists.

Avoid implying biomechanical comparability between recordings without calibration.

## E. Session sharing preparation

Design an exportable analysis package or safe future share mechanism.

Do not implement unauthenticated public access to private recordings.

## F. Interactive research methodology

Create elegant explanations of the algorithms and their limitations using real configuration information.

These enhancements are optional.

Do not sacrifice core correctness to implement them.

---

# 23. IMPLEMENTATION ORDER

Work in this order.

## Phase 4A - Baseline inspection

- Inspect current repository
- Run baseline tests
- Identify defects and unfinished workflows
- Preserve stable checkpoint

## Phase 4B - Real-world recording readiness

- Build smartphone capture interface
- Implement device capability handling
- Improve paired recording workflow
- Improve synchronization guidance
- Add metadata and data-quality checks

## Phase 4C - Core analytical experience

- Improve replay
- Improve Sensor Fusion Challenge
- Add failure-case exploration
- Improve experiment comparison
- Improve scientific explanations

## Phase 4D - Computer vision and performance

- Investigate pose sampling
- Improve processing consistency where feasible
- Improve quality reporting
- Optimize replay and large-data handling

## Phase 4E - Product polish

- Upgrade visual design
- Improve navigation
- Refine responsiveness
- Improve onboarding
- Add professional empty/loading/error states

## Phase 4F - Reliability and readiness

- Backend hardening
- Public-demo safety design
- Deployment-ready configurations
- Documentation
- End-to-end verification

## Phase 4G - Final evidence

- Capture actual screenshots
- Record verified workflows
- Complete test reports
- Update project documentation
- Prepare final handoff

Work autonomously through these phases.

Do not stop after an internal subphase unless blocked by something that genuinely requires human input.

---

# 24. SUCCESS CRITERIA

Step 4 is complete when the following are substantially satisfied.

## Product

- The application runs locally.
- The landing page is professionally designed.
- The demonstration is easy to explore.
- The research dashboard is intuitive.
- Replay interactions are reliable.
- Sensor Fusion Challenge is fully integrated.
- Experimental failures can be inspected.
- Reports reflect genuine stored results.
- Mobile layouts work appropriately.

## Real-world readiness

- Smartphone capture works on supported APIs or provides a clear fallback.
- CSV ingestion remains functional.
- Paired data collection is documented and supported by the UI.
- Synchronization evidence can be recorded.
- Device limitations are communicated.
- Real recordings can enter the existing inference pipeline.

## Engineering

- Existing backend architecture remains stable.
- Existing experiments and sessions are preserved.
- Critical algorithms retain their scientific meaning.
- Tests pass or any failures are explained.
- Major performance bottlenecks have been investigated.
- The application handles errors gracefully.
- Important security limitations are documented.

## Presentation

- The demonstration is visually excellent.
- Core interactions genuinely work.
- Scientific results are clearly labeled.
- Synthetic data is never misrepresented.
- The project is understandable without extensive explanation.
- A technical reviewer can inspect its architecture and research methodology.

## Deployment preparation

- Production configurations are documented.
- A deployment architecture is recommended.
- Public-demo access risks are addressed.
- No deployment has occurred.

---

# 25. FINAL VERIFICATION REQUIREMENTS

Before declaring completion:

1. Run the full backend test suite.
2. Run the frontend unit tests.
3. Run strict TypeScript checking.
4. Run linting.
5. Verify API contract consistency.
6. Verify database migrations.
7. Build production images.
8. Run production-mode browser tests.
9. Verify actual replay and inference flows.
10. Verify synthetic fixture transparency.
11. Verify session persistence.
12. Verify that existing Step 3 results remain intact.
13. Inspect desktop and mobile screenshots.
14. Perform a local application smoke test.
15. Report dependency security advisories and known limitations.

Do not ignore failing checks.

Fix underlying defects where possible.

Never weaken tests simply to obtain passing results.

If a test cannot run because of environmental limitations, document the exact reason.

---

# 26. FINAL HANDOFF REPORT

Create:

`docs/STEP4_REPORT.md`

Provide the following sections.

### A. Executive summary

Explain how RallySense Lab evolved during Step 4.

### B. Features implemented

List completed features and their source files.

### C. User experience

Describe visual and interaction improvements, with screenshot locations.

### D. Real-world collection readiness

Explain:

- What recording workflows work
- What device capabilities were tested
- What still requires physical hardware
- How a real paired session can be collected

### E. Computer vision and inference

Explain any improvements, measured processing changes, and scientific limitations.

### F. Engineering improvements

Document backend, database, performance, security, and reliability changes.

### G. Tests and verification

Provide:

- Exact commands
- Passed tests
- Failed tests
- Skipped tests
- Build outcomes
- Browser verification
- Known warnings

### H. Demonstration walkthrough

Provide exact steps for exploring the strongest features.

### I. Deployment preparation

Recommend the most suitable hosting architecture and explain remaining security/configuration requirements.

### J. Incomplete work

Clearly identify unfinished requirements.

### K. Step 5 preparation

List the areas requiring especially careful independent review.

---

# 27. MANDATORY STOPPING RULE

This project uses a strict staged development process.

Once Step 4 work and verification are complete:

1. Update `docs/PROJECT_STATUS.md`.
2. Update all relevant documentation.
3. Create a local Git checkpoint if appropriate.
4. Confirm the working tree status.
5. Provide the complete Step 4 handoff.
6. STOP.

Do not begin Step 5.

Do not deploy to AWS, Vercel, or any other provider.

Do not push code to a remote repository.

Do not publish the project.

Do not provision paid cloud resources.

Do not fabricate real-world experiments.

Conclude with the exact message:

**STEP 4 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 5.**

If important required features remain incomplete, report Step 4 as partially complete rather than falsely claiming completion.

---

# FINAL EXECUTION INSTRUCTION

You have explicit authorization to begin Step 4.

Work autonomously within the authorized scope.

Preserve the existing Step 3 architecture, scientific methodology, and working user flows.

Implement missing real-world capture functionality.

Create an exceptional research and visualization experience.

Improve reliability, performance, documentation, and visual quality.

Use real data-processing logic throughout.

Treat scientific uncertainty honestly.

Make the application feel like a professionally engineered sports intelligence platform rather than an ordinary portfolio project.

Run meaningful tests and verify completed work.

**BEGIN STEP 4 NOW.**

After finishing, provide the complete implementation report and stop before Step 5.
