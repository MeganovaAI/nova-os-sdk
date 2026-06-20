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

export interface NovaClientOptions {
  /** Base URL of the Nova OS instance. */
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
    const res = await this.rest.api.GET("/v1/agents");
    throwIfError(res);
    return ((res.data as { data?: Agent[] })?.data ?? []) as Agent[];
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

  // ── internals ──────────────────────────────────────────────────────────

  /** Bearer-injected, refresh-on-401 raw fetch for SSE/multipart surfaces. */
  private async rawFetch(path: string, init: RequestInit): Promise<Response> {
    // Bind to globalThis so a bare `window.fetch` isn't called detached (browsers
    // throw "Illegal invocation" when fetch loses its window receiver).
    const baseFetch = this.opts.fetch ?? (globalThis as { fetch?: typeof fetch }).fetch?.bind(globalThis);
    if (!baseFetch) throw new Error("No fetch available.");
    const url = this.opts.baseUrl.replace(/\/+$/, "") + path;

    const withAuth = async (token: string | undefined): Promise<RequestInit> => {
      const headers = new Headers(init.headers);
      if (token) headers.set("authorization", `Bearer ${token}`);
      return { ...init, headers };
    };

    const token = this.auth ? await this.auth.getAccessToken() : undefined;
    let res = await baseFetch(url, await withAuth(token));
    if (res.status === 401 && this.auth?.refresh) {
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
