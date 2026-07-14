/**
 * Framework-agnostic SSE parser over a fetch `Response` body.
 *
 * Port of the Python SDK's `_sse.py`: consumes the raw `text/event-stream` body,
 * splits on the SSE frame boundary (blank line), and yields the parsed JSON
 * `data:` payload of each frame. Knows nothing about React/axios — works in any
 * runtime with `fetch` + `ReadableStream` (browser, Node 22, RN with a polyfill).
 */

import type { AgUiEvent } from "./events.js";

/** A single parsed SSE frame: its `event:` name (if any) and decoded `data` payload. */
export interface SseFrame<T = unknown> {
  /** The SSE `event:` field, when the server set one. */
  event?: string;
  /** Parsed JSON from the (possibly multi-line) `data:` field. */
  data: T;
  /** The SSE `id:` field, when present (for Last-Event-ID resume). */
  id?: string;
}

/**
 * Parse a fetch `Response` whose body is `text/event-stream` into an async
 * iterator of {@link SseFrame}. Comment lines (`:` prefix — e.g. LibraOS's
 * `:nova-heartbeat`) and frames without a JSON-parseable `data` are skipped.
 */
export async function* parseSse<T = unknown>(
  response: Response,
): AsyncGenerator<SseFrame<T>, void, unknown> {
  const body = response.body;
  if (!body) {
    throw new Error("SSE response has no body");
  }
  const reader = body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by a blank line. Normalize CRLF first.
      let sep: number;
      // eslint-disable-next-line no-cond-assign
      while ((sep = indexOfFrameBoundary(buffer)) !== -1) {
        const rawFrame = buffer.slice(0, sep);
        buffer = buffer.slice(sep).replace(/^(\r?\n){1,2}/, "");
        const frame = parseFrame<T>(rawFrame);
        if (frame) yield frame;
      }
    }
    // Flush any trailing frame without a terminating blank line.
    const tail = buffer.trim();
    if (tail) {
      const frame = parseFrame<T>(tail);
      if (frame) yield frame;
    }
  } finally {
    reader.releaseLock();
  }
}

/** Convenience: iterate a `text/event-stream` body as typed {@link AgUiEvent}s.
 *
 * The kernel's /v1/messages is Anthropic-Messages-compatible and streams
 * Anthropic-native SSE (`message_start` / `content_block_delta` / `message_stop`
 * / `error`). Older builds streamed AG-UI events directly. We normalize BOTH:
 * AG-UI frames pass through by their `type`; Anthropic frames are translated to
 * the AG-UI equivalents the consumers switch on, so a kernel format change never
 * silently drops the stream. */
export async function* parseAgUiStream(
  response: Response,
): AsyncGenerator<AgUiEvent, void, unknown> {
  const AGUI_TYPES = new Set([
    "RUN_STARTED", "RUN_FINISHED", "RUN_ERROR",
    "TEXT_MESSAGE_START", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_END",
    "TOOL_CALL_START", "TOOL_CALL_ARGS", "TOOL_CALL_END", "STATE_DELTA", "CUSTOM",
  ]);
  for await (const frame of parseSse<Record<string, unknown>>(response)) {
    const d = frame.data;
    if (!d || typeof d !== "object" || !("type" in d)) continue;
    const t = (d as { type: string }).type;
    if (AGUI_TYPES.has(t)) {
      yield d as unknown as AgUiEvent;
      continue;
    }
    // ── Anthropic-native SSE → AG-UI translation ──
    if (t === "content_block_delta") {
      const delta = (d as { delta?: { type?: string; text?: string } }).delta;
      if (delta?.type === "text_delta" && typeof delta.text === "string") {
        yield { type: "TEXT_MESSAGE_CONTENT", messageId: "", delta: delta.text } as AgUiEvent;
      }
    } else if (t === "message_stop") {
      yield { type: "RUN_FINISHED", threadId: "", runId: "" } as AgUiEvent;
    } else if (t === "error") {
      const err = (d as { error?: { message?: string } }).error;
      yield { type: "RUN_ERROR", message: err?.message ?? "stream error" } as AgUiEvent;
    }
    // message_start / content_block_start / content_block_stop / message_delta /
    // ping — no AG-UI equivalent needed; skip.
  }
}

function indexOfFrameBoundary(buf: string): number {
  const lf = buf.indexOf("\n\n");
  const crlf = buf.indexOf("\r\n\r\n");
  if (lf === -1) return crlf;
  if (crlf === -1) return lf;
  return Math.min(lf, crlf);
}

function parseFrame<T>(raw: string): SseFrame<T> | undefined {
  let event: string | undefined;
  let id: string | undefined;
  const dataLines: string[] = [];

  for (const line of raw.split(/\r?\n/)) {
    if (line === "" || line.startsWith(":")) continue; // comment / heartbeat
    const colon = line.indexOf(":");
    const field = colon === -1 ? line : line.slice(0, colon);
    // Per the SSE spec a single leading space after the colon is stripped.
    let val = colon === -1 ? "" : line.slice(colon + 1);
    if (val.startsWith(" ")) val = val.slice(1);

    if (field === "event") event = val;
    else if (field === "id") id = val;
    else if (field === "data") dataLines.push(val);
  }

  if (dataLines.length === 0) return undefined;
  const dataStr = dataLines.join("\n");
  if (dataStr === "[DONE]") return undefined;

  try {
    return { event, id, data: JSON.parse(dataStr) as T };
  } catch {
    return undefined;
  }
}
