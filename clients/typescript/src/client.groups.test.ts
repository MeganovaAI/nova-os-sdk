import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const rawGroup = {
  id: "grp_1", tenant_id: "acme", name: "support", description: "Support team",
  created_at: "t1", updated_at: "t2",
};

describe("groups", () => {
  it("listGroups unwraps {groups} and maps snake_case", async () => {
    const fetchMock = vi.fn(async () => mk({ groups: [rawGroup] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.listGroups()).toEqual([
      { id: "grp_1", tenantId: "acme", name: "support", description: "Support team", createdAt: "t1", updatedAt: "t2", members: undefined },
    ]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/groups");
  });

  it("createGroup POSTs {name, description}", async () => {
    const fetchMock = vi.fn(async () => mk({ group: rawGroup }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const g = await client.createGroup({ name: "support", description: "Support team" });
    expect(g.id).toBe("grp_1");
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toEqual({ name: "support", description: "Support team" });
  });

  it("getGroup maps members with roles", async () => {
    const fetchMock = vi.fn(async () =>
      mk({ group: { ...rawGroup, members: [{ user_id: "u1", role: "approver", created_at: "t3" }] } }),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const g = await client.getGroup("grp_1");
    expect(g.members).toEqual([{ userId: "u1", role: "approver", createdAt: "t3" }]);
  });

  it("member add/remove hit the members subresource; deleteGroup DELETEs", async () => {
    const calls: Array<{ url: string; init: RequestInit }> = [];
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => { calls.push({ url, init }); return mk({}); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.addGroupMember("grp_1", "u1", "approver");
    await client.removeGroupMember("grp_1", "u1");
    await client.deleteGroup("grp_1");
    expect(calls.map((c) => `${c.init.method} ${c.url}`)).toEqual([
      "POST http://x/v1/managed/groups/grp_1/members",
      "DELETE http://x/v1/managed/groups/grp_1/members/u1",
      "DELETE http://x/v1/managed/groups/grp_1",
    ]);
    expect(JSON.parse(calls[0]!.init.body as string)).toEqual({ user_id: "u1", role: "approver" });
  });
});
