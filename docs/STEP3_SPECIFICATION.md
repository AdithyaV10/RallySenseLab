# RALLYSENSE LAB - STEP 3 EXECUTION PROMPT
## Advanced Motion Inference, Sensor Fusion, and Scientific Evaluation

**AUTHORIZED STAGE: STEP 3 ONLY**

CONTINUE TO STEP 3.

You are now acting as a Principal Computer Vision Engineer, Sensor Fusion Research Scientist, Applied Machine Learning Engineer, and Senior Full-Stack Engineer.

Your task is to transform the existing RallySense Lab MVP into a technically sophisticated, scientifically credible tennis motion-inference research platform.

This is the most intellectually demanding stage of the project.

**You must autonomously implement, integrate, debug, test, and verify all Step 3 requirements before stopping.**

Do not merely provide an implementation plan.

Do not rebuild the application from scratch.

Do not begin Step 4.

Do not deploy anything.

---

# 1. PROJECT CONTEXT

RallySense Lab is an AI-powered sports movement intelligence platform inspired by the engineering challenges of FramePoint at Opus 133.

The goal is to investigate how much information about tennis movement can be inferred from sparse observations, particularly inertial sensor measurements, with video-based observations providing an additional modality and reference.

The application must demonstrate capabilities relevant to:

**FP01 - AI and Motion Inference Engineering**
- Computer vision
- Human pose estimation
- Time-series inference
- Inertial sensing
- Sensor fusion
- Coordinate frames
- Synchronization
- Generalization and uncertainty
- Reproducible experimental evaluation

**FP04 - Software and Data Systems Engineering**
- Sensor ingestion
- Data quality
- Versioned recordings
- Synchronized replay
- Model integration
- Experimental infrastructure
- Latency measurement
- Reliable software interfaces

Our goal is to produce an impressive working research application, not an artificially sophisticated AI dashboard.

---

# 2. EXISTING STEP 2 IMPLEMENTATION

Step 2 is complete and must be preserved.

The existing application includes:

- Next.js 16.4.4 with React and TypeScript
- FastAPI backend
- PostgreSQL database
- SQLAlchemy and Alembic
- Docker Compose
- Worker-based processing
- Persistent recording sessions
- Video validation and storage
- Browser-based MediaPipe pose extraction
- Pose landmark persistence
- Accelerometer and gyroscope CSV ingestion
- SI unit normalization
- Signal filtering
- Gyroscope peak detection
- Immutable synchronization offset revisions
- Interactive replay timeline
- Skeleton overlays
- Sensor plots
- Event navigation
- Manual annotations
- Blinded annotation mode
- Explicitly labeled synthetic demonstration session
- API contracts and automated tests

The existing `gyro_peak_v1` algorithm identifies angular-speed peaks. These are not automatically confirmed tennis swing events or racket-ball impacts.

Step 2 reportedly passed:

- 17 backend tests
- 6 frontend tests
- 3 Playwright browser tests
- TypeScript checks
- Linting
- API contract checks
- Docker production builds
- Database migration checks

The user has also manually launched the application and confirmed that the landing page and synthetic replay load and render correctly.

Preserve these working capabilities.

---

# 3. REQUIRED PRE-IMPLEMENTATION AUDIT

Before writing new functionality, inspect the actual existing repository.

Read:

- `docs/PROJECT_STATUS.md`
- `docs/STEP2_REPORT.md`
- `docs/ARCHITECTURE.md`
- `docs/RESEARCH_DESIGN.md`
- `docs/INFERENCE_CONTRACTS.md`
- `docs/DECISIONS.md`
- `docs/IMPLEMENTATION_PLAN.md`
- Existing tests
- Existing database migrations
- Relevant frontend and backend source code

Also inspect the current replay and MediaPipe implementations.

Do not trust the Step 2 report blindly.

Verify what is implemented.

Check the working Git checkpoint and avoid destructive changes.

Create a concise internal execution plan, then begin implementation immediately.

Do not stop after planning.

---

# 4. SCIENTIFIC CORRECTNESS AUDIT

Carefully inspect the existing numerical pipeline.

Review:

1. Accelerometer and gyroscope unit conversions
2. Timestamp origin normalization
3. Sample-rate estimation
4. Missing samples
5. Filtering assumptions
6. Filter behavior near recording boundaries
7. Peak detection
8. Time-based event separation
9. Sensor coordinate-frame handling
10. Synchronization offset signs
11. Pose landmark visibility
12. Derived image-space features
13. Handling of pose gaps
14. Prediction timestamps

Correct invalid assumptions.

Preserve recorded raw observations.

Do not silently alter event definitions.

Explicitly document what each detector actually measures.

In particular:

**A peak in angular speed must not automatically be labeled a tennis swing apex or ball impact.**

Investigate whether the current event definitions are suitable for comparing different modalities.

Where event definitions differ, implement explicit matching or refuse unsupported comparisons.

---

# 5. BUILD REAL VIDEO-ONLY INFERENCE

Implement a genuine computer-vision-based movement-event baseline using actual MediaPipe pose tracks.

The inference engine must operate on stored pose landmarks and their presentation timestamps.

Potential features:

- Wrist trajectories
- Wrist movement speed
- Wrist movement acceleration
- Elbow-angle changes
- Shoulder movement features
- Torso-relative wrist displacement
- Temporal movement windows
- Landmark visibility and coverage
- Missing-frame conditions

Build a documented inference method.

Suggested identifier:

`video_motion_event_v1`

You may choose a better identifier based on the scientifically defensible event definition.

Requirements:

- Actual signal processing from pose data
- Deterministic configuration
- Timestamped predictions
- Quality information
- Reproducible results
- Clear missing-data handling
- No hardcoded predicted events
- No invented accuracy

The existing pose extraction targets approximately 10 Hz.

Fast tennis movements may occur between sampled frames.

Investigate this limitation.

Where justified, improve the extraction or event localization approach without destabilizing the existing system.

Do not claim exact impact timing from low-frequency pose landmarks.

Tests must verify feature computation and event detection against known fixtures.

---

# 6. IMPROVE IMU MOTION INFERENCE

Review and enhance the existing inertial baseline.

Investigate:

- Gyroscope magnitude
- Acceleration magnitude
- Filtering parameters
- Peak prominence
- Adaptive thresholds
- Movement window segmentation
- Event duration
- Motion intensity
- Signal noise
- Sampling irregularity
- Gap handling
- Motion-event confidence or quality
- Repeated movement patterns

Maintain `gyro_peak_v1` compatibility where needed.

If introducing a new algorithm, version it explicitly.

Potential outputs:

- Angular-speed peak timestamp
- Candidate movement window
- Peak rotational intensity
- Signal-quality information
- Detection strength
- Required sensor channels
- Detection limitations

Do not present detector strength as a calibrated probability unless it is genuinely calibrated.

Implement meaningful tests and document assumptions.

---

# 7. IMPLEMENT REAL MULTIMODAL SENSOR FUSION

This is a critical project requirement.

Build a genuine fusion method using synchronized inertial measurements and video-derived motion information.

The fusion method must operate on actual input signals or inference outputs from both modalities.

Possible approaches:

- Event-level temporal association
- Quality-aware event matching
- Joint movement-window estimation
- Feature-level fusion
- Weighted observation integration when justified

Select the approach that best fits the available data and the existing application architecture.

**Scientific constraints:**

1. Fusion must actually use information from both modalities.
2. Event definitions must be compatible.
3. Alignment must be explicit.
4. Missing or unreliable observations must be handled.
5. The method must not manufacture agreement.
6. Results must remain traceable to source data.
7. The model must not claim biomechanics reconstruction unsupported by the sensors.

Proposed identifier:

`multimodal_fusion_v1`

Document:

- Input features
- Algorithm
- Synchronization assumptions
- Parameter choices
- Output event definition
- Quality handling
- Failure cases
- Limitations

If insufficient meaningful cross-modal evidence exists, implement a defensible association baseline and identify it accurately rather than inventing an advanced trained fusion model.

---

# 8. BUILD THE SENSOR FUSION CHALLENGE

This should become the standout research feature of RallySense Lab.

Create a visually impressive and fully interactive comparison environment.

The user should be able to choose:

**Mode A - Video Only**

Uses visual pose-derived information.

**Mode B - IMU Only**

Uses accelerometer/gyroscope measurements.

**Mode C - Multimodal Fusion**

Uses aligned visual and inertial observations.

The interface should include:

- Inference mode selection
- Real processing status
- Prediction timelines
- Detected event markers
- Signal visualizations
- Algorithm configurations
- Data-quality indicators
- Event-level comparison
- Experiment results
- Failure-case inspection
- Model limitations

If appropriate, support displaying two or three inference methods side by side.

The results must come from actual algorithms.

Do not hardcode F1 scores or fabricate example performance.

If a session lacks a required modality, disable that experiment with a clear explanation.

If the data is synthetic, label it prominently.

The feature should be easy for a technical recruiter to understand without requiring extensive instructions.

---

# 9. IMPLEMENT VERSIONED HUMAN REFERENCE LABELS

The existing application supports editable human annotations and immutable synthetic reference markers.

Extend it to support reproducible evaluation.

Implement:

- Annotation-set creation
- Annotation-set versions
- Frozen reference snapshots
- Clear distinction between human and generated labels
- Event definition metadata
- Label provenance
- Evaluation eligibility
- Immutable references for completed experiments

Avoid treating generated prediction timestamps as independent labels.

When an annotation set changes, previous experiments must remain associated with the original frozen reference revision.

Preserve existing annotation workflows.

Test revision behavior and stale-edit handling.

---

# 10. BUILD RIGOROUS EVENT-LEVEL EVALUATION

Implement scientifically meaningful evaluation.

Required metrics:

- True positives
- False positives
- False negatives
- Precision
- Recall
- F1 score
- Absolute event-timing error
- Mean absolute timing error
- Median absolute timing error
- Per-event errors
- Per-session evaluation
- Inference latency

Use explicit event-matching rules.

Requirements:

1. Configurable timing tolerance
2. One-to-one prediction/reference matching
3. Deterministic tie handling
4. Appropriate handling of unmatched predictions
5. Appropriate handling of missed references
6. Explicit rules for empty prediction sets
7. Consistent timestamp coordinate systems
8. No duplicate reuse of one reference event
9. No unsupported metrics when ground truth is unavailable

Do not silently match fundamentally different event types.

Document the chosen matching algorithm and explain why it is appropriate.

Where useful, include a confusion matrix for supported categorical classification tasks, but do not create meaningless confusion matrices for timestamp-only event detection.

---

# 11. EXPERIMENT MANAGEMENT AND REPRODUCIBILITY

Build a proper experiment system.

Each experiment should preserve:

- Session ID
- Input asset identifiers
- Source modality
- Algorithm name
- Algorithm version
- Algorithm parameters
- Preprocessing settings
- Synchronization revision
- Reference annotation revision
- Execution timestamp
- Input data fingerprint or stable artifact identity
- Predictions
- Evaluation metrics
- Processing latency
- Failure information

Support rerunning experiments.

Preserve old experiment results.

Do not overwrite existing results simply because parameters change.

Use database migrations where necessary.

Create clear API contracts and frontend integration.

Provide a comparison interface for runs using different configurations.

Avoid unnecessary duplication of large sensor or pose datasets.

---

# 12. SCIENTIFIC FAILURE AND ROBUSTNESS EXPERIMENTS

Build controlled experiments that investigate how predictions change under degraded observations.

Include appropriate simulations of:

### A. Missing IMU samples
Remove a configurable portion of sensor observations.

### B. Sensor noise
Apply controlled perturbations to selected inertial channels.

### C. Irregular sampling
Investigate sensitivity to timestamp gaps and sampling irregularity.

### D. Landmark occlusion
Hide selected pose landmarks or time windows to simulate loss of visual observations.

### E. Incorrect synchronization
Introduce a controlled time offset to examine changes in fusion agreement.

Use deterministic random seeds where applicable.

Record the configuration of each corruption experiment.

Preserve the original recordings.

Do not mutate source measurements.

Do not present artificially degraded data as actual recorded sensor failures.

Allow comparison between clean and degraded experiment results.

Create professional visualizations showing how predictions and evaluation metrics change.

---

# 13. UNCERTAINTY AND QUALITY REPORTING

Implement scientifically grounded quality indicators.

Examples:

- Landmark visibility
- Pose detection coverage
- Sensor sample availability
- Sampling irregularity
- Missing time windows
- Alignment quality
- Event signal strength
- Cross-modal disagreement
- Prediction instability under perturbation

Distinguish:

- Signal quality
- Prediction strength
- Model confidence
- Empirical accuracy

These are not interchangeable.

Do not display arbitrary confidence percentages.

If probability calibration is unavailable, use descriptive quality labels or documented scores rather than pretending to output statistically calibrated confidence.

---

# 14. ADD A RESEARCH RESULTS DASHBOARD

Build a professional experiment evaluation interface.

Include:

- Experiment summary
- Input modalities
- Algorithm configurations
- Predictions and labels
- Event timing comparison
- Precision, recall, and F1 when supported
- Mean and median timing error
- False positives and missed events
- Signal-quality information
- Processing latency
- Experiment-to-experiment comparisons
- Known limitations

Design the page so that a technical interviewer can immediately understand what was tested and what the results mean.

Use clear explanations and tooltips.

A session with no independent reference labels must not display fabricated accuracy.

---

# 15. RESEARCH REPORT GENERATION

Implement exportable experiment summaries.

At minimum, support Markdown or JSON export.

PDF is optional if it can be added without disrupting the main development work.

Reports should include:

- Research question
- Dataset provenance
- Session characteristics
- Input modalities
- Algorithm versions
- Parameter configuration
- Synchronization method
- Reference labeling procedure
- Evaluation metrics
- Failure cases
- Processing latency
- Limitations
- Reproduction instructions

Generated reports must reflect actual stored results.

Do not produce hypothetical research findings disguised as measured observations.

---

# 16. API AND BACKEND REQUIREMENTS

Extend the existing FastAPI architecture.

Implement appropriate endpoints for:

- Running video inference
- Running fusion inference
- Creating experiments
- Listing experiment history
- Retrieving predictions
- Freezing annotation sets
- Running evaluation
- Retrieving metrics
- Comparing experiments
- Exporting reports

Use existing conventions where practical.

Ensure:

- Pydantic validation
- Typed responses
- Proper error codes
- Durable jobs where needed
- Safe failure handling
- Session ownership checks
- Immutable experiment references
- Database migration compatibility

Do not create an entirely separate backend.

Do not introduce unnecessary infrastructure.

---

# 17. FRONTEND INTEGRATION REQUIREMENTS

Integrate all advanced research features into the existing design system.

Preserve the dark, premium RallySense Lab visual identity.

Prioritize:

- Elegant layouts
- Readable scientific charts
- Consistent terminology
- Smooth interaction
- Meaningful loading states
- Clear failure messages
- Accessible controls
- Responsive layouts
- Correct timeline behavior

Make the Sensor Fusion Challenge and evaluation dashboard standout experiences.

However, prioritize genuine functionality over visual decoration.

Every significant control must execute a meaningful operation.

Do not replace real data visualizations with static illustrations.

---

# 18. REAL DATA AND SYNTHETIC DATA POLICY

The existing demonstration session is synthetic.

It contains approximately 1,801 sensor rows over 18 seconds.

Its generated references exist for deterministic software testing.

That is acceptable.

However:

- Do not claim synthetic F1 scores represent real-world tennis accuracy.
- Do not assume synthetic sensor pulses represent real racket dynamics.
- Do not claim the unrelated MediaPipe test video and synthetic IMU recording were physically synchronized.
- Do not report cross-player generalization without actual player-separated data.
- Do not claim precise racket impact timing without validated reference measurements.

If genuine paired tennis recordings are unavailable, implement the full processing and evaluation framework using labeled fixtures.

Clearly distinguish software verification from real-world experimental validity.

Prepare the application to accept real recordings without architectural changes.

---

# 19. TESTING AND VERIFICATION

Implement extensive tests for the new scientific and engineering functionality.

### Numerical tests

Verify:

- Video feature extraction
- Event detection
- Fusion
- Timestamp conversion
- Synchronization
- One-to-one event matching
- Precision and recall
- F1 score
- Timing errors
- Empty input cases
- Missing modalities
- Corrupted data
- Deterministic robustness experiments

### Backend integration tests

Verify:

- Database migrations
- Inference persistence
- Frozen reference versions
- Experiment immutability
- Rerun behavior
- API response correctness
- Failure handling

### Frontend tests

Verify:

- Inference mode selection
- Experiment execution
- Result rendering
- Missing-data states
- Synthetic-data labels
- Evaluation eligibility
- Experiment comparison

### End-to-end browser tests

Test:

1. Opening a demonstration session
2. Running IMU inference
3. Running video inference when actual pose input exists
4. Running fusion when suitable paired data exists
5. Creating/freezing annotations
6. Evaluating predictions
7. Inspecting comparisons
8. Navigating replay with prediction markers
9. Reviewing failure-case experiments

Tests must use meaningful input fixtures.

Do not mock successful analysis outcomes in integration or end-to-end tests.

Run all relevant existing tests to detect regressions.

Fix genuine failures rather than weakening assertions to obtain a passing test suite.

---

# 20. PERFORMANCE AND RELIABILITY

Maintain the existing application's responsiveness.

Measure relevant processing times.

Avoid unnecessary repeated pose extraction.

Cache or reuse valid derived artifacts when inputs and configurations are unchanged.

Handle:

- Missing inputs
- Failed jobs
- Interrupted processing
- Invalid algorithm parameters
- Unsynchronized data
- Insufficient sensor coverage
- Empty inference outputs

Ensure that experiments are traceable and do not corrupt original recordings.

---

# 21. DOCUMENTATION

Update:

- `docs/RESEARCH_DESIGN.md`
- `docs/INFERENCE_CONTRACTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/PROJECT_STATUS.md`
- `docs/TESTING.md`
- `docs/API.md`

Create:

- `docs/STEP3_REPORT.md`
- `docs/RESEARCH.md`
- `docs/EXPERIMENTS.md`

Document:

- Actual algorithms
- Mathematical definitions
- Parameter choices
- Event semantics
- Evaluation methodology
- Data limitations
- Model limitations
- Actual test results
- Reproducibility procedures

Include a practical guide for collecting real tennis movement videos paired with smartphone inertial measurements.

Explain safe sensor placement and synchronization.

Do not claim those recordings already exist.

---

# 22. IMPORTANT IMPLEMENTATION PRIORITIES

Complete work in this order:

**Priority 0 - Scientific correctness**

Audit the Step 2 mathematics, event definitions, synchronization, and existing inference behavior.

**Priority 1 - Core advanced inference**

Implement video-only inference and real multimodal fusion.

**Priority 2 - Reproducible research**

Implement frozen annotations, experiment storage, event matching, and evaluation metrics.

**Priority 3 - Standout experience**

Build the Sensor Fusion Challenge and research dashboard.

**Priority 4 - Robustness experiments**

Add degradation and sensitivity analysis.

**Priority 5 - Polish and documentation**

Refine presentation, tests, exports, and engineering documentation.

Do not compromise Priority 0–2 to add optional visual effects.

---

# 23. SUCCESS CRITERIA

Step 3 should be considered complete only when:

- Existing Step 2 functionality remains working.
- Video-only inference produces real predictions.
- IMU-only inference remains operational.
- Multimodal inference genuinely uses both modalities.
- Event semantics are defensible.
- Sync revisions are respected.
- Reference labels can be frozen.
- Experiment runs are reproducible.
- Evaluation metrics are mathematically correct.
- Synthetic and real data remain clearly distinguished.
- The Sensor Fusion Challenge works.
- Experiment comparisons display real stored results.
- Robustness experiments have functioning algorithms.
- Important edge cases are covered by tests.
- The application builds and runs locally.
- Documentation is updated.
- No deployment has occurred.

If a requirement cannot be fulfilled because the required real data is unavailable, implement the valid software portion, document the limitation, and do not invent a successful experimental result.

---

# 24. MANDATORY FINAL VERIFICATION

Before declaring completion:

1. Run backend tests.
2. Run frontend tests.
3. Run TypeScript type checking.
4. Run lint checks.
5. Validate database migrations.
6. Run API contract checks.
7. Run production builds.
8. Run available Playwright tests.
9. Run a local application smoke test.
10. Verify that existing sessions and data remain usable after migration.

Record actual commands and results.

If any check fails, investigate and resolve it where possible.

Do not claim successful verification of tests that were not run.

---

# 25. FINAL STEP 3 REPORT

When implementation and verification are finished, produce a detailed completion report.

Include:

### A. Implemented functionality
List every completed research and inference feature.

### B. Algorithms
Explain the video, IMU, and fusion approaches in understandable technical language.

### C. Scientific validity
Explain which results are genuine measurements, which are synthetic, and what remains unvalidated.

### D. Experiments
Describe the available experiment workflows and their actual results.

### E. Testing
Report exact commands, numbers of passed and failed tests, skipped tests, builds, and unresolved warnings.

### F. Application verification
Explain how to run and manually explore the new features.

### G. Outstanding limitations
Identify scientific, data, performance, and software limitations.

### H. Step 4 recommendations
Explain what requires further polish, testing, or real-world validation.

Update `docs/PROJECT_STATUS.md`.

Create a local Git commit for the completed Step 3 work if the repository is in a valid state.

Do not push anything remotely.

Do not deploy anything.

---

# 26. MANDATORY STOPPING RULE

This is an explicit stage-gated engineering workflow.

After completing all feasible Step 3 requirements and reporting verification:

**STOP COMPLETELY.**

Do not begin Step 4.

Do not deploy the application.

Do not publish the repository.

Do not provision AWS or other cloud resources.

Do not change the overall project scope without justification.

Conclude with the exact message:

**STEP 3 COMPLETE - AWAITING USER AUTHORIZATION FOR STEP 4.**

If critical requirements remain unfinished, report Step 3 as partially complete instead of falsely claiming completion.

---

# EXECUTE NOW

You have explicit authorization to begin Step 3.

Inspect the existing repository, audit the Step 2 implementation, and proceed autonomously through advanced inference, fusion, evaluation, interface integration, testing, and documentation.

Make this an exceptionally well-engineered research platform.

Prioritize technical correctness, reproducibility, working functionality, and professional presentation.

**BEGIN STEP 3 NOW.**
