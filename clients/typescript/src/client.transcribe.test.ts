import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("transcribeAudio", () => {
  it("POSTs multipart to /v1/audio/transcriptions with bearer + fields, returns text", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify({ text: "hello", language: "english" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
    );
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const blob = new Blob(["audio"], { type: "audio/webm" });

    const out = await client.transcribeAudio(blob, { fileName: "speech.webm", model: "m", language: "en" });

    expect(out.text).toBe("hello");
    expect(out.language).toBe("english");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/v1/audio/transcriptions");
    expect(init.method).toBe("POST");
    expect(init.body).toBeInstanceOf(FormData);
    const form = init.body as FormData;
    expect(form.get("file")).toBeInstanceOf(Blob);
    expect(form.get("model")).toBe("m");
    expect(form.get("language")).toBe("en");
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer tok");
  });

  it("rejects on a non-ok response", async () => {
    const fetchMock = vi.fn(async () => new Response("bad", { status: 400 }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await expect(client.transcribeAudio(new Blob(["a"], { type: "audio/webm" }))).rejects.toBeTruthy();
  });
});
