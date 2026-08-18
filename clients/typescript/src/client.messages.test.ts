import { describe, expect, it, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("createMessage model observability", () => {
  it("surfaces the provider model and fallback recorded by response headers", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      id: "msg-1",
      type: "message",
      role: "assistant",
      content: [{ type: "text", text: "answer" }],
      model: "support-assistant",
      stop_reason: "end_turn",
    }), {
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-nova-model-used": "Qwen/Qwen3.6-Plus",
        "x-nova-model-fallback-triggered": "1",
      },
    }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

    const response = await client.createMessage({
      model: "support-assistant",
      max_tokens: 128,
      stream: false,
      messages: [{ role: "user", content: "test" }],
    });

    expect(response.model).toBe("support-assistant");
    expect(response.model_used).toBe("Qwen/Qwen3.6-Plus");
    expect(response.fallback_triggered).toBe(true);
  });
});
