// Agent authoring. `defineAgent` returns a serializable definition that
// `LibraAdk.deploy` writes to the LibraOS control plane (`/v1/agents`) and
// `LibraAdk.run` executes on the managed runtime.

import type { ToolDefinition } from "./tool.js";

export type MemoryScope = "per-user" | "corporate" | "none";

export interface GuardrailsConfig {
  piiRedactor?: boolean;
}

export interface AgentDefinition {
  /** Unique agent name / slug. */
  name: string;
  /** Model id — e.g. "libraos/brain", "anthropic/claude-opus-4-8", "openai/…", "gemini/…". */
  model?: string;
  /** System prompt. */
  system?: string;
  /** LibraOS server-side skills to enable (e.g. "docx", "xlsx"). */
  skills?: string[];
  /** Knowledge-collection bindings for RAG (collection ids). */
  knowledge?: string[];
  /** Cross-session memory scope. */
  memory?: MemoryScope;
  /** Per-agent guardrails. */
  guardrails?: GuardrailsConfig;
  /** Capabilities the planner may dispatch to (multi-agent). */
  capabilities?: string[];
  /** Structured-output JSON Schema (maps to LibraOS `output_type`). */
  outputType?: Record<string, unknown>;
  /** Developer-supplied tools (in-process or webhook). */
  tools?: ToolDefinition[];
  /** Max agent-loop turns. */
  maxTurns?: number;
  /** Visibility on the LibraOS control plane. */
  visibility?: "public" | "private";
}

export interface Agent {
  readonly definition: AgentDefinition;
  /** Look up a tool by name (used by the runtime callback in v2). */
  tool(name: string): ToolDefinition | undefined;
  /** Serialize to the LibraOS `POST/PUT /v1/agents` request body. */
  toManagedAgentBody(): Record<string, unknown>;
}

/** Author a LibraOS agent. Deploy + run it with {@link LibraAdk}. */
export function defineAgent(definition: AgentDefinition): Agent {
  if (!definition.name?.trim()) throw new Error("defineAgent: `name` is required");
  const tools = definition.tools ?? [];
  const byName = new Map(tools.map((t) => [t.name, t]));
  if (byName.size !== tools.length) throw new Error("defineAgent: duplicate tool names");
  return {
    definition,
    tool: (name) => byName.get(name),
    toManagedAgentBody: () => toManagedAgentBody(definition),
  };
}

/**
 * Map the SDK's AgentDefinition onto the LibraOS managed-agent body
 * (docs/design/managed-agents-compat.md). Tools are serialized as custom-tool
 * declarations (name + input schema); their execution model — webhook (v1) vs.
 * in-process (v2) — is resolved at run time, not here.
 */
function toManagedAgentBody(def: AgentDefinition): Record<string, unknown> {
  const body: Record<string, unknown> = { name: def.name };
  if (def.model) body.model = def.model;
  if (def.system) body.system = def.system;
  if (def.skills?.length) body.skills = def.skills;
  if (def.capabilities?.length) body.capabilities = def.capabilities;
  if (def.knowledge?.length) body.knowledge_bindings = def.knowledge;
  if (def.maxTurns != null) body.max_turns = def.maxTurns;
  if (def.visibility) body.visibility = def.visibility;
  if (def.outputType) body.output_type = def.outputType;
  if (def.guardrails) body.guardrails = { pii_redactor: def.guardrails.piiRedactor ?? false };
  if (def.tools?.length) {
    body.custom_tools = def.tools.map((t) => ({
      name: t.name,
      description: t.description ?? "",
      input_schema: t.inputSchema,
      ...(t.webhookUrl ? { callback: t.webhookUrl } : {}),
    }));
  }
  return body;
}
