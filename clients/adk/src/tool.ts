// Tool authoring primitive. A tool is a name + JSON-Schema input + either an
// in-process handler (the SDK answers the tool call locally — the v2 round-trip,
// see docs/design/agent-sdk-rfc.md §7) or a webhook URL (LibraOS HMAC-POSTs the
// call — works today, v1).

/** A JSON Schema object describing a tool's input. */
export type JSONSchema = Record<string, unknown>;

/** The developer's tool implementation, invoked with the validated input. */
export type ToolHandler = (input: Record<string, unknown>) => unknown | Promise<unknown>;

export interface ToolDefinition {
  name: string;
  description?: string;
  /** JSON Schema for the tool input. */
  inputSchema: JSONSchema;
  /**
   * In-process handler — invoked when the agent calls this tool. Requires the
   * v2 custom-tool round-trip on the server (libraos/libraos#842). Mutually
   * exclusive with `webhookUrl`.
   */
  handler?: ToolHandler;
  /** Webhook endpoint LibraOS HMAC-POSTs the tool call to (v1 model). */
  webhookUrl?: string;
}

export interface ToolOptions {
  description?: string;
  webhookUrl?: string;
}

/**
 * Define a tool the agent can call.
 *
 * Provide a `handler` for the in-process round-trip (the SDK answers the tool
 * call locally), or pass `{ webhookUrl }` for the webhook model that works
 * today. `inputSchema` is a JSON Schema object.
 */
export function tool(
  name: string,
  inputSchema: JSONSchema,
  handler?: ToolHandler,
  opts: ToolOptions = {},
): ToolDefinition {
  if (!name.trim()) throw new Error("tool: `name` is required");
  return {
    name,
    inputSchema,
    ...(handler ? { handler } : {}),
    ...(opts.description ? { description: opts.description } : {}),
    ...(opts.webhookUrl ? { webhookUrl: opts.webhookUrl } : {}),
  };
}
