import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

describe("listAgents", () => {
  it("sends the managed-agents beta header on the wire and unwraps {data}", async () => {
    // openapi-fetch passes a Request as `input` (with the per-call header) AND
    // an `init`; a real fetch(input, init) uses init.headers when both are
    // present, so the header that actually reaches the server is init.headers.
    // Assert on THAT (not the Request input) — the previous test asserted on
    // the Request and gave a false pass while the auth wrapper dropped the header.
    let captured: { input: Request | string; init?: RequestInit } | undefined;
    const fetchMock = vi.fn(async (input: Request | string, init?: RequestInit) => {
      captured = { input, init };
      return mk({ data: [{ id: "marketing-assistant", name: "Marketing", agent_type: "persona", brain: true }] });
    });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

    const agents = await client.listAgents();

    expect(agents).toEqual([
      { id: "marketing-assistant", name: "Marketing", agent_type: "persona", brain: true },
    ]);
    const url = typeof captured!.input === "string" ? captured!.input : captured!.input.url;
    expect(url).toContain("/v1/agents");
    const sent = new Headers(captured!.init?.headers);
    expect(sent.get("anthropic-beta")).toBe("managed-agents-2026-04-01");
    expect(sent.get("authorization")).toBe("Bearer tok");
  });
});

describe("agent CRUD (#61)", () => {
  // openapi-fetch calls fetch(request, init): method + body live on the
  // `Request` input; the beta header is merged onto `init.headers` by the auth
  // wrapper (same as the listAgents test above).
  const cap = () => {
    let c: { input: Request | string; init?: RequestInit } | undefined;
    const fetchMock = vi.fn(async (input: Request | string, init?: RequestInit) => {
      c = { input, init };
      return mk({ id: "new-agent", name: "New", agent_type: "persona", brain: true });
    });
    return { fetchMock, get: () => c! };
  };
  const req = (c: { input: Request | string }) => c.input as Request;
  const method = (c: { input: Request | string; init?: RequestInit }) =>
    c.init?.method ?? (typeof c.input === "string" ? undefined : c.input.method);
  const url = (c: { input: Request | string }) => (typeof c.input === "string" ? c.input : c.input.url);
  const beta = (c: { init?: RequestInit }) => new Headers(c.init?.headers).get("anthropic-beta");

  it("createAgent POSTs /v1/agents with the beta header handled internally", async () => {
    const { fetchMock, get } = cap();
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const agent = await client.createAgent({ name: "New", agent_type: "persona" });
    expect(agent).toMatchObject({ id: "new-agent" });
    expect(url(get())).toContain("/v1/agents");
    expect(method(get())).toBe("POST");
    expect(beta(get())).toBe("managed-agents-2026-04-01");
    expect(await req(get()).clone().json()).toMatchObject({ name: "New", agent_type: "persona" });
  });

  it("getAgent GETs /v1/agents/{id} with the beta header", async () => {
    const { fetchMock, get } = cap();
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.getAgent("marketing-assistant");
    expect(url(get())).toContain("/v1/agents/marketing-assistant");
    expect(method(get())).toBe("GET");
    expect(beta(get())).toBe("managed-agents-2026-04-01");
  });

  it("updateAgent PUTs only the supplied fields with the beta header", async () => {
    const { fetchMock, get } = cap();
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.updateAgent("marketing-assistant", { system: "Use the house style." });
    expect(url(get())).toContain("/v1/agents/marketing-assistant");
    expect(method(get())).toBe("PUT");
    expect(beta(get())).toBe("managed-agents-2026-04-01");
    expect(await req(get()).clone().json()).toEqual({ system: "Use the house style." });
  });

  it("deleteAgent DELETEs /v1/agents/{id} with the beta header", async () => {
    let c: { input: Request | string; init?: RequestInit } | undefined;
    const fetchMock = vi.fn(async (input: Request | string, init?: RequestInit) => {
      c = { input, init };
      return new Response(null, { status: 204 });
    });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.deleteAgent("old-agent");
    const u = typeof c!.input === "string" ? c!.input : c!.input.url;
    const m = c!.init?.method ?? (typeof c!.input === "string" ? undefined : c!.input.method);
    expect(u).toContain("/v1/agents/old-agent");
    expect(m).toBe("DELETE");
    expect(new Headers(c!.init?.headers).get("anthropic-beta")).toBe("managed-agents-2026-04-01");
  });
});
