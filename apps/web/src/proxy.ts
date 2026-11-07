import { NextResponse, type NextRequest } from "next/server";
import { timingSafeEqual, createHash } from "node:crypto";

/** Optional single-workspace gate for trusted local HTTPS. Not a multiuser identity system. */
export function proxy(request: NextRequest) {
  const password = process.env.SITE_ACCESS_PASSWORD;
  if (!password) return NextResponse.next();
  const authorization = request.headers.get("authorization") || "";
  let supplied = "";
  if (authorization.startsWith("Basic ")) {
    try {
      supplied = Buffer.from(authorization.slice(6), "base64").toString("utf8");
    } catch {
      /* challenge */
    }
  }
  const expected = `lab:${password}`;
  const digest = (s: string) => createHash("sha256").update(s).digest();
  if (
    password.length < 20 ||
    !timingSafeEqual(digest(supplied), digest(expected))
  )
    return new NextResponse("Workspace access requires operator credentials.", {
      status: 401,
      headers: {
        "WWW-Authenticate":
          'Basic realm="RallySense local workspace", charset="UTF-8"',
        "Cache-Control": "no-store",
      },
    });
  return NextResponse.next();
}
