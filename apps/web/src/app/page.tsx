"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Activity,
  Layers3,
  ScanLine,
  MoveUpRight,
} from "lucide-react";

import { Brand, Badge, ErrorBox } from "@/components/ui";
import { openDemonstration, useCapabilities } from "@/lib/capabilities";
import { Court } from "@/components/court";
export default function Landing() {
  const router = useRouter();
  const capabilities = useCapabilities();
  const paired = useMutation({
    mutationFn: () => openDemonstration(true),
    onSuccess: (s) => router.push(`/sessions/${s.id}?tab=research`),
  });
  const demo = useMutation({
    mutationFn: () => openDemonstration(),
    onSuccess: (s) => router.push(`/sessions/${s.id}`),
  });
  return (
    <div className="landing">
      <nav className="landing-nav">
        <Brand />
        <div>
          <Link href="/docs">The methodology</Link>
          <Link className="button secondary" href="/sessions">
            Open workspace <ArrowUpRight size={15} />
          </Link>
        </div>
      </nav>
      <div className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="tiny-line" /> SPARSE SIGNALS. DEEPER QUESTIONS.
          </div>
          <h1>
            Understand
            <br />
            the movement.
            <br />
            <em>Question the signal.</em>
          </h1>
          <p>
            A research workspace connecting video observations with inertial
            data. See the motion, inspect the evidence, and explore what a
            sparse sensor can actually tell you.
          </p>
          <div className="hero-actions">
            <button
              className="button primary"
              disabled={demo.isPending}
              onClick={() => demo.mutate()}
            >
              {demo.isPending ? "Preparing session…" : "Explore the demo"}
              <ArrowRight size={17} />
            </button>
            <Link className="text-link" href="/sessions">
              Enter the lab <ArrowUpRight size={16} />
            </Link>
          </div>
          <button
            className="text-link"
            disabled={paired.isPending || !capabilities.data}
            onClick={() => paired.mutate()}
          >
            Explore the paired research demo <ArrowUpRight size={16} />
          </button>
          <ErrorBox error={demo.error || paired.error} />
          <div className="hero-footnote">
            <span className="dot" />
            Local-first research platform <span>04 / RESEARCH & CAPTURE</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="visual-bar">
            <span>
              <i /> MOVEMENT OBSERVATORY
            </span>
            <Badge tone="amber">Synthetic illustration</Badge>
          </div>
          <Court time={1.3} />
          <div className="visual-footer">
            <div>
              <small>OBSERVATION</small>
              <strong>Every signal has a story.</strong>
            </div>
            <div className="axis-icon">
              <MoveUpRight size={31} />
            </div>
          </div>
          <div className="visual-caption">
            Programmatic visual · No athlete measurement or accuracy claim
          </div>
        </div>
      </div>
      <section className="landing-features">
        <div>
          <span className="section-number">01 / THE TOOLKIT</span>
          <h2>
            One timeline.
            <br />
            Multiple perspectives.
          </h2>
        </div>
        {[
          {
            icon: ScanLine,
            title: "Observe",
            text: "Extract actual pose landmarks with MediaPipe. Keep visibility, missing frames, and source timestamps in view.",
          },
          {
            icon: Activity,
            title: "Inspect",
            text: "Import motion measurements. Normalize units, find signal peaks, and examine the quality behind each observation.",
          },
          {
            icon: Layers3,
            title: "Align",
            text: "Bring video and sensor clocks together. Add independent reference labels without losing their provenance.",
          },
        ].map((item) => (
          <article key={item.title}>
            <item.icon size={22} />
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </section>
      <footer className="landing-footer">
        <Brand />
        <span>Built for exploration. Grounded in evidence.</span>
        <Link href="/docs">
          Read the research notes <ArrowUpRight size={14} />
        </Link>
      </footer>
    </div>
  );
}
