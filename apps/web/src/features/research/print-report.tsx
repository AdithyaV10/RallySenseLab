"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ErrorBox, Loading, Badge } from "@/components/ui";
import { type Experiment, percent, millis, record, modeOf } from "./types";
export function PrintReport({ id }: { id: string }) {
  const query = useQuery({
    queryKey: ["experiment", id],
    queryFn: () => api<Experiment>(`/experiments/${id}`),
  });
  if (query.isLoading) return <Loading label="Loading stored experiment" />;
  const run = query.data;
  if (!run) return <ErrorBox error={query.error} />;
  const score = run.result.evaluation,
    kind = String(record(run.manifest.session).dataset_kind || "unknown");
  return (
    <main className="print-report">
      <div className="report-actions">
        <Link
          className="button"
          href={`/sessions/${run.session_id}?tab=research`}
        >
          Return to research
        </Link>
        <button className="button primary" onClick={() => window.print()}>
          Print / Save PDF
        </button>
        <a
          className="button"
          href={`/api/v1/experiments/${id}/report`}
          download
        >
          Download Markdown
        </a>
      </div>
      <div className="eyebrow">RALLYSENSE LAB / EXPERIMENT RECORD</div>
      <h1>{run.name}</h1>
      <Badge tone={kind === "synthetic" ? "amber" : "neutral"}>
        {kind} observations · {run.status}
      </Badge>
      <p>{run.result.evaluation_note}</p>
      <p>
        Experiment {run.id}
        <br />
        Created {run.created_at}
        <br />
        Mode {modeOf(run)} · {String(run.manifest.algorithm)}
        <br />
        Question:{" "}
        {String(record(run.manifest.request).question || "Not recorded")}
      </p>
      <h2>Computed observations</h2>
      <p>
        {(run.result.events || []).length} events ·{" "}
        {run.result.processing_ms?.toFixed(1) ?? "unknown"} ms processing.
        Strength and event count are not accuracy.
      </p>
      {score ? (
        <p>
          Precision {percent(score.precision)} · Recall {percent(score.recall)}{" "}
          · F1 {percent(score.f1)}
          <br />
          TP {score.tp} · FP {score.fp} · FN {score.fn}
          <br />
          Mean absolute timing error {millis(score.mean_absolute_error_us)} ·
          tolerance {millis(score.tolerance_us)}
        </p>
      ) : (
        <p>Accuracy unavailable: no eligible frozen reference was scored.</p>
      )}
      <table>
        <thead>
          <tr>
            <th>Event</th>
            <th>Session seconds</th>
            <th>Definition</th>
            <th>Strength</th>
            <th>Timing error</th>
          </tr>
        </thead>
        <tbody>
          {(run.result.events || []).map((e, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>{(e.t_session_us / 1e6).toFixed(6)}</td>
              <td>{e.event_type}</td>
              <td>{e.magnitude.toFixed(4)}</td>
              <td>
                {millis(
                  score?.matches.find((m) => m.prediction_index === i)
                    ?.absolute_error_us,
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Quality, pairing & limitations</h2>
      {run.error && <p>{run.error}</p>}
      {(run.result.limitations || []).map((s) => (
        <p key={s}>{s}</p>
      ))}
      <pre>
        {JSON.stringify(
          {
            quality: run.result.quality,
            coverage: run.result.coverage,
            corruption: run.result.corruption,
            sync: run.manifest.sync,
          },
          null,
          2,
        )}
      </pre>
      <details className="report-manifest">
        <summary>Inspect frozen reproducibility manifest</summary>
        <pre>{JSON.stringify(run.manifest, null, 2)}</pre>
      </details>
      <section className="report-print-manifest">
        <h2>Frozen reproducibility manifest</h2>
        <pre>{JSON.stringify(run.manifest, null, 2)}</pre>
      </section>
      <p>
        Generated from the stored experiment. Synthetic fixture results verify
        software behavior. No independent tennis accuracy, ball impact
        detection, biomechanical reconstruction or calibrated confidence is
        established.
      </p>
    </main>
  );
}
