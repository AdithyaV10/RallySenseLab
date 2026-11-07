# Small controlled movement pilot

This is a proposed protocol, not a completed dataset or validated tennis study. Physical participation, consent, a suitable private space and securely attached equipment are prerequisites. Begin with slow controlled shadow movements, not competitive play.

## Equipment and placement

Use a fixed camera/tripod with the full relevant body visible, a phone with verified motion export or browser capture, secure purpose-designed attachment, and a private workstation running RallySense. Keep the floor clear and allow ample separation from people and equipment. Never swing while loosely holding a phone. If secure attachment is unavailable, collect stationary controlled observations or stop. Do not attach a phone to a racket for this initial pilot. Pocket, torso, forearm and wrist measurements are mechanically different; record each explicitly and analyze separately.

Use pseudonyms rather than names. Confirm permission for video and motion storage, retention and deletion before recording. Exclude bystanders. Keep raw media and identity mapping private; do not add them to Git, public demos, screenshots or report examples. The application is a single-workspace tool, not a participant consent-management system.

## One usable paired session checklist

1. Create a session in Collection studio. Enter pseudonym, movement, handedness, camera view, sensor placement/attachment, device model/app and conditions. Confirm consent. Unknown details remain unknown.
2. Verify actual incoming channels and chosen acceleration quantity. Check the CSV preview/export units. Perform a short stillness recording to inspect gross noise and dropouts; do not claim this is a calibrated reference.
3. Fix the camera, keep the body and dominant wrist visible, verify adequate light and a stable frame. Mark the attachment's device-axis orientation in notes; avoid rotating the device during the attempt.
4. Start camera and IMU recording. Use a safe distinctive visible movement cue that appears in both observations, separate from evaluation movements. Record approximately 20–40 seconds initially.
5. Perform 5–10 slow controlled repetitions of one defined shadow movement, with 2–3 seconds of rest between repetitions. Stop for discomfort, attachment movement or loss of balance. Add stillness, walking, setup motions and other safe negative examples. Do not label every angular-rate peak as a swing.
6. Repeat the cue at the end. Stop, save both sources and export a private backup immediately. Inspect actual file duration, sample count, cadence, missing channels, gaps and source origin. Recollect unusable observations rather than filling gaps with invented measurements.
7. Align the visible/source cue times in Collection studio. Record cue uncertainty and pairing evidence. Inspect end residual. If timing error is comparable to the planned matching tolerance, mark the session unsuitable for precise timing evaluation. Offset-only alignment cannot repair drift.
8. Open replay. Extract real MediaPipe landmarks, inspect observed cadence, large gaps, detections and missing wrists. Reuse an existing suitable track. Seek-and-process sampling may improve temporal coverage but cannot recover absent source frames or guarantee calibrated joint locations.
9. Define the visual event before labeling: for example a specific observable wrist-extension apex, with an explicit ambiguous-case rule. Choose blinded replay, select/create an independent human annotation set, record timestamps and ambiguity notes, then freeze the set with source video, labeler, procedure and independence declaration. Exclude sync cues from the movement reference definition.
10. Run IMU, video and temporal association under compatible evaluation intervals/tolerance. Unlike event definitions require an explicit proxy hypothesis. Inspect matches, false positives, misses and missing evidence. Export the actual report and immutable manifest.

## Repeats and evaluation design

Start with a few short sessions of the same controlled task, allowing comfortable rest between sessions. Record failures and excluded attempts as well as successful ones. Keep negatives and transitions in evaluation intervals. Repeated sessions from one person are not independent held-out player evidence.

Before collecting a larger dataset, predefine event semantics, placement groups, clock uncertainty, exclusion rules, tolerance, sampling criteria, participant separation and a held-out evaluation plan. Avoid tuning offsets or detector thresholds against the same labels later used to claim accuracy. Ideally have a second blinded observer label a subset and examine disagreements before adjudication. The current software stores independent label sets and ambiguity notes; it does not calculate a structured inter-rater uncertainty model or cohort confidence intervals.

Report session counts, provenance, durations, eligible observation coverage, reference procedure and all relevant misses. Distinguish synthetic robustness tests from observed real-world recording failures. Do not infer ball impact, racket speed, biomechanical ground truth, coaching effectiveness or trained movement classification from these baselines. No such physical validation has been performed here.
