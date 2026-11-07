import Link from "next/link";
import {
  ArrowUpRight,
  BookOpen,
  Activity,
  Clock3,
  ShieldCheck,
} from "lucide-react";
import { Shell } from "@/components/ui";
export default function Docs() {
  return (
    <Shell>
      <div className="page-content docs-page">
        <div className="eyebrow">THE RESEARCH NOTEBOOK</div>
        <h1>
          Understand your observations<span className="heading-dot">.</span>
        </h1>
        <p className="docs-lead">
          A small set of principles keeps the workspace useful, reproducible,
          and honest.
        </p>
        <div className="docs-grid">
          {[
            {
              icon: Activity,
              title: "A peak is a signal event",
              text: "The IMU baseline filters angular-speed magnitude and detects local peaks. These are measured signal events, not confirmed swings or ball impacts. Thresholds are engineering settings whose usefulness depends on placement and recording conditions.",
            },
            {
              icon: Clock3,
              title: "Two sources. One timeline.",
              text: "Sensor time starts at the first imported timestamp. Video uses its presentation clock. A positive offset moves sensor events later relative to video. Saving alignment creates a new revision; previous inference runs retain their original mapping.",
            },
            {
              icon: BookOpen,
              title: "Keep references independent",
              text: "Human observations are stored separately from algorithm outputs. Use Blinded labels in replay to hide sensor signals and predicted markers while labeling video. The swing apex label means maximum visible dominant-wrist extension during the forward movement, not ball impact.",
            },
            {
              icon: Activity,
              title: "Observe the wrist, preserve the gaps",
              text: "The video baseline measures image wrist speed relative to torso scale from stored pose observations. It does not differentiate across missing observations. Wrist-speed maxima and angular-speed maxima have different meanings; their strength is not calibrated confidence.",
            },
            {
              icon: Clock3,
              title: "Association is a testable hypothesis",
              text: "Multimodal temporal association pairs events one-to-one within a declared time interval, retaining both observation times and the IMU anchor. Agreement can support a hypothesis but does not confirm a swing, impact or reconstructed racket trajectory. Mixed unrelated sources cannot establish physical pairing.",
            },
            {
              icon: ShieldCheck,
              title: "Local storage and retention",
              text: "Recordings remain in the local artifact volume until their session is deleted. Deletion immediately blocks session access and schedules tracked file cleanup. This foundation is single-user and loopback-only. It has no cloud upload or public sharing.",
            },
          ].map((x) => (
            <article className="panel" key={x.title}>
              <x.icon size={23} />
              <h2>{x.title}</h2>
              <p>{x.text}</p>
            </article>
          ))}
        </div>
        <section className="panel prose-panel">
          <h2>What the demonstration shows</h2>
          <p>
            The included session is generated from a deterministic 100 Hz
            mathematical signal. Its five pulse centers are stored as generated
            fixture references. The backend runs the ordinary CSV normalization
            and analytical detection pipeline. The animated player is a
            programmatic illustration, not an athlete recording or a MediaPipe
            pose track. These fixtures demonstrate software behavior without
            measuring real-world model accuracy.
          </p>
          <h2>Pose extraction and its limits</h2>
          <p>
            Uploaded video can be processed with the locally hosted MediaPipe
            Pose Landmarker Lite model. Extraction samples presented frames,
            targets 10 Hz or 30 Hz with slower playback, and stores actual media
            timestamps and missing detections. A classic worker keeps inference
            off the UI thread where compatible; an explicit CPU main-thread
            fallback is used if initialization fails. Visibility, occlusion,
            camera perspective, decoding, and browser scheduling limit coverage.
            World landmarks are model estimates, not calibrated motion capture.
          </p>
          <h2>Prepare your recording</h2>
          <p>
            Collection studio records actual browser motion and optional camera
            video where supported. Select linear acceleration or acceleration
            including gravity explicitly; missing channels remain missing.
            Angular rate uses raw device axes, not a world orientation estimate.
            Save or export before leaving. Permission denial, absent
            measurements or incompatible devices have a CSV fallback.
          </p>
          <p>
            Use safely secured equipment and controlled shadow movements. Record
            distinct start and end cues, document source-clock times and
            uncertainty, and inspect the end residual. Offset-only alignment
            does not correct drift. No physical phone or paired tennis pilot is
            claimed by the software demonstration.
          </p>
          <p>
            Use MP4 H.264 or WebM VP8/VP9 up to 500 MiB, 10 minutes, and
            1920×1080 pixels. Import UTF-8 CSV measurements up to 50 MiB and
            1,000,000 rows. Map timestamps and complete xyz streams, declare
            units and gravity handling, and record sensor placement. Use
            extracted phyphox CSVs individually. Their layouts may differ.
          </p>
          <Link href="/record" className="text-link">
            Open Collection studio <ArrowUpRight size={15} />
          </Link>
          <h2>Accuracy needs an independent reference</h2>
          <p>
            Freeze an explicitly defined annotation set before evaluation.
            Matches use the stored interval, tolerance and one-to-one evaluation
            rule; reports retain false positives and missed references,
            including misses during unavailable observations. Different event
            definitions require a declared proxy hypothesis. Without an eligible
            reference, accuracy is unavailable. Generated fixture scores verify
            software behavior only.
          </p>
          <p>
            In Sensor Fusion Challenge, compare compatible runs, introduce
            controlled missing samples, noise, occlusion or timing error, then
            inspect actual changed results. Failure explorer seeks stored
            timestamps; its explanations do not diagnose a physical cause.
            Print-ready reports preserve computed results and the frozen
            configuration.
          </p>
        </section>
      </div>
    </Shell>
  );
}
