import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });
const client = (f: unknown) => new NovaClient({ baseUrl: "http://x", auth, fetch: f as unknown as typeof fetch });

describe("personal domain policy", () => {
  it("maps the policy and its caveat", async () => {
    const fetchMock = vi.fn(async () => mk({
      policy: { domains: ["acme.com"], advisory: true, advisory_reason: "not a security boundary…", updated_by: "u1" },
    }));
    expect(await client(fetchMock).getPersonalDomainPolicy()).toEqual({
      domains: ["acme.com"], advisory: true, advisoryReason: "not a security boundary…",
      updatedAt: undefined, updatedBy: "u1",
    });
  });

  // An older kernel that does not send the field is one where the control is
  // advisory too. The safe default is the caveat, never its absence.
  it("advisory defaults to TRUE when the field is absent", async () => {
    const fetchMock = vi.fn(async () => mk({ policy: { domains: [] } }));
    expect((await client(fetchMock).getPersonalDomainPolicy()).advisory).toBe(true);
  });

  // Empty is a real instruction — "remove the restriction" — not a no-op the
  // client should optimise away.
  it("an empty list is sent, not skipped", async () => {
    const fetchMock = vi.fn(async () => mk({ policy: { domains: [] } }));
    await client(fetchMock).setPersonalDomainPolicy([]);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/connectors/personal-domains");
    expect(init.method).toBe("PUT");
    expect(JSON.parse(init.body as string)).toEqual({ domains: [] });
  });

  it("a 400 from the server surfaces as an error", async () => {
    const fetchMock = vi.fn(async () => mk({ error: "invalid_domain", message: "looks like an email address" }, 400));
    await expect(client(fetchMock).setPersonalDomainPolicy(["alice@acme.com"])).rejects.toThrow();
  });
});
