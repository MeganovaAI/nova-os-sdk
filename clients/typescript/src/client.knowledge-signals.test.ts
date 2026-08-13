import { describe, expect, it, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const rawSignal = {
  id: "sig-1", tenant: "acme", app: "desk", employee_id: "support-assistant",
  type: "correction", fact_key: "pgwp", content: "Approved answer", source_chunk_id: "ticket-5",
  status: "promoted", created_at: "2026-08-13T00:00:00Z", signature: "signed",
};

describe("knowledge signal mutations", () => {
  it("files a pending starter-set proposal", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ signal: { ...rawSignal, status: "pending" } }), { status: 201 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const signal = await client.createKnowledgeSignal({ factKey: "pgwp.scope", content: "Reviewed scope", idempotencyKey: "setup:p1", sourceChunkId: "setup:s1" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/knowledge-signals");
    expect(JSON.parse(init.body as string)).toMatchObject({ fact_key: "pgwp.scope", idempotency_key: "setup:p1", source_chunk_id: "setup:s1" });
    expect(signal.status).toBe("pending");
  });
  it("promotes with scope and maps the durable receipt", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      signal: rawSignal,
      receipt: {
        id: "kspr-1", signal_id: "sig-1", tenant: "acme", knowledge_document_id: "knowledge-signal-1",
        collection: "firm-guidance", audience: "employees", actor: "admin", source_chunk_id: "ticket-5",
        published_at: "2026-08-13T00:01:00Z",
      },
    }), { status: 200, headers: { "content-type": "application/json" } }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.promoteKnowledgeSignalWithReceipt("sig-1", { collection: "firm-guidance", audience: "employees" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/knowledge-signals/sig-1/promote");
    expect(JSON.parse(init.body as string)).toEqual({ collection: "firm-guidance", audience: "employees" });
    expect(result.signal.status).toBe("promoted");
    expect(result.receipt).toMatchObject({ id: "kspr-1", signalId: "sig-1", sourceChunkId: "ticket-5" });
  });

  it("keeps the legacy convenience method returning only the signal", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ signal: rawSignal }), { status: 200 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect((await client.promoteKnowledgeSignal("sig-1")).id).toBe("sig-1");
  });

  it("unwraps rejected mutations", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ signal: { ...rawSignal, status: "rejected" } }), { status: 200 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect((await client.rejectKnowledgeSignal("sig-1")).status).toBe("rejected");
  });
});
