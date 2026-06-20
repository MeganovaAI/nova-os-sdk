import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";
const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

describe("projects", () => {
  it("createProject POSTs {name} and maps the project", async () => {
    const fetchMock = vi.fn(async () => mk({ id: "p1", owner_id: "u", name: "Acme", description: "d", created_at: "t1", updated_at: "t2" }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const p = await client.createProject({ name: "Acme" });
    expect(p).toEqual({ id: "p1", name: "Acme", description: "d", createdAt: "t1", updatedAt: "t2" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/v1/projects");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toEqual({ name: "Acme" });
  });

  it("listProjects unwraps {projects}", async () => {
    const fetchMock = vi.fn(async () => mk({ projects: [{ id: "p1", owner_id: "u", name: "Acme", created_at: "t1", updated_at: "t2" }] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listProjects();
    expect(out).toEqual([{ id: "p1", name: "Acme", description: undefined, createdAt: "t1", updatedAt: "t2" }]);
  });

  it("listProjectConversations GETs /v1/projects/:id/conversations", async () => {
    const fetchMock = vi.fn(async () => mk({ conversations: [{ id: "c1", agent_id: "m", title: null, created_at: "t", last_active_at: "t", message_count: 1, project_id: "p1" }] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listProjectConversations("p1");
    expect(out[0]!.projectId).toBe("p1");
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toContain("/v1/projects/p1/conversations");
  });

  it("createConversation POSTs project_id; delete/rename use DELETE/PATCH", async () => {
    const calls: Array<{ url: string; init: RequestInit }> = [];
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => { calls.push({ url, init }); return mk({ id: "c1", agent_id: "m", title: null, created_at: "t", last_active_at: "t", message_count: 0, project_id: "p1" }, 201); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const conv = await client.createConversation({ id: "c1", agentId: "m", projectId: "p1" });
    expect(conv.projectId).toBe("p1");
    expect(calls[0]!.url).toContain("/v1/conversations");
    expect(JSON.parse(calls[0]!.init.body as string)).toEqual({ id: "c1", agent_id: "m", project_id: "p1" });
    await client.deleteProject("p1"); await client.renameProject("p1", { name: "New" });
    expect(calls[1]!.init.method).toBe("DELETE");
    expect(calls[2]!.init.method).toBe("PATCH");
    expect(JSON.parse(calls[2]!.init.body as string)).toEqual({ name: "New" });
  });
});
