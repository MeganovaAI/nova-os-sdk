---
layout: default
title: Desk chat API
---

# The Desk chat API — building a native chat client

The contract a chat client speaks to a LibraOS deployment: authentication,
conversations, streaming messages, and the events on the wire. The Libra Desk
web app (`services/employee-ui` in the desk repo) and the official TypeScript
client in this repo are both built on exactly what is documented here — there
is no private surface behind them.

**Scope note.** "The Desk API" in practice means the **kernel** API: chat is
served by the LibraOS kernel (`/v1/*`, `/oauth/*`), and every endpoint below
appears in [`openapi/libra-os-partner.v1.yaml`](https://github.com/libraos/sdk/blob/main/openapi/libra-os-partner.v1.yaml),
which is the source of truth when this page and the spec disagree. The Desk
*runtime*'s own endpoints (`/api/ag-ui/*`, `/api/copilotkit/*`,
`/connectors/*`) are internal to the Desk web app and are **not** part of the
client contract — a native client never calls them.

Reference implementations, in this repo:

| What | Where |
|---|---|
| Full client (conversations, streaming, jobs) | [`clients/typescript/src/client.ts`](https://github.com/libraos/sdk/blob/main/clients/typescript/src/client.ts) |
| OIDC auth-code + PKCE flow | [`clients/typescript/src/auth/oidc.ts`](https://github.com/libraos/sdk/blob/main/clients/typescript/src/auth/oidc.ts) |
| SSE / AG-UI parsing | [`clients/typescript/src/streaming/`](https://github.com/libraos/sdk/blob/main/clients/typescript/src/streaming/) |
| AG-UI event schema | [`openapi/ag-ui-events.schema.json`](https://github.com/libraos/sdk/blob/main/openapi/ag-ui-events.schema.json) |

## 1. Authentication

OIDC authorization-code + PKCE against the kernel's embedded provider. Every
API request then carries `Authorization: Bearer <access_token>`.

| Step | Endpoint |
|---|---|
| Discovery | `GET /.well-known/openid-configuration` |
| Authorize (browser/custom tab) | `GET /oauth/authorize?response_type=code&client_id=…&redirect_uri=…&scope=openid profile email offline_access&code_challenge=…&code_challenge_method=S256&state=…` |
| Code exchange | `POST /oauth/token` (form) `grant_type=authorization_code&code=…&client_id=…&redirect_uri=…&code_verifier=…` |
| Refresh | `POST /oauth/token` (form) `grant_type=refresh_token&refresh_token=…&client_id=…` |
| Who am I | `GET /oauth/userinfo` |

Notes that matter for a mobile client:

- Request `offline_access` or there is no refresh token and the session dies
  at access-token expiry.
- Refresh tokens are **single-use and rotated**: every refresh response
  carries a new `refresh_token`; presenting an already-rotated token revokes
  the whole lineage (leak detection). Persist the newest one atomically.
- The `client_id` must be registered on the deployment (its redirect URI is
  matched byte-for-byte). Deployments register clients via
  `LIBRA_OS_OIDC_CLIENTS`; ask the operator which client id your app uses.
- Tenant/user isolation is enforced server-side per bearer. The client never
  filters other users' data — a conversation that is not yours is a 404, not
  a filtered-out row.

## 2. Conversations

All endpoints require the bearer. The server owns ordering and timestamps.

| Call | Shape |
|---|---|
| `GET /v1/conversations?agent=…&limit=…` | → `{conversations: Conversation[]}`, newest first. `limit` 1–200, default 50. |
| `POST /v1/conversations` `{id?, agent_id?, title?, metadata?}` | → `201 Conversation`. Idempotent on `id`: re-posting returns the existing row without overwriting owner or metadata. |
| `GET /v1/conversations/{id}` | → `ConversationDetail` — the summary **plus the full message log** (`messages: [{role, content, timestamp}]`). This is the history-restore call. 404 covers both "does not exist" and "not yours". |
| `PATCH /v1/conversations/{id}` `{title}` | Rename. Trimmed; empty clears; ≤ 200 chars. |
| `DELETE /v1/conversations/{id}` | Delete. |
| `PATCH /v1/conversations/{id}/metadata` `{metadata}` | **Replace** (not merge) the app-owned metadata map. `nova_`-prefixed keys rejected; serialized map ≤ 4 KB. |

`Conversation`: `{id, agent_id, title?, created_at, last_active_at,
message_count, metadata?}`.

You do not have to create a conversation before chatting: `POST /v1/messages`
with a fresh `conversation_id` auto-creates it. Explicit create exists for
clients that want the row (title, metadata) before the first turn.

## 3. Sending a message (streaming)

```
POST /v1/messages
Authorization: Bearer <token>
Content-Type: application/json
Accept: text/event-stream
X-Protocol: ag-ui
```

```json
{
  "messages": [{ "role": "user", "content": "Hello" }],
  "model": "employee",
  "max_tokens": 1024,
  "stream": true,
  "scope": "corporate",
  "conversation_id": "c-3f2…",
  "message_id": "f81d…",
  "metadata": { "agent_id": "employee" }
}
```

Field by field, as the Desk web client sends it:

- `messages` — the new user turn only. Server-side conversation persistence
  means you do **not** replay history; the kernel loads it from
  `conversation_id`.
- `model` — the agent/persona id. LibraOS resolves a persona id here and the
  persona then uses its own configured model and knowledge grounding; also
  set `metadata.agent_id` to the same value.
- `stream: true` + `X-Protocol: ag-ui` — selects the AG-UI SSE dialect below.
  Without the header you get the Anthropic-style `StreamEvent` dialect
  instead; with `stream: false` you get one JSON `MessageResponse`.
- `scope` — `"personal" | "corporate"`, the personal/company data membrane.
  Same transport, distinct data boundary; send the scope the surface the user
  is in belongs to. Omitted = corporate.
- `conversation_id` — persists the turn into that conversation, auto-creating
  it on first use.
- `message_id` — client-minted idempotency key for **this user turn**. A
  retry of a failed send must reuse the failed turn's id: the kernel dedupes
  the user row (#909) and, when the turn already completed server-side,
  **replays the stored assistant answer instead of re-running the model**
  (#916). It is echoed back as the message `id` in
  `GET /v1/conversations/{id}`, which is what reconciliation matches on.

## 4. The AG-UI event stream

SSE: each event is one `event:` line naming the type plus one `data:` line of
JSON. Full schema: [`ag-ui-events.schema.json`](https://github.com/libraos/sdk/blob/main/openapi/ag-ui-events.schema.json).

A typical assistant turn:

```
RUN_STARTED
TEXT_MESSAGE_START          (assistant message opens)
TEXT_MESSAGE_CONTENT …      (append `delta` to the visible text, in order)
TEXT_MESSAGE_END
RUN_FINISHED
```

Also in the vocabulary:

- `REASONING_MESSAGE_START/CONTENT/END` — model reasoning, render separately
  or not at all.
- `TOOL_CALL_START/ARGS/END` — the agent using a tool mid-turn; between END
  and the next TEXT_MESSAGE the agent is waiting on the tool.
- **Citations/sources** ride dedicated source events on the same stream (and,
  from some agents, as structured source markers in the text — the TypeScript
  client's `streaming/events.ts` shows both being handled). Render them per
  assistant message.
- `RUN_ERROR` — terminal; carries a message. The turn is over; anything
  already streamed stays on screen.

Parse defensively: unknown event types must be skipped, not crash the client
— the vocabulary grows.

## 5. Disconnects, retries, reconnecting

The stream is plain SSE over one HTTP response; a dropped network drops the
stream mid-turn. The recovery contract, exactly as the Desk web client
implements it:

1. **Reconcile first.** On reconnect, `GET /v1/conversations/{id}` and match
   your pending turn by its `message_id` (echoed as the message `id` in the
   log): if the assistant's reply is there, the turn completed while you were
   gone — render it and do not resend.
2. Otherwise resend with the **same** `message_id`. On current kernels this
   is safe end to end: the user row is deduped (#909) and a turn that
   completed in the meantime is answered by **replaying the stored reply**,
   not by running the model again (#916). Against older kernels that predate
   #916, a repeated send re-ran the model and appended a duplicate answer —
   which is why reconcile-first is the documented order rather than a blind
   retry loop.
3. There is no mid-stream byte resume for `/v1/messages`: you reconnect to
   state (the conversation log), not to the stream. (Long-running *jobs* do
   support `Last-Event-ID` resume — see `streamJob` in the client — but chat
   turns are short and the log is the recovery mechanism.)

## 6. Spec gaps (tracked)

Everything above is live kernel behavior, but four request/response fields
lag in `libra-os-partner.v1.yaml` at the time of writing:

- `MessageRequest.scope` (`"personal" | "corporate"`, #673)
- `MessageRequest.conversation_id` (and its AG-UI alias `threadId`, #721)
- `MessageRequest.message_id` (#909/#916)
- `ConversationMessage.id` (the echoed idempotency key)

The kernel accepts and returns them today; the spec addition is coordinated
with the kernel's pinned spec hash and tracked separately. When the spec and
this page disagree on anything *else*, the spec wins.

## 7. Errors

Error bodies are `{error, message?}`. The ones a chat client must handle:

| Status | Meaning | Client behavior |
|---|---|---|
| 401 | Token expired/invalid | Refresh once, then re-auth interactively. |
| 404 | Not found **or not yours** (deliberately indistinguishable) | Drop the local reference. |
| 413 | Metadata over 4 KB | Fix the payload; not retryable as-is. |
| 429 | Rate limited | Back off; honor `Retry-After` when present. |
| `RUN_ERROR` (in-stream) | Turn failed server-side | Show the message; keep streamed partials; offer retry per §5. |
