import { describe, expect, it, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("LibraOSClient Desk chat contract", () => {
  it("sends persistence, idempotency, and scope fields over AG-UI", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(
      'data: {"type":"RUN_FINISHED","threadId":"c1","runId":"r1"}\n\n',
      { status: 200, headers: { "content-type": "text/event-stream" } },
    ));
    const client = new LibraOSClient({ baseUrl: "https://libraos.example", auth, fetch: fetchMock as unknown as typeof fetch });

    const events = [];
    for await (const event of client.streamMessage({
      model: "support-assistant",
      messages: [{ role: "user", content: "hello" }],
      max_tokens: 1024,
      stream: true,
      conversation_id: "c1",
      message_id: "turn-1",
      scope: "corporate",
      metadata: { agent_id: "support-assistant" },
    })) events.push(event);

    expect(events.map((event) => event.type)).toEqual(["RUN_FINISHED"]);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("https://libraos.example/v1/messages");
    const headers = new Headers(init.headers);
    expect(headers.get("x-protocol")).toBe("ag-ui");
    expect(headers.get("authorization")).toBe("Bearer tok");
    expect(JSON.parse(String(init.body))).toMatchObject({
      conversation_id: "c1",
      message_id: "turn-1",
      scope: "corporate",
      stream: true,
    });
  });

  it("maps a rejected stream to the typed API error before parsing SSE", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(
      JSON.stringify({ type: "permission_error", message: "agent is not available to this app" }),
      { status: 403, headers: { "content-type": "application/json" } },
    ));
    const client = new LibraOSClient({ baseUrl: "https://libraos.example", auth, fetch: fetchMock as unknown as typeof fetch });

    const consume = async () => {
      for await (const _event of client.streamMessage({
        model: "support-assistant",
        messages: [{ role: "user", content: "hello" }],
        max_tokens: 1024,
        stream: true,
        scope: "corporate",
      })) { /* consume */ }
    };

    await expect(consume()).rejects.toMatchObject({ status: 403, type: "permission_error" });
  });

  it("passes Last-Event-ID when a resumable server supplied an SSE id", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(
      'id: 8\ndata: {"type":"RUN_FINISHED","threadId":"c1","runId":"r1"}\n\n',
      { status: 200, headers: { "content-type": "text/event-stream" } },
    ));
    const client = new LibraOSClient({ baseUrl: "https://libraos.example", auth, fetch: fetchMock as unknown as typeof fetch });

    const events = [];
    for await (const event of client.streamMessage({
      model: "support-assistant",
      messages: [{ role: "user", content: "hello" }],
      max_tokens: 1024,
      stream: true,
      scope: "corporate",
    }, { lastEventId: "7" })) events.push(event);

    const headers = new Headers(fetchMock.mock.calls[0]?.[1]?.headers);
    expect(headers.get("last-event-id")).toBe("7");
    expect(events[0]?.sseId).toBe("8");
  });
});
