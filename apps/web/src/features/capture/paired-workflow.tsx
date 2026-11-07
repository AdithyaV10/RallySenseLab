"use client";
import Link from "next/link";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Link2 } from "lucide-react";
import { api, type LabSession, type SessionDetail } from "@/lib/api";
import type { components } from "@/lib/schema";
import { Badge, ErrorBox } from "@/components/ui";
import { DataManager } from "@/features/ingestion/data-manager";
import { MotionCapture } from "./motion-capture";
import { CameraCapture } from "./camera-capture";
import { AlignmentEditor } from "./sync-editor";
type Profile = components["schemas"]["CollectionProfile"];
const emptyProfile: Profile = {
  participant_pseudonym: "",
  movement: "",
  camera_view: "",
  sensor_placement: "",
  attachment: "",
  device_model: "",
  conditions: "",
  consent_confirmed: false,
  pairing_note: "",
};
const fields: [keyof Omit<Profile, "consent_confirmed">, string][] = [
  ["participant_pseudonym", "Participant pseudonym"],
  ["movement", "Movement / task"],
  ["camera_view", "Camera view / distance"],
  ["sensor_placement", "Sensor placement"],
  ["attachment", "Secure attachment method"],
  ["device_model", "Device model / sensor app"],
  ["conditions", "Conditions / recording notes"],
  ["pairing_note", "Pairing evidence / cue plan"],
];

export function PairedWorkflow() {
  const [sessionId, setSessionId] = useState(""),
    [title, setTitle] = useState(""),
    [profile, setProfile] = useState<Profile>(emptyProfile),
    [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(false);
  const [kind, setKind] = useState<"recorded" | "synthetic">("recorded"),
    [handedness, setHandedness] = useState<"left" | "right">("right");
  const queryClient = useQueryClient();
  const capabilities = useQuery({
    queryKey: ["capabilities"],
    queryFn: () =>
      api<components["schemas"]["CapabilitiesOut"]>("/capabilities"),
  });
  const library = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api<LabSession[]>("/sessions"),
  });
  const detail = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => api<SessionDetail>(`/sessions/${sessionId}`),
    enabled: !!sessionId,
    refetchInterval: sessionId ? 2000 : false,
  });
  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
  };
  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const row = await api<LabSession>("/sessions", {
        method: "POST",
        body: JSON.stringify({
          title,
          dataset_kind: kind,
          handedness,
          collection_profile: profile,
        }),
      });
      setSessionId(row.id);
      void queryClient.invalidateQueries({ queryKey: ["sessions"] });
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  if (capabilities.data && !capabilities.data.mutations_allowed)
    return (
      <div className="panel capture-card">
        <Badge tone="amber">READ-ONLY DEMONSTRATION</Badge>
        <h2>Collection is disabled in this workspace.</h2>
        <p>
          Explore approved synthetic sessions. Capture, uploads, metadata edits
          and experiments are blocked by the API.
        </p>
        <Link className="button" href="/sessions">
          Explore demonstrations <ArrowRight size={15} />
        </Link>
      </div>
    );
  const session = detail.data;
  return (
    <>
      <div className="collection-steps" aria-label="Collection workflow">
        <span>
          <b>01</b> Describe
        </span>
        <span>
          <b>02</b> Capture / import
        </span>
        <span>
          <b>03</b> Inspect quality
        </span>
        <span>
          <b>04</b> Align & analyze
        </span>
      </div>
      <section className="panel capture-card">
        <div className="capture-card-title">
          <h2>{session ? session.title : "Prepare a paired session"}</h2>
          {session && <Badge tone="teal">SESSION SAVED</Badge>}
        </div>
        {!sessionId && (
          <>
            <label>
              Continue an existing session
              <select
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
              >
                <option value="">Create a new collection below</option>
                {library.data?.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </label>
            <form onSubmit={create} className="collection-form">
              <label>
                Session title
                <input
                  required
                  maxLength={160}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Controlled movement · session 01"
                />
              </label>
              <label>
                Source provenance
                <select
                  value={kind}
                  onChange={(e) => setKind(e.target.value as typeof kind)}
                >
                  <option value="recorded">Recorded observations</option>
                  <option value="synthetic">Synthetic software test</option>
                </select>
              </label>
              <ProfileFields profile={profile} setProfile={setProfile} />
              <label>
                Dominant hand
                <select
                  value={handedness}
                  onChange={(e) =>
                    setHandedness(e.target.value as typeof handedness)
                  }
                >
                  <option value="right">Right</option>
                  <option value="left">Left</option>
                </select>
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  required
                  checked={profile.consent_confirmed}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      consent_confirmed: e.target.checked,
                    }))
                  }
                />
                I have permission to record and store these observations.
              </label>
              <button
                className="button primary"
                disabled={busy || !capabilities.data?.mutations_allowed}
              >
                {busy ? "Creating…" : "Create collection session"}
                <ArrowRight size={15} />
              </button>
            </form>
          </>
        )}
        {session && (
          <>
            <div className="collection-metadata">
              {fields.map(([key, label]) => (
                <div key={key}>
                  <span>{label}</span>
                  <b>{String(session.collection_profile[key] || "unknown")}</b>
                </div>
              ))}
            </div>
            <div className="capture-actions">
              <Link className="button" href={`/sessions/${session.id}`}>
                Open replay <ArrowRight size={15} />
              </Link>
              <button className="button" onClick={() => setSessionId("")}>
                Choose another session
              </button>
            </div>
            <CollectionEditor
              key={session.collection_revision}
              session={session}
              refresh={refresh}
            />
          </>
        )}
        <ErrorBox error={error || detail.error} />
      </section>
      {session && (
        <>
          <div className="capture-grid">
            <MotionCapture
              key={`motion-${session.id}`}
              session={session}
              refresh={refresh}
            />
            <CameraCapture
              key={`camera-${session.id}`}
              session={session}
              refresh={refresh}
            />
          </div>
          <section className="panel capture-card">
            <Badge>EXTERNAL RECORDINGS</Badge>
            <DataManager session={session} refresh={refresh} />
          </section>
          <AlignmentEditor session={session} refresh={refresh} />
        </>
      )}
      <div className="research-note">
        <Link2 size={20} />
        <p>
          Use a fixed camera and a safely attached sensor. Record a visible
          sensor-detectable cue at the start and end. Simultaneous start buttons
          do not establish a shared clock.{" "}
          <Link href="/docs">Read the collection methodology.</Link>
        </p>
      </div>
    </>
  );
}
function ProfileFields({
  profile,
  setProfile,
}: {
  profile: Profile;
  setProfile: React.Dispatch<React.SetStateAction<Profile>>;
}) {
  return (
    <>
      {fields.map(([key, label]) => (
        <label key={key}>
          {label}
          <input
            required={key === "participant_pseudonym" || key === "movement"}
            maxLength={
              key === "conditions"
                ? 1000
                : key === "pairing_note"
                  ? 1500
                  : key === "participant_pseudonym"
                    ? 80
                    : 160
            }
            value={profile[key] ?? ""}
            onChange={(e) =>
              setProfile((p) => ({ ...p, [key]: e.target.value }))
            }
          />
        </label>
      ))}
    </>
  );
}
function CollectionEditor({
  session,
  refresh,
}: {
  session: SessionDetail;
  refresh: () => void;
}) {
  const [profile, setProfile] = useState<Profile>({
      ...emptyProfile,
      ...session.collection_profile,
    } as Profile),
    [error, setError] = useState<unknown>(null),
    [busy, setBusy] = useState(false);
  return (
    <details className="collection-editor">
      <summary>
        Edit collection metadata · revision {session.collection_revision}
      </summary>
      <form
        className="collection-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setError(null);
          try {
            await api(`/sessions/${session.id}/collection`, {
              method: "PATCH",
              body: JSON.stringify({
                revision: session.collection_revision,
                profile,
              }),
            });
            refresh();
          } catch (e) {
            setError(e);
          } finally {
            setBusy(false);
          }
        }}
      >
        <ProfileFields profile={profile} setProfile={setProfile} />
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={profile.consent_confirmed}
            onChange={(e) =>
              setProfile((p) => ({ ...p, consent_confirmed: e.target.checked }))
            }
          />
          Recording consent confirmed
        </label>
        <button className="button" disabled={busy}>
          Save metadata revision
        </button>
        <ErrorBox error={error} />
      </form>
    </details>
  );
}
