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
