"use client";
import { Experiment, modeOf, percent, millis, record } from "./types";
import Link from "next/link";
import { comparisonCompatible, comparisonInsight } from "./insights";
import { FailureExplorer } from "./failure-explorer";

export function ResultComparison({
  runs,
  onSeek,
}: {
  runs: Experiment[];
  onSeek: (time: number) => void;
}) {
  if (!runs.length)
    return (
      <div className="research-empty">
        <span>01 / ESTABLISH A BASELINE</span>
        <h3>Your observations, tested.</h3>
        <p>
          Run a mode to see computed events, measured quality, and processing
          time. Accuracy appears only with an eligible frozen reference.
        </p>
      </div>
    );
  const comparable = comparisonCompatible(runs);
  return (
    <>
      {!comparable && (
        <div className="research-notice">
          Different references, intervals, tolerance, hypothesis, or alignment.
          Inspect separately; metric differences do not isolate algorithm
          effects.
        </div>
      )}
      <div
        className="research-results"
        style={{
          gridTemplateColumns: `repeat(${runs.length}, minmax(0, 1fr))`,
        }}
      >
        {runs.map((run) => {
          const result = run.result,
            score = result.evaluation,
            request = record(run.manifest.request);
          const start = Number(request.start_us || 0),
            end = Number(request.end_us || 18e6);
          const x = (time: number) =>
            Math.max(0, Math.min(100, ((time - start) / (end - start)) * 100));
          const components = Object.entries(result.components || {});
          return (
            <article
              className={`panel research-result ${modeOf(run)}`}
              key={run.id}
              data-testid="experiment-result"
            >
              <div className="research-result-head">
                <span className="eyebrow">
                  {modeOf(run).toUpperCase()} / {run.status}
                </span>
                <span className="mono">{run.id.slice(0, 8)}</span>
              </div>
              <h3>{run.name}</h3>
              <p className="research-algorithm">
                {String(run.manifest.algorithm)}
              </p>
              {run.error && <div className="error-box">{run.error}</div>}
              <div className="research-result-count">
                <strong>
                  {run.status === "succeeded"
                    ? (result.events || []).length
                    : "—"}
                </strong>
                <span>
                  computed events
                  <br />
                  {result.processing_ms == null
                    ? "Awaiting worker"
                    : `${result.processing_ms.toFixed(1)} ms processing`}
                </span>
              </div>
              <div
                className="research-event-lane"
                aria-label={`${modeOf(run)} prediction timeline`}
              >
                {(result.events || []).map((e, i) => (
                  <button
                    key={i}
                    style={{ left: `${x(e.t_session_us)}%` }}
                    aria-label={`Inspect ${modeOf(run)} event ${(e.t_session_us / 1e6).toFixed(2)} seconds`}
                    title={`${(e.t_session_us / 1e6).toFixed(3)} s · ${e.event_type}`}
                    onClick={() => onSeek(e.t_session_us)}
                  />
                ))}
              </div>
              <div className="research-axis">
                <span>{(start / 1e6).toFixed(2)} s</span>
                <span>{(end / 1e6).toFixed(2)} s</span>
              </div>
              {!!result.references?.length && (
                <>
                  <div
                    className="research-reference-lane"
                    aria-label="Frozen reference timeline"
                  >
                    {result.references.map((ref, i) => {
                      const t = Number(ref.t_session_us);
                      return (
                        <button
                          key={i}
                          style={{ left: `${x(t)}%` }}
                          aria-label={`Inspect reference ${(t / 1e6).toFixed(2)} seconds`}
                          title={`Frozen reference ${(t / 1e6).toFixed(3)} s`}
                          onClick={() => onSeek(t)}
                        />
                      );
                    })}
                  </div>
                  <small className="research-reference-caption">
                    FROZEN REFERENCES · SAME SESSION CLOCK
                  </small>
                </>
              )}
              {components.map(([name, component]) => {
                const points = (component.signal || []).filter(
                  (p) => p.t_session_us >= start && p.t_session_us <= end,
                );
                const finite = points.filter((p) => p.value != null);
                const max = Math.max(1, ...finite.map((p) => p.value!));
                const steps = points
                  .slice(1)
                  .map((p, i) => p.t_session_us - points[i].t_session_us)
                  .sort((a, b) => a - b);
                const gap = (steps[Math.floor(steps.length / 2)] || 1e5) * 3;
                let previous: number | null = null;
                const path = points
                  .map((p) => {
                    if (p.value == null) {
                      previous = null;
                      return "";
                    }
                    const command =
                      previous == null || p.t_session_us - previous > gap
                        ? "M"
                        : "L";
                    previous = p.t_session_us;
                    return `${command}${x(p.t_session_us) * 6},${65 - (p.value / max) * 55}`;
                  })
                  .join(" ");
                return (
                  <div className="research-mini-signal" key={name}>
                    <div>
                      <span>{name.toUpperCase()} OBSERVATIONS</span>
                      <small>{component.score_kind}</small>
                    </div>
                    <svg
                      viewBox="0 0 600 72"
                      role="img"
                      aria-label={`${name} computed signal`}
                      preserveAspectRatio="none"
                    >
                      <path
                        d={path}
                        fill="none"
                        stroke={name === "imu" ? "#73dfbb" : "#9ea7ff"}
                        strokeWidth="1.7"
                        vectorEffect="non-scaling-stroke"
                      />
                    </svg>
                  </div>
                );
              })}
              {score ? (
                <>
                  <div className="research-score-grid">
                    <div>
                      <small>PRECISION</small>
                      <strong>{percent(score.precision)}</strong>
                    </div>
                    <div>
                      <small>RECALL</small>
                      <strong>{percent(score.recall)}</strong>
                    </div>
                    <div>
                      <small>F1</small>
                      <strong>{percent(score.f1)}</strong>
                    </div>
                  </div>
                  <div className="research-counts">
                    <span>
                      TP <b>{score.tp}</b>
                    </span>
                    <span>
                      FP <b>{score.fp}</b>
                    </span>
                    <span>
                      FN <b>{score.fn}</b>
                    </span>
                  </div>
                  <dl className="research-stats">
                    <div>
                      <dt>Mean absolute timing error</dt>
                      <dd>{millis(score.mean_absolute_error_us)}</dd>
                    </div>
                    <div>
                      <dt>Median absolute timing error</dt>
                      <dd>{millis(score.median_absolute_error_us)}</dd>
                    </div>
                    <div>
                      <dt>Matching tolerance</dt>
                      <dd>{millis(score.tolerance_us)}</dd>
                    </div>
                  </dl>
                </>
              ) : (
                <div className="research-unscored">
                  <strong>Accuracy unavailable</strong>
                  <p>
                    No eligible frozen reference was scored. Event counts and
                    strength are not accuracy.
                  </p>
                </div>
              )}
              <p className="research-evidence">{result.evaluation_note}</p>
              {run.id !== runs[0].id && (
                <p className="research-insight">
                  {comparisonInsight(runs[0], run)}
                </p>
              )}
              <FailureExplorer run={run} onSeek={onSeek} />
              <details>
                <summary>Quality & failure inspection</summary>
                <pre>
                  {JSON.stringify(
                    {
                      quality: result.quality,
                      coverage: result.coverage,
                      components: Object.fromEntries(
                        components.map(([k, v]) => [k, v.quality]),
                      ),
                      artificial_corruption: result.corruption,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
              <details>
                <summary>Events & timing errors</summary>
                <div className="research-event-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Event</th>
                        <th>Time</th>
                        <th>Strength</th>
                        <th>Error</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(result.events || []).map((e, i) => (
                        <tr key={i}>
                          <td>
                            <button onClick={() => onSeek(e.t_session_us)}>
                              #{i + 1}
                            </button>
                          </td>
                          <td>{(e.t_session_us / 1e6).toFixed(3)} s</td>
                          <td>{e.magnitude.toFixed(2)}</td>
                          <td>
                            {millis(
                              score?.matches.find(
                                (m) => m.prediction_index === i,
                              )?.absolute_error_us,
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {score && (
                  <p>
                    Unmatched predictions:{" "}
                    {score.unmatched_predictions.map((i) => i + 1).join(", ") ||
                      "none"}
                    . Missed reference times:{" "}
                    {score.missed_references
                      .map(
                        (i) =>
                          `${(Number(result.references?.[i]?.t_session_us) / 1e6).toFixed(3)} s`,
                      )
                      .join(", ") || "none"}
                    .
                  </p>
                )}
              </details>
              <details>
                <summary>Frozen configuration & limitations</summary>
                <pre>{JSON.stringify(run.manifest, null, 2)}</pre>
                {(result.limitations || []).map((text) => (
                  <p key={text}>{text}</p>
                ))}
              </details>
              <div className="research-export">
                <Link
                  className="button secondary"
                  href={`/experiments/${run.id}/report`}
                >
                  Print-ready report
                </Link>
                <a
                  className="button secondary"
                  href={`/api/v1/experiments/${run.id}/report`}
                  download
                >
                  Export Markdown
                </a>
                <button
                  className="button ghost"
                  onClick={() => {
                    const url = URL.createObjectURL(
                      new Blob([JSON.stringify(run, null, 2)], {
                        type: "application/json",
                      }),
                    );
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `rallysense-${run.id}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  JSON
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}
