"use client";
import { useQuery } from "@tanstack/react-query";
import { api, type LabSession } from "./api";
import type { components } from "./schema";
export function useCapabilities() {
  return useQuery({
    queryKey: ["capabilities"],
    queryFn: () =>
      api<components["schemas"]["CapabilitiesOut"]>("/capabilities"),
    staleTime: 60_000,
  });
}
export async function openDemonstration(paired = false) {
  const capabilities =
    await api<components["schemas"]["CapabilitiesOut"]>("/capabilities");
  if (capabilities.mutations_allowed)
    return api<LabSession>(
      paired ? "/research-demo-sessions" : "/demo-sessions",
      { method: "POST" },
    );
  const demos = await api<LabSession[]>("/demonstrations");
  const selected = demos.find((s) =>
    paired
      ? s.title.startsWith("Paired motion")
      : s.title.startsWith("Baseline"),
  );
  if (!selected)
    throw new Error(
      "No approved demonstration is available. The operator must seed and allowlist it before enabling read-only mode.",
    );
  return selected;
}
