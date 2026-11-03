# User experience specification

Design only. Route availability follows the authorized implementation stage; future modules must not appear as working buttons in the MVP.

## Visual system and navigation

Brand: RallySense Lab, with subtitle AI-Powered Sports Movement Intelligence. Use near-black canvas (#101416), charcoal panels (#192125), light neutral text (#E8F0F2), cyan/teal data accents (#45D6D0), and amber event markers (#FFB35C). These are proposed tokens; verify actual contrast on rendered components. Use a locally hosted readable sans-serif, tabular numerals for measurements, restrained borders, generous plotting space, and reduced-motion-aware transitions. Avoid decorative performance scores or marketing claims of accuracy.

Desktop navigation: Sessions, Recording Studio, Research (Step 3), and Documentation. Session navigation: Overview, Data, Replay, and Results (Step 3). A compact session selector and provenance badge remain visible. Mobile uses a drawer and stacked panels; replay controls stay reachable without obscuring video. Page state survives navigation through URL session/run IDs, selected tab, and bounded timeline query parameters.

## Screens and interactions

| Route / screen | Content and behavior | Availability |
| --- | --- | --- |
| `/` Landing | Clear research question, actual capabilities, technical illustration based on labeled synthetic motion, Explore Demo, Enter Platform | Step 2 |
| `/sessions` Dashboard | Persisted sessions, search/filter, create dialog, modality/quality/status badges, recent run, empty/error states | Step 2 |
| `/sessions/[id]` Overview | Capture/provenance metadata, video/sensor cards, last processing outcomes, links to Data and Replay, deletion with storage explanation | Step 2 |
| `/sessions/[id]/data` Upload | Drag/drop and file picker; size/format hints; sensor mapping preview; unit and placement selection; real validation errors and processing jobs | Step 2 |
| `/record` Recording Studio | Capture instructions and CSV-import route in MVP; real permission flow, capture/export controls, and measured samples later | Instructions in Step 2; working phone capture in Step 4 |
| `/sessions/[id]/replay` Movement Replay | Media/pose, sensor panels, events, annotation editor, alignment controls, quality ranges, run configuration | Step 2 |
| `/research/challenge` Sensor Fusion Challenge | Select frozen dataset/run; configure noise/dropout; generate derived inputs; run comparisons; label artificial perturbation | Step 3 |
| `/experiments/[id]` Evaluation | Dataset and manifest, paired method table, precision/recall/F1 with denominators, timing chart, false/missed events, coverage and exclusions | Step 3 |
| `/docs` Documentation | Getting started, units/placement, event definitions, algorithms, limitations, privacy/retention, reproducibility | Step 2 foundational; expand later |

Explore Demo creates or opens an idempotently seeded synthetic session through the ordinary backend pipeline. Show “Synthetic software demonstration — not athlete validation” on the landing preview, session, replay, and exports. A generated animation may substitute for video; it is labeled “Programmatic animation” and its skeleton must not be claimed as MediaPipe output. Synthetic reference events have generated provenance, not “human labels.”

No sensor input leads to a guided import state; no video leaves a working signal-only replay clock. Missing pose allows normal video replay with an explicit unavailable overlay state. Every displayed metric identifies the source/run and unit; absent results show an empty state rather than zero or a decorative chart.

## Replay composition

Desktop: left two-thirds for video with overlay and shared transport; right third for selected event/annotation details, quality, and algorithm configuration. Underneath, full-width acceleration and gyroscope plots share a time axis and cursor. A compact event lane distinguishes predictions, human references, synthetic references, synchronization cues, and missing intervals through both shape and color. A source/run legend makes each visible layer explicit.

At narrower widths, stack video, transport, timeline, signals, and details. Keep channel toggles and labels usable by touch. Charts provide a text summary and event table so access does not depend on color or precise pointer interaction. Event markers have accessible names including type, source, and timestamp.

### Clock ownership

Use one `ReplayController` with `t_session_us`, `playing`, `playback_rate`, `view_window`, `active_sync_revision`, `seek_generation`, and `clock_source` (`video` or `synthetic`). While video is active, the video element owns playback; the controller consumes displayed-frame media time. UI graphs never advance independent timers. With no video, a monotonic elapsed-time clock drives the timeline, clearly labeled signal-only or animation playback.

Seeking: a graph click, event click, scrub, or keyboard action submits one session-time intent. Convert it to the primary media clock, clamp to valid media bounds, increment seek generation, set video time, and update the cursor. On `seeked`/next presented frame, use the actual presented timestamp and ignore callbacks from older generations. Paused seeks refresh overlays and charts. Rate changes are applied to video and derived synthetic clock; they do not rescale source timestamps.

Overlay: select the nearest valid pose frame within `max_pose_age_us` (initial 100,000, configurable and visible in provenance). Do not reuse stale skeletons through gaps. Map normalized coordinates into the actual letterboxed video rectangle, including rotation, mirroring, intrinsic aspect ratio, and device-pixel ratio. Handle resize and fullscreen using the same transform. Interpolation, if later enabled, is explicitly identified and never used as raw data.

Signal access: map session window into each source clock using the active immutable sync configuration. Fetch bounded/downsampled windows with margins; retain full-resolution values for exact tooltip queries. Invalidate requests when revision or generation changes. Missing data creates gaps in curves. Predictions from a different sync revision show an explicit stale-alignment notice; do not silently shift frozen results.

### Primary tasks

1. Import: choose session/file, review column/unit/clock mapping, inspect quality, commit. Show actual upload bytes and processed rows; use an indeterminate processing state where no denominator is known.
2. Align: display video and sensor cue markers, provide signed offset numeric input and small increment buttons, preview changes locally, then save a new revision. Explain “positive moves sensor events later on the video timeline.” Provide cancel/revert before save; old runs remain reproducible.
3. Analyze: choose available algorithm, review requirements and parameters, submit, see real job state, inspect returned candidates and exclusions. Unsupported algorithms are absent from Step 2 actions.
4. Annotate: pause or scrub to a frame, add event, choose definition/category, record uncertainty and notes, save. Edit or remove with revision conflict handling and an undo draft where practical. Blinded labeling mode hides predictions and sensor cues while preserving raw video transport.
5. Compare (Step 3): select immutable runs and frozen labels, review window/tolerance, run evaluation, inspect paired errors and unmatched events, export actual results. Undefined metrics display “Not defined” with the reason.

## Phone recording flow (Step 4 specification)

Detect secure context, API existence, and permissions before capture. The user presses Enable Sensors; request permission within that gesture where required. Start a local buffer, record event timestamps and received sample times, show actual measured rate, and expose Stop/Export. Null channels are unavailable, not zero-valued signals. Mark background/visibility interruptions; mobile capture cannot guarantee uninterrupted cadence. Failed permission or unsupported hardware leads to practical CSV import instructions. Motion capture generally needs a secure context and may require user-gesture permission. [MDN device motion guidance](https://developer.mozilla.org/en-US/docs/Web/API/Device_orientation_events/Detecting_device_orientation)

A phone cannot use the desktop's localhost address. Step 4 must document an authorized private HTTPS development path for on-device testing; loopback desktop testing does not validate phone capture. Do not open network ports or publish a tunnel during Step 1 or claim real iOS/Android testing from emulation.

## States, accessibility, and acceptance

Persisted job states distinguish queued, processing, cancelling, cancelled, failed, and complete. Retry creates or resumes only an eligible operation and shows which raw data will be reused. A closed browser can interrupt pose extraction; explain that restarting extraction creates a new track. Backend restarts do not fabricate completion.

Use semantic landmarks/headings, keyboard-operable dialogs, visible focus, labeled numeric controls, live status announcements with throttling, reduced motion, and contrast verified against WCAG AA targets. Shortcuts (Space, arrows, annotation key) work only outside text inputs and have documented equivalents. Destructive session deletion identifies the session and data affected and uses a confirmation dialog; this is product UX, not a new agent authorization gate.

Replay acceptance in Step 2: seeking from video, plots, and markers updates all panels; paused seeks work; speed changes do not change alignment; resizing preserves overlay registration; missing intervals do not show stale pose or continuous lines; saved offsets and labels survive reload; stale network responses do not overwrite newer seek state. Validate practical synchronization within a displayed video frame and the configured overlay tolerance, and report measured limits rather than promising subframe accuracy.
