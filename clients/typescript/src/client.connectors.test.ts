import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const raw = {
  kind: "freshdesk", tenant_id: "acme", enabled: true, group_id: "support",
  config: { subdomain: "acme" }, secret_keys: ["api_key", "webhook_secret"], updated_at: "t1",
};

describe("connector configs", () => {
  it("listConnectorConfigs unwraps {connectors} and maps the masked view", async () => {
    const fetchMock = vi.fn(async () => mk({ connectors: [raw] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.listConnectorConfigs()).toEqual([{
      kind: "freshdesk", tenantId: "acme", enabled: true, groupId: "support",
      config: { subdomain: "acme" }, secretKeys: ["api_key", "webhook_secret"], updatedAt: "t1",
    }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/connectors");
  });

  it("putConnectorConfig PUTs snake_case with secrets merge payload", async () => {
    const fetchMock = vi.fn(async () => mk({ connector: raw }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.putConnectorConfig("freshdesk", {
      enabled: true, groupId: "support",
      config: { subdomain: "acme" },
      secrets: { api_key: "rotated", webhook_secret: "" },
    });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/connectors/freshdesk");
    expect(init.method).toBe("PUT");
    expect(JSON.parse(init.body as string)).toMatchObject({
      enabled: true, group_id: "support",
      config: { subdomain: "acme" },
      secrets: { api_key: "rotated", webhook_secret: "" },
    });
  });

  it("getConnectorConfig unwraps {connector}; delete DELETEs", async () => {
    const calls: string[] = [];
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => { calls.push(`${init.method} ${url}`); return mk({ connector: raw }); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect((await client.getConnectorConfig("freshdesk")).secretKeys).toContain("api_key");
    await client.deleteConnectorConfig("freshdesk");
    expect(calls).toEqual([
      "GET http://x/v1/managed/connectors/freshdesk",
      "DELETE http://x/v1/managed/connectors/freshdesk",
    ]);
  });
});
