"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { components } from "@/lib/schema";
import { Badge, ErrorBox, Loading } from "./ui";
import { useState } from "react";
export function Diagnostics() {
  const [error, setError] = useState<unknown>(null);
  const query = useQuery({
    queryKey: ["diagnostics"],
    queryFn: async () => {
      const start = performance.now();
      const data =
        await api<components["schemas"]["DiagnosticsOut"]>("/diagnostics");
      return { ...data, roundTripMs: performance.now() - start };
    },
    refetchInterval: 10_000,
  });
  const d = query.data;
  if (!d)
    return query.isLoading ? (
      <Loading label="Checking local services" />
    ) : (
      <ErrorBox error={query.error} />
    );
  return (
    <>
      <div className="measurement-strip">
        <div>
          <span>
            <small>DATABASE</small>
            <strong>{d.database}</strong>
          </span>
        </div>
        <div>
          <span>
            <small>WORKER HEARTBEAT</small>
            <strong>{d.worker}</strong>
          </span>
        </div>
        <div>
          <span>
            <small>API ROUND TRIP</small>
            <strong>
              {d.roundTripMs.toFixed(0)}
              <em> ms</em>
            </strong>
          </span>
        </div>
        <div>
          <span>
            <small>STORAGE FREE</small>
            <strong>
              {d.storage_free_bytes === null
                ? "unknown"
                : `${(d.storage_free_bytes / 1024 ** 3).toFixed(1)} GiB`}
            </strong>
          </span>
        </div>
      </div>
      <section className="panel capture-card">
        <Badge tone={d.mode === "local" ? "teal" : "amber"}>{d.mode}</Badge>
        <h2>Runtime readiness</h2>
        <p>
          Environment {d.environment} · build {d.build_id} · Python{" "}
          {d.python_version}
          <br />
          Migration {d.migration} · FFprobe{" "}
          {d.ffprobe_available ? "available" : "unavailable"}
          <br />
          Worker state {d.worker_state ?? "unknown"} · heartbeat age{" "}
          {d.worker_age_s?.toFixed(1) ?? "unknown"} s. A heartbeat older than 45
          seconds is stale.
        </p>
        <p>
          Job counts below cover the latest 100 visible jobs, not a lifetime
          total.
        </p>
        <pre>{JSON.stringify(d.job_counts, null, 2)}</pre>
        <ErrorBox error={error || query.error} />
        <div className="quality-list">
          {d.recent_jobs.map((j) => (
            <div key={j.id}>
              <b>{j.kind}</b>
              <Badge tone={j.state === "failed" ? "red" : "neutral"}>
                {j.state}
              </Badge>
              <span>
                {j.id.slice(0, 8)} · attempt {j.attempt}
              </span>
              {j.error && <span>{j.error}</span>}
              {d.mutations_allowed &&
                ["failed", "cancelled"].includes(j.state) &&
                ["normalize", "video_probe"].includes(j.kind) && (
                  <button
                    className="button small"
                    onClick={async () => {
                      try {
                        await api(`/jobs/${j.id}/retry`, { method: "POST" });
                        await query.refetch();
                      } catch (e) {
                        setError(e);
                      }
                    }}
                  >
                    Retry source validation
                  </button>
                )}
            </div>
          ))}
        </div>
        <p>
          Retry creates a new source-validation job and preserves the failed
          record. Scientific experiments must be rerun as new immutable
          experiments.
        </p>
      </section>
    </>
  );
}
