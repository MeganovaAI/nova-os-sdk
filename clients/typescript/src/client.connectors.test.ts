import { describe, it, expect, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const raw = {
  kind: "freshdesk", tenant_id: "acme", enabled: true, group_id: "support",
  config: { subdomain: "acme" }, secret_keys: ["api_key", "webhook_secret"], updated_at: "t1",
  governance_mode: "external", governance_enforcement: "audited; connector service receives credentials",
};

describe("connector configs", () => {
  it("listConnectorConfigs unwraps {connectors} and maps the masked view", async () => {
    const fetchMock = vi.fn(async () => mk({ connectors: [raw] }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.listConnectorConfigs()).toEqual([{
      kind: "freshdesk", tenantId: "acme", enabled: true, groupId: "support",
      config: { subdomain: "acme" }, secretKeys: ["api_key", "webhook_secret"], updatedAt: "t1",
      // #240 policy: absent on the wire reads as false, i.e. deny-by-default.
      personalAllowed: false,
      governanceMode: "external",
      governanceEnforcement: "audited; connector service receives credentials",
    }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/connectors");
  });

  it("putConnectorConfig PUTs snake_case with secrets merge payload", async () => {
    const fetchMock = vi.fn(async () => mk({ connector: raw }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
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
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect((await client.getConnectorConfig("freshdesk")).secretKeys).toContain("api_key");
    await client.deleteConnectorConfig("freshdesk");
    expect(calls).toEqual([
      "GET http://x/v1/managed/connectors/freshdesk",
      "DELETE http://x/v1/managed/connectors/freshdesk",
    ]);
  });

  // #240: the policy field must be OMITTED from the body when the caller does
  // not name it — the server preserves it on absence, so serializing `false`
  // here would silently revoke everyone's permission on every secret rotation.
  it("omits personal_allowed unless the caller names it", async () => {
    const fetchMock = vi.fn(async () => mk({ connector: raw }));
    const c = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await c.putConnectorConfig("freshdesk", { enabled: true, secrets: { api_key: "rotated" } });
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(init.body as string)).not.toHaveProperty("personal_allowed");

    const fetchMock2 = vi.fn(async () => mk({ connector: { ...raw, personal_allowed: true } }));
    const c2 = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock2 as unknown as typeof fetch });
    const out = await c2.putConnectorConfig("freshdesk", { enabled: true, personalAllowed: true });
    const [, init2] = fetchMock2.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(init2.body as string).personal_allowed).toBe(true);
    expect(out.personalAllowed).toBe(true);
  });
});
