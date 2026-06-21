import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";
const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(b === null ? null : JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

describe("move + facts", () => {
  it("moveConversation PATCHes project_id (and '' for General)", async () => {
    const calls: RequestInit[] = [];
    const fetchMock = vi.fn(async (_u: string, init: RequestInit) => { calls.push(init); return mk(null, 204); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.moveConversation("c1", "p1");
    await client.moveConversation("c1", null);
    expect(calls[0]!.method).toBe("PATCH");
    expect(JSON.parse(calls[0]!.body as string)).toEqual({ project_id: "p1" });
    expect(JSON.parse(calls[1]!.body as string)).toEqual({ project_id: "" });
  });
  it("setProjectFacts PATCHes facts; Project maps facts", async () => {
    const fetchMock = vi.fn(async () => mk(null, 204));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.setProjectFacts("p1", ["a", "b"]);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/v1/projects/p1");
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string)).toEqual({ facts: ["a", "b"] });
  });
  it("listProjects maps facts from the response", async () => {
    const fetchMock = vi.fn(async () => mk({ projects: [{ id: "p1", owner_id: "u", name: "Acme", created_at: "t", updated_at: "t", facts: ["x"] }] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listProjects();
    expect(out[0]!.facts).toEqual(["x"]);
  });
});
