import { afterEach, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { proxy } from "@/proxy";
afterEach(() => vi.unstubAllEnvs());
it("keeps ordinary loopback access available when the optional gate is unset", () => {
  vi.stubEnv("SITE_ACCESS_PASSWORD", "");
  expect(proxy(new NextRequest("http://localhost/")).status).toBe(200);
});
it("challenges every path and requires the full configured workspace credential", () => {
  const password = "synthetic-gate-test-password-only";
  vi.stubEnv("SITE_ACCESS_PASSWORD", password);
  expect(
    proxy(new NextRequest("https://example.invalid/api/v1/sessions")).status,
  ).toBe(401);
  const request = (credential: string) =>
    new NextRequest("https://example.invalid/pose-worker.js", {
      headers: {
        authorization: `Basic ${Buffer.from(credential).toString("base64")}`,
      },
    });
  expect(proxy(request("lab:wrong")).status).toBe(401);
  expect(proxy(request(`lab:${password}`)).status).toBe(200);
  expect(proxy(request(`someone:${password}`)).status).toBe(401);
  vi.stubEnv("SITE_ACCESS_PASSWORD", "short");
  expect(proxy(request("lab:short")).status).toBe(401);
});
