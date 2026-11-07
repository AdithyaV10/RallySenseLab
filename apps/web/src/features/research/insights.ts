import { type Experiment, record } from "./types";
export function comparisonCompatible(runs: Experiment[]) {
  if (!runs.length) return false;
  const signature = (r: Experiment) =>
    JSON.stringify([
      r.session_id,
      r.manifest.reference,
      record(r.manifest.request).start_us,
      record(r.manifest.request).end_us,
      record(r.manifest.request).tolerance_us,
      record(r.manifest.request).comparison,
      record(r.manifest.request).hypothesis,
    ]);
  const syncs = runs.map((r) => record(r.manifest.sync).id).filter(Boolean);
  const inputIds = (key: string) =>
    runs.map((r) => record(record(r.manifest.inputs)[key]).id).filter(Boolean);
  return (
    runs.every((r) => signature(r) === signature(runs[0])) &&
    new Set(syncs).size <= 1 &&
    ["sensor", "pose"].every((key) => new Set(inputIds(key)).size <= 1)
  );
}
export function comparisonInsight(base: Experiment, other: Experiment) {
  if (!comparisonCompatible([base, other]))
    return "References, sources, intervals, hypotheses or alignment differ. Metric changes do not isolate an algorithm effect.";
  const a = base.result,
    b = other.result;
  const count = (b.events?.length || 0) - (a.events?.length || 0);
  const delta = `${count >= 0 ? "+" : ""}${count} events relative to ${base.name}.`;
  const score =
    a.evaluation?.f1 != null && b.evaluation?.f1 != null
      ? ` F1 difference ${((b.evaluation.f1 - a.evaluation.f1) * 100).toFixed(1)} percentage points under the frozen evaluation contract.`
      : " Accuracy difference unavailable without defined scores for both runs.";
  const condition =
    JSON.stringify(a.corruption) !== JSON.stringify(b.corruption)
      ? " Stored input corruption differs; inspect the exact conditions below."
      : " Stored corruption settings agree.";
  return (
    delta +
    score +
    condition +
    " These are observed software outputs, not proof of real-world fusion benefit."
  );
}
