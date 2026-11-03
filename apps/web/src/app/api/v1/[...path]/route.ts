import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const host = request.headers.get("host")?.split(":")[0];
  if (host !== "127.0.0.1" && host !== "localhost")
    return Response.json(
      { error: { message: "Local host required" } },
      { status: 403 },
    );
  const origin = request.headers.get("origin");
  const localOrigins = ["http://127.0.0.1:3000", "http://localhost:3000"];
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
  const headers = new Headers();
  for (const name of ["content-type", "range", "if-range"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
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
        body: ["GET", "HEAD"].includes(request.method)
          ? undefined
          : request.body,
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
    return Response.json(
      {
        error: {
          message: "API unavailable. Start the local API and database.",
        },
      },
      { status: 503 },
    );
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
