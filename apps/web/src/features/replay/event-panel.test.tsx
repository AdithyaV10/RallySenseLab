import React from "react";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { it, expect, vi, afterEach } from "vitest";
import { EventPanel } from "./event-panel";
import type { SessionDetail } from "@/lib/api";
afterEach(cleanup);
const session = {
  id: "session",
  annotations: [
    {
      id: "label",
      set_id: "set",
      t_session_us: 2e6,
      event_type: "synthetic_reference",
      revision: 1,
      note: "Generated pulse center",
    },
  ],
  predictions: [
    {
      id: "peak",
      run_id: "run",
      t_session_us: 2.2e6,
      event_type: "gyro_peak_v1",
      magnitude: 6.5,
      prominence: 6,
    },
  ],
} as SessionDetail;
it("keeps measured events distinct from immutable generated references", () => {
  const seek = vi.fn();
  render(
    <EventPanel
      session={session}
      timeUs={0}
      onSeek={seek}
      refresh={() => {}}
      runId="run"
      onError={() => {}}
    />,
  );
  expect(screen.getByText(/not been validated/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /Gyro peak/ }));
  expect(seek).toHaveBeenCalledWith(2.2e6);
  fireEvent.click(screen.getByRole("button", { name: /References/ }));
  expect(screen.getByText("Generated")).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Edit reference" }),
  ).not.toBeInTheDocument();
});
it("removes prediction navigation while labeling blind", () => {
  render(
    <EventPanel
      session={session}
      timeUs={0}
      onSeek={() => {}}
      refresh={() => {}}
      runId="run"
      onError={() => {}}
      blind
    />,
  );
  expect(
    screen.queryByRole("button", { name: /Signal events/ }),
  ).not.toBeInTheDocument();
  expect(screen.getByText("Generated")).toBeInTheDocument();
});
