import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";
const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

describe("project files", () => {
  it("uploadProjectFile POSTs multipart to /v1/projects/:id/files", async () => {
    const fetchMock = vi.fn(async () => mk({ id: "project_p1/a.txt", name: "a.txt", size: 5, status: "indexing" }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const f = new Blob(["hello"], { type: "text/plain" });
    const out = await client.uploadProjectFile("p1", f, { fileName: "a.txt" });
    expect(out).toEqual({ id: "project_p1/a.txt", name: "a.txt", size: 5, status: "indexing" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/v1/projects/p1/files");
    expect(init.method).toBe("POST");
    expect(init.body instanceof FormData).toBe(true);
  });

  it("listProjectFiles unwraps {files}", async () => {
    const fetchMock = vi.fn(async () => mk({ files: [{ id: "f1", name: "a.txt", size: 5, status: "ready" }] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listProjectFiles("p1");
    expect(out).toEqual([{ id: "f1", name: "a.txt", size: 5, status: "ready" }]);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toContain("/v1/projects/p1/files");
  });

  it("deleteProjectFile DELETEs the file path", async () => {
    const calls: Array<{ url: string; init: RequestInit }> = [];
    // Note: Node.js undici rejects new Response(body, {status: 204}) with a non-null body,
    // so we use new Response(null, {status: 204}) directly (204 No Content has no body).
    const fetchMock = vi.fn(async (url: string, init: RequestInit) => { calls.push({ url, init }); return new Response(null, { status: 204 }); });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.deleteProjectFile("p1", "f1");
    expect(calls[0]!.url).toContain("/v1/projects/p1/files/f1");
    expect(calls[0]!.init.method).toBe("DELETE");
  });
});
