import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const raw = {
  id: "srv-1", name: "acme", url: "https://mcp.acme.example/rpc",
  description: "internal tools", default_policy: "ask",
  enabled: false, has_auth: true, created_at: "t0", updated_at: "t1",
};

const client = (fetchMock: unknown) =>
  new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

/**
 * The external MCP server registry (desk#269). These are admin-only routes and
 * the properties worth pinning at this layer are the ones a UI would otherwise
 * get wrong: registration never activates, and an omitted credential is
 * "unchanged", never "delete".
 */
describe("mcp servers", () => {
  it("maps the masked view and hits the admin surface", async () => {
    const fetchMock = vi.fn(async () => mk({ servers: [raw] }));
    expect(await client(fetchMock).listMcpServers()).toEqual([{
      id: "srv-1", name: "acme", url: "https://mcp.acme.example/rpc",
      description: "internal tools", defaultPolicy: "ask",
      enabled: false, hasAuth: true, createdAt: "t0", updatedAt: "t1",
    }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0])
      .toBe("http://x/v1/managed/mcp/servers");
  });

  // A policy string this client does not understand must read as the RESTRICTIVE
  // end. Rendering "allow" for a value nobody could interpret would be an
  // assertion no admin made.
  it("an unknown default_policy degrades to never, not allow", async () => {
    const fetchMock = vi.fn(async () => mk({ servers: [{ ...raw, default_policy: "auto" }] }));
    const servers = await client(fetchMock).listMcpServers();
    expect(servers[0]?.defaultPolicy).toBe("never");
  });

  it("createMcpServer cannot activate a server", async () => {
    const fetchMock = vi.fn(async () => mk({ server: raw }));
    await client(fetchMock).createMcpServer({
      name: "acme", url: "https://mcp.acme.example/rpc", authToken: "sk-live",
    });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/mcp/servers");
    expect(init.method).toBe("POST");
    const body = JSON.parse(init.body as string);
    // There is no `enabled` to send. Registration and activation are separate
    // acts and the API records them as separate audit events.
    expect(body).not.toHaveProperty("enabled");
    // Nor a tenant: the server takes it from the signed claim, and a client
    // that could name one would be a client that could try to name another's.
    expect(body).not.toHaveProperty("tenant_id");
    expect(body).toMatchObject({ name: "acme", auth_token: "sk-live" });
  });

  // The one that protects a stored credential from an unrelated edit.
  it("updateMcpServer omits auth_token entirely when not given", async () => {
    const fetchMock = vi.fn(async () => mk({ server: raw }));
    await client(fetchMock).updateMcpServer("srv-1", { description: "renamed" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/mcp/servers/srv-1");
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string)).not.toHaveProperty("auth_token");
  });

  it("an explicit empty auth_token survives serialization as a revoke", async () => {
    const fetchMock = vi.fn(async () => mk({ server: { ...raw, has_auth: false } }));
    await client(fetchMock).updateMcpServer("srv-1", { authToken: "" });
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(init.body as string).auth_token).toBe("");
  });

  it("enabling is a patch of one field", async () => {
    const fetchMock = vi.fn(async () => mk({ server: { ...raw, enabled: true } }));
    const s = await client(fetchMock).updateMcpServer("srv-1", { enabled: true });
    expect(s.enabled).toBe(true);
    expect(JSON.parse((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1].body as string))
      .toEqual({ enabled: true });
  });

  it("ids are encoded, and delete is a DELETE", async () => {
    const fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
    await client(fetchMock).deleteMcpServer("srv/1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/mcp/servers/srv%2F1");
    expect(init.method).toBe("DELETE");
  });

  it("a 403 from the admin gate surfaces as an error, not an empty list", async () => {
    const fetchMock = vi.fn(async () => mk({ error: "admin_required" }, 403));
    await expect(client(fetchMock).listMcpServers()).rejects.toThrow();
  });
});
