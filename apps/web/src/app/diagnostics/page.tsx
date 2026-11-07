import { Shell } from "@/components/ui";
import { Diagnostics } from "@/components/diagnostics";
export default function DiagnosticsPage() {
  return (
    <Shell>
      <div className="page-content">
        <div className="eyebrow">SYSTEM / OBSERVABILITY</div>
        <h1>
          Workspace readiness<span className="heading-dot">.</span>
        </h1>
        <p className="docs-lead">
          Live service checks and processing state. Unknown means unobserved.
        </p>
        <Diagnostics />
      </div>
    </Shell>
  );
}
