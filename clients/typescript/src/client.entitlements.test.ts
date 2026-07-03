import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const raw = {
  tenant_id: "acme",
  flags: {
    autonomy_auto_resolve: false,
    compliance_pack: true,
    grounding_permission_aware: false,
    oversight_org_analytics: false,
    connector_limit: 10,
  },
  updated_at: "t1",
};

describe("tenant entitlements", () => {
  it("getEntitlements unwraps {entitlements} and maps snake_case → camelCase", async () => {
    const fetchMock = vi.fn(async () => mk({ entitlements: raw }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.getEntitlements("acme")).toEqual({
      tenantId: "acme",
      flags: {
        autonomy_auto_resolve: false,
        compliance_pack: true,
        grounding_permission_aware: false,
        oversight_org_analytics: false,
        connector_limit: 10,
      },
      updatedAt: "t1",
    });
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/entitlements/acme");
  });

  it("putEntitlements PUTs {flags} and maps the response", async () => {
    const fetchMock = vi.fn(async () => mk({ entitlements: raw }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.putEntitlements("acme", { compliance_pack: true, connector_limit: 10 });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/entitlements/acme");
    expect(init.method).toBe("PUT");
    expect(JSON.parse(init.body as string)).toEqual({
      flags: { compliance_pack: true, connector_limit: 10 },
    });
    expect(out.tenantId).toBe("acme");
    expect(out.flags.compliance_pack).toBe(true);
  });

  it("getEntitlements defaults flags to {} and updatedAt to undefined when absent", async () => {
    const fetchMock = vi.fn(async () => mk({ entitlements: { tenant_id: "empty" } }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.getEntitlements("empty")).toEqual({
      tenantId: "empty",
      flags: {},
      updatedAt: undefined,
    });
  });
});
