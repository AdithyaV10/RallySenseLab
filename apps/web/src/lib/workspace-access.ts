import { timingSafeEqual, createHash } from "node:crypto";

/** Shared single-workspace gate. API routes authenticate independently of Next Proxy. */
export function workspaceAccessResponse(headers: Headers): Response | null {
  const password = process.env.SITE_ACCESS_PASSWORD;
  if (!password && process.env.REQUIRE_WORKSPACE_AUTH !== "true") return null;
  const authorization = headers.get("authorization") || "";
  const supplied = authorization.startsWith("Basic ")
    ? Buffer.from(authorization.slice(6), "base64").toString("utf8")
    : "";
  const digest = (value: string) => createHash("sha256").update(value).digest();
  if (
    !password ||
    password.startsWith("CHANGE_ME") ||
    password.length < 20 ||
    !timingSafeEqual(digest(supplied), digest(`lab:${password}`))
  ) {
    return new Response("Workspace access requires operator credentials.", {
      status: 401,
      headers: {
        "WWW-Authenticate":
          'Basic realm="RallySense workspace", charset="UTF-8"',
        "Cache-Control": "no-store",
      },
    });
  }
  return null;
}
