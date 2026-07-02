import { describe, it, expect, vi } from "vitest";
import { NovaClient } from "./client";
import { NovaApiError } from "./errors";

const auth = { getAccessToken: async () => "tok" };
const mk = (b: unknown, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });

const rawAction = {
  id: "pa_1", agent_id: "support-assistant", user_id: "", tenant_id: "acme", session_id: "",
  tool_name: "freshdesk_writeback", risk: "high", status: "pending",
  created_at: "t1", input: { kind: "public_reply", ticket_id: 42, body: "Answer" },
  preview: { draft_note: "The draft" }, source: "freshdesk", external_ref: "42", group_id: "grp_support",
};

const mapped = {
  id: "pa_1", agentId: "support-assistant", userId: "", tenantId: "acme", sessionId: "",
  toolName: "freshdesk_writeback", risk: "high", status: "pending", result: undefined,
  createdAt: "t1", decidedAt: null,
  input: { kind: "public_reply", ticket_id: 42, body: "Answer" },
  preview: { draft_note: "The draft" },
  source: "freshdesk", externalRef: "42", groupId: "grp_support", claimedBy: undefined, decidedBy: undefined,
};

describe("pending actions", () => {
  it("listPendingActions passes filters and maps snake_case", async () => {
    const fetchMock = vi.fn(async () => mk({ actions: [rawAction] }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const out = await client.listPendingActions({ status: "pending", source: "freshdesk", externalRef: "42", limit: 10 });
    expect(out).toEqual([mapped]);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/actions?status=pending&source=freshdesk&external_ref=42&limit=10");
    expect(init.method).toBe("GET");
    expect((init.headers as Headers).get("authorization")).toBe("Bearer tok");
  });

  it("getPendingAction unwraps {action}", async () => {
    const fetchMock = vi.fn(async () => mk({ action: rawAction }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    expect(await client.getPendingAction("pa_1")).toEqual(mapped);
    expect((fetchMock.mock.calls[0] as unknown as [string])[0]).toBe("http://x/v1/managed/actions/pa_1");
  });

  it("createPendingAction sends the #767 contract (snake_case + secret_ref)", async () => {
    const fetchMock = vi.fn(async () => mk({ action: rawAction }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.createPendingAction({
      toolName: "freshdesk_writeback",
      input: { kind: "set_status", ticket_id: 42, status: 4 },
      source: "freshdesk",
      externalRef: "42",
      groupId: "grp_support",
      agentId: "support-assistant",
      risk: "high",
      callback: { url: "http://cw:8790/webhooks/freshdesk/execute", auth: { type: "hmac", secretRef: "FRESHDESK_CALLBACK_SECRET" }, timeoutSec: 10 },
    });
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toMatchObject({
      tool_name: "freshdesk_writeback",
      input: { kind: "set_status", ticket_id: 42, status: 4 },
      source: "freshdesk",
      external_ref: "42",
      group_id: "grp_support",
      agent_id: "support-assistant",
      risk: "high",
      callback: { url: "http://cw:8790/webhooks/freshdesk/execute", auth: { type: "hmac", secret_ref: "FRESHDESK_CALLBACK_SECRET" }, timeout_sec: 10 },
    });
  });

  it("claim/approve POST to the action subresources", async () => {
    const fetchMock = vi.fn(async () => mk({ action: { ...rawAction, status: "approved" } }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.claimPendingAction("pa_1");
    const approved = await client.approvePendingAction("pa_1");
    expect(approved.status).toBe("approved");
    const urls = fetchMock.mock.calls.map((c) => (c as unknown as [string])[0]);
    expect(urls).toEqual(["http://x/v1/managed/actions/pa_1/claim", "http://x/v1/managed/actions/pa_1/approve"]);
  });

  it("rejectPendingAction sends the audited reason", async () => {
    const fetchMock = vi.fn(async () => mk({ action: { ...rawAction, status: "rejected", result: "not appropriate" } }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.rejectPendingAction("pa_1", "not appropriate");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://x/v1/managed/actions/pa_1/reject");
    expect(JSON.parse(init.body as string)).toEqual({ reason: "not appropriate" });
  });

  it("surfaces the 503 error code so UIs can branch (pending_actions_disabled)", async () => {
    const fetchMock = vi.fn(async () => mk({ error: "pending_actions_disabled", message: "disabled" }, 503));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const err = await client.listPendingActions().catch((e) => e as NovaApiError);
    expect(err).toBeInstanceOf(NovaApiError);
    expect((err as NovaApiError).status).toBe(503);
    expect(((err as NovaApiError).body as { error?: string })?.error).toBe("pending_actions_disabled");
  });

  it("surfaces 409 already_decided on approve races", async () => {
    const fetchMock = vi.fn(async () => mk({ error: "already_decided", status: "rejected" }, 409));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const err = await client.approvePendingAction("pa_1").catch((e) => e as NovaApiError);
    expect((err as NovaApiError).status).toBe(409);
  });
});
