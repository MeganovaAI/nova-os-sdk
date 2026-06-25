import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) =>
  new Response(b === null ? null : JSON.stringify(b), {
    status: s,
    headers: { "content-type": "application/json" },
  });

/** Sample snake_case collection as returned by the server. */
const sampleRaw = {
  id: "col-1",
  name: "Engineering Docs",
  description: "All eng documents",
  access_level: "corporate",
  document_count: 42,
  chunk_count: 300,
  agent_bindings: ["agent-a", "agent-b"],
  created_at: "2025-01-01T00:00:00Z",
};

/** Expected camelCase mapping. */
const sampleMapped = {
  id: "col-1",
  name: "Engineering Docs",
  description: "All eng documents",
  accessLevel: "corporate",
  documentCount: 42,
  chunkCount: 300,
  agentBindings: ["agent-a", "agent-b"],
  createdAt: "2025-01-01T00:00:00Z",
};

describe("Knowledge Collection CRUD + agent binding", () => {
  // ── listCollections ───────────────────────────────────────────────────

  it("listCollections() GETs /api/knowledge/collections and maps snake→camel", async () => {
    const fetchMock = vi.fn(async () => mk([sampleRaw]));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.listCollections();
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("GET");
    expect(url).toContain("/api/knowledge/collections");
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject(sampleMapped);
  });

  // ── createCollection ──────────────────────────────────────────────────

  it("createCollection() POSTs snake_case body and maps the returned collection", async () => {
    const calls: [string, RequestInit][] = [];
    const fetchMock = vi.fn(async (u: string, init: RequestInit) => {
      calls.push([u, init]);
      return mk(sampleRaw, 201);
    });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.createCollection({
      name: "Engineering Docs",
      description: "All eng documents",
      accessLevel: "corporate",
    });
    const [url, init] = calls[0]!;
    expect(init.method).toBe("POST");
    expect(url).toContain("/api/knowledge/collections");
    expect(JSON.parse(init.body as string)).toEqual({
      name: "Engineering Docs",
      description: "All eng documents",
      access_level: "corporate",
    });
    expect(result).toMatchObject(sampleMapped);
  });

  // ── getCollection ─────────────────────────────────────────────────────

  it("getCollection(id) GETs /api/knowledge/collections/:id", async () => {
    const fetchMock = vi.fn(async () => mk(sampleRaw));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.getCollection("col-1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("GET");
    expect(url).toContain("/api/knowledge/collections/col-1");
    expect(result).toMatchObject(sampleMapped);
  });

  // ── deleteCollection ──────────────────────────────────────────────────

  it("deleteCollection(id) DELETEs /api/knowledge/collections/:id", async () => {
    const fetchMock = vi.fn(async () => mk(null, 204));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.deleteCollection("col-1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("DELETE");
    expect(url).toContain("/api/knowledge/collections/col-1");
  });

  // ── listCollectionDocuments ───────────────────────────────────────────

  it("listCollectionDocuments(id) GETs /api/knowledge/collections/:id/documents", async () => {
    const docs = [
      { id: "doc-1", collection_id: "col-1", filename: "a.pdf", content_type: "application/pdf", chunk_count: 5 },
    ];
    const fetchMock = vi.fn(async () => mk(docs));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.listCollectionDocuments("col-1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("GET");
    expect(url).toContain("/api/knowledge/collections/col-1/documents");
    expect(result).toEqual(docs);
  });

  // ── ingestCollectionText ──────────────────────────────────────────────

  it("ingestCollectionText(id, content, {title}) POSTs {content, collection, source} to /api/knowledge/ingest", async () => {
    const fetchMock = vi.fn(async () => mk(null, 200));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.ingestCollectionText("col-1", "Hello world", { title: "my-doc" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(url).toContain("/api/knowledge/ingest");
    const body = JSON.parse(init.body as string);
    expect(body).toEqual({ content: "Hello world", collection: "col-1", source: "my-doc" });
    const headers = new Headers(init.headers as HeadersInit);
    expect(headers.get("content-type")).toContain("application/json");
  });

  // ── uploadCollectionDocument ──────────────────────────────────────────

  it("uploadCollectionDocument(id, blob, {fileName}) POSTs multipart to /api/documents/upload/:id", async () => {
    const fetchMock = vi.fn(async () => mk({ uploaded: "test.pdf", size: 1024 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const blob = new Blob(["content"], { type: "application/pdf" });
    const result = await client.uploadCollectionDocument("col-1", blob, { fileName: "test.pdf" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(url).toContain("/api/documents/upload/col-1");
    expect(init.body).toBeInstanceOf(FormData);
    expect(result).toEqual({ uploaded: "test.pdf", size: 1024 });
  });

  // ── deleteCollectionDocument ──────────────────────────────────────────

  it("deleteCollectionDocument(sourceId) DELETEs /api/knowledge/:sourceId", async () => {
    const fetchMock = vi.fn(async () => mk(null, 204));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.deleteCollectionDocument("my-source-id");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("DELETE");
    expect(url).toContain("/api/knowledge/my-source-id");
  });

  // ── bindAgentCollection ───────────────────────────────────────────────

  it("bindAgentCollection(agentId, collectionId) POSTs {collection_id} to /api/agents/:id/collections", async () => {
    const fetchMock = vi.fn(async () => mk({ status: "bound" }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.bindAgentCollection("agent-a", "col-1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(url).toContain("/api/agents/agent-a/collections");
    expect(JSON.parse(init.body as string)).toEqual({ collection_id: "col-1" });
    expect(result).toEqual({ status: "bound" });
  });

  // ── unbindAgentCollection ─────────────────────────────────────────────

  it("unbindAgentCollection(agentId, collectionId) DELETEs /api/agents/:id/collections/:collectionId", async () => {
    const fetchMock = vi.fn(async () => mk(null, 204));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.unbindAgentCollection("agent-a", "col-1");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("DELETE");
    expect(url).toContain("/api/agents/agent-a/collections/col-1");
  });

  // ── listAgentCollections ──────────────────────────────────────────────

  it("listAgentCollections(agentId) returns ids of collections whose agent_bindings includes agentId", async () => {
    const col1 = { ...sampleRaw, id: "col-1", agent_bindings: ["agent-a", "agent-b"] };
    const col2 = { ...sampleRaw, id: "col-2", agent_bindings: ["agent-b"] }; // not bound to agent-a
    const fetchMock = vi.fn(async () => mk([col1, col2]));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.listAgentCollections("agent-a");
    // Should return only col-1 (bound to agent-a)
    expect(result).toHaveLength(1);
    expect(result[0]!.id).toBe("col-1");
  });
});
