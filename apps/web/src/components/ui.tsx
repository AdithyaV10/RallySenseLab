"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  ChevronRight,
  FlaskConical,
  LayoutGrid,
  Radio,
  RefreshCw,
} from "lucide-react";
import * as Dialog from "@radix-ui/react-dialog";

export function Brand() {
  return (
    <Link href="/" className="brand">
      <span className="brand-mark">
        <Activity size={21} />
      </span>
      <span>
        RallySense<span className="brand-lab"> LAB</span>
      </span>
    </Link>
  );
}
export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand />
        <div className="nav-caption">WORKSPACE</div>
        <nav>
          <Link
            className={path.startsWith("/sessions") ? "active" : ""}
            href="/sessions"
          >
            <LayoutGrid size={17} />
            Sessions
            <ChevronRight size={14} />
          </Link>
          <Link className={path === "/record" ? "active" : ""} href="/record">
            <Radio size={17} />
            Recording guide
          </Link>
          <Link className={path === "/docs" ? "active" : ""} href="/docs">
            <BookOpen size={17} />
            Lab notes
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <div className="local-status">
            <i /> LOCAL WORKSPACE
          </div>
          <p>
            Observations first.
            <br />
            Evidence follows.
          </p>
          <span className="version">FOUNDATION / V0.2</span>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            <FlaskConical size={15} />
            <span>Movement intelligence</span>
            <span className="topbar-slash">/</span>
            <b>Research workspace</b>
          </div>
          <Link href="/docs">
            Methodology <ArrowUpRight size={14} />
          </Link>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "teal" | "amber" | "red";
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <div className="error-box" role="alert">
      {error instanceof Error ? error.message : String(error)}
    </div>
  );
}
export function Loading({ label = "Loading workspace" }: { label?: string }) {
  return (
    <div className="loading">
      <RefreshCw size={18} className="spin" />
      {label}
    </div>
  );
}
export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="modal-overlay" />
        <Dialog.Content className="modal-content">
          <Dialog.Title>{title}</Dialog.Title>
          <Dialog.Description>{description}</Dialog.Description>
          {children}
          <Dialog.Close className="modal-close" aria-label="Close dialog">
            ×
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
