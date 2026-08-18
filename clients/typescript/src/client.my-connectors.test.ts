import { describe, it, expect, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const raw = {
  kind: "gmail", enabled: true,
  config: { address: "alice@acme.com" }, secret_keys: ["refresh_token"], updated_at: "t1",
};

const client = (fetchMock: unknown) =>
  new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

/**
 * The employee half of connector config (desk#240). The property worth
 * pinning at this layer is what these calls DON'T send: no user id, ever.
 */
describe("my connections", () => {
  it("listMyConnectors hits the /me surface and maps the masked view", async () => {
    const fetchMock = vi.fn(async () => mk({ connectors: [raw] }));
    expect(await client(fetchMock).listMyConnectors()).toEqual([{
      kind: "gmail", enabled: true,
      config: { address: "alice@acme.com" }, secretKeys: ["refresh_token"], updatedAt: "t1",
    }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0])
      .toBe("http://x/v1/managed/me/connectors");
  });

  // The owner comes from the token. A client that could name a user would be
  // a client that could try to name someone else's.
  it("never sends an owner — not in the path, the query or the body", async () => {
    const fetchMock = vi.fn(async () => mk({ connector: raw }));
    await client(fetchMock).putMyConnector("gmail", {
      enabled: true, config: { address: "alice@acme.com" }, secrets: { refresh_token: "t" },
    });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/me/connectors/gmail");
    expect(url).not.toMatch(/user|owner/i);
    const body = JSON.parse(init.body as string);
    expect(body).not.toHaveProperty("user_id");
    expect(body).not.toHaveProperty("tenant_id");
    expect(body).not.toHaveProperty("group_id");
    expect(body).toMatchObject({ enabled: true, secrets: { refresh_token: "t" } });
  });

  it("putMyConnector keeps the org path's secret-merge semantics", async () => {
    const fetchMock = vi.fn(async () => mk({ connector: raw }));
    await client(fetchMock).putMyConnector("slack", {
      enabled: true, secrets: { bot_token: "rotated", signing_secret: "" },
    });
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    // empty string is a DELETE instruction and must survive serialization
    expect(JSON.parse(init.body as string).secrets).toEqual({ bot_token: "rotated", signing_secret: "" });
  });

  it("listMyConnectorCatalog returns the kinds an admin has opened", async () => {
    const fetchMock = vi.fn(async () => mk({ kinds: ["gmail", "slack"] }));
    expect(await client(fetchMock).listMyConnectorCatalog()).toEqual(["gmail", "slack"]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0])
      .toBe("http://x/v1/managed/me/connectors/catalog");
  });

  // Deny-by-default is server-side; the client must surface it rather than
  // swallow it, so the UI can say who can change the policy.
  it("surfaces the 403 when a kind is not opened for personal connection", async () => {
    const fetchMock = vi.fn(async () => mk({ error: "personal_connection_not_allowed" }, 403));
    await expect(client(fetchMock).putMyConnector("slack", { enabled: true }))
      .rejects.toMatchObject({ status: 403 });
  });

  it("deleteMyConnector DELETEs my row", async () => {
    const fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
    await client(fetchMock).deleteMyConnector("gmail");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/me/connectors/gmail");
    expect(init.method).toBe("DELETE");
  });

  it("an absent catalog or connector list degrades to empty, not undefined", async () => {
    expect(await client(vi.fn(async () => mk({}))).listMyConnectors()).toEqual([]);
    expect(await client(vi.fn(async () => mk({}))).listMyConnectorCatalog()).toEqual([]);
  });
});
