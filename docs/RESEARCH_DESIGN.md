# Research and evaluation design

This is a proposed protocol, not a completed study. No recordings, human labels, performance measurements, or validation results exist in this repository at Step 1.

## Question, hypotheses, and evidence levels

Question: how reliably can sparse inertial observations detect swing-like activity and estimate event time when compared with independently annotated video observations?

Primary hypotheses to test: an angular-speed peak detector can identify some swing-like events under fixed placement; video-based wrist motion provides a different observation; agreement-based late fusion can trade recall for precision. These are falsifiable hypotheses, not product claims. Smartphone placement, participant, camera view, handedness, and recording conditions are covariates. No arbitrary full-body reconstruction, verified impact detection, coaching grade, or injury diagnosis is claimed.

Every result identifies its evidence level: deterministic synthetic software fixture, controlled recorded pilot, or held-out recorded evaluation. Synthetic and recorded metrics appear in separate reports. A large synthetic sample is not evidence of participant generalization. No trained classifier is required; add one only with sufficient labeled recordings and defensible splits.

## Collection protocol

1. Use consenting adults in a clear practice area; record only necessary pseudonyms and permission to retain/use the video. Capture handedness, placement, attachment method, phone model, browser/app, sensor API, orientation, camera view, resolution, and date.
2. Fix the camera so the full subject and relevant arm remain visible. Begin with shadow swings; record the actual sampling cadence. A nominal 30/60 fps or 50/100 Hz is a collection target, not a verified rate.
3. Secure the sensor consistently without compromising movement. Do not instruct users to fasten an unsecured phone to a racket. Compare placements as separate conditions; a pocket recording does not support direct racket kinematics.
4. Record a visible, sensor-detectable deliberate cue near the start and end, such as a small controlled movement of the instrumented hand before/after the task. Keep cue intervals outside evaluation. A clap visible in video is not automatically detectable by an unrelated sensor placement.
5. Record several repetitions plus rest, walking, ball pickup, and non-swing arm movements as meaningful negative examples. Include varied speed and purposeful failures of visibility, without assuming each motion is a tennis stroke.
6. Preserve raw exports, time origins, pauses, and file hashes. Log an annotation-independent alignment decision before prediction evaluation. Independent clocks require offset and possibly drift checks.

Initial pilot target: at least 5 participants, 2 separately recorded sessions each, roughly 20 swing attempts plus negative activity per session, if feasible. This is a planning target for failure discovery, not a power analysis or sufficient evidence of population accuracy. If fewer participants are available, report a feasibility case study and avoid generalization claims.

## Reference event definition and labeling

The primary reference `swing_apex_v1` is the frame at greatest visible extension of the dominant wrist away from the torso during the forward portion of a manually identified swing, before follow-through. Annotators first bracket the swing, then scrub nearby frames, choose the maximal-extension frame, and record an uncertainty interval spanning visually indistinguishable candidates. In a plateau choose the midpoint frame; tie rules must be applied consistently. This operational image-space event is deliberately narrower than racket impact or a biomechanical swing phase boundary.

Store event type/version, frame presentation time, session time under a frozen sync revision, labeler pseudonym, source video hash, uncertainty bounds, and ambiguity/exclusion notes. Optionally label swing start/end and stroke-like category as separate event definitions; do not pool them with primary timestamp metrics.

Hide prediction overlays and sensor peaks during reference labeling. Labelers do not derive timestamps from the detector being evaluated. Two independent labelers should annotate a pilot subset and disagreements; record raw labels, timing disagreement distribution, and adjudication separately. Exclude a reference only under a predefined visibility/ambiguity rule, and publish excluded counts and durations. Ambiguous events may be retained for sensitivity analysis with clearly separated results.

Gyro and wrist-speed peaks are proxy predictions of this reference, not identical physical definitions. A consistent offset is a research finding. A learned timing correction is allowed only if fit on development data, frozen, and evaluated on held-out recordings. If the reference cannot be labeled reliably in available views, revise the protocol/version before analysis rather than reporting spurious precision.

## Alignment and valid evaluation intervals

Freeze source time mappings before scoring. A manually set offset is acceptable if documented and supported by independent cues. For two cues, the affine map is `a=(v2-v1)/(s2-s1)`, `b=v1-a*s1`; require separated cues and positive scale. More cues permit residual analysis. Cue localization ranges and residuals indicate alignment uncertainty, not a confidence interval without a statistical model.

Predeclare included session intervals, rest periods, negative examples, excluded cues, and unlabelable intervals. Compute both full-task evaluation and a modality-comparable analysis on the common observable interval. In full-task evaluation, abstention/missing sensor coverage does not erase reference events: those remain missed events where the reference is labelable. In the common-interval analysis, show excluded duration/events so selective coverage cannot masquerade as improvement. Report no-overlap or zero usable duration as unevaluable, not 100% accurate.

## One-to-one event matching

For each recording and event definition, sort predictions and references by time. Permit a pair only when absolute time error is <= tolerance; proposed primary tolerance 150 ms, fixed before held-out scoring. Also report 50/100/250 ms sensitivity without selecting the best threshold post hoc.

Matching objective is lexicographic: first maximize the number of valid pairs, then minimize total absolute timing error, then break ties deterministically by timestamp/ID. For one-dimensional ordered event lists, dynamic programming with skip-prediction, skip-reference, and allowed-match transitions can enforce this objective. A carefully dummy-augmented assignment solver is another option; a naive full assignment followed by threshold filtering is not equivalent. SciPy supplies an assignment primitive, but the tolerance/cardinality objective must be implemented explicitly. [SciPy assignment documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)

Required adversarial fixture: predictions [0,80] ms, references [60,140] ms, tolerance 70 ms. Nearest-first pairing 80->60 leaves a false miss; the required matching is 0->60 and 80->140, yielding two matches. Also test duplicates, inclusive tolerance boundaries, reordered inputs, different event types, empty sets, and deterministic ties.

## Metrics and interpretation

Let TP = matched pairs, FP = unmatched predictions, FN = unmatched included references.

| Metric | Definition / edge behavior |
| --- | --- |
| Precision | TP/(TP+FP); null with reason if no predictions |
| Recall | TP/(TP+FN); null with reason if no references |
| F1 | 2TP/(2TP+FP+FN); null when both event sets empty, otherwise defined including zero |
| Signed timing error | prediction minus reference, ms; positive means late |
| Timing summaries | mean signed bias, median absolute error, mean absolute error, p90 absolute error over matched pairs; null if no matches |
| False positives per minute | FP divided by included observation duration in minutes; null for zero duration |
| Coverage | observed/eligible seconds and fraction of intended interval, plus reference counts in excluded intervals |

Report raw denominators alongside all rates. True negatives are not defined by this event-matching task; do not invent event accuracy or use sampled-frame accuracy to hide misses. Timing metrics are conditional on matched events and must be shown beside recall. Summaries over participants use both pooled micro counts and macro per-participant metrics with explicit handling of undefined values.

If data supports intervals, bootstrap participants (or whole sessions for a single-participant feasibility study), not individual frames/events treated as independent. Record seed, cluster count, and resampling count. With very few clusters, present descriptive ranges and state that intervals are unstable; do not imply statistical certainty. Algorithm strengths, MediaPipe visibility, annotation ambiguity, and empirically estimated statistical intervals are four distinct quantities.

## Splits, reproducibility, and comparisons

Partition by participant for cross-person claims, with a separately documented within-person/session protocol if appropriate. Never randomly split windows from the same recording across train/test. All repeated recordings and their augmented/corrupted copies stay in the same split. Fit normalization, thresholds, feature selection, score calibration, and timing corrections only on training/development partitions. Keep test labels out of sync adjustment and UI parameter tuning. Group-aware validation is an established means of holding related samples together. [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)

An experiment manifest freezes source hashes, provenance, participants/splits, sync IDs, label-set revisions, included/excluded intervals, algorithm versions/configs, model/runtime hashes, code commit, seed, evaluator version, tolerance, and corruption recipe. If sources or labels change, create a new manifest. Run all compared methods on the same recordings and reference definitions, reporting failures/coverage separately. Claim fusion improvement only if supported by held-out results and uncertainty, not just a demonstration chart.

## Sensor Fusion Challenge (Step 3)

Generate derived artifacts from immutable baseline inputs using recorded seeds. Conditions: additive noise with explicit SI standard deviation, random dropout (e.g. 5/20%), contiguous missing bursts (e.g. 100/500 ms), reduced sample rate with anti-aliasing, and timestamp offset/drift perturbation (e.g. +/-50/150 ms, +/-100 ppm). Values are illustrative experiment settings, not measured phone noise. Keep recipes and masks identical across paired comparisons where relevant. Never corrupt reference labels or use reference events to choose favorable corruption locations.

Show clean and corrupted results together; tag every plot and export with artificial corruption and dataset kind. Test one perturbation at a time before combinations. Recompute quality and eligibility from corrupted inputs. Report abstention and full-task misses as well as common-coverage results; otherwise dropout can artificially improve scores. Predictions must come from rerun algorithms, not edited output timestamps or fabricated accuracy sliders.

## Planned scientific tests and report

Analytical tests cover filter behavior on known signals, unit/axis conversion, timestamp mapping and drift, gap exclusion, peak separation, one-to-one matching, fusion weights, and undefined metrics. Metamorphic tests cover a common time shift preserving matches, event permutation preserving counts, unit-equivalent input preserving predictions, and rejected incompatible event definitions. Synthetic fixtures include noise-free, noisy, irregular, missing, flat, and invalid streams with known generation parameters.

The final research report must identify dataset type and size, independent label procedure, algorithms/configs, split policy, matching rules, actual metrics, uncertainty definition, failure cases, runtime environment, and reproduction commands. No report is produced in Step 1 because no experiments have run. Real-world capabilities remain unverified until actual recordings and independent labels pass through the implemented pipeline.
