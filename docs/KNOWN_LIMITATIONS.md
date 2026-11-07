# Known limitations at final audit

2026-11-07. See [FINAL_AUDIT](FINAL_AUDIT.md) for confirmed defects, severity and evidence. This inventory separates implemented behavior from research and release claims that have not been established.

## Open defects and implemented fix

- **A01 HIGH:** Next global Proxy truncates multipart bodies around 10 MiB; both valid large CSV and MP4 web-upload regressions fail. Direct backend normalization/probing succeeds.
- **A02 HIGH:** frozen dependency/runtime descriptors are recorded but not checked against the research worker's executing environment. Two mismatch regressions fail.
- **A03 MEDIUM:** the client/server batch combination supports 10,000 extracted observations, below the possible ten-minute dense-track count.
- **A04 MEDIUM:** readiness does not verify artifact writability in writable mode.
- **A05 MEDIUM:** a saved offset can leave a stale zoomed sensor window until reload.
- **A06 MEDIUM, fixed:** cancelled/exhausted source job state now propagates to the source; ready/succeeded artifacts are preserved. Regression suite passes.
- **A07 LOW deployed-runtime relevance:** ten moderate development-tool dependency findings remain; no automatic major downgrade was made.

## Scientific limits

No independent held-out tennis accuracy, trained stroke classifier, calibrated confidence, impact timing, metric racket velocity, full-body biomechanics, orientation reconstruction, coaching grade or injury inference exists. Gyro events are angular-speed maxima; visual events are normalized image wrist-speed maxima; fusion is one-to-one temporal association. Matching within tolerance is not proof that two modalities observed the same physical event.

Generated references/analytical landmarks test software. They are not MediaPipe output or independent athlete labels. The permitted integration clip establishes real model execution, not real-world tennis accuracy. No participant-separated cohort evaluation, inter-rater study, statistical uncertainty analysis, aggregate participant metrics or power analysis was performed. Pairing, placement, consent and labeling independence are operator attestations.

Default thresholds, visibility gates, smoothing and filter guards are engineering assumptions. Offline zero-phase filtering is not a real-time causal detector. Median-rate interpolation cannot restore missing high-frequency information or eliminate aliasing. Image projection, camera motion, torso geometry, subject switching and sensor placement can change event results. The old replay feature strip and newer research speed baseline have different normalization/timestamp semantics.

Synchronization is offset-only. Two cues expose an end residual but do not estimate/correct clock drift, latency or cross-device clock quality. Tuning alignment or thresholds against held-out reference labels would invalidate an accuracy claim; software cannot independently police the research protocol.

## Capture and vision limits

No physical iOS/Android or full cross-browser sensor/camera verification was performed. Tests inject explicitly synthetic DeviceMotion or use Chromium's synthetic camera while exercising real browser/backend processing. Permission, sensor availability, sampling rate, axes/signs and codecs need physical verification.

Motion/camera capture is foreground and memory-backed until save/export. Backgrounding/interruption stops capture; a browser crash, route navigation or component replacement can lose unsaved buffers. beforeunload warnings do not protect all SPA navigation. There are no durable drafts, guaranteed background capture or automatic camera/IMU synchronization. A permission request resolving after navigation and repeated permission/start interactions were not comprehensively stress-tested.

MediaPipe uses one person and CPU execution, with classic worker and initialization fallback. Stored observations use actual presentation timestamps; repeated extraction is scheduling/tracker-history dependent. FFprobe correspondence was checked for one short clip, not arbitrary VFR, rotations, nonzero origins, very long media or every browser. No pixel-identity/frame-perfect guarantee follows. The late-window API works, but the batch ingestion cap limits long browser extraction. Half-prominence windows are descriptive signal intervals, not physiological certainty bounds.

## Operations, security and performance limits

The system is one local workspace. UUIDs and a shared token/password are not tenant isolation. No per-user ownership model, public upload sandbox, distributed quotas, S3 adapter or signed direct multipart upload exists. Read-only fixture allowlisting cannot sanitize private content already attached to a fixture; public demos require fresh inspected volumes. Worker maintenance and already queued jobs are not disabled merely by HTTP read-only mode.

Bounded uploads, subprocess timeouts and restricted protocols are not comprehensive hostile-media containment. Full container OS scans, independent penetration testing, maximum concurrent load and disaster-recovery restore remain unperformed. Backups and migrations need an operational owner. Readiness does not currently detect every storage failure.

Windowed output bounds do not guarantee bounded underlying database/file-processing cost. Experiment summaries still load full result JSONB before projection; session detail and histories can accumulate. Video median smoothing examines each segment repeatedly, and event matching is O(n*m) with a 2,000-event-per-list guard. No public throughput, capacity, tail-latency or memory-peak claim is supported by the local navigation measurements.

Basic desktop/mobile layout, headings, button names and ordinary interactions were checked. Complete keyboard-only, screen-reader, contrast, focus and reduced-motion certification was not performed. Dense research views require guidance on small screens. No participant data or private recordings were published.
