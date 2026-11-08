import { NextRequest } from "next/server";
import { workspaceAccessResponse } from "@/lib/workspace-access";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
let activeUploads = 0;
const MAX_UPLOADS = 2;
const errorResponse = (status: number, code: string, message: string) =>
  Response.json(
    { error: { code, message } },
    { status, headers: { "cache-control": "no-store", connection: "close" } },
  );

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const denied = workspaceAccessResponse(request.headers);
  if (denied) return denied;
  const { path } = await context.params;
  const host = request.headers.get("host")?.split(":")[0];
  const allowedHosts = (
    process.env.WEB_ALLOWED_HOSTS || "127.0.0.1,localhost"
  ).split(",");
  if (!host || !allowedHosts.includes(host))
    return Response.json(
      { error: { message: "Local host required" } },
      { status: 403 },
    );
  const origin = request.headers.get("origin");
  const localOrigins = (
    process.env.WEB_ALLOWED_ORIGINS ||
    "http://127.0.0.1:3000,http://localhost:3000"
  ).split(",");
  if (origin && !localOrigins.includes(origin))
    return Response.json(
      { error: { message: "Origin rejected" } },
      { status: 403 },
    );
  if (
    !["GET", "HEAD"].includes(request.method) &&
    request.headers.get("x-lab-client") !== "rallysense"
  ) {
    return Response.json(
      { error: { message: "Local client header required" } },
      { status: 403 },
    );
  }
  const upload =
    request.method === "POST" &&
    ["videos", "sensor-imports"].includes(path.at(-1) || "");
  const limit =
    (upload ? (path.at(-1) === "videos" ? 501 : 51) : 2) * 1024 * 1024;
  const length = request.headers.get("content-length");
  if (length && (!/^\d+$/.test(length) || Number(length) > limit))
    return errorResponse(413, "RESOURCE_LIMIT", "Request body exceeds limit");
  if (upload && activeUploads >= MAX_UPLOADS)
    return new Response("Upload concurrency limit reached; retry shortly.", {
      status: 429,
      headers: { "retry-after": "5", "cache-control": "no-store" },
    });
  if (upload) activeUploads++;
  const controller = new AbortController();
  let exceeded = false,
    timedOut = false;
  const abort = () => controller.abort();
  request.signal.addEventListener("abort", abort, { once: true });
  if (request.signal.aborted) controller.abort();
  const timeout = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, 300_000);
  let idleTimer: ReturnType<typeof setTimeout>;
  const resetIdle = () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 30_000);
  };
  const reader = request.body?.getReader();
  let received = 0;
  const body =
    reader && !["GET", "HEAD"].includes(request.method)
      ? new ReadableStream<Uint8Array>(
          {
            async pull(output) {
              resetIdle();
              try {
                const chunk = await reader.read();
                clearTimeout(idleTimer);
                if (chunk.done) {
                  output.close();
                  return;
                }
                received += chunk.value.byteLength;
                if (received > limit) {
                  exceeded = true;
                  controller.abort();
                  void reader.cancel().catch(() => {});
                  output.error(new Error("Request body exceeds limit"));
                } else output.enqueue(chunk.value);
              } catch (error) {
                output.error(error);
              }
            },
            cancel: () => {
              void reader.cancel().catch(() => {});
            },
          },
          { highWaterMark: 1 },
        )
      : undefined;
  const headers = new Headers();
  for (const name of ["content-type", "range", "if-range"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  if (origin) headers.set("origin", origin);
  headers.set(
    "x-lab-token",
    process.env.LOCAL_TOKEN || "rallysense-local-development",
  );
  try {
    const upstream = await fetch(
      `${process.env.API_INTERNAL_URL || "http://127.0.0.1:8000"}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`,
      {
        method: request.method,
        headers,
        body,
        signal: controller.signal,
        redirect: "error",
        cache: "no-store",
        duplex: "half",
      } as RequestInit & { duplex: string },
    );
    const responseHeaders = new Headers();
    for (const name of [
      "content-type",
      "content-length",
      "content-range",
      "accept-ranges",
      "x-request-id",
      "retry-after",
    ]) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    responseHeaders.set("cache-control", "no-store");
    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    });
  } catch {
    if (exceeded)
      return errorResponse(413, "RESOURCE_LIMIT", "Request body exceeds limit");
    if (request.signal.aborted)
      return errorResponse(499, "CLIENT_ABORTED", "Upload cancelled");
    if (timedOut)
      return errorResponse(408, "REQUEST_TIMEOUT", "Request upload timed out");
    return Response.json(
      {
        error: {
          message: "API unavailable. Start the local API and database.",
        },
      },
      { status: 503 },
    );
  } finally {
    clearTimeout(timeout);
    clearTimeout(idleTimer!);
    request.signal.removeEventListener("abort", abort);
    if (upload) activeUploads--;
    // A cancelled incoming stream can wait for the client to close. Never hold
    // the rejection response or upload slot while awaiting that close handshake.
    if (reader) void reader.cancel().catch(() => {});
  }
}
export {
  proxy as GET,
  proxy as POST,
  proxy as PUT,
  proxy as PATCH,
  proxy as DELETE,
  proxy as HEAD,
};
