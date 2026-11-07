import { Shell, Badge } from "@/components/ui";
import { PairedWorkflow } from "@/features/capture/paired-workflow";
export default function Record() {
  return (
    <Shell>
      <div className="page-content collection-page">
        <div className="eyebrow">OBSERVATIONS / COLLECTION STUDIO</div>
        <h1>
          Make movement measurable<span className="heading-dot">.</span>
        </h1>
        <p className="docs-lead">
          Describe the attempt. Capture the signals. Preserve the clocks.
        </p>
        <Badge tone="teal">REAL CAPTURE · EXPLICIT PROVENANCE</Badge>
        <PairedWorkflow />
      </div>
    </Shell>
  );
}
