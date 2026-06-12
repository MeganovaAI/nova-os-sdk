import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "../src/index.js";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("NovaClient", () => {
  it("attaches a static bearer token", async () => {
    const fetchMock = vi.fn(async (_url: unknown, _init?: RequestInit) =>
      jsonResponse(200, { version: "v0.1.9", capabilities: ["async_jobs"] }),
    );
    const client = new NovaClient({
      baseUrl: "https://nova.example",
      auth: "tok_static",
      fetch: fetchMock as unknown as typeof fetch,
    });
    const dep = await client.getDeployment();
    expect(dep.version).toBe("v0.1.9");
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer tok_static");
  });

  it("refreshes once and retries on 401", async () => {
    let n = 0;
    const fetchMock = vi.fn(async () => {
      n += 1;
      if (n === 1) return jsonResponse(401, { type: "authentication_error", message: "expired" });
      return jsonResponse(200, { version: "v0.1.9", capabilities: [] });
    });
    const refresh = vi.fn(async () => "tok_fresh");
    const client = new NovaClient({
      baseUrl: "https://nova.example",
      auth: { getAccessToken: () => "tok_old", refresh },
      fetch: fetchMock as unknown as typeof fetch,
    });
    const dep = await client.getDeployment();
    expect(dep.version).toBe("v0.1.9");
    expect(refresh).toHaveBeenCalledOnce();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("throws a typed NovaApiError on non-2xx", async () => {
    const fetchMock = vi.fn(async () =>
      jsonResponse(404, { type: "not_found_error", message: "no such job" }),
    );
    const client = new NovaClient({
      baseUrl: "https://nova.example",
      auth: "t",
      fetch: fetchMock as unknown as typeof fetch,
    });
    await expect(client.getJob("missing")).rejects.toMatchObject({
      status: 404,
      type: "not_found_error",
    });
  });
});
