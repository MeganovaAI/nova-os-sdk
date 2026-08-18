import { describe, expect, it, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("document readiness helpers", () => {
  it("extracts a named office document without publishing it", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ text: "Sheet: Fees", doc_type: "xlsx", char_count: 11, metadata: { sheet_count: "2" }, elapsed_ms: 4 }), { status: 200 }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.extractDocument(new Blob(["xlsx"]), { fileName: "fees.xlsx" });
    const [url] = fetchMock.mock.calls[0] as unknown as [string];
    expect(url).toBe("http://x/v1/managed/documents/extract");
    expect(result).toMatchObject({ text: "Sheet: Fees", docType: "xlsx", charCount: 11, metadata: { sheet_count: "2" } });
  });

  it("maps OCR cost/cache disclosures", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ markdown: "page", page_count: 1, fallback_chain_triggered: false, cache_hit: true, cost_usd: 0 }), { status: 200 }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.ocrDocument(new Blob(["pdf"]), { fileName: "scan.pdf" })).toMatchObject({ markdown: "page", pageCount: 1, cacheHit: true, costUsd: 0 });
  });
});
