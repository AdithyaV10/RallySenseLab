"use client";
import { useState } from "react";
import { api, SessionDetail } from "@/lib/api";
import { FreezeRequest, LabelSet, Reference } from "./types";

export function ReferenceManager({
  session,
  sets,
  references,
  refresh,
  action,
  busy,
}: {
  session: SessionDetail;
  sets: LabelSet[];
  references: Reference[];
  refresh: () => void;
  action: (fn: () => Promise<unknown>) => Promise<void>;
  busy: boolean;
}) {
  const [setId, setSetId] = useState("");
  const selected = sets.find((s) => s.id === setId) || sets[0];
  const [name, setName] = useState("Independent visual labels");
  const [eventType, setEventType] =
    useState<FreezeRequest["event_type"]>("movement_reference");
  const [time, setTime] = useState("0");
  const [definition, setDefinition] = useState("");
  const [procedure, setProcedure] = useState("");
  const [labeler, setLabeler] = useState("local-labeler");
  const [independent, setIndependent] = useState(false);
  const [videoId, setVideoId] = useState(session.videos[0]?.id || "");
  const generated = selected?.provenance === "synthetic";
  return (
    <details className="panel research-reference">
      <summary>
        <span>Reference laboratory</span>
        <span>
          {references.length} frozen snapshots · create, label & freeze
        </span>
      </summary>
      <p>
        Use blinded replay before labeling. Freezing copies this revision; later
        edits cannot change completed experiments. Generated labels establish
        software behavior only.
      </p>
      <div className="research-fields">
        <label className="field">
          Annotation set
          <select
            aria-label="Annotation set"
            value={selected?.id || ""}
            onChange={(e) => setSetId(e.target.value)}
          >
            {sets.map((s) => (
              <option value={s.id} key={s.id}>
                {s.name} · revision {s.revision} · {s.provenance}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          New set name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <button
          className="button secondary"
          disabled={busy}
          onClick={() =>
            action(async () => {
              const s = await api<LabelSet>(
                `/sessions/${session.id}/annotation-sets`,
                { method: "POST", body: JSON.stringify({ name }) },
              );
              setSetId(s.id);
              refresh();
            })
          }
        >
          Create annotation set
        </button>
      </div>
      <div className="research-fields">
        <label className="field">
          Event definition
          <select
            aria-label="Reference event definition"
            disabled={generated}
            value={generated ? "synthetic_reference" : eventType}
            onChange={(e) =>
              setEventType(e.target.value as FreezeRequest["event_type"])
            }
          >
            <option value="movement_reference">Human movement reference</option>
            <option value="swing_apex_v1">
              Visible wrist extension (swing_apex_v1)
            </option>
            <option value="gyro_peak_v1">Angular-speed maximum</option>
            <option value="wrist_speed_peak_v1">
              Image wrist-speed maximum
            </option>
            <option value="multimodal_association_v1">
              Multimodal temporal association
            </option>
            <option value="synthetic_reference">
              Generated fixture reference
            </option>
          </select>
        </label>
        <label className="field">
          Label time (seconds)
          <input
            aria-label="Research label time"
            type="number"
            min="0"
            step=".01"
            value={time}
            onChange={(e) => setTime(e.target.value)}
          />
        </label>
        <button
          className="button secondary"
          disabled={busy || !selected || generated}
          onClick={() =>
            action(async () => {
              await api(
                `/sessions/${session.id}/annotations?set_id=${selected!.id}`,
                {
                  method: "POST",
                  body: JSON.stringify({
                    t_session_us: Math.round(Number(time) * 1e6),
                    event_type: eventType,
                    note: procedure,
                  }),
                },
              );
              refresh();
            })
          }
        >
          Add research label
        </button>
      </div>
      <div className="research-fields">
        <label className="field">
          Operational definition
          <textarea
            aria-label="Operational definition"
            value={definition}
            onChange={(e) => setDefinition(e.target.value)}
            placeholder="Describe the exact observable event and tie rule."
          />
        </label>
        <label className="field">
          Labeling procedure
          <textarea
            aria-label="Labeling procedure"
            value={procedure}
            onChange={(e) => setProcedure(e.target.value)}
            placeholder="Source, blinded procedure, ambiguity and exclusions."
          />
        </label>
        <label className="field">
          Labeler pseudonym
          <input value={labeler} onChange={(e) => setLabeler(e.target.value)} />
        </label>
      </div>
      <label className="field">
        Reference source video
        <select
          aria-label="Reference source video"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
        >
          <option value="">No video / document source in procedure</option>
          {session.videos.map((video) => (
            <option value={video.id} key={video.id}>
              {video.name}
            </option>
          ))}
        </select>
      </label>
      <div className="research-actions">
        <label className="check-label">
          <input
            type="checkbox"
            checked={independent && !generated}
            disabled={generated}
            onChange={(e) => setIndependent(e.target.checked)}
          />{" "}
          I labeled independently of predictions
        </label>
        <button
          className="button primary"
          disabled={
            busy || !selected || definition.length < 12 || procedure.length < 12
          }
          onClick={() =>
            action(async () => {
              const payload: FreezeRequest = {
                revision: selected!.revision,
                event_type: generated ? "synthetic_reference" : eventType,
                definition,
                procedure,
                labeler,
                independent: independent && !generated,
                video_id: videoId || undefined,
              };
              await api(`/annotation-sets/${selected!.id}/freeze`, {
                method: "POST",
                body: JSON.stringify(payload),
              });
              refresh();
            })
          }
        >
          Freeze reference revision
        </button>
      </div>
      <small>
        {selected
          ? `${session.annotations.filter((a) => a.set_id === selected.id && a.event_type === (generated ? "synthetic_reference" : eventType)).length} labels of the selected event type will be frozen.`
          : "Create an annotation set to begin."}{" "}
        Empty reference sets mean explicitly reviewed negative intervals, not
        unavailable labels.
      </small>
    </details>
  );
}
