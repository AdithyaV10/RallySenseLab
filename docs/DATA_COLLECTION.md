# Collection software and source conventions

The Collection studio at `/record` creates a durable session, stores a pseudonymous collection profile, accepts motion/video capture or file imports, shows actual worker validation and quality, and saves immutable alignment revisions. Physical participation has not occurred in this development session. See [the pilot protocol](REAL_WORLD_PILOT.md).

## Capture one source

Use a supported current browser on localhost or trusted HTTPS. Press **Start motion capture** in a user gesture. A permission prompt may appear; denial and unsupported APIs offer CSV import instead. Some desktop browsers expose the API but emit no measurements; recording stops after ten seconds without events. Keep the page visible, screen unlocked and device orientation fixed. Hiding the page, changing orientation or exceeding 20 minutes / 120,000 observations stops capture. Interruptions retain the current in-memory buffer. Save or export before reload/navigation; there is no durable background recording or automatic draft recovery.

Select the acceleration quantity explicitly. `acceleration` is device-provided linear acceleration; `accelerationIncludingGravity` includes gravity. Missing linear acceleration is never replaced with gravity-inclusive acceleration. Rotation rate is angular velocity, not attitude. W3C `beta` maps to device x, `gamma` to y and `alpha` to z; degrees/second are converted to radians/second. The raw rotation values also remain in the exported CSV. No world-frame transformation, orientation integration, calibration or racket trajectory is inferred. See the [DeviceMotion API](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent) and [orientation event specification](https://www.w3.org/TR/orientation-event/).

The first accepted `event.timeStamp` becomes zero microseconds. Original event timestamps, first timestamp, browser time origin, UTC start description, axis mapping, discarded nonmonotonic timestamps, missing channels and rough operator cues are retained. UTC descriptions do not synchronize devices. Missing values stay blank; at least one complete xyz stream is required for normalization. Mean cadence describes accepted observations, not guaranteed sensor frequency. Native sampling, delivery jitter and browser pauses can differ.

Exports include raw CSV and a metadata JSON sidecar. **Save motion to session** uploads the CSV plus mapping/capture metadata through the ordinary normalization job. Raw source artifacts remain immutable. Missing gyro prevents the gyro detector; acceleration-only capture is still a valid observation source.

Optional camera capture uses `getUserMedia` and `MediaRecorder`, requests video only and stops its camera tracks on completion/interruption. It is bounded to ten minutes / approximately 100 MiB in memory; a final chunk can cross the byte threshold. Save/export before leaving. The worker probes actual codec, dimensions and duration. A streamed browser WebM missing final container metadata receives a bounded, video-only remux, preserving the original artifact/hash and encoded frames; no re-encoding or drift compensation occurs. This fallback does not guarantee support for every mobile codec, rotated/VFR file or interrupted recording. External MP4 H.264 / WebM VP8/VP9 upload remains available.

Each source has an explicit origin choice. Actual camera and device observations default to **recorded**. Select synthetic only for known generated/software input. Adding recorded sources to a synthetic session produces mixed provenance. Pseudonyms and declared pairing are operator attestations, not externally verified facts. Unknown metadata stays unknown.

## Pair sources

Use a fixed camera plus safely attached sensor, often on separate devices. The same browser may capture both but has no common encoded presentation/event clock guarantee. Record a distinct visible and sensor-detectable cue before and after the task. Operator cue buttons preserve rough sample markers; independently inspect the corresponding visible video cue.

In **Quality & alignment**, select the correct sensor/video, enter start cue times and optionally end cue times in their own source clocks, enter timing uncertainty, describe evidence and attest whether these record the same attempt. The saved offset is `video_start - sensor_start`, with `session_time = sensor_time + offset`. End residual is `video_end - sensor_end - offset`. A residual suggests inconsistent localization, clock drift or a pause; it does not distinguish the cause. Inspect or recollect if it is material relative to evaluation tolerance. Offset alignment never fits drift. New experiments freeze metadata and alignment evidence; existing manifests are preserved.

## Compatibility and verification scope

| Path | Verification |
| --- | --- |
| Chromium software DeviceMotion fixture | Automated UI, units/missing values/timestamps, real CSV transport, PostgreSQL, normalization and inference; generated fixture only |
| Permission denied / absent API | Automated actionable fallback states |
| Chromium synthetic camera | Actual MediaRecorder encoding and backend FFprobe/remux; no physical camera |
| Physical Safari/iOS and Android devices | Requires participant hardware; not verified here |
| Trusted phone HTTPS | Opt-in configuration prepared; no LAN listener, trust-store or firewall change performed during implementation |

Motion permission support and requirements differ by browser. See [requestPermission](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent/requestPermission_static) and [MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder). A responsive viewport test is layout evidence only. For mobile access use the explicit [local HTTPS instructions](LOCAL_DEVELOPMENT.md), or export CSV with phyphox and transfer privately.
