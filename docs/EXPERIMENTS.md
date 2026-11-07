# Running reproducible experiments

Start from PowerShell:

```powershell
Set-Location C:\RallySenseLab
docker compose up -d --build
```

Open `http://127.0.0.1:3000`. Existing Step 2 sessions and stored observations remain usable after the additive research migration. Open a session, then **Sensor Fusion Challenge**. The interface runs the same FastAPI/PostgreSQL worker pipeline as the API; it does not substitute illustrative charts for predictions.

## Quick research walkthrough

1. Open the original demo and choose **Open paired synthetic lab** in the challenge. Rendering the generated stick-figure clip is a durable worker job. The paired session contains 801 synthetic IMU observations, 241 analytical landmark observations, an eight-second generated video, and two generated reference centers. Landmarks in this fixture are explicitly not MediaPipe output.
2. Open **Reference laboratory**. Select the generated reference set. Describe its operational definition and generation procedure, then **Freeze reference revision**. Generated references cannot be declared independent human labels.
3. Choose the frozen snapshot in **Experiment setup**. Run **IMU only**. Then run **Video only**. Select **Multimodal fusion**, attest that these generated inputs share a fixture, and document the generated shared clock. Run fusion.
4. Select up to three runs in history. Inspect actual prediction/reference timelines, component signals, event counts, precision/recall/F1, conditional timing error, eligible coverage and elapsed processing time. All fixture metrics are software verification, not tennis performance.
5. Choose **Incorrect synchronization**, set one second, name the run accordingly and run again. With the default 150 ms association gate, the paired fixture's clean two associations disappear. The same two generated references remain missed. The old clean result is unchanged.
6. Try missing samples, inertial noise, timestamp irregularity, an IMU missing window or wrist occlusion. The recipe and seed appear in the result and export. Some severe conditions legitimately fail for insufficient input. Acceleration noise changes acceleration diagnostics; it is a negative control for the gyro-only event rule.
7. Click a prediction marker to seek its actual session timestamp in replay. Use the explicit frozen reference markers or the event/timing table for failure inspection. Export Markdown or JSON from any stored result.

Changing names or parameters creates a new manifest. Repeating an identical complete request reuses an existing queued/running/successful experiment. The history rerun button forces a new experiment with the frozen configuration, retaining the previous result. Re-extraction is not required for each video/fusion run: all use the immutable stored pose artifact.

## Your own observations

Create a session with truthful source provenance, import a sensor CSV, upload a paired video and extract pose. The standard 10 Hz target is retained; the optional 30 Hz target slows extraction playback to provide more processing time. Inspect achieved cadence, gaps and visibility, not just the selected target. Unknown device coordinates and gravity handling stay explicit.

Save alignment in replay. Positive offset moves IMU events later relative to video. The challenge lets you choose an explicit historical alignment revision. Document independently observed cues rather than maximizing prediction agreement. Offset-only alignment cannot compensate for clock drift. If drift is material, shorten/recollect the interval or analyze the limitation; do not claim it was fitted automatically.

Use blinded replay to create human labels before inspecting predictions. Create separate label sets for labelers or adjudication. The reference laboratory supports adding typed markers at an explicit time; existing replay supports editing/deleting human draft markers with optimistic revision checking. Freeze the selected event type with its definition, labeler and procedure. Each freeze is a separate immutable snapshot. A checked independence declaration records your attestation; it does not automatically prove scientific independence.

Exact evaluation refuses unlike event definitions. To test whether a signal peak estimates a human movement or maximum-extension reference, explicitly choose **proxy-to-reference hypothesis** and explain the proposed relationship. The prediction retains its measured-event type. An unrelated mixed-source session can run unimodal baselines but cannot run paired fusion. A session without eligible references shows **Accuracy unavailable**.

The evaluation interval includes negatives and rest. Missing coverage does not remove missed references. If evaluating a deliberately empty reference set, document that the entire interval was actually reviewed as negative. An empty set must not stand in for absent annotation work.

## API examples and reproduction

The browser proxy accepts the `x-lab-client: rallysense` mutation header. Direct FastAPI requests use the local token configured in Compose. See [API.md](API.md) and the generated OpenAPI at `http://127.0.0.1:8000/docs` for complete typed schemas. Never expose this local credential or stack publicly.

An experiment request identifies `mode`, `sensor_id`/`pose_id`, `sync_id`, optional `reference_id`, full interval, detector settings, association/evaluation tolerances, comparison semantics, pairing evidence and corruption recipe. `POST /sessions/{id}/experiments` returns an immutable experiment identity and queues actual computation. Poll `GET /experiments/{id}` until succeeded, failed or cancelled. Inspect the session's jobs for queue/lease state.

`POST /experiments/{id}/evaluate` creates/reuses a new experiment with the requested frozen reference/tolerance/hypothesis; it never overwrites the source experiment. `GET /sessions/{id}/experiment-comparison?ids=...&ids=...` returns up to three same-session runs. The frontend warns when references, intervals, comparison semantics, tolerances or applicable alignment revisions differ. Differences across those protocols cannot isolate algorithm effects.

Reports include the research question, source hashes/IDs and mapping, provenance/placement, pose runtime/model configuration, algorithm version, implementation/dependency hashes, numerical runtime versions, alignment revision/evidence, reference snapshot hash and labeling procedure, all parameters, predictions, errors/misses, coverage, measured latency, failures and reproduction request. Session deletion deliberately removes experiments/references along with private artifacts; export first if you want to preserve a report.

## Collecting a real paired tennis pilot

No such collection is claimed to exist here. Recruit consenting adults, use pseudonyms, agree on local retention, and avoid recording bystanders. Begin with controlled shadow swings in a clear area. Fix a camera with the whole torso and relevant arm visible; record actual resolution, frame rate, view and handedness. A 60 fps source may help visually locate rapid events, but browser extraction still samples and must be assessed.

Use a securely fitted sensor holder that does not interfere with motion. Do not attach a loose phone to a racket or hold one while swinging. Record exact placement, attachment, phone model, app/export settings, sensor axes/orientation, timestamp units and whether acceleration includes gravity. Pocket, torso and arm observations must be analyzed as different placement conditions; they do not directly measure racket impact.

Record a small, deliberate movement of the instrumented body part visible in the camera near both the start and end. A generic clap is not an inertial cue for an unrelated placement. Record cue time ranges in both modalities and save the offset sign/evidence before evaluating predictions. Check the second cue for drift. Keep cues outside the declared scoring interval.

Include rest, walking, pickup and non-swing arm motions as negative examples, not only isolated successful strokes. Preserve original files and export each source clock independently. Annotate a subset with two blinded labelers, retain disagreements/uncertainty notes and adjudication separately, and define exclusions before scoring. Keep repeated sessions and all corrupted copies together in any participant-level split. With a small pilot, report feasibility and failure cases rather than population accuracy or cross-player generalization.

The next stage may improve collection ergonomics and device coverage after authorization. It cannot replace the need for real paired observations and independent labels.

## Step 4 review workflow

From the paired synthetic lab, freeze the generated reference set, run compatible modes/conditions and select up to three experiments. Failure explorer jumps to matched/unmatched predictions, missed reference times and unavailable observation intervals. Open **Print-ready report** to inspect/export the actual stored record through browser print. Comparison text reports actual event/F1 differences only under compatible contracts; observed differences are not causal proof.

History loads lightweight summaries, while selected experiments fetch their immutable full payloads. Default API history without `summaries=true` remains full for existing clients. Scientific exports and original results are unchanged. Real collection uses the Collection studio and REAL_WORLD_PILOT; freeze independently labeled human references after blinded replay, rather than reusing generated labels to claim real accuracy.
