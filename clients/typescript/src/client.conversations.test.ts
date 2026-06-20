import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

describe("conversations", () => {
  it("listConversations: GET /v1/conversations with agent+limit, envelope→array, snake→camel", async () => {
    const fetchMock = vi.fn(async () =>
      mk({ conversations: [{ id: "c1", agent_id: "marketing", title: "Q3", created_at: "t1", last_active_at: "t2", message_count: 4 }] }),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listConversations({ agentId: "marketing", limit: 20 });
    expect(out).toEqual([{ id: "c1", agentId: "marketing", title: "Q3", createdAt: "t1", lastActiveAt: "t2", messageCount: 4, projectId: null }]);
    const [url] = fetchMock.mock.calls[0] as unknown as [string];
    expect(url).toContain("/v1/conversations");
    expect(url).toContain("agent=marketing");
    expect(url).toContain("limit=20");
  });

  it("getConversation: returns {conversation, messages} mapped", async () => {
    const fetchMock = vi.fn(async () =>
      mk({ id: "c1", agent_id: "marketing", title: null, created_at: "t1", last_active_at: "t2", message_count: 2,
           messages: [{ id: "m1", role: "user", content: "hi", timestamp: "ts1", seq: 1 }] }),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.getConversation("c1");
    expect(out.conversation).toEqual({ id: "c1", agentId: "marketing", title: null, createdAt: "t1", lastActiveAt: "t2", messageCount: 2, projectId: null });
    expect(out.messages).toEqual([{ id: "m1", role: "user", content: "hi", timestamp: "ts1", seq: 1 }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toContain("/v1/conversations/c1");
  });

  it("deleteConversation: DELETE; renameConversation: PATCH with title", async () => {
    const calls: Array<{ url: string; init: RequestInit }> = [];
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => { calls.push({ url, init }); return mk({}); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.deleteConversation("c1");
    await client.renameConversation("c1", "New title");
    expect(calls[0]!.init.method).toBe("DELETE");
    expect(calls[0]!.url).toContain("/v1/conversations/c1");
    expect(calls[1]!.init.method).toBe("PATCH");
    expect(JSON.parse(calls[1]!.init.body as string)).toEqual({ title: "New title" });
  });

  it("rejects on non-ok", async () => {
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: (async () => mk("e", 500)) as unknown as typeof fetch });
    await expect(client.listConversations()).rejects.toBeTruthy();
  });
});
