import {execFileSync} from "node:child_process";
import {readFileSync} from "node:fs";
const before=readFileSync("apps/web/src/lib/schema.d.ts","utf8");
execFileSync(process.platform==="win32"?"uv.exe":"uv",["run","--project","apps/api","python","scripts/export_openapi.py"],{stdio:"inherit"});
// cmd shims cannot be passed to execFile on Windows; use the package's actual JS entry point.
execFileSync(process.execPath,["apps/web/node_modules/openapi-typescript/bin/cli.js","packages/shared-contracts/openapi.json","-o","apps/web/src/lib/schema.d.ts"],{stdio:"inherit"});
execFileSync(process.execPath,["apps/web/node_modules/prettier/bin/prettier.cjs","--write","apps/web/src/lib/schema.d.ts"],{stdio:"inherit"});
const after=readFileSync("apps/web/src/lib/schema.d.ts","utf8");
if(before!==after){console.error("Generated API contract drift. Review and commit regenerated files.");process.exitCode=1;}else console.log("API contract matches Pydantic OpenAPI.");
