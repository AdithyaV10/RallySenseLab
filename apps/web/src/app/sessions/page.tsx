"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Search,
  Play,
  FlaskConical,
  CalendarDays,
  Trash2,
  FileVideo,
  Activity,
} from "lucide-react";
import { api, LabSession, provenanceLabel } from "@/lib/api";
import { Shell, Badge, ErrorBox, Loading, Modal } from "@/components/ui";
import { Court } from "@/components/court";
export default function Sessions() {
  const router = useRouter(),
    query = useQueryClient();
  const [search, setSearch] = useState(""),
    [open, setOpen] = useState(false),
    [title, setTitle] = useState(""),
    [datasetKind, setDatasetKind] = useState("recorded"),
    [handedness, setHandedness] = useState("right"),
    [deleting, setDeleting] = useState<LabSession | null>(null);
  const sessions = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api<LabSession[]>("/sessions"),
  });
  const create = useMutation({
    mutationFn: () =>
      api<LabSession>("/sessions", {
        method: "POST",
        body: JSON.stringify({ title, dataset_kind: datasetKind, handedness }),
      }),
    onSuccess: (s) => {
      query.invalidateQueries({ queryKey: ["sessions"] });
      router.push(`/sessions/${s.id}?tab=data`);
    },
  });
  const demo = useMutation({
    mutationFn: () => api<LabSession>("/demo-sessions", { method: "POST" }),
    onSuccess: (s) => router.push(`/sessions/${s.id}`),
  });
  const remove = useMutation({
    mutationFn: () => api(`/sessions/${deleting?.id}`, { method: "DELETE" }),
    onSuccess: () => {
      setDeleting(null);
      query.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
  const filtered =
    sessions.data?.filter((s) =>
      s.title.toLowerCase().includes(search.toLowerCase()),
    ) || [];
  return (
    <Shell>
      <div className="page-content">
        <div className="page-heading">
          <div>
            <div className="eyebrow">YOUR RESEARCH WORKSPACE</div>
            <h1>
              Session library<span className="heading-dot">.</span>
            </h1>
            <p>Collect observations. Connect timelines. Stay curious.</p>
          </div>
          <button className="button primary" onClick={() => setOpen(true)}>
            <Plus size={17} />
            New session
          </button>
        </div>
        <div className="library-feature">
          <div className="feature-copy">
            <Badge tone="teal">
              <FlaskConical size={12} /> THE BASELINE STUDY
            </Badge>
            <h2>
              Start with a signal.
              <br />
              Follow the movement.
            </h2>
            <p>
              Explore a deterministic synthetic recording with synchronized
              signal traces, calculated gyro peaks, and generated reference
              markers.
            </p>
            <button
              className="button light"
              disabled={demo.isPending}
              onClick={() => demo.mutate()}
            >
              <Play size={15} />
              {demo.isPending ? "Preparing…" : "Open demonstration"}
              <ArrowUpRight size={16} />
            </button>
            <small>SYNTHETIC FIXTURE · NOT REAL-WORLD VALIDATION</small>
          </div>
          <div className="feature-court">
            <Court compact time={1.3} />
          </div>
        </div>
        <ErrorBox error={sessions.error || demo.error} />
        <div className="section-toolbar">
          <div className="section-label">
            ALL SESSIONS <span>{sessions.data?.length ?? 0}</span>
          </div>
          <label className="search-box">
            <Search size={15} />
            <input
              aria-label="Search sessions"
              placeholder="Search your sessions…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        {sessions.isLoading ? (
          <Loading />
        ) : (
          <div className="session-grid">
            {filtered.map((s) => (
              <article className="session-card" key={s.id}>
                <div className="session-card-top">
                  <span className={`session-symbol ${s.dataset_kind}`}>
                    <Activity size={22} />
                  </span>
                  <Badge
                    tone={s.dataset_kind === "synthetic" ? "amber" : "neutral"}
                  >
                    {provenanceLabel(s.dataset_kind)}
                  </Badge>
                  <button
                    className="icon-button delete-session"
                    aria-label={`Delete ${s.title}`}
                    onClick={() => setDeleting(s)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <Link href={`/sessions/${s.id}`} className="session-card-title">
                  <h3>{s.title}</h3>
                  <ArrowUpRight size={19} />
                </Link>
                <p>
                  {s.notes ||
                    "A new recording workspace. Add video or sensor measurements to begin."}
                </p>
                <div className="session-card-meta">
                  <span>
                    <CalendarDays size={13} />
                    {new Date(s.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </span>
                  <span>{s.handedness} handed</span>
                </div>
                <Link className="card-open" href={`/sessions/${s.id}`}>
                  Open workspace <ArrowRight size={15} />
                </Link>
              </article>
            ))}
            <button
              className="session-card new-card"
              onClick={() => setOpen(true)}
            >
              <span>
                <Plus size={23} />
              </span>
              <h3>Create a new study</h3>
              <p>Bring your own video and motion data.</p>
            </button>
          </div>
        )}
        <div className="research-note">
          <FileVideo size={18} />
          <p>
            <strong>Your recordings stay local.</strong> Videos and measurements
            are stored in this workspace until you delete their session.{" "}
            <Link href="/docs">
              Storage & methodology <ArrowUpRight size={12} />
            </Link>
          </p>
        </div>
        <Modal
          open={open}
          onOpenChange={setOpen}
          title="Create a session"
          description="Start a private local workspace for a recording."
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              create.mutate();
            }}
          >
            <label className="field">
              SESSION NAME
              <input
                autoFocus
                required
                maxLength={160}
                placeholder="e.g. Forehand practice / 01"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </label>
            <label className="field">
              DATASET ORIGIN
              <select
                aria-label="Dataset origin"
                value={datasetKind}
                onChange={(e) => setDatasetKind(e.target.value)}
              >
                <option value="recorded">Recorded observations</option>
                <option value="synthetic">Synthetic software fixture</option>
                <option value="mixed">
                  Mixed recorded and synthetic sources
                </option>
              </select>
            </label>
            <label className="field">
              DOMINANT HAND
              <select
                value={handedness}
                onChange={(e) => setHandedness(e.target.value)}
              >
                <option value="right">Right hand</option>
                <option value="left">Left hand</option>
              </select>
            </label>
            <ErrorBox error={create.error} />
            <button
              className="button primary"
              disabled={create.isPending || !title.trim()}
            >
              {create.isPending ? "Creating…" : "Create session"}
              <ArrowRight size={16} />
            </button>
          </form>
        </Modal>
        <Modal
          open={!!deleting}
          onOpenChange={(v) => {
            if (!v) setDeleting(null);
          }}
          title="Delete session?"
          description={`Remove “${deleting?.title}” and its recordings, annotations, and results. File cleanup runs as a tracked local job.`}
        >
          <ErrorBox error={remove.error} />
          <button
            className="button danger"
            disabled={remove.isPending}
            onClick={() => remove.mutate()}
          >
            Delete session and data
          </button>
        </Modal>
      </div>
    </Shell>
  );
}
