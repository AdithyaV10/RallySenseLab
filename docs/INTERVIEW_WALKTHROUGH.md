# Technical demonstration walkthrough

## First minute

Open `http://127.0.0.1:3000`. RallySense asks what sparse inertial observations can reveal, and how uncertain video observations can corroborate them. Click **Explore the demo**, play/scrub the synchronized timeline and inspect a measured angular-speed peak. The court figure and signals are explicitly synthetic, not athlete measurements. Guidance can be dismissed.

Open **Explore the paired research demo** from the landing page, or **Open paired synthetic lab** in Sensor Fusion Challenge. This fixture has generated video, analytical landmark observations and IMU pulses on one known clock; those landmark observations are not MediaPipe output. Freeze the generated reference set, select it with synthetic-fixture evaluation, and run each of the three modes. Select up to three stored runs, then repeat with a missing interval, wrist occlusion or synchronization error. The worker computes every displayed result. Failure explorer jumps to stored matched/unmatched events, missed references and unavailable windows; it does not invent causes.

## Explain the engineering

Sparse sensors are useful because they are inexpensive and locally observable, but a placement-specific angular-rate stream cannot reconstruct every joint, racket trajectory or ball contact. The IMU baseline normalizes units, preserves gaps, filters angular-speed magnitude and detects adaptive height/prominence/separation peaks. Its output is `gyro_peak_v1`, a measured signal event.

Actual MediaPipe browser extraction uses the installed Tasks Vision CPU runtime in a classic worker, with a working main-thread fallback. It stores actual presented video timestamps, detections and missing observations. Playback sampling remains supported; optional seek/backpressure waits for each observed frame to finish processing before moving forward. Achieved cadence/gaps are reported separately from target frequency. Monocular landmarks have perspective, visibility and model errors. Stored-pose inference computes image wrist speed relative to torso scale, with no derivatives across invalid gaps, then detects `wrist_speed_peak_v1` events. Neither output automatically confirms a tennis swing.

Multimodal temporal association matches unlike sensor/video events one-to-one within a declared interval, keeps both observation times and anchors output to the IMU event. It is an interpretable association baseline, not a trained biomechanical reconstruction model. It rejects unpaired mixed sources. Agreement does not prove correctness. A hypothesis is required when evaluating a proxy against a different human event definition.

Synchronization is offset-only: sensor time plus offset equals the video/session clock. A revision binds sources and can retain start/end cues, uncertainty, pairing note and end residual. It does not fit drift. Do not tune alignment against predictions and then claim independent accuracy. Existing experiment manifests preserve the exact revision and later edits cannot rewrite completed runs.

Evaluation uses explicit event definitions, a frozen reference revision, interval, tolerance and matching objective. It reports TP/FP/FN, precision/recall/F1 when denominators are defined, timing errors and unmatched events. Missing observations retain reference misses. No eligible reference means accuracy unavailable. Synthetic clean/corrupted results demonstrate software behavior; they do not establish real-world fusion benefit or a held-out player result.

## Inspect working software

Show **Collection studio**: pseudonymous task/device/attachment metadata, explicit linear versus gravity-inclusive acceleration, angular-rate units/device axes, capture permission/fallback, CSV/video imports, real validation jobs and cue-based alignment. Physical collection still requires people and supported hardware; no pilot has been claimed.

Show **System readiness**, the failed source-job retry and immutable failed record, a print-ready report with actual manifest, and the PostgreSQL migration/tests. API response commits occur before success headers; durable jobs use leases; raw artifacts have content hashes; stored experiments reference immutable inputs. Replay fetches bounded pose windows; experiment history loads summaries and selected full details. These boundaries support future algorithms without silently rewriting evidence.

Finish with limitations and next research steps: collect securely attached, independently labeled paired controlled movements; predefine semantics/placement/tolerance; quantify clock and labeling uncertainty; separate tuning and held-out participants; inspect negatives and missing coverage. Public hosting and any Step 5 audit remain subject to explicit authorization.
