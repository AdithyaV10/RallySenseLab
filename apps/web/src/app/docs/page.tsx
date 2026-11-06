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
            Use MP4 H.264 or WebM VP8/VP9 up to 500 MiB, 10 minutes, and
            1920×1080 pixels. Import UTF-8 CSV measurements up to 50 MiB and
            1,000,000 rows. Map timestamps and complete xyz streams, declare
            units and gravity handling, and record sensor placement. Use
            extracted phyphox CSVs individually. Their layouts may differ.
          </p>
          <Link href="/record" className="text-link">
            Read the recording guide <ArrowUpRight size={15} />
          </Link>
        </section>
      </div>
    </Shell>
  );
}
