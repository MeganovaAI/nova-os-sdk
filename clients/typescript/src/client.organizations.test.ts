import { describe, expect, it, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("operator organizations", () => {
  it("lists the caller's memberships from the managed organization registry", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      orgs: [
        { id: "org-1", name: "Jim's organization", slug: "jims-organization", role: "owner" },
      ],
    }), { status: 200, headers: { "content-type": "application/json" } }));
    const client = new NovaClient({
      baseUrl: "http://x",
      auth,
      fetch: fetchMock as unknown as typeof fetch,
    });

    await expect(client.listMyOrganizations()).resolves.toEqual([
      { id: "org-1", name: "Jim's organization", slug: "jims-organization", role: "owner" },
    ]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/orgs/mine");
    expect(new Headers((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1].headers).get("authorization"))
      .toBe("Bearer tok");
  });

  it("normalizes an omitted organization list", async () => {
    const fetchMock = vi.fn(async () => new Response("{}", { status: 200 }));
    const client = new NovaClient({
      baseUrl: "http://x",
      auth,
      fetch: fetchMock as unknown as typeof fetch,
    });

    await expect(client.listMyOrganizations()).resolves.toEqual([]);
  });
});
