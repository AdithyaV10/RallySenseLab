import fs from "node:fs";
import path from "node:path";
const root = path.resolve("apps/showcase");
const lines = [
  "RallySense Lab — static showcase",
  "",
  "The generated motion video, analytical landmarks and synthetic signals are project-created fixtures. They are not athlete recordings or MediaPipe output.",
  "No MediaPipe runtime/model or FFmpeg executable is included.",
  "",
];
for (const name of ["react", "react-dom", "scheduler", "lucide-react"]) {
  const dir = path.join(root, "node_modules", name);
  const pkg = JSON.parse(
    fs.readFileSync(path.join(dir, "package.json"), "utf8"),
  );
  const file = fs
    .readdirSync(dir)
    .find((n) => /^license(?:\.txt|\.md)?$/i.test(n));
  if (!file) throw new Error(`Missing upstream license: ${name}`);
  lines.push(
    `===== ${name} ${pkg.version} (${pkg.license}) =====`,
    fs.readFileSync(path.join(dir, file), "utf8"),
    "",
  );
}
fs.writeFileSync(path.join(root, "public/NOTICES.txt"), lines.join("\n").trimEnd() + "\n");
console.log(
  "Preserved actual installed React, React DOM, Scheduler and Lucide licenses.",
);
