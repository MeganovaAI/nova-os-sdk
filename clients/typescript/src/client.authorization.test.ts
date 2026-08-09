import { describe, expect, it, vi } from "vitest";
import { NovaClient } from "./client";

const auth = { getAccessToken: async () => "user-jwt", refresh: vi.fn(async () => "fresh-user-jwt") };
const mk = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

const dataScope = {
  resource: "ticket",
  operation: "reply",
  selectors: { queue: "support" },
  connector: { kind: "freshdesk", connection_id: "org", details: { visibility: "public" } },
};

const intent = {
  id: "intent:1", tenant_id: "acme", agent_id: "support", session_id: "s1", tool_name: "reply",
  action_class: "ticket/reply", params: { ticket: 42 }, data_scope: dataScope, side_effects: { sends: true },
  reversible: false, max_authorization_seconds: 60, risk_tier: "medium", purpose: "answer customer",
  source: "brokered", external_ref: "42", group_id: "support", proposed_by: "capability:1",
  proposed_by_kind: "service", proposed_at: "2026-08-09T00:00:00Z", policy_version: "p1",
};

const evidence = {
  agent_id: "support", action_class: "ticket/reply", risk_tier: "medium", policy_version: "p1",
  data_scope: dataScope, profile_hash: "profile", weighted_approved: 22, weighted_rejected: 1,
  effective_approval_rate: 0.956, current_decisions: 23, historical_decisions: 2, incidents: 0,
  eligible: true, reason: "evidence threshold satisfied", decay: [{ kind: "current", decisions: 23, multiplier: 1 }],
  reviewers: [{ reviewer: "u1", decisions: 23, edited: 1, rejected: 1, fast: 2, batched: 0,
    edit_rate: 0.043, reject_rate: 0.043, fast_rate: 0.087 }],
};

const grant = {
  id: "grant-1", revision: 2, previous_grant_id: "grant-0", tenant_id: "acme", agent_id: "support",
  action_class: "ticket/reply", tool_bindings: ["reply"], risk_tier: "medium", data_scope: dataScope,
  policy_version: "p1", runtime_profile: { model: "m" }, profile_hash: "profile", evidence_window: evidence,
  constraints: { auto_sample_rate: 0.1 }, issued_by: "admin", issued_at: "2026-08-09T00:00:00Z",
  expires_at: "2026-08-16T00:00:00Z", lifecycle_state: "issued", lifecycle_reason: "threshold met",
  lifecycle_changed_at: "2026-08-09T00:00:00Z",
};

describe("authorization lifecycle", () => {
  it("maps the operational graph including immutable receipt attempt metadata", async () => {
    const fetchMock = vi.fn(async () => mk({
      intent,
      decisions: [{ id: "d1", intent_id: "intent:1", outcome: "approved", risk_tier: "medium",
        grant_id: "grant-1", grant_revision: 2, policy_version: "p1", evaluated_at: "t1", decided_by: "grant",
        decided_by_kind: "service", decided_at: "t1", reason: "authorized", edited: false,
        evidence_weight: 0, corrected: false }],
      receipts: [{ id: "r1", intent_id: "intent:1", attempt_no: 2, started_at: "t2", finished_at: "t3",
        outcome: "unknown", verification_status: "unverified", effect_summary: "provider timed out",
        idempotency_key: "action-1", rollback_available: false }],
      grant, state: "execution_unknown",
    }));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const graph = await client.getAuthorizationGraph("intent:1");
    expect(graph.intent.dataScope?.connector.connectionId).toBe("org");
    expect(graph.decisions[0]).toMatchObject({ grantId: "grant-1", grantRevision: 2 });
    expect(graph.receipts[0]).toMatchObject({ attemptNo: 2, outcome: "unknown", verificationStatus: "unverified" });
    expect(graph.grant?.evidenceWindow.reviewers[0]?.fastRate).toBe(0.087);
  });

  it("serializes canonical data scope and explicit tool bindings when evaluating a grant", async () => {
    const fetchMock = vi.fn(async () => mk({ grant, evidence }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    await client.evaluateAndIssueGrant({
      agentId: "support", actionClass: "ticket/reply", toolBindings: ["reply"], riskTier: "medium",
      policyVersion: "p1", dataScope: { resource: "ticket", operation: "reply",
        connector: { kind: "freshdesk", connectionId: "org", details: { visibility: "public" } } },
      minEvidence: 20, ttlSeconds: 604800, sampleRate: 0.1,
    });
    const body = JSON.parse((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(body).toMatchObject({ tool_bindings: ["reply"], data_scope: { connector: { connection_id: "org" } } });
  });

  it("uses the one-time lcap token and never replaces it with the configured user JWT", async () => {
    const fetchMock = vi.fn(async (_url: string, init: RequestInit) => {
      expect(new Headers(init.headers).get("authorization")).toBe("Bearer lcap_once");
      return mk({ status: "awaiting_approval", action_id: "a1", intent_id: "intent:a1" }, 202);
    });
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.executeCapability("lcap_once", { params: { ticket: 42 }, purpose: "answer" });
    expect(result).toMatchObject({ status: "awaiting_approval", actionId: "a1" });
    expect(auth.refresh).not.toHaveBeenCalled();
  });

  it("issues the native Slack lifecycle without sending raw connector credentials", async () => {
    const capability = {
      id: "cap-1", grant_id: "grant-1", grant_revision: 2, tenant_id: "acme", agent_id: "support",
      tool_name: "slack_send_message", action_class: "message/send", risk_tier: "medium",
      data_scope: { resource: "message", operation: "send", connector: { kind: "slack", connection_id: "slack-1" } },
      policy: "allow", policy_version: "p1", governance_mode: "desk_managed",
      runtime_profile: { runtime: "libraos" }, issued_by: "admin", issued_at: "t1", expires_at: "t2", token: "lcap_once",
    };
    const fetchMock = vi.fn(async () => mk({ capability, governance_mode: "desk_managed",
      governance_enforcement: "raw connector credentials remain in Desk", warning: "shown once" }, 201));
    const client = new NovaClient({ baseUrl: "http://x", auth, fetch: fetchMock as unknown as typeof fetch });
    const result = await client.issueExecutionCapability({
      grantId: "grant-1", agentId: "support", toolName: "slack_send_message", actionClass: "message/send",
      riskTier: "medium", policy: "allow", policyVersion: "p1", governanceMode: "desk_managed",
      dataScope: { resource: "message", operation: "send", connector: { kind: "slack", connectionId: "slack-1" } },
      managedConnector: { connector: "slack", integrationId: "slack-1" },
    });
    const body = JSON.parse((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1].body as string);
    expect(body).toMatchObject({ governance_mode: "desk_managed", managed_connector: { connector: "slack", integration_id: "slack-1" } });
    expect(body).not.toHaveProperty("callback");
    expect(JSON.stringify(body)).not.toContain("token");
    expect(result.capability).toMatchObject({ governanceMode: "desk_managed", token: "lcap_once" });
  });
});
