import { describe, expect, it, vi } from "vitest";
import { LibraOSClient } from "./client";

const auth = { getAccessToken: async () => "tok" };

describe("usage summary", () => {
  it("requests the selected range and maps the wire response", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      range: "30d", fetched_at: "2026-08-09T12:00:00Z",
      pricing: { fetched_at: "2026-08-09T11:30:00Z", stale: false },
      totals: {
        tokens: 1200, prompt_tokens: 900, completion_tokens: 300, calls: 7,
        cost_usd: 1.25, has_pricing: true, unique_models: 2, unique_agents: 1, unique_users: 3,
      },
      series: [{ date: "2026-08-09", tokens: 1200, calls: 7, cost_usd: 1.25 }],
      by_agent: [{ agent_id: "quanta", tokens: 1200, prompt_tokens: 900, completion_tokens: 300, calls: 7, cost_usd: 1.25, has_pricing: true }],
      by_model: [{ model: "openai/gpt-5", tokens: 1200, prompt_tokens: 900, completion_tokens: 300, calls: 7, cost_usd: 1.25, has_pricing: true }],
    }), { status: 200, headers: { "content-type": "application/json" } }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

    const result = await client.getUsageSummary("30d");

    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/api/usage/summary?range=30d");
    expect(result.totals).toEqual({
      tokens: 1200, promptTokens: 900, completionTokens: 300, calls: 7,
      costUsd: 1.25, hasPricing: true, uniqueModels: 2, uniqueAgents: 1, uniqueUsers: 3,
    });
    expect(result.byAgent[0]).toMatchObject({ agentId: "quanta", tokens: 1200, costUsd: 1.25 });
    expect(result.byModel[0]).toMatchObject({ model: "openai/gpt-5", calls: 7, hasPricing: true });
    expect(result.series[0]).toEqual({ date: "2026-08-09", tokens: 1200, calls: 7, costUsd: 1.25 });
  });

  it("normalizes omitted arrays and counters", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ range: "today" }), { status: 200 }));
    const client = new LibraOSClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });

    const result = await client.getUsageSummary("today");

    expect(result.totals.tokens).toBe(0);
    expect(result.byAgent).toEqual([]);
    expect(result.byApplication).toEqual([]);
  });
});
