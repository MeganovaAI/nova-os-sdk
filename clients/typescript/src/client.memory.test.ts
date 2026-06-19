import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("getMemory", () => {
  it("GETs /v1/managed/memory with agent_id + scope, maps snake→camel", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            agent_id: "marketing",
            scope: "personal",
            content: "- prefers bullets",
            last_observed_at: "2026-06-18T10:22:00Z",
            updated_at: "2026-06-18T10:22:00Z",
            enabled: true,
          }),
          { status: 200, headers: { "content-type": "application/json" } },
        ),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.getMemory("marketing", { scope: "personal" });
    expect(out).toEqual({
      agentId: "marketing",
      scope: "personal",
      content: "- prefers bullets",
      lastObservedAt: "2026-06-18T10:22:00Z",
      enabled: true,
    });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/v1/managed/memory");
    expect(url).toContain("agent_id=marketing");
    expect(url).toContain("scope=personal");
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer tok");
  });

  it("rejects on a non-ok response", async () => {
    const fetchMock = vi.fn(async () => new Response("bad", { status: 500 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await expect(client.getMemory("marketing")).rejects.toBeTruthy();
  });
});
