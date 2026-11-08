import { NextResponse, type NextRequest } from "next/server";
import { workspaceAccessResponse } from "@/lib/workspace-access";

/** Optional single-workspace gate for trusted local HTTPS. Not a multiuser identity system. */
export function proxy(request: NextRequest) {
  return workspaceAccessResponse(request.headers) || NextResponse.next();
}

// API routes apply the same gate themselves, before consuming a bounded stream.
// Running global Proxy there would clone/truncate the incoming multipart body.
export const config = { matcher: "/((?!api/).*)" };
