import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });
const client = (fetchMock: unknown) =>
  new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

describe("action dispositions", () => {
  it("maps the record and always carries the denominator", async () => {
    const fetchMock = vi.fn(async () => mk({
      dispositions: [{ agent_id: "support", approved_as_is: 40, edited_then_approved: 7, rejected: 3, decided: 50 }],
    }));
    expect(await client(fetchMock).listActionDispositions()).toEqual([
      { agentId: "support", approvedAsIs: 40, editedThenApproved: 7, rejected: 3, decided: 50 },
    ]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0])
      .toBe("http://x/v1/managed/actions/dispositions");
  });

  // A missing count is 0, never undefined: `undefined` propagated into a rate
  // renders as NaN next to the autonomy dial, which reads as broken rather
  // than as "no decisions yet".
  it("absent counts default to zero", async () => {
    const fetchMock = vi.fn(async () => mk({ dispositions: [{ agent_id: "quiet" }] }));
    const out = await client(fetchMock).listActionDispositions();
    expect(out[0]).toEqual({ agentId: "quiet", approvedAsIs: 0, editedThenApproved: 0, rejected: 0, decided: 0 });
  });

  it("a window is forwarded, and a nonsense one is not", async () => {
    const fetchMock = vi.fn(async () => mk({ dispositions: [] }));
    await client(fetchMock).listActionDispositions(200);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toContain("?window=200");
    await client(fetchMock).listActionDispositions(0);
    // calls[1], not calls[0] — the second invocation is the one under test.
    expect((fetchMock.mock.calls[1] as unknown as [string])[0]).not.toContain("window");
  });

  it("a 403 from the admin gate is an error, not an empty record", async () => {
    // "No decisions yet" and "we could not look" must not render identically
    // next to a dial an operator is about to move.
    const fetchMock = vi.fn(async () => mk({ error: "admin_required" }, 403));
    await expect(client(fetchMock).listActionDispositions()).rejects.toThrow();
  });
});
