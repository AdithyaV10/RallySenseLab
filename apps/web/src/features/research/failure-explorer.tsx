import { type Experiment, record, millis } from "./types";
export function FailureExplorer({
  run,
  onSeek,
}: {
  run: Experiment;
  onSeek: (time: number) => void;
}) {
  const result = run.result,
    score = result.evaluation,
    request = record(run.manifest.request);
  const start = Number(request.start_us || 0),
    end = Number(request.end_us || 0);
  const components = Object.entries(result.components || {});
  return (
    <details className="failure-explorer">
      <summary>
        Failure explorer · matched, unmatched & missing observations
      </summary>
      <p>
        Jump to the stored session timestamp. Missing observation windows can
        explain unavailable evidence; they do not establish the physical cause
        of a mismatch.
      </p>
      <div className="failure-links">
        {score?.matches.map((m, i) => (
          <button
            className="button ghost small"
            key={`match-${i}`}
            onClick={() => onSeek(m.prediction_us)}
          >
            Matched #{m.prediction_index + 1} · {millis(m.signed_error_us)}{" "}
            signed
          </button>
        ))}
        {score?.unmatched_predictions.map((i) => (
          <button
            className="button ghost small"
            key={`fp-${i}`}
            onClick={() => onSeek((result.events || [])[i].t_session_us)}
          >
            Unmatched prediction #{i + 1} ·{" "}
            {((result.events || [])[i].t_session_us / 1e6).toFixed(3)} s
          </button>
        ))}
        {score?.missed_references.map((i) => (
          <button
            className="button ghost small"
            key={`fn-${i}`}
            onClick={() => onSeek(Number(result.references?.[i]?.t_session_us))}
          >
            Missed reference #{i + 1} ·{" "}
            {(Number(result.references?.[i]?.t_session_us) / 1e6).toFixed(3)} s
          </button>
        ))}
      </div>
      {!score && (
        <p>Unscored run: no true/false-positive interpretation is available.</p>
      )}
      {components.map(([name, c]) => {
        let cursor = start;
        const gaps: { start: number; end: number }[] = [];
        for (const interval of [...(c.eligible_intervals || [])].sort(
          (a, b) => a.start_us - b.start_us,
        )) {
          if (interval.start_us > cursor)
            gaps.push({ start: cursor, end: Math.min(end, interval.start_us) });
          cursor = Math.max(cursor, interval.end_us);
        }
        if (cursor < end) gaps.push({ start: cursor, end });
        return (
          <div className="failure-links" key={name}>
            {gaps
              .filter((g) => g.end > g.start)
              .slice(0, 30)
              .map((g, i) => (
                <button
                  className="button ghost small"
                  key={i}
                  onClick={() => onSeek((g.start + g.end) / 2)}
                >
                  {name} unavailable {(g.start / 1e6).toFixed(2)}–
                  {(g.end / 1e6).toFixed(2)} s
                </button>
              ))}
          </div>
        );
      })}
    </details>
  );
}
