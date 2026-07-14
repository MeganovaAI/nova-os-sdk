/**
 * AG-UI streaming event types.
 *
 * Hand-maintained mirror of `openapi/ag-ui-events.schema.json` — the typed shape
 * of the AG-UI events LibraOS emits over SSE on the `X-Protocol: ag-ui` gated
 * stream. This is a SEPARATE contract from the OpenAPI partner spec's
 * `StreamEvent` union (the #99-native snake_case dialect): AG-UI is the adopted
 * streaming standard (nova-os #370). Wire fields are camelCase and `type` carries
 * the canonical `@ag-ui/core` SCREAMING_SNAKE discriminator. The OpenAPI codegen
 * does NOT produce these (it emits no SSE runtime) — same split as the Python
 * SDK's hand-written `_sse.py`.
 *
 * Each event is one `data: {json}\n\n` SSE frame; `type` discriminates.
 */

/** Lifecycle — the agent run has begun. First frame of a stream. */
export interface RunStarted {
  type: "RUN_STARTED";
  threadId: string;
  runId: string;
}

/** Lifecycle — terminal success frame. `result` is optional. */
export interface RunFinished {
  type: "RUN_FINISHED";
  threadId: string;
  runId: string;
  result?: unknown;
}

/** Lifecycle — terminal error frame, emitted instead of RUN_FINISHED on failure. */
export interface RunError {
  type: "RUN_ERROR";
  message: string;
  code?: string;
}

/** Text streaming — opens an assistant text message. */
export interface TextMessageStart {
  type: "TEXT_MESSAGE_START";
  messageId: string;
  role: string;
}

/** Text streaming — one incremental chunk of the open text message. */
export interface TextMessageContent {
  type: "TEXT_MESSAGE_CONTENT";
  messageId: string;
  delta: string;
}

/** Text streaming — closes the open text message. */
export interface TextMessageEnd {
  type: "TEXT_MESSAGE_END";
  messageId: string;
}

/** Reasoning/thinking stream — opens a reasoning message (gated on stream_thinking). */
export interface ReasoningMessageStart {
  type: "REASONING_MESSAGE_START";
  messageId: string;
}

/** Reasoning/thinking stream — one incremental chunk of reasoning. */
export interface ReasoningMessageContent {
  type: "REASONING_MESSAGE_CONTENT";
  messageId: string;
  delta: string;
}

/** Reasoning/thinking stream — closes the reasoning message. */
export interface ReasoningMessageEnd {
  type: "REASONING_MESSAGE_END";
  messageId: string;
}

/** Tool call — the agent is invoking a tool. Precedes its TOOL_CALL_RESULT. */
export interface ToolCallStart {
  type: "TOOL_CALL_START";
  toolCallId: string;
  toolCallName: string;
}

/** Tool call — one chunk of the serialized-JSON tool arguments, accumulated by toolCallId. */
export interface ToolCallArgs {
  type: "TOOL_CALL_ARGS";
  toolCallId: string;
  /** Serialized JSON chunk; concatenate over toolCallId to reconstruct the args object. */
  delta: string;
}

/** Tool call — argument streaming for this call is complete. */
export interface ToolCallEnd {
  type: "TOOL_CALL_END";
  toolCallId: string;
}

/** Tool call — the result of a completed tool call. */
export interface ToolCallResult {
  type: "TOOL_CALL_RESULT";
  messageId: string;
  toolCallId: string;
  content: string;
  role: string;
}

/** State — an RFC 6902 JSON Patch of incremental changes to shared agent state. */
export interface StateDelta {
  type: "STATE_DELTA";
  /** RFC 6902 JSON Patch — array of operation objects. */
  delta: Array<Record<string, unknown>>;
}

/** State — full state snapshot (alternative to STATE_DELTA). */
export interface StateSnapshot {
  type: "STATE_SNAPSHOT";
  snapshot: unknown;
}

/**
 * Escape hatch for Nova-OS-specific extensions without a standard AG-UI type.
 * `name` is a `nova.<x>` namespaced inner event (e.g. "nova.route_hint").
 * Canonical discriminator "CUSTOM" (NOT "CUSTOM_EVENT").
 */
export interface CustomEvent {
  type: "CUSTOM";
  name: string;
  value: unknown;
}

/** AG-UI passthrough for protocol-aware proxies. Canonical discriminator "RAW". */
export interface RawEvent {
  type: "RAW";
  data: unknown;
}

/** Discriminated union of every AG-UI event LibraOS emits. Switch on `.type`. */
export type AgUiEvent =
  | RunStarted
  | RunFinished
  | RunError
  | TextMessageStart
  | TextMessageContent
  | TextMessageEnd
  | ReasoningMessageStart
  | ReasoningMessageContent
  | ReasoningMessageEnd
  | ToolCallStart
  | ToolCallArgs
  | ToolCallEnd
  | ToolCallResult
  | StateDelta
  | StateSnapshot
  | CustomEvent
  | RawEvent;

/** The set of valid AG-UI `type` discriminator values. */
export type AgUiEventType = AgUiEvent["type"];
