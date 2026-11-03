import Link from "next/link";
import { ArrowRight, Radio, FileSpreadsheet } from "lucide-react";
import { Shell, Badge } from "@/components/ui";
export default function Record() {
  return (
    <Shell>
      <div className="page-content docs-page">
        <div className="eyebrow">COLLECTION NOTES</div>
        <h1>
          Start with a good recording<span className="heading-dot">.</span>
        </h1>
        <p className="docs-lead">
          Consistent placement and explicit clocks matter more than a
          complicated capture setup.
        </p>
        <div className="panel prose-panel">
          <Badge tone="teal">
            <FileSpreadsheet size={12} />
            CSV INGESTION AVAILABLE
          </Badge>
          <h2>Collect, export, inspect.</h2>
          <ol>
            <li>
              Record a video with the subject and movement visible. Keep the
              camera fixed.
            </li>
            <li>
              Capture acceleration and angular-rate measurements with a phone
              sensor application such as phyphox. Secure the phone safely and
              document placement.
            </li>
            <li>
              Include a deliberate visible and sensor-detectable movement cue
              before the task. Keep it separate from the movements you want to
              study.
            </li>
            <li>
              Export UTF-8 CSV measurements. Preserve original units and any
              pause/resume metadata.
            </li>
            <li>
              Create a session, upload the video and CSV, review the mapping,
              then align their clocks in replay.
            </li>
          </ol>
          <Link href="/sessions" className="button primary">
            Open the session library <ArrowRight size={16} />
          </Link>
        </div>
        <div className="research-note">
          <Radio size={20} />
          <p>
            <strong>Phone browser capture is planned for Step 4.</strong> The
            current MVP supports CSV import. Live sensor capture has not been
            validated on physical iOS or Android hardware.
          </p>
        </div>
      </div>
    </Shell>
  );
}
