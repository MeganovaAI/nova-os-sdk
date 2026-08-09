/**
 * Thin convenience client tying REST + auth + streaming together.
 *
 * Framework-agnostic: depends only on `fetch`, Web Crypto (via the OIDC helper),
 * and the generated types. Methods cover the key partner surfaces — messages,
 * agents, jobs, documents, sessions, deployment — plus typed SSE iterators.
 */

import type { components } from "./_generated/schema.js";
import { createRestClient, throwIfError, type AuthProvider, type RestClient } from "./rest.js";
import { OidcClient } from "./auth/oidc.js";
import { NovaApiError } from "./errors.js";
import { parseAgUiStream } from "./streaming/sse.js";
import type { AgUiEvent } from "./streaming/events.js";

type Schemas = components["schemas"];
export type MessageRequest = Schemas["MessageRequest"];
export type MessageResponse = Schemas["MessageResponse"];
export type JobCreate = Schemas["JobCreate"];
export type Job = Schemas["Job"];
export type Document = Schemas["Document"];
export type Session = Schemas["Session"];
export type SessionCreate = Schemas["SessionCreate"];
export type Deployment = Schemas["Deployment"];
export type Agent = Schemas["Agent"];
/** Body accepted by {@link NovaClient.createAgent}. Mirrors the OpenAPI createAgent request. */
export type CreateAgentRequest = Record<string, unknown>;

/** Result of {@link NovaClient.transcribeAudio}. `json` returns `{text, language?}`; `verbose_json` adds `duration`. */
export interface Transcription {
  text: string;
  language?: string;
  duration?: number;
}

/** A user's observational memory for one persona, from {@link NovaClient.getMemory}. */
export interface MemoryView {
  agentId: string;
  scope: "corporate" | "personal";
  content: string;
  lastObservedAt?: string;
  enabled: boolean;
}

/** A file attached to a project, available for retrieval-augmented generation. */
export interface ProjectFile {
  id: string;
  name: string;
  size?: number;
  status?: string;
}

/**
 * A document in the company-wide `default` knowledge collection.
 * Returned by {@link NovaClient.listCorporateDocuments}.
 * `id` is the chunk source path — pass it to {@link NovaClient.deleteCorporateDocument}.
 */
export interface CorporateDocument {
  id: string;
  collection_id: string;
  filename: string;
  content_type: string;
  chunk_count: number;
}

/**
 * A named knowledge collection, returned by {@link NovaClient.listCollections},
 * {@link NovaClient.createCollection}, and {@link NovaClient.getCollection}.
 */
export interface Collection {
  id: string;
  name: string;
  description: string;
  accessLevel: string;
  documentCount: number;
  chunkCount: number;
  agentBindings: string[];
  createdAt: string;
}

/**
 * A knowledge-signal entry emitted by an employee session and queued for
 * admin curation. Returned by {@link NovaClient.listKnowledgeSignals},
 * {@link NovaClient.promoteKnowledgeSignal}, and
 * {@link NovaClient.rejectKnowledgeSignal}.
 */
export interface KnowledgeSignal {
  id: string;
  tenant: string;
  app: string;
  employeeId: string;
  type: "gap" | "explicit_keep" | "correction" | "stale" | string;
  factKey: string;
  content: string;
  sourceChunkId: string;
  status: "pending" | "quarantined" | "eligible" | "promoted" | "rejected" | "superseded" | string;
  createdAt: string;
  signature: string;
}

/**
 * A tenant user record, returned by user-management methods.
 * All optional fields may be `undefined` when the server omits them.
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  displayName?: string;
  role?: string;
  tenantId?: string;
  roles?: string[];
  mustChangePassword?: boolean;
  isActive?: boolean;
  createdAt?: string;
  updatedAt?: string;
  lastLoginAt?: string;
}

/** A project containing conversations. */
export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  facts?: string[];
}

/** One of the caller's conversations (from {@link NovaClient.listConversations}). */
export interface ConversationSummary {
  id: string;
  agentId: string;
  title: string | null;
  createdAt: string;
  lastActiveAt: string;
  messageCount: number;
  projectId?: string | null;
}

/** A persisted message in a conversation. */
export interface ConversationMessage {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  seq?: number;
}

/** A pending side-effecting action awaiting approval (nova-os#546/#767/#768). */
export interface PendingAction {
  id: string;
  agentId: string;
  userId: string;
  tenantId: string;
  sessionId: string;
  toolName: string;
  risk: string;
  status: string;
  result?: string;
  createdAt: string;
  decidedAt?: string | null;
  input?: unknown;
  preview?: unknown;
  source?: string;
  externalRef?: string;
  groupId?: string;
  claimedBy?: string;
  decidedBy?: string;
}

/** Canonical connector-qualified data envelope used by authorization policy. */
export interface AuthorizationDataScope {
  resource: string;
  operation: string;
  selectors?: Record<string, unknown>;
  constraints?: Record<string, unknown>;
  connector: {
    kind: string;
    connectionId?: string;
    /** Connector vocabulary stays namespaced here so the outer envelope remains comparable. */
    details?: Record<string, unknown>;
  };
}

export interface AuthorizationIntent {
  id: string;
  tenantId: string;
  agentId: string;
  sessionId: string;
  toolName: string;
  actionClass: string;
  params: unknown;
  dataScope?: AuthorizationDataScope;
  sideEffects?: unknown;
  reversible: boolean | null;
  maxAuthorizationSeconds: number | null;
  riskTier: string;
  purpose: string;
  source: string;
  externalRef: string;
  groupId: string;
  proposedBy: string;
  proposedByKind: string;
  proposedAt: string;
  legacyActionId?: string;
  policyVersion?: string;
  agentConfigHash?: string;
  runtimeProfile?: unknown;
  toolSchemaHash?: string;
}

export interface AuthorizationDecision {
  id: string;
  intentId: string;
  outcome: string;
  riskTier: string;
  grantId?: string;
  grantRevision?: number;
  policyVersion?: string;
  runtimeProfile?: unknown;
  evaluatedAt: string;
  decidedBy: string;
  decidedByKind: string;
  decidedAt: string;
  reason: string;
  edited: boolean;
  originalParams?: unknown;
  reviewDurationMs?: number;
  batchId?: string;
  evidenceWeight: number;
  corrected: boolean;
  correctionReason?: string;
}

export type ExecutionOutcome = "succeeded" | "failed" | "unknown";
export type VerificationStatus = "verified" | "unverified" | "contradicted";

/** One immutable execution-attempt result. Retries create additional receipts. */
export interface ExecutionReceipt {
  id: string;
  intentId: string;
  attemptNo: number;
  startedAt: string;
  finishedAt: string;
  outcome: ExecutionOutcome;
  verificationStatus: VerificationStatus;
  providerReference?: string;
  effectSummary: string;
  effect?: unknown;
  error?: string;
  idempotencyKey: string;
  rollbackAvailable: boolean;
  rollback?: unknown;
}

export interface EvidenceDecayBucket {
  kind: string;
  decisions: number;
  multiplier: number;
}

export interface ReviewerEvidence {
  reviewer: string;
  decisions: number;
  edited: number;
  rejected: number;
  fast: number;
  batched: number;
  editRate: number;
  rejectRate: number;
  fastRate: number;
}

export interface AuthorizationEvidenceProfile {
  agentId: string;
  actionClass: string;
  riskTier: string;
  policyVersion: string;
  dataScope: AuthorizationDataScope;
  profileHash: string;
  weightedApproved: number;
  weightedRejected: number;
  effectiveApprovalRate: number;
  currentDecisions: number;
  historicalDecisions: number;
  incidents: number;
  eligible: boolean;
  reason: string;
  decay: EvidenceDecayBucket[];
  reviewers: ReviewerEvidence[];
}

export type GrantLifecycleState = "issued" | "suspended" | "resumed" | "expired" | "revoked" | "superseded";

/** Immutable grant definition plus its projected lifecycle state. */
export interface AutonomyGrant {
  id: string;
  revision: number;
  previousGrantId?: string;
  tenantId: string;
  agentId: string;
  actionClass: string;
  toolBindings: string[];
  riskTier: string;
  dataScope: AuthorizationDataScope;
  policyVersion: string;
  runtimeProfile: unknown;
  profileHash: string;
  evidenceWindow: AuthorizationEvidenceProfile;
  constraints: Record<string, unknown>;
  issuedBy: string;
  issuedAt: string;
  expiresAt: string;
  lifecycleState: GrantLifecycleState;
  lifecycleReason: string;
  lifecycleChangedAt: string;
  supersededBy?: string;
}

export interface AuthorizationGraph {
  intent: AuthorizationIntent;
  decisions: AuthorizationDecision[];
  receipts: ExecutionReceipt[];
  grant?: AutonomyGrant;
  state: string;
}

export interface ExecutionCapability {
  id: string;
  grantId?: string;
  grantRevision?: number;
  tenantId: string;
  agentId: string;
  toolName: string;
  actionClass: string;
  riskTier: string;
  dataScope: AuthorizationDataScope;
  policy: "allow" | "ask" | "never";
  policyVersion: string;
  runtimeProfile: unknown;
  issuedBy: string;
  issuedAt: string;
  expiresAt: string;
  revokedAt?: string;
  revocationReason?: string;
  /** Returned exactly once by the issue endpoint. */
  token?: string;
}

/** A named group in the kernel registry (nova-os#768). */
export interface Group {
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  members?: GroupMember[];
}

export interface GroupMember {
  userId: string;
  role: string;
  createdAt: string;
}

/** One of the caller's own memberships, from {@link NovaClient.listMyGroups}. */
export interface MyGroup {
  id: string;
  name: string;
  description?: string;
  role: string;
}

/**
 * A connector's kernel-owned settings, MASKED: secretKeys names which
 * credentials are set — values never reach the client (nova-os#777).
 */
export type GovernanceMode = "desk_managed" | "brokered" | "external";

export interface ConnectorConfig {
  kind: string;
  tenantId?: string;
  enabled: boolean;
  groupId?: string;
  config: Record<string, unknown>;
  secretKeys: string[];
  updatedAt: string;
  /** May employees connect their OWN account for this kind (desk#240)? */
  personalAllowed?: boolean;
  /** How strongly Desk can enforce policy before this connector executes. */
  governanceMode: GovernanceMode;
  governanceEnforcement: string;
}

/**
 * ONE EMPLOYEE's own connection to a service (desk#240) — their Gmail, their
 * Slack — as opposed to the org-wide {@link ConnectorConfig}.
 *
 * No `groupId`: approval groups route ORG actions to approvers, which has no
 * meaning for a connection acting as one person on their own account. No
 * `tenantId` and no owner id either — the server takes both from the token,
 * and every row you can see is yours, so echoing them back would only suggest
 * these could describe somebody else.
 */
export interface MyConnectorConfig {
  kind: string;
  enabled: boolean;
  config: Record<string, unknown>;
  /** WHICH secrets are set — values never leave the server. */
  secretKeys: string[];
  updatedAt: string;
}

/**
 * How an agent's proposals have actually been received (desk#270): of its last
 * N DECIDED actions, how many a human approved untouched, corrected first, or
 * refused.
 *
 * `decided` is the denominator and is always sent. A rate without a visible
 * denominator is the exact shape of a reassuring number — 97% of 3 decisions
 * and 97% of 300 render identically and are completely different evidence — so
 * compute rates against this field rather than against the counts alone.
 *
 * `editedThenApproved` is the interesting one. Approved-vs-rejected alone reads
 * as a pass rate, and an agent whose drafts are always rewritten before they go
 * out scores a perfect one.
 */
export interface ActionDisposition {
  agentId: string;
  approvedAsIs: number;
  editedThenApproved: number;
  rejected: number;
  decided: number;
}

/**
 * The org's allowlist of email domains for personal connections (desk#268).
 *
 * `advisory` is ALWAYS true today and is carried as data rather than assumed by
 * each caller. Personal connections are credential forms, so the address is
 * typed by the employee and the credential is what actually decides which
 * account is reached — this list prevents mistakes and states the policy, and
 * is not a security boundary until these connections use OAuth.
 *
 * Render `advisoryReason` next to the list. When the check moves to a
 * provider-verified address the flag flips, and a surface that read the field
 * gets the correction for free; one that hard-coded the caveat does not.
 *
 * Empty `domains` means NO restriction — the default, and what every
 * deployment that has never set one reads.
 */
export interface PersonalDomainPolicy {
  domains: string[];
  advisory: boolean;
  advisoryReason: string;
  updatedAt?: string;
  updatedBy?: string;
}

/** Seed policy for the tools discovered on an MCP server (desk#269/#270). */
export type McpServerPolicy = "allow" | "ask" | "never";

/**
 * An EXTERNAL MCP server an admin has registered (desk#269).
 *
 * Not a connector: a connector is an adapter we wrote, this is an address an
 * admin pointed the deployment at. Every route behind these methods is
 * admin-only, reads included — the list of endpoints an org has wired into its
 * agents, and which of them carry a credential, is a map of its outbound reach.
 *
 * `hasAuth` reports only WHETHER a credential is stored. There is no method
 * that returns one, on purpose: an admin who forgets a token re-enters it.
 */
export interface McpServer {
  id: string;
  name: string;
  url: string;
  description: string;
  /** Discovered tools start here. `ask` parks the first call for approval. */
  defaultPolicy: McpServerPolicy;
  /** Registration does not activate — a new server is always created off. */
  enabled: boolean;
  hasAuth: boolean;
  createdAt: string;
  updatedAt: string;
  governanceMode: GovernanceMode;
  governanceEnforcement: string;
}

/**
 * A tenant's entitlement flags (employee-assistant #80). Flags gate premium
 * capabilities; a tenant with no stored row reads the "free floor" (every
 * premium flag OFF, connector_limit at the free cap). Upgrading is a flag flip.
 */
export interface Entitlements {
  tenantId: string;
  flags: Record<string, unknown>;
  updatedAt?: string;
}

export interface NovaClientOptions {
  /** Base URL of the LibraOS instance. */
  baseUrl: string;
  /**
   * Auth source. Either a static bearer token (partner-minted JWT), an
   * {@link OidcClient} (interactive end-user login w/ auto-refresh), or a custom
   * {@link AuthProvider}. Omit for unauthenticated calls (e.g. deployment read).
   */
  auth?: string | OidcClient | AuthProvider;
  /** Injected fetch; defaults to globalThis.fetch. */
  fetch?: typeof fetch;
}

function toAuthProvider(auth: NovaClientOptions["auth"]): AuthProvider | undefined {
  if (!auth) return undefined;
  if (typeof auth === "string") {
    return { getAccessToken: () => auth };
  }
  if (auth instanceof OidcClient) {
    return {
      getAccessToken: () => auth.getAccessToken(),
      refresh: async () => {
        try {
          return (await auth.refresh()).accessToken;
        } catch {
          return undefined;
        }
      },
    };
  }
  return auth;
}

export class NovaClient {
  private readonly rest: RestClient;
  private readonly opts: NovaClientOptions;
  private readonly auth?: AuthProvider;

  constructor(options: NovaClientOptions) {
    this.opts = options;
    this.auth = toAuthProvider(options.auth);
    this.rest = createRestClient({
      baseUrl: options.baseUrl,
      auth: this.auth,
      fetch: options.fetch,
    });
  }

  /** The underlying typed openapi-fetch client for any endpoint not wrapped below. */
  get api() {
    return this.rest.api;
  }

  // ── Deployment / capabilities ──────────────────────────────────────────

  /** Read this instance's capabilities (features, model tiers, locales, auth). */
  async getDeployment(): Promise<Deployment> {
    const res = await this.rest.api.GET("/v1/managed/deployment");
    throwIfError(res);
    return res.data as Deployment;
  }

  // ── Agents ─────────────────────────────────────────────────────────────

  /** List agents. */
  async listAgents(): Promise<Agent[]> {
    const res = await this.rest.api.GET("/v1/agents", {
      headers: { "anthropic-beta": "managed-agents-2026-04-01" },
    });
    throwIfError(res);
    return ((res.data as { data?: Agent[] })?.data ?? []) as Agent[];
  }

  /** Create (or upsert) an agent. The managed-agents beta header is handled
   *  internally, so callers no longer reach into `rest.api` and hand-set it
   *  (employee-assistant#83, #61). */
  async createAgent(body: CreateAgentRequest): Promise<Agent> {
    const res = await this.rest.api.POST("/v1/agents", {
      headers: { "anthropic-beta": "managed-agents-2026-04-01" },
      body: body as never,
    });
    throwIfError(res);
    return res.data as Agent;
  }

  /** Fetch a single agent by id. */
  async getAgent(agentId: string): Promise<Agent> {
    const res = await this.rest.api.GET("/v1/agents/{agent_id}", {
      headers: { "anthropic-beta": "managed-agents-2026-04-01" },
      params: { path: { agent_id: agentId } },
    });
    throwIfError(res);
    return res.data as Agent;
  }

  /** Delete an agent by id. */
  async deleteAgent(agentId: string): Promise<void> {
    const res = await this.rest.api.DELETE("/v1/agents/{agent_id}", {
      headers: { "anthropic-beta": "managed-agents-2026-04-01" },
      params: { path: { agent_id: agentId } },
    });
    throwIfError(res);
  }

  // ── Messages (Anthropic-shaped) ────────────────────────────────────────

  /** Send a non-streaming message. Target an agent via `metadata.agent_id`. */
  async createMessage(request: MessageRequest): Promise<MessageResponse> {
    const res = await this.rest.api.POST("/v1/messages", {
      body: { ...request, stream: false },
    });
    throwIfError(res);
    return res.data as MessageResponse;
  }

  /**
   * Send a streaming message and iterate AG-UI events. Sets `X-Protocol: ag-ui`
   * so the server emits the AG-UI dialect. Yields typed {@link AgUiEvent}s.
   */
  async *streamMessage(request: MessageRequest): AsyncGenerator<AgUiEvent, void, unknown> {
    const res = await this.rawFetch("/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "text/event-stream",
        "x-protocol": "ag-ui",
      },
      body: JSON.stringify({ ...request, stream: true }),
    });
    yield* parseAgUiStream(res);
  }

  // ── Async jobs ─────────────────────────────────────────────────────────

  /** Submit a long-running job (202). */
  async createJob(request: JobCreate): Promise<Job> {
    const res = await this.rest.api.POST("/v1/managed/agents/jobs", { body: request });
    throwIfError(res);
    return res.data as Job;
  }

  /** Fetch a job's current state. */
  async getJob(jobId: string): Promise<Job> {
    const res = await this.rest.api.GET("/v1/managed/agents/jobs/{job_id}", {
      params: { path: { job_id: jobId } },
    });
    throwIfError(res);
    return res.data as Job;
  }

  /** Cancel a job (graceful drain). */
  async cancelJob(jobId: string): Promise<void> {
    const res = await this.rest.api.DELETE("/v1/managed/agents/jobs/{job_id}", {
      params: { path: { job_id: jobId } },
    });
    throwIfError(res);
  }

  /**
   * Stream a job's AG-UI events. `lastEventId` replays via `Last-Event-ID`
   * (events with seq > lastEventId), then continues live until terminal.
   */
  async *streamJob(
    jobId: string,
    lastEventId?: string,
  ): AsyncGenerator<AgUiEvent, void, unknown> {
    const headers: Record<string, string> = {
      accept: "text/event-stream",
      "x-protocol": "ag-ui",
    };
    if (lastEventId) headers["last-event-id"] = lastEventId;
    const res = await this.rawFetch(`/v1/managed/agents/jobs/${encodeURIComponent(jobId)}/stream`, {
      method: "GET",
      headers,
    });
    yield* parseAgUiStream(res);
  }

  // ── Documents ──────────────────────────────────────────────────────────

  /** Upload a document (multipart). `file` is a Blob/File; auto-indexed server-side. */
  async uploadDocument(file: Blob, opts?: { fileName?: string; collectionId?: string }): Promise<Document> {
    const form = new FormData();
    form.append("file", file, opts?.fileName);
    if (opts?.collectionId) form.append("collection_id", opts.collectionId);
    const res = await this.rawFetch("/v1/managed/documents/upload", {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as Document;
  }

  /** Transcribe audio (speech-to-text). `file` is a Blob/File; multipart → /v1/audio/transcriptions. */
  async transcribeAudio(
    file: Blob,
    opts?: {
      fileName?: string;
      model?: string;
      language?: string;
      responseFormat?: "json" | "text" | "verbose_json";
      signal?: AbortSignal;
    },
  ): Promise<Transcription> {
    const form = new FormData();
    form.append("file", file, opts?.fileName ?? "speech.webm");
    if (opts?.model) form.append("model", opts.model);
    if (opts?.language) form.append("language", opts.language);
    if (opts?.responseFormat) form.append("response_format", opts.responseFormat);
    const res = await this.rawFetch("/v1/audio/transcriptions", {
      method: "POST",
      body: form,
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    if (opts?.responseFormat === "text") return { text: await res.text() };
    return (await res.json()) as Transcription;
  }

  /** Read the caller's own observational memory for a persona (read-only). */
  async getMemory(
    agentId: string,
    opts?: { scope?: "corporate" | "personal"; signal?: AbortSignal },
  ): Promise<MemoryView> {
    const qs = new URLSearchParams({ agent_id: agentId });
    if (opts?.scope) qs.set("scope", opts.scope);
    const res = await this.rawFetch(`/v1/managed/memory?${qs.toString()}`, {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as {
      agent_id: string;
      scope: "corporate" | "personal";
      content: string;
      last_observed_at?: string;
      enabled: boolean;
    };
    return {
      agentId: j.agent_id,
      scope: j.scope,
      content: j.content ?? "",
      lastObservedAt: j.last_observed_at,
      enabled: j.enabled,
    };
  }

  // ── Conversations ──────────────────────────────────────────────────────

  /** List the caller's conversations (newest first), optionally for one agent. */
  async listConversations(opts?: { agentId?: string; limit?: number; signal?: AbortSignal }): Promise<ConversationSummary[]> {
    const qs = new URLSearchParams();
    if (opts?.agentId) qs.set("agent", opts.agentId);
    if (opts?.limit != null) qs.set("limit", String(opts.limit));
    const q = qs.toString();
    const res = await this.rawFetch(`/v1/conversations${q ? `?${q}` : ""}`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as {
      conversations?: Array<{ id: string; agent_id: string; title: string | null; created_at: string; last_active_at: string; message_count: number; project_id?: string | null }>;
    };
    return (j.conversations ?? []).map((c) => ({
      id: c.id, agentId: c.agent_id, title: c.title ?? null,
      createdAt: c.created_at, lastActiveAt: c.last_active_at, messageCount: c.message_count, projectId: c.project_id ?? null,
    }));
  }

  /** Load one conversation's metadata + full message history. */
  async getConversation(id: string, opts?: { signal?: AbortSignal }): Promise<{ conversation: ConversationSummary; messages: ConversationMessage[] }> {
    const res = await this.rawFetch(`/v1/conversations/${encodeURIComponent(id)}`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as {
      id: string; agent_id: string; title: string | null; created_at: string; last_active_at: string; message_count: number; project_id?: string | null;
      messages?: Array<{ id?: string; role: string; content: string; timestamp: string; seq?: number }>;
    };
    return {
      conversation: { id: j.id, agentId: j.agent_id, title: j.title ?? null, createdAt: j.created_at, lastActiveAt: j.last_active_at, messageCount: j.message_count, projectId: j.project_id ?? null },
      messages: (j.messages ?? []).map((m) => ({ id: m.id, role: m.role as ConversationMessage["role"], content: m.content, timestamp: m.timestamp, seq: m.seq })),
    };
  }

  /** Delete a conversation. */
  async deleteConversation(id: string): Promise<void> {
    const res = await this.rawFetch(`/v1/conversations/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  /** Set a conversation's title. */
  async renameConversation(id: string, title: string): Promise<void> {
    const res = await this.rawFetch(`/v1/conversations/${encodeURIComponent(id)}`, {
      method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ title }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /** Move a conversation to a project; pass null to move to General. */
  async moveConversation(id: string, projectId: string | null): Promise<void> {
    const res = await this.rawFetch(`/v1/conversations/${encodeURIComponent(id)}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ project_id: projectId ?? "" }) });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Projects ───────────────────────────────────────────────────────────

  private toProject(j: { id: string; name: string; description?: string; created_at: string; updated_at: string; facts?: string[] }): Project {
    return { id: j.id, name: j.name, description: j.description, createdAt: j.created_at, updatedAt: j.updated_at, facts: j.facts ?? [] };
  }

  async listProjects(opts?: { signal?: AbortSignal }): Promise<Project[]> {
    const res = await this.rawFetch("/v1/projects", { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { projects?: Array<Parameters<NovaClient["toProject"]>[0]> };
    return (j.projects ?? []).map((p) => this.toProject(p));
  }

  async createProject(input: { name: string; description?: string }): Promise<Project> {
    const res = await this.rawFetch("/v1/projects", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(input) });
    if (!res.ok) throw await this.toApiError(res);
    return this.toProject(await res.json() as Parameters<NovaClient["toProject"]>[0]);
  }

  async getProject(id: string): Promise<Project> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(id)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    return this.toProject(await res.json() as Parameters<NovaClient["toProject"]>[0]);
  }

  async renameProject(id: string, input: { name?: string; description?: string }): Promise<void> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(id)}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify(input) });
    if (!res.ok) throw await this.toApiError(res);
  }

  async setProjectFacts(id: string, facts: string[]): Promise<void> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(id)}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ facts }) });
    if (!res.ok) throw await this.toApiError(res);
  }

  async deleteProject(id: string): Promise<void> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Project files ──────────────────────────────────────────────────────

  /** Upload a file to a project (multipart). Auto-indexed for RAG server-side. */
  async uploadProjectFile(projectId: string, file: Blob, opts?: { fileName?: string; signal?: AbortSignal }): Promise<ProjectFile> {
    const form = new FormData();
    form.append("file", file, opts?.fileName ?? "upload");
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(projectId)}/files`, { method: "POST", body: form, signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { id: string; name: string; size?: number; status?: string };
    return { id: j.id, name: j.name, size: j.size, status: j.status };
  }

  /** List all files attached to a project. */
  async listProjectFiles(projectId: string, opts?: { signal?: AbortSignal }): Promise<ProjectFile[]> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(projectId)}/files`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { files?: Array<{ id: string; name: string; size?: number; status?: string }> };
    return (j.files ?? []).map((f) => ({ id: f.id, name: f.name, size: f.size, status: f.status }));
  }

  /** Delete a file from a project. */
  async deleteProjectFile(projectId: string, fileId: string): Promise<void> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(projectId)}/files/${encodeURIComponent(fileId)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Corporate Knowledge (default collection) ───────────────────────────

  /**
   * List documents in the company-wide `default` knowledge collection.
   * Requires admin role (server-enforced). Each document's `id` is the
   * chunk source path — use it with {@link deleteCorporateDocument}.
   */
  async listCorporateDocuments(opts?: { signal?: AbortSignal }): Promise<CorporateDocument[]> {
    const res = await this.rawFetch("/api/knowledge/collections/default/documents", {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as CorporateDocument[];
  }

  /**
   * Upload a file into the company-wide `default` knowledge collection.
   * Multipart POST to `/api/documents/upload/` with form field `file`.
   * Admin scope auto-routes to the `default` collection (server-enforced).
   * Returns `{ uploaded: string; size: number }` on success.
   */
  async uploadCorporateDocument(
    file: Blob,
    opts?: { fileName?: string; signal?: AbortSignal },
  ): Promise<{ uploaded: string; size: number }> {
    const form = new FormData();
    form.append("file", file, opts?.fileName ?? "upload");
    const res = await this.rawFetch("/api/documents/upload/", {
      method: "POST",
      body: form,
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as { uploaded: string; size: number };
  }

  /**
   * Delete a document from the `default` knowledge collection by its source id.
   * `id` is the value from {@link CorporateDocument.id} (the chunk source path).
   * Admin-only (server-enforced).
   */
  async deleteCorporateDocument(id: string): Promise<void> {
    const res = await this.rawFetch(`/api/knowledge/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Ingest raw text directly into the corporate (`default`) knowledge collection
   * — no file needed. `source` is an optional human label. Admin-only
   * (server-enforced via CanWrite on `default`). POST `/api/knowledge/ingest`.
   */
  async ingestCorporateText(content: string, opts?: { title?: string; signal?: AbortSignal }): Promise<void> {
    const res = await this.rawFetch("/api/knowledge/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, collection: "default", source: opts?.title ?? "" }),
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Knowledge Collections (named, multi-tenant) ────────────────────────

  /** Map a raw snake_case collection object to the camelCase {@link Collection} interface. */
  private toCollection(j: {
    id: string; name: string; description: string; access_level: string;
    document_count: number; chunk_count: number; agent_bindings: string[]; created_at: string;
  }): Collection {
    return {
      id: j.id,
      name: j.name,
      description: j.description,
      accessLevel: j.access_level,
      documentCount: j.document_count,
      chunkCount: j.chunk_count,
      agentBindings: j.agent_bindings ?? [],
      createdAt: j.created_at,
    };
  }

  /** List all knowledge collections. GET `/api/knowledge/collections`. */
  async listCollections(opts?: { signal?: AbortSignal }): Promise<Collection[]> {
    const res = await this.rawFetch("/api/knowledge/collections", {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return ((await res.json()) as Array<Parameters<NovaClient["toCollection"]>[0]>).map((c) => this.toCollection(c));
  }

  /**
   * Create a new knowledge collection (admin-only). POST `/api/knowledge/collections`.
   * Defaults: `description: ""`, `accessLevel: "corporate"`.
   */
  async createCollection(
    input: { name: string; description?: string; accessLevel?: string },
    opts?: { signal?: AbortSignal },
  ): Promise<Collection> {
    const res = await this.rawFetch("/api/knowledge/collections", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: input.name,
        description: input.description ?? "",
        access_level: input.accessLevel ?? "corporate",
      }),
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return this.toCollection(await res.json() as Parameters<NovaClient["toCollection"]>[0]);
  }

  /** Get a single knowledge collection by id. GET `/api/knowledge/collections/:id`. */
  async getCollection(id: string, opts?: { signal?: AbortSignal }): Promise<Collection> {
    const res = await this.rawFetch(`/api/knowledge/collections/${encodeURIComponent(id)}`, {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return this.toCollection(await res.json() as Parameters<NovaClient["toCollection"]>[0]);
  }

  /** Delete a knowledge collection by id (admin-only). DELETE `/api/knowledge/collections/:id`. */
  async deleteCollection(id: string): Promise<void> {
    const res = await this.rawFetch(`/api/knowledge/collections/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * List documents in a named knowledge collection.
   * GET `/api/knowledge/collections/:id/documents`. Returns `CorporateDocument[]`.
   */
  async listCollectionDocuments(id: string, opts?: { signal?: AbortSignal }): Promise<CorporateDocument[]> {
    const res = await this.rawFetch(`/api/knowledge/collections/${encodeURIComponent(id)}/documents`, {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as CorporateDocument[];
  }

  /**
   * Ingest raw text into a named collection. POST `/api/knowledge/ingest`.
   * Requires write permission on the collection.
   */
  async ingestCollectionText(
    collectionId: string,
    content: string,
    opts?: { title?: string; signal?: AbortSignal },
  ): Promise<void> {
    const res = await this.rawFetch("/api/knowledge/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, collection: collectionId, source: opts?.title ?? "" }),
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Upload a file into a named collection. Multipart POST `/api/documents/upload/:collectionId`.
   * Returns `{ uploaded: string; size: number }`.
   */
  async uploadCollectionDocument(
    collectionId: string,
    file: Blob,
    opts?: { fileName?: string; signal?: AbortSignal },
  ): Promise<{ uploaded: string; size: number }> {
    const form = new FormData();
    form.append("file", file, opts?.fileName ?? "upload");
    const res = await this.rawFetch(`/api/documents/upload/${encodeURIComponent(collectionId)}`, {
      method: "POST",
      body: form,
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as { uploaded: string; size: number };
  }

  /**
   * Delete a document from any collection by its bare source id (admin-only).
   * DELETE `/api/knowledge/:sourceId`.
   */
  async deleteCollectionDocument(sourceId: string): Promise<void> {
    const res = await this.rawFetch(`/api/knowledge/${encodeURIComponent(sourceId)}`, {
      method: "DELETE",
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Bind a collection to an agent (admin-only). POST `/api/agents/:id/collections`.
   * Returns `{ status: "bound" }`.
   */
  async bindAgentCollection(agentId: string, collectionId: string): Promise<{ status: string }> {
    const res = await this.rawFetch(`/api/agents/${encodeURIComponent(agentId)}/collections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ collection_id: collectionId }),
    });
    if (!res.ok) throw await this.toApiError(res);
    return (await res.json()) as { status: string };
  }

  /**
   * Remove a collection binding from an agent (admin-only, idempotent).
   * DELETE `/api/agents/:id/collections/:collectionId`.
   */
  async unbindAgentCollection(agentId: string, collectionId: string): Promise<void> {
    const res = await this.rawFetch(
      `/api/agents/${encodeURIComponent(agentId)}/collections/${encodeURIComponent(collectionId)}`,
      { method: "DELETE" },
    );
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * List all collections bound to a given agent.
   * Calls `listCollections` internally and filters by `agent_bindings` containing `agentId`.
   */
  async listAgentCollections(agentId: string, opts?: { signal?: AbortSignal }): Promise<Collection[]> {
    // `bound_collections` from GET /api/agents/:id is the PG-backed source of
    // truth; the collections list's `agent_bindings` is unreliable (always []
    // in that view), so filtering on it returned nothing for bound agents (#53).
    const res = await this.rawFetch(`/api/agents/${encodeURIComponent(agentId)}`, {
      method: "GET",
      signal: opts?.signal,
    });
    if (!res.ok) throw await this.toApiError(res);
    const detail = (await res.json()) as { bound_collections?: string[] };
    const ids = new Set(detail.bound_collections ?? []);
    if (ids.size === 0) return [];
    const all = await this.listCollections(opts);
    return all.filter((c) => ids.has(c.id));
  }

  async listProjectConversations(id: string, opts?: { signal?: AbortSignal }): Promise<ConversationSummary[]> {
    const res = await this.rawFetch(`/v1/projects/${encodeURIComponent(id)}/conversations`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { conversations?: Array<{ id: string; agent_id: string; title: string | null; created_at: string; last_active_at: string; message_count: number; project_id?: string | null }> };
    return (j.conversations ?? []).map((c) => ({ id: c.id, agentId: c.agent_id, title: c.title ?? null, createdAt: c.created_at, lastActiveAt: c.last_active_at, messageCount: c.message_count, projectId: c.project_id ?? null }));
  }

  async createConversation(input?: { id?: string; agentId?: string; projectId?: string; metadata?: Record<string, unknown> }): Promise<ConversationSummary> {
    const body: Record<string, unknown> = {};
    if (input?.id) body.id = input.id;
    if (input?.agentId) body.agent_id = input.agentId;
    if (input?.projectId) body.project_id = input.projectId;
    if (input?.metadata) body.metadata = input.metadata;
    const res = await this.rawFetch("/v1/conversations", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (!res.ok) throw await this.toApiError(res);
    const c = (await res.json()) as { id: string; agent_id: string; title?: string | null; created_at: string; last_active_at: string; message_count: number; project_id?: string | null };
    return { id: c.id, agentId: c.agent_id, title: c.title ?? null, createdAt: c.created_at, lastActiveAt: c.last_active_at, messageCount: c.message_count, projectId: c.project_id ?? null };
  }

  // ── Knowledge Signals (KSG curator) ───────────────────────────────────

  /** Map a raw snake_case signal object to the camelCase {@link KnowledgeSignal} interface. */
  private toKnowledgeSignal(r: {
    id: string; tenant: string; app: string; employee_id: string;
    type: string; fact_key: string; content: string; source_chunk_id: string;
    status: string; created_at: string; signature: string;
  }): KnowledgeSignal {
    return {
      id: r.id, tenant: r.tenant, app: r.app, employeeId: r.employee_id,
      type: r.type, factKey: r.fact_key, content: r.content,
      sourceChunkId: r.source_chunk_id, status: r.status,
      createdAt: r.created_at, signature: r.signature,
    };
  }

  /**
   * List knowledge signals. Requires admin role (server-enforced).
   * Returns 503 `{"error":"knowledge signals unavailable"}` when KSG is disabled;
   * throws a {@link NovaApiError} with `status === 503` in that case.
   */
  async listKnowledgeSignals(opts?: { status?: string; limit?: number; tenant?: string; signal?: AbortSignal }): Promise<KnowledgeSignal[]> {
    const qs = new URLSearchParams();
    if (opts?.status) qs.set("status", opts.status);
    if (opts?.limit != null) qs.set("limit", String(opts.limit));
    if (opts?.tenant) qs.set("tenant", opts.tenant);
    const q = qs.toString();
    const res = await this.rawFetch(`/v1/managed/knowledge-signals${q ? `?${q}` : ""}`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { signals?: Array<Parameters<NovaClient["toKnowledgeSignal"]>[0]> };
    return (j.signals ?? []).map((s) => this.toKnowledgeSignal(s));
  }

  /**
   * List fact-key strings that are eligible for promotion.
   * Requires admin role. Returns 503 when KSG is disabled.
   */
  async listKnowledgeSignalCandidates(opts?: { tenant?: string; signal?: AbortSignal }): Promise<string[]> {
    const qs = new URLSearchParams();
    if (opts?.tenant) qs.set("tenant", opts.tenant);
    const q = qs.toString();
    const res = await this.rawFetch(`/v1/managed/knowledge-signals/candidates${q ? `?${q}` : ""}`, { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { fact_keys?: string[] };
    return j.fact_keys ?? [];
  }

  /**
   * Promote a knowledge signal (POST /:id/promote). Admin-only.
   * Returns the updated {@link KnowledgeSignal}.
   */
  async promoteKnowledgeSignal(id: string): Promise<KnowledgeSignal> {
    const res = await this.rawFetch(`/v1/managed/knowledge-signals/${encodeURIComponent(id)}/promote`, { method: "POST" });
    if (!res.ok) throw await this.toApiError(res);
    return this.toKnowledgeSignal(await res.json() as Parameters<NovaClient["toKnowledgeSignal"]>[0]);
  }

  /**
   * Reject a knowledge signal (POST /:id/reject). Admin-only.
   * Returns the updated {@link KnowledgeSignal}.
   */
  async rejectKnowledgeSignal(id: string): Promise<KnowledgeSignal> {
    const res = await this.rawFetch(`/v1/managed/knowledge-signals/${encodeURIComponent(id)}/reject`, { method: "POST" });
    if (!res.ok) throw await this.toApiError(res);
    return this.toKnowledgeSignal(await res.json() as Parameters<NovaClient["toKnowledgeSignal"]>[0]);
  }

  // ── User management (admin-gated) ──────────────────────────────────────

  /** Map a raw snake_case user object to the camelCase {@link User} interface. */
  private toUser(r: {
    id: string; email: string; name?: string | null; display_name?: string | null;
    role?: string | null; tenant_id?: string | null; roles?: string[] | null;
    must_change_password?: boolean | null; is_active?: boolean | null;
    created_at?: string | null; updated_at?: string | null; last_login_at?: string | null;
  }): User {
    return {
      id: r.id, email: r.email, name: r.name ?? undefined, displayName: r.display_name ?? undefined,
      role: r.role ?? undefined, tenantId: r.tenant_id ?? undefined, roles: r.roles ?? undefined,
      mustChangePassword: r.must_change_password ?? undefined, isActive: r.is_active ?? undefined,
      createdAt: r.created_at ?? undefined, updatedAt: r.updated_at ?? undefined,
      lastLoginAt: r.last_login_at ?? undefined,
    };
  }

  /**
   * List all users in the tenant. Admin-only (403 `{"error":"admin_required"}`
   * when called by a non-admin — throws a {@link NovaApiError} with `status === 403`).
   */
  async listUsers(opts?: { signal?: AbortSignal }): Promise<User[]> {
    const res = await this.rawFetch("/api/users", { method: "GET", signal: opts?.signal });
    if (!res.ok) throw await this.toApiError(res);
    return ((await res.json()) as Array<Parameters<NovaClient["toUser"]>[0]>).map((u) => this.toUser(u));
  }

  /**
   * Create a new user. Admin-only. Role defaults to `employee` server-side.
   * Returns the created {@link User} (201).
   */
  async createUser(input: { email: string; name?: string; role?: string; password: string }): Promise<User> {
    const res = await this.rawFetch("/api/users", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(input),
    });
    if (!res.ok) throw await this.toApiError(res);
    return this.toUser(await res.json() as Parameters<NovaClient["toUser"]>[0]);
  }

  /**
   * Partially update a user. Admin-only. Maps camelCase `isActive` → `is_active` in the body.
   * Omit fields you are not changing. Returns the updated {@link User}.
   */
  async updateUser(id: string, patch: { name?: string; role?: string; isActive?: boolean }): Promise<User> {
    const body: Record<string, unknown> = {};
    if (patch.name !== undefined) body.name = patch.name;
    if (patch.role !== undefined) body.role = patch.role;
    if (patch.isActive !== undefined) body.is_active = patch.isActive;
    const res = await this.rawFetch(`/api/users/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw await this.toApiError(res);
    return this.toUser(await res.json() as Parameters<NovaClient["toUser"]>[0]);
  }

  /**
   * Delete a user. Admin-only. Returns `{ status: "deleted" }` server-side;
   * the method resolves `void` on success.
   */
  async deleteUser(id: string): Promise<void> {
    const res = await this.rawFetch(`/api/users/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Set a new password for a user and force a password change at next login.
   * Admin-only. POST `/api/admin/users/:id/reset-password`.
   */
  async resetUserPassword(id: string, password: string): Promise<void> {
    const res = await this.rawFetch(`/api/admin/users/${encodeURIComponent(id)}/reset-password`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Sessions (#185) ────────────────────────────────────────────────────

  /** Create a managed session. */
  async createSession(request: SessionCreate): Promise<Session> {
    const res = await this.rest.api.POST("/v1/managed/sessions", { body: request });
    throwIfError(res);
    return res.data as Session;
  }

  /** Fetch a managed session by id. */
  async getSession(sessionId: string): Promise<Session> {
    const res = await this.rest.api.GET("/v1/managed/sessions/{session_id}", {
      params: { path: { session_id: sessionId } },
    });
    throwIfError(res);
    return res.data as Session;
  }

  // ── Pending actions + groups (#546/#767/#768, sdk#56) ──────────────────
  //
  // 503 responses carry {error: "pending_actions_disabled" | "no_database" |
  // "executor_not_wired"} in NovaApiError.body — UIs branch on error, not text.

  /** List pending actions. Non-admins see actions of groups they belong to. */
  async listPendingActions(opts?: { status?: string; source?: string; externalRef?: string; limit?: number }): Promise<PendingAction[]> {
    const qs = new URLSearchParams();
    if (opts?.status) qs.set("status", opts.status);
    if (opts?.source) qs.set("source", opts.source);
    if (opts?.externalRef) qs.set("external_ref", opts.externalRef);
    if (opts?.limit != null) qs.set("limit", String(opts.limit));
    const q = qs.toString();
    const res = await this.rawFetch(`/v1/managed/actions${q ? `?${q}` : ""}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { actions?: RawPendingAction[] };
    return (j.actions ?? []).map(toPendingAction);
  }

  async getPendingAction(id: string): Promise<PendingAction> {
    const res = await this.rawFetch(`/v1/managed/actions/${encodeURIComponent(id)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { action: RawPendingAction };
    return toPendingAction(j.action);
  }

  /**
   * Submit a connector-sourced action for approval (nova-os#767). Requires an
   * admin/service credential. `callback.auth.secretRef` names an env var ON
   * THE NOVA OS SERVER holding the shared HMAC secret.
   */
  async createPendingAction(input: {
    toolName: string;
    input: unknown;
    source: string;
    callback: { url: string; auth: { type: string; secretRef: string }; timeoutSec?: number };
    agentId?: string;
    userId?: string;
    tenantId?: string;
    sessionId?: string;
    groupId?: string;
    preview?: unknown;
    risk?: string;
    externalRef?: string;
  }): Promise<PendingAction> {
    const res = await this.rawFetch("/v1/managed/actions", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        agent_id: input.agentId,
        user_id: input.userId,
        tenant_id: input.tenantId,
        session_id: input.sessionId,
        group_id: input.groupId,
        tool_name: input.toolName,
        input: input.input,
        preview: input.preview,
        risk: input.risk,
        source: input.source,
        external_ref: input.externalRef,
        callback: {
          url: input.callback.url,
          auth: { type: input.callback.auth.type, secret_ref: input.callback.auth.secretRef },
          timeout_sec: input.callback.timeoutSec,
        },
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { action: RawPendingAction };
    return toPendingAction(j.action);
  }

  /** Soft-claim an action to avoid double-handling. 409 (already_claimed) when someone else won. */
  async claimPendingAction(id: string): Promise<PendingAction> {
    const res = await this.rawFetch(`/v1/managed/actions/${encodeURIComponent(id)}/claim`, { method: "POST" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { action: RawPendingAction };
    return toPendingAction(j.action);
  }

  /** Approve and execute. 409 (already_decided) when raced; 403 without an approver role. */
  async approvePendingAction(id: string): Promise<PendingAction> {
    const res = await this.rawFetch(`/v1/managed/actions/${encodeURIComponent(id)}/approve`, { method: "POST" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { action: RawPendingAction };
    return toPendingAction(j.action);
  }

  /** Reject without executing; the optional reason is audited on the row. */
  async rejectPendingAction(id: string, reason?: string): Promise<PendingAction> {
    const res = await this.rawFetch(`/v1/managed/actions/${encodeURIComponent(id)}/reject`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(reason ? { reason } : {}),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { action: RawPendingAction };
    return toPendingAction(j.action);
  }

  // ── Authorization lifecycle (desk#277) ─────────────────────────────

  /** List append-only action intents, newest first. */
  async listAuthorizationIntents(limit?: number): Promise<AuthorizationIntent[]> {
    const q = limit == null ? "" : `?limit=${encodeURIComponent(String(limit))}`;
    const res = await this.rawFetch(`/v1/managed/authorization/intents${q}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { intents?: RawAuthorizationIntent[] };
    return (j.intents ?? []).map(toAuthorizationIntent);
  }

  /** Read Intent → Decisions → Receipts and the snapshotted grant basis. */
  async getAuthorizationGraph(intentId: string): Promise<AuthorizationGraph> {
    const res = await this.rawFetch(`/v1/managed/authorization/intents/${encodeURIComponent(intentId)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    return toAuthorizationGraph((await res.json()) as RawAuthorizationGraph);
  }

  async listAuthorizationGrants(includeExpired = false): Promise<AutonomyGrant[]> {
    const q = includeExpired ? "?include_expired=true" : "";
    const res = await this.rawFetch(`/v1/managed/authorization/grants${q}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { grants?: RawAutonomyGrant[] };
    return (j.grants ?? []).map(toAutonomyGrant);
  }

  /** Evaluate weighted evidence and, only when eligible, issue a new immutable grant revision. */
  async evaluateAndIssueGrant(input: {
    agentId: string;
    actionClass: string;
    toolBindings: string[];
    riskTier: string;
    policyVersion: string;
    dataScope: AuthorizationDataScope;
    minEvidence?: number;
    ttlSeconds?: number;
    sampleRate?: number;
  }): Promise<{ grant: AutonomyGrant; evidence: AuthorizationEvidenceProfile }> {
    const res = await this.rawFetch("/v1/managed/authorization/grants/evaluate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        agent_id: input.agentId,
        action_class: input.actionClass,
        tool_bindings: input.toolBindings,
        risk_tier: input.riskTier,
        policy_version: input.policyVersion,
        data_scope: fromAuthorizationDataScope(input.dataScope),
        min_evidence: input.minEvidence,
        ttl_seconds: input.ttlSeconds,
        sample_rate: input.sampleRate,
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { grant: RawAutonomyGrant; evidence: RawAuthorizationEvidenceProfile };
    return { grant: toAutonomyGrant(j.grant), evidence: toEvidenceProfile(j.evidence) };
  }

  async revokeAuthorizationGrant(id: string, reason: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/authorization/grants/${encodeURIComponent(id)}/revoke`, {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ reason }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Issue a short-lived brokered capability. The returned token is visible
   * once; store it in the executor, never in browser persistence or logs.
   */
  async issueExecutionCapability(input: {
    grantId?: string;
    agentId: string;
    toolName: string;
    actionClass: string;
    riskTier: string;
    dataScope: AuthorizationDataScope;
    policy: "allow" | "ask" | "never";
    policyVersion: string;
    callback: { url: string; auth: { secretRef: string } };
    ttlSeconds?: number;
  }): Promise<{ capability: ExecutionCapability; governanceMode: GovernanceMode; governanceEnforcement: string; warning: string }> {
    const res = await this.rawFetch("/v1/managed/authorization/capabilities", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        grant_id: input.grantId,
        agent_id: input.agentId,
        tool_name: input.toolName,
        action_class: input.actionClass,
        risk_tier: input.riskTier,
        data_scope: fromAuthorizationDataScope(input.dataScope),
        policy: input.policy,
        policy_version: input.policyVersion,
        callback: { url: input.callback.url, auth: { secret_ref: input.callback.auth.secretRef } },
        ttl_seconds: input.ttlSeconds,
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { capability: RawExecutionCapability; governance_mode: GovernanceMode; governance_enforcement: string; warning: string };
    return { capability: toExecutionCapability(j.capability), governanceMode: j.governance_mode, governanceEnforcement: j.governance_enforcement, warning: j.warning };
  }

  async revokeExecutionCapability(id: string, reason: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/authorization/capabilities/${encodeURIComponent(id)}/revoke`, {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ reason }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /** Append an evidence correction without mutating the original Decision. */
  async markAuthorizationIncident(decisionId: string, reason: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/authorization/decisions/${encodeURIComponent(decisionId)}/incident`, {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ reason }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * Execute with an `lcap_` token. An ordinary configured user JWT is never
   * substituted on 401: the capability is the credential for this endpoint.
   */
  async executeCapability(token: string, input: { params: unknown; purpose: string; externalRef?: string; sessionId?: string }): Promise<{
    status: "executed" | "awaiting_approval";
    sampled?: boolean;
    actionId?: string;
    intentId?: string;
    intent?: AuthorizationGraph;
  }> {
    const res = await this.rawFetch("/v1/capabilities/execute", {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
      body: JSON.stringify({ params: input.params, purpose: input.purpose, external_ref: input.externalRef, session_id: input.sessionId }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { status: "executed" | "awaiting_approval"; sampled?: boolean; action_id?: string; intent_id?: string; intent?: RawAuthorizationGraph };
    return { status: j.status, sampled: j.sampled, actionId: j.action_id, intentId: j.intent_id, intent: j.intent ? toAuthorizationGraph(j.intent) : undefined };
  }

  /** List groups (admin). */
  async listGroups(): Promise<Group[]> {
    const res = await this.rawFetch("/v1/managed/groups", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { groups?: RawGroup[] };
    return (j.groups ?? []).map(toGroup);
  }

  async createGroup(input: { name: string; description?: string }): Promise<Group> {
    const res = await this.rawFetch("/v1/managed/groups", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: input.name, description: input.description }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { group: RawGroup };
    return toGroup(j.group);
  }

  /** Group detail, including members. */
  async getGroup(id: string): Promise<Group> {
    const res = await this.rawFetch(`/v1/managed/groups/${encodeURIComponent(id)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { group: RawGroup };
    return toGroup(j.group);
  }

  async deleteGroup(id: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/groups/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  /** Add (or re-role) a member. Roles: member | approver | lead. */
  async addGroupMember(groupId: string, userId: string, role: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/groups/${encodeURIComponent(groupId)}/members`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ user_id: userId, role }),
    });
    if (!res.ok) throw await this.toApiError(res);
  }

  async removeGroupMember(groupId: string, userId: string): Promise<void> {
    const res = await this.rawFetch(
      `/v1/managed/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(userId)}`,
      { method: "DELETE" },
    );
    if (!res.ok) throw await this.toApiError(res);
  }

  /**
   * The CALLER's own group memberships with roles (nova-os#774). Authenticated
   * but not admin-gated — group-conditional UI (e.g. the Inbox) branches on
   * this. Returns [] for users in no groups.
   */
  async listMyGroups(): Promise<MyGroup[]> {
    const res = await this.rawFetch("/v1/managed/groups/mine", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { groups?: Array<{ id: string; name: string; description?: string; role: string }> };
    return (j.groups ?? []).map((g) => ({ id: g.id, name: g.name, description: g.description || undefined, role: g.role }));
  }

  // ── Connector configs (nova-os#777, employee-assistant #38) ────────────

  /** List connector configs (admin; masked — secret values never serialize). */
  async listConnectorConfigs(): Promise<ConnectorConfig[]> {
    const res = await this.rawFetch("/v1/managed/connectors", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connectors?: RawConnectorConfig[] };
    return (j.connectors ?? []).map(toConnectorConfig);
  }

  async getConnectorConfig(kind: string): Promise<ConnectorConfig> {
    const res = await this.rawFetch(`/v1/managed/connectors/${encodeURIComponent(kind)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connector: RawConnectorConfig };
    return toConnectorConfig(j.connector);
  }

  /**
   * Upsert a connector's settings (admin). Secret merge semantics: a
   * non-empty value overwrites that credential, an empty string DELETES it,
   * and absent keys are preserved — rotate one secret without the others.
   */
  async putConnectorConfig(kind: string, input: {
    enabled: boolean;
    groupId?: string;
    tenantId?: string;
    config?: Record<string, unknown>;
    secrets?: Record<string, string>;
    /**
     * Open/close this kind for personal connection (desk#240). OMIT to leave
     * the policy alone — the server preserves it on absence, precisely so a
     * secret rotation cannot silently revoke everyone's permission.
     */
    personalAllowed?: boolean;
  }): Promise<ConnectorConfig> {
    const res = await this.rawFetch(`/v1/managed/connectors/${encodeURIComponent(kind)}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        enabled: input.enabled,
        group_id: input.groupId,
        tenant_id: input.tenantId,
        config: input.config ?? {},
        secrets: input.secrets ?? {},
        // undefined serializes away, which is exactly "leave the policy alone".
        personal_allowed: input.personalAllowed,
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connector: RawConnectorConfig };
    return toConnectorConfig(j.connector);
  }

  async deleteConnectorConfig(kind: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/connectors/${encodeURIComponent(kind)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── My own connections (desk#240) ──────────────────────────────────────
  //
  // The employee half of the surface above. These need no admin role, and
  // they are ALWAYS scoped to the caller — there is no user id to pass,
  // because the server reads the owner from the token and ignores anything
  // else. That is why none of these methods take one.

  /** My connections (masked — secret values never serialize). */
  async listMyConnectors(): Promise<MyConnectorConfig[]> {
    const res = await this.rawFetch("/v1/managed/me/connectors", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connectors?: RawMyConnectorConfig[] };
    return (j.connectors ?? []).map(toMyConnectorConfig);
  }

  /**
   * Which kinds an admin has opened for personal connection.
   *
   * Deny-by-default server-side: a kind absent from this list cannot be
   * connected, and PUT will 403. Build the "add a connection" catalog from
   * this rather than from a hard-coded list, or the UI will offer doors that
   * do not open.
   */
  async listMyConnectorCatalog(): Promise<string[]> {
    const res = await this.rawFetch("/v1/managed/me/connectors/catalog", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { kinds?: string[] };
    return j.kinds ?? [];
  }

  async getMyConnector(kind: string): Promise<MyConnectorConfig> {
    const res = await this.rawFetch(`/v1/managed/me/connectors/${encodeURIComponent(kind)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connector: RawMyConnectorConfig };
    return toMyConnectorConfig(j.connector);
  }

  /**
   * Connect or update MY connection to a service. Same secret-merge semantics
   * as the org path: non-empty overwrites, empty string DELETES that
   * credential, absent keys are preserved.
   *
   * Throws 403 `personal_connection_not_allowed` when an admin has not opened
   * this kind — check {@link listMyConnectorCatalog} first.
   */
  async putMyConnector(kind: string, input: {
    enabled: boolean;
    config?: Record<string, unknown>;
    secrets?: Record<string, string>;
  }): Promise<MyConnectorConfig> {
    const res = await this.rawFetch(`/v1/managed/me/connectors/${encodeURIComponent(kind)}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        enabled: input.enabled,
        config: input.config ?? {},
        secrets: input.secrets ?? {},
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { connector: RawMyConnectorConfig };
    return toMyConnectorConfig(j.connector);
  }

  /**
   * Disconnect, destroying the stored credential.
   *
   * Works even after an admin closes the kind — a policy change must never
   * strand your token with no way to revoke it.
   */
  async deleteMyConnector(kind: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/me/connectors/${encodeURIComponent(kind)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── External MCP servers (desk#269) ────────────────────────────────────
  //
  // ADMIN-ONLY, reads included. There is deliberately no employee-facing
  // counterpart and no method here that takes a URL from anywhere but an
  // admin's own call: an agent's outbound reach is bounded by this registry,
  // so a prompt-injected agent cannot talk itself into a new endpoint.
  //
  // A kernel that predates this feature answers 404. Treat that as "the
  // deployment has not shipped it" and render nothing, exactly as the personal
  // connections surface does — not as an error.

  /** Every registered server, masked. Credentials never serialize. */
  async listMcpServers(): Promise<McpServer[]> {
    const res = await this.rawFetch("/v1/managed/mcp/servers", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { servers?: RawMcpServer[] };
    return (j.servers ?? []).map(toMcpServer);
  }

  async getMcpServer(id: string): Promise<McpServer> {
    const res = await this.rawFetch(`/v1/managed/mcp/servers/${encodeURIComponent(id)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { server: RawMcpServer };
    return toMcpServer(j.server);
  }

  /**
   * Register a server. It is ALWAYS created disabled — there is no `enabled`
   * input, because registering a server and arming it for agents are different
   * intentions and the server records them as separate audit events. Enable it
   * with {@link updateMcpServer}.
   *
   * `name` becomes the tool-namespace prefix (`<name>__<tool>`): lowercase
   * letters, digits, `_` and `-`, no `__`, max 40 chars. The server rejects
   * anything else with a 400 that names the rule.
   */
  async createMcpServer(input: {
    name: string;
    url: string;
    description?: string;
    defaultPolicy?: McpServerPolicy;
    authToken?: string;
  }): Promise<McpServer> {
    const res = await this.rawFetch("/v1/managed/mcp/servers", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        name: input.name,
        url: input.url,
        description: input.description ?? "",
        default_policy: input.defaultPolicy,
        auth_token: input.authToken,
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { server: RawMcpServer };
    return toMcpServer(j.server);
  }

  /**
   * Patch a server. Every field is optional and an omitted one is UNCHANGED.
   *
   * That matters most for `authToken`. Reads never return the credential, so a
   * caller re-submitting a whole record necessarily omits it; if omission meant
   * "delete", an unrelated rename would silently revoke the token and the
   * server would keep working until its next call. Pass `""` to revoke on purpose.
   */
  async updateMcpServer(id: string, input: {
    name?: string;
    url?: string;
    description?: string;
    defaultPolicy?: McpServerPolicy;
    enabled?: boolean;
    authToken?: string;
  }): Promise<McpServer> {
    const res = await this.rawFetch(`/v1/managed/mcp/servers/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        name: input.name,
        url: input.url,
        description: input.description,
        default_policy: input.defaultPolicy,
        enabled: input.enabled,
        // undefined serializes away, which is exactly "leave the credential alone".
        auth_token: input.authToken,
      }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { server: RawMcpServer };
    return toMcpServer(j.server);
  }

  /**
   * Per-agent approval record over each agent's last `window` decided actions
   * (default 50, capped server-side at 500). Admin-only.
   *
   * Reports; does not gate. Whether a poor record should BLOCK raising an agent
   * to `auto` is a product decision nobody has made.
   */
  async listActionDispositions(window?: number): Promise<ActionDisposition[]> {
    const q = window && window > 0 ? `?window=${encodeURIComponent(String(window))}` : "";
    const res = await this.rawFetch(`/v1/managed/actions/dispositions${q}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { dispositions?: RawActionDisposition[] };
    return (j.dispositions ?? []).map((d) => ({
      agentId: d.agent_id,
      approvedAsIs: d.approved_as_is ?? 0,
      editedThenApproved: d.edited_then_approved ?? 0,
      rejected: d.rejected ?? 0,
      decided: d.decided ?? 0,
    }));
  }

  /** Read the personal-connection domain allowlist (admin). */
  async getPersonalDomainPolicy(): Promise<PersonalDomainPolicy> {
    const res = await this.rawFetch("/v1/managed/connectors/personal-domains", { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { policy: RawPersonalDomainPolicy };
    return toPersonalDomainPolicy(j.policy);
  }

  /**
   * Replace the allowlist (admin). An EMPTY array removes the restriction,
   * which is a legitimate and reversible choice — not a no-op.
   *
   * Entries are domains, not addresses: `acme.com`, not `alice@acme.com`. The
   * server refuses an address with a 400 naming the rule, because a full
   * address would allow exactly one person while reading like it allows a
   * company.
   */
  async setPersonalDomainPolicy(domains: string[]): Promise<PersonalDomainPolicy> {
    const res = await this.rawFetch("/v1/managed/connectors/personal-domains", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ domains }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { policy: RawPersonalDomainPolicy };
    return toPersonalDomainPolicy(j.policy);
  }

  async deleteMcpServer(id: string): Promise<void> {
    const res = await this.rawFetch(`/v1/managed/mcp/servers/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!res.ok) throw await this.toApiError(res);
  }

  // ── Tenant entitlements (employee-assistant #80) ───────────────────────

  /**
   * Read a tenant's entitlement flags (admin). A tenant with no stored row
   * returns the free floor — every premium flag OFF, connector_limit at the
   * free cap — so the read path is stable whether or not the tenant is upgraded.
   */
  async getEntitlements(tenant: string): Promise<Entitlements> {
    const res = await this.rawFetch(`/v1/managed/entitlements/${encodeURIComponent(tenant)}`, { method: "GET" });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { entitlements: RawEntitlements };
    return toEntitlements(j.entitlements);
  }

  /**
   * Upsert a tenant's entitlement flags (admin). The stored map replaces any
   * prior map; the read path overlays it on the free floor, so flipping one
   * premium flag on is all it takes to unlock that capability.
   */
  async putEntitlements(tenant: string, flags: Record<string, unknown>): Promise<Entitlements> {
    const res = await this.rawFetch(`/v1/managed/entitlements/${encodeURIComponent(tenant)}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ flags }),
    });
    if (!res.ok) throw await this.toApiError(res);
    const j = (await res.json()) as { entitlements: RawEntitlements };
    return toEntitlements(j.entitlements);
  }

  // ── internals ──────────────────────────────────────────────────────────

  /** Bearer-injected, refresh-on-401 raw fetch for SSE/multipart surfaces. */
  private async rawFetch(path: string, init: RequestInit): Promise<Response> {
    // Bind to globalThis so a bare `window.fetch` isn't called detached (browsers
    // throw "Illegal invocation" when fetch loses its window receiver).
    const baseFetch = this.opts.fetch ?? (globalThis as { fetch?: typeof fetch }).fetch?.bind(globalThis);
    if (!baseFetch) throw new Error("No fetch available.");
    const url = this.opts.baseUrl.replace(/\/+$/, "") + path;

    const explicitAuthorization = new Headers(init.headers).has("authorization");
    const withAuth = async (token: string | undefined): Promise<RequestInit> => {
      const headers = new Headers(init.headers);
      if (token && !explicitAuthorization) headers.set("authorization", `Bearer ${token}`);
      return { ...init, headers };
    };

    const token = this.auth ? await this.auth.getAccessToken() : undefined;
    let res = await baseFetch(url, await withAuth(token));
    if (res.status === 401 && !explicitAuthorization && this.auth?.refresh) {
      const fresh = await this.auth.refresh();
      if (fresh) res = await baseFetch(url, await withAuth(fresh));
    }
    return res;
  }

  private async toApiError(res: Response): Promise<NovaApiError> {
    try {
      const body = await res.json();
      return new NovaApiError(res.status, body);
    } catch {
      return new NovaApiError(res.status);
    }
  }
}

// ── pending-actions/groups wire shapes (snake_case → camelCase) ───────────

interface RawPendingAction {
  id: string; agent_id: string; user_id: string; tenant_id: string; session_id: string;
  tool_name: string; risk: string; status: string; result?: string;
  created_at: string; decided_at?: string | null;
  input?: unknown; preview?: unknown;
  source?: string; external_ref?: string; group_id?: string; claimed_by?: string; decided_by?: string;
}

interface RawAuthorizationDataScope {
  resource: string; operation: string;
  selectors?: Record<string, unknown>; constraints?: Record<string, unknown>;
  connector: { kind: string; connection_id?: string; details?: Record<string, unknown> };
}

interface RawAuthorizationIntent {
  id: string; tenant_id: string; agent_id: string; session_id: string; tool_name: string; action_class: string;
  params: unknown; data_scope?: RawAuthorizationDataScope; side_effects?: unknown; reversible: boolean | null;
  max_authorization_seconds: number | null; risk_tier: string; purpose: string; source: string; external_ref: string;
  group_id: string; proposed_by: string; proposed_by_kind: string; proposed_at: string; legacy_action_id?: string;
  policy_version?: string; agent_config_hash?: string; runtime_profile?: unknown; tool_schema_hash?: string;
}

interface RawAuthorizationDecision {
  id: string; intent_id: string; outcome: string; risk_tier: string; grant_id?: string; grant_revision?: number;
  policy_version?: string; runtime_profile?: unknown; evaluated_at: string; decided_by: string; decided_by_kind: string;
  decided_at: string; reason: string; edited: boolean; original_params?: unknown; review_duration_ms?: number;
  batch_id?: string; evidence_weight: number; corrected: boolean; correction_reason?: string;
}

interface RawExecutionReceipt {
  id: string; intent_id: string; attempt_no: number; started_at: string; finished_at: string;
  outcome: ExecutionOutcome; verification_status: VerificationStatus; provider_reference?: string;
  effect_summary: string; effect?: unknown; error?: string; idempotency_key: string;
  rollback_available: boolean; rollback?: unknown;
}

interface RawEvidenceDecayBucket { kind: string; decisions: number; multiplier: number }
interface RawReviewerEvidence {
  reviewer: string; decisions: number; edited: number; rejected: number; fast: number; batched: number;
  edit_rate: number; reject_rate: number; fast_rate: number;
}
interface RawAuthorizationEvidenceProfile {
  agent_id: string; action_class: string; risk_tier: string; policy_version: string; data_scope: RawAuthorizationDataScope;
  profile_hash: string; weighted_approved: number; weighted_rejected: number; effective_approval_rate: number;
  current_decisions: number; historical_decisions: number; incidents: number; eligible: boolean; reason: string;
  decay?: RawEvidenceDecayBucket[]; reviewers?: RawReviewerEvidence[];
}

interface RawAutonomyGrant {
  id: string; revision: number; previous_grant_id?: string; tenant_id: string; agent_id: string; action_class: string;
  tool_bindings?: string[]; risk_tier: string; data_scope: RawAuthorizationDataScope; policy_version: string;
  runtime_profile?: unknown; profile_hash: string; evidence_window: RawAuthorizationEvidenceProfile;
  constraints?: Record<string, unknown>; issued_by: string; issued_at: string; expires_at: string;
  lifecycle_state: GrantLifecycleState; lifecycle_reason: string; lifecycle_changed_at: string; superseded_by?: string;
}

interface RawAuthorizationGraph {
  intent: RawAuthorizationIntent; decisions?: RawAuthorizationDecision[]; receipts?: RawExecutionReceipt[];
  grant?: RawAutonomyGrant; state: string;
}

interface RawExecutionCapability {
  id: string; grant_id?: string; grant_revision?: number; tenant_id: string; agent_id: string; tool_name: string;
  action_class: string; risk_tier: string; data_scope: RawAuthorizationDataScope; policy: "allow" | "ask" | "never";
  policy_version: string; runtime_profile?: unknown; issued_by: string; issued_at: string; expires_at: string;
  revoked_at?: string; revocation_reason?: string; token?: string;
}

function toAuthorizationDataScope(s: RawAuthorizationDataScope): AuthorizationDataScope {
  return {
    resource: s.resource, operation: s.operation, selectors: s.selectors, constraints: s.constraints,
    connector: { kind: s.connector.kind, connectionId: s.connector.connection_id, details: s.connector.details },
  };
}

function fromAuthorizationDataScope(s: AuthorizationDataScope): RawAuthorizationDataScope {
  return {
    resource: s.resource, operation: s.operation, selectors: s.selectors, constraints: s.constraints,
    connector: { kind: s.connector.kind, connection_id: s.connector.connectionId, details: s.connector.details },
  };
}

function toAuthorizationIntent(i: RawAuthorizationIntent): AuthorizationIntent {
  return {
    id: i.id, tenantId: i.tenant_id, agentId: i.agent_id, sessionId: i.session_id, toolName: i.tool_name,
    actionClass: i.action_class, params: i.params, dataScope: i.data_scope ? toAuthorizationDataScope(i.data_scope) : undefined,
    sideEffects: i.side_effects, reversible: i.reversible, maxAuthorizationSeconds: i.max_authorization_seconds,
    riskTier: i.risk_tier, purpose: i.purpose, source: i.source, externalRef: i.external_ref, groupId: i.group_id,
    proposedBy: i.proposed_by, proposedByKind: i.proposed_by_kind, proposedAt: i.proposed_at,
    legacyActionId: i.legacy_action_id, policyVersion: i.policy_version, agentConfigHash: i.agent_config_hash,
    runtimeProfile: i.runtime_profile, toolSchemaHash: i.tool_schema_hash,
  };
}

function toAuthorizationDecision(d: RawAuthorizationDecision): AuthorizationDecision {
  return {
    id: d.id, intentId: d.intent_id, outcome: d.outcome, riskTier: d.risk_tier, grantId: d.grant_id,
    grantRevision: d.grant_revision, policyVersion: d.policy_version, runtimeProfile: d.runtime_profile,
    evaluatedAt: d.evaluated_at, decidedBy: d.decided_by, decidedByKind: d.decided_by_kind, decidedAt: d.decided_at,
    reason: d.reason, edited: d.edited, originalParams: d.original_params, reviewDurationMs: d.review_duration_ms,
    batchId: d.batch_id, evidenceWeight: d.evidence_weight, corrected: d.corrected, correctionReason: d.correction_reason,
  };
}

function toExecutionReceipt(r: RawExecutionReceipt): ExecutionReceipt {
  return {
    id: r.id, intentId: r.intent_id, attemptNo: r.attempt_no, startedAt: r.started_at, finishedAt: r.finished_at,
    outcome: r.outcome, verificationStatus: r.verification_status, providerReference: r.provider_reference,
    effectSummary: r.effect_summary, effect: r.effect, error: r.error, idempotencyKey: r.idempotency_key,
    rollbackAvailable: r.rollback_available, rollback: r.rollback,
  };
}

function toEvidenceProfile(p: RawAuthorizationEvidenceProfile): AuthorizationEvidenceProfile {
  return {
    agentId: p.agent_id, actionClass: p.action_class, riskTier: p.risk_tier, policyVersion: p.policy_version,
    dataScope: toAuthorizationDataScope(p.data_scope), profileHash: p.profile_hash, weightedApproved: p.weighted_approved,
    weightedRejected: p.weighted_rejected, effectiveApprovalRate: p.effective_approval_rate,
    currentDecisions: p.current_decisions, historicalDecisions: p.historical_decisions, incidents: p.incidents,
    eligible: p.eligible, reason: p.reason, decay: p.decay ?? [],
    reviewers: (p.reviewers ?? []).map((r) => ({
      reviewer: r.reviewer, decisions: r.decisions, edited: r.edited, rejected: r.rejected, fast: r.fast,
      batched: r.batched, editRate: r.edit_rate, rejectRate: r.reject_rate, fastRate: r.fast_rate,
    })),
  };
}

function toAutonomyGrant(g: RawAutonomyGrant): AutonomyGrant {
  return {
    id: g.id, revision: g.revision, previousGrantId: g.previous_grant_id, tenantId: g.tenant_id,
    agentId: g.agent_id, actionClass: g.action_class, toolBindings: g.tool_bindings ?? [], riskTier: g.risk_tier,
    dataScope: toAuthorizationDataScope(g.data_scope), policyVersion: g.policy_version, runtimeProfile: g.runtime_profile,
    profileHash: g.profile_hash, evidenceWindow: toEvidenceProfile(g.evidence_window), constraints: g.constraints ?? {},
    issuedBy: g.issued_by, issuedAt: g.issued_at, expiresAt: g.expires_at, lifecycleState: g.lifecycle_state,
    lifecycleReason: g.lifecycle_reason, lifecycleChangedAt: g.lifecycle_changed_at, supersededBy: g.superseded_by,
  };
}

function toAuthorizationGraph(g: RawAuthorizationGraph): AuthorizationGraph {
  return {
    intent: toAuthorizationIntent(g.intent), decisions: (g.decisions ?? []).map(toAuthorizationDecision),
    receipts: (g.receipts ?? []).map(toExecutionReceipt), grant: g.grant ? toAutonomyGrant(g.grant) : undefined,
    state: g.state,
  };
}

function toExecutionCapability(c: RawExecutionCapability): ExecutionCapability {
  return {
    id: c.id, grantId: c.grant_id, grantRevision: c.grant_revision, tenantId: c.tenant_id, agentId: c.agent_id,
    toolName: c.tool_name, actionClass: c.action_class, riskTier: c.risk_tier, dataScope: toAuthorizationDataScope(c.data_scope),
    policy: c.policy, policyVersion: c.policy_version, runtimeProfile: c.runtime_profile, issuedBy: c.issued_by,
    issuedAt: c.issued_at, expiresAt: c.expires_at, revokedAt: c.revoked_at,
    revocationReason: c.revocation_reason, token: c.token,
  };
}

function toPendingAction(a: RawPendingAction): PendingAction {
  return {
    id: a.id, agentId: a.agent_id, userId: a.user_id, tenantId: a.tenant_id, sessionId: a.session_id,
    toolName: a.tool_name, risk: a.risk, status: a.status, result: a.result,
    createdAt: a.created_at, decidedAt: a.decided_at ?? null,
    input: a.input, preview: a.preview,
    source: a.source, externalRef: a.external_ref, groupId: a.group_id,
    claimedBy: a.claimed_by, decidedBy: a.decided_by,
  };
}

interface RawGroup {
  id: string; tenant_id: string; name: string; description?: string;
  created_at: string; updated_at: string;
  members?: Array<{ user_id: string; role: string; created_at: string }>;
}

function toGroup(g: RawGroup): Group {
  return {
    id: g.id, tenantId: g.tenant_id, name: g.name, description: g.description,
    createdAt: g.created_at, updatedAt: g.updated_at,
    members: g.members?.map((m) => ({ userId: m.user_id, role: m.role, createdAt: m.created_at })),
  };
}

interface RawConnectorConfig {
  kind: string; tenant_id?: string; enabled: boolean; group_id?: string;
  config?: Record<string, unknown>; secret_keys?: string[]; updated_at: string;
  personal_allowed?: boolean;
  governance_mode?: GovernanceMode; governance_enforcement?: string;
}

function toConnectorConfig(c: RawConnectorConfig): ConnectorConfig {
  return {
    kind: c.kind, tenantId: c.tenant_id || undefined, enabled: c.enabled,
    groupId: c.group_id || undefined, config: c.config ?? {},
    secretKeys: c.secret_keys ?? [], updatedAt: c.updated_at,
    personalAllowed: c.personal_allowed ?? false,
    governanceMode: c.governance_mode ?? "external",
    governanceEnforcement: c.governance_enforcement ?? "audited; connector service receives credentials",
  };
}

interface RawMyConnectorConfig {
  kind: string; enabled: boolean;
  config?: Record<string, unknown>; secret_keys?: string[]; updated_at: string;
}

function toMyConnectorConfig(c: RawMyConnectorConfig): MyConnectorConfig {
  return {
    kind: c.kind, enabled: c.enabled, config: c.config ?? {},
    secretKeys: c.secret_keys ?? [], updatedAt: c.updated_at,
  };
}

interface RawActionDisposition {
  agent_id: string; approved_as_is?: number; edited_then_approved?: number;
  rejected?: number; decided?: number;
}

interface RawPersonalDomainPolicy {
  domains?: string[]; advisory?: boolean; advisory_reason?: string;
  updated_at?: string; updated_by?: string;
}

function toPersonalDomainPolicy(p: RawPersonalDomainPolicy): PersonalDomainPolicy {
  return {
    domains: p.domains ?? [],
    // Defaults to TRUE when absent. An older kernel that does not send the
    // field is one where the control is advisory too, so the safe default is
    // the caveat, never its absence.
    advisory: p.advisory ?? true,
    advisoryReason: p.advisory_reason ?? "",
    updatedAt: p.updated_at, updatedBy: p.updated_by,
  };
}

interface RawMcpServer {
  id: string; name: string; url: string; description?: string;
  default_policy?: string; enabled?: boolean; has_auth?: boolean;
  created_at?: string; updated_at?: string;
  governance_mode?: GovernanceMode; governance_enforcement?: string;
}

function toMcpServer(s: RawMcpServer): McpServer {
  return {
    id: s.id, name: s.name, url: s.url, description: s.description ?? "",
    // An unrecognised policy reads as `never`, not as `allow`. A value this
    // client cannot interpret must not be rendered as the permissive end of
    // the scale — a UI showing "allow" for a policy it did not understand
    // would be an assertion nobody made.
    defaultPolicy: s.default_policy === "allow" || s.default_policy === "ask"
      ? s.default_policy
      : "never",
    enabled: s.enabled ?? false,
    hasAuth: s.has_auth ?? false,
    createdAt: s.created_at ?? "", updatedAt: s.updated_at ?? "",
    governanceMode: s.governance_mode ?? "external",
    governanceEnforcement: s.governance_enforcement ?? "audited; external server receives credentials",
  };
}

interface RawEntitlements {
  tenant_id: string; flags?: Record<string, unknown>; updated_at?: string;
}

function toEntitlements(e: RawEntitlements): Entitlements {
  return {
    tenantId: e.tenant_id, flags: e.flags ?? {}, updatedAt: e.updated_at || undefined,
  };
}
