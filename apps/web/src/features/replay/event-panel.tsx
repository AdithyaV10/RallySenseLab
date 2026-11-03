"use client";
import { useState } from "react";
import { Plus, Trash2, Pencil, Check, X, LocateFixed } from "lucide-react";
import { api, Annotation, SessionDetail, clock } from "@/lib/api";
import { Badge } from "@/components/ui";
export function EventPanel({
  session,
  timeUs,
  onSeek,
  refresh,
  runId,
  onError,
  blind = false,
}: {
  session: SessionDetail;
  timeUs: number;
  onSeek: (t: number) => void;
  refresh: () => void;
  runId?: string;
  onError: (e: unknown) => void;
  blind?: boolean;
}) {
  const [type, setType] = useState("movement_reference"),
    [note, setNote] = useState(""),
    [editing, setEditing] = useState<Annotation | null>(null),
    [editTime, setEditTime] = useState(""),
    [busy, setBusy] = useState(false),
    [tab, setTab] = useState<"events" | "labels">("events");
  const events = session.predictions
    .filter((p) => p.run_id === runId)
    .sort((a, b) => a.t_session_us - b.t_session_us);
  const activeTab = blind ? "labels" : tab;
  async function action(fn: () => Promise<unknown>) {
    setBusy(true);
    try {
      await fn();
      refresh();
    } catch (e) {
      onError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="panel events-panel">
      <div className="event-tabs">
        {!blind && (
          <button
            className={activeTab === "events" ? "active" : ""}
            onClick={() => setTab("events")}
          >
            Signal events <span>{events.length}</span>
          </button>
        )}
        <button
          className={activeTab === "labels" ? "active" : ""}
          onClick={() => setTab("labels")}
        >
          References <span>{session.annotations.length}</span>
        </button>
      </div>
      {activeTab === "events" ? (
        <>
          <div className="event-explainer">
            <span className="small-label">ANGULAR-SPEED PEAKS</span>
            <p>
              Measured gyro events. Their relationship to tennis swings has not
              been validated.
            </p>
          </div>
          <div className="event-list">
            {events.map((p, i) => (
              <button
                key={p.id}
                className={`event-item ${Math.abs(p.t_session_us - timeUs) < 150000 ? "current" : ""}`}
                onClick={() => onSeek(p.t_session_us)}
              >
                <span className="event-number">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <strong>Gyro peak</strong>
                  <small>
                    {p.magnitude.toFixed(2)} rad/s · prominence{" "}
                    {p.prominence.toFixed(2)}
                  </small>
                </div>
                <time>{clock(p.t_session_us)}</time>
              </button>
            ))}
            {!events.length && (
              <div className="empty-state small">
                <LocateFixed size={22} />
                <p>Run the baseline to inspect calculated signal events.</p>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="annotation-list">
          {session.annotations
            .slice()
            .sort((a, b) => a.t_session_us - b.t_session_us)
            .map((a) => (
              <div className="annotation-item" key={a.id}>
                {editing?.id === a.id ? (
                  <>
                    <input
                      aria-label="Reference time in seconds"
                      type="number"
                      step=".001"
                      min="0"
                      value={editTime}
                      onChange={(e) => setEditTime(e.target.value)}
                    />
                    <button
                      className="icon-button"
                      aria-label="Save reference edit"
                      disabled={busy}
                      onClick={() =>
                        action(async () => {
                          await api(`/annotations/${a.id}`, {
                            method: "PATCH",
                            body: JSON.stringify({
                              ...a,
                              t_session_us: Math.round(Number(editTime) * 1e6),
                              revision: a.revision,
                            }),
                          });
                          setEditing(null);
                        })
                      }
                    >
                      <Check size={14} />
                    </button>
                    <button
                      className="icon-button"
                      aria-label="Cancel edit"
                      onClick={() => setEditing(null)}
                    >
                      <X size={14} />
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      className="annotation-jump"
                      onClick={() => onSeek(a.t_session_us)}
                    >
                      <strong>{a.event_type.replaceAll("_", " ")}</strong>
                      <small>
                        {clock(a.t_session_us)} ·{" "}
                        {a.note || "Manual observation"}
                      </small>
                    </button>
                    {a.event_type !== "synthetic_reference" ? (
                      <>
                        <button
                          className="icon-button"
                          aria-label="Edit reference"
                          onClick={() => {
                            setEditing(a);
                            setEditTime((a.t_session_us / 1e6).toFixed(3));
                          }}
                        >
                          <Pencil size={13} />
                        </button>
                        <button
                          className="icon-button"
                          aria-label="Delete reference"
                          disabled={busy}
                          onClick={() =>
                            action(() =>
                              api(
                                `/annotations/${a.id}?revision=${a.revision}`,
                                { method: "DELETE" },
                              ),
                            )
                          }
                        >
                          <Trash2 size={13} />
                        </button>
                      </>
                    ) : (
                      <Badge tone="amber">Generated</Badge>
                    )}
                  </>
                )}
              </div>
            ))}
        </div>
      )}
      <div className="annotation-form">
        <div className="panel-heading">
          <h3>Add a reference</h3>
          <span className="mono">{clock(timeUs)}</span>
        </div>
        <p>Independent observations stay separate from signal events.</p>
        <label className="field">
          EVENT TYPE
          <select
            aria-label="Reference event type"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <option value="movement_reference">Movement reference</option>
            <option value="swing_apex_v1">
              Swing apex · manual visual label
            </option>
            <option value="sync_cue">Synchronization cue</option>
          </select>
        </label>
        <input
          aria-label="Reference note"
          placeholder="Observation note (optional)"
          value={note}
          maxLength={1000}
          onChange={(e) => setNote(e.target.value)}
        />
        <button
          className="button secondary full"
          disabled={busy}
          onClick={() =>
            action(async () => {
              await api(`/sessions/${session.id}/annotations`, {
                method: "POST",
                body: JSON.stringify({
                  t_session_us: Math.round(timeUs),
                  event_type: type,
                  note,
                }),
              });
              setNote("");
              setTab("labels");
            })
          }
        >
          <Plus size={14} />
          Add marker at cursor
        </button>
      </div>
    </div>
  );
}
