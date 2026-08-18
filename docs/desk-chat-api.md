---
title: Desk Chat and Conversation API
---

# Desk chat and conversation API

This is the public client contract used by Libra Desk, the Android app, and
other first-party chat clients. The API is served by the LibraOS kernel; Desk
does not introduce a second chat server, message store, or event protocol.

Use this contract when a client needs to:

- list, open, create, rename, or delete a user's conversations;
- send a turn and persist it into a conversation;
- stream assistant text, citations, and lifecycle events;
- keep personal and organization data separated; or
- recover after a dropped stream without duplicating a turn.

Connector administration and Desk-only aggregation routes under
`/api/ag-ui/*` and `/api/copilotkit/*` are not part of this public contract.

## Authentication and ownership

Every request carries a LibraOS OIDC access token:

```http
Authorization: Bearer <access-token>
```

Use authorization code + PKCE for an interactive client. On `401`, refresh the
token once and retry once. See [OIDC client flow](oidc-client-flow.md).

| Step | Endpoint |
|---|---|
| Discovery | `GET /.well-known/openid-configuration` |
| Public signing keys | `GET /.well-known/jwks.json` |
| Authorize in a browser/custom tab | `GET /oauth/authorize` |
| Exchange code or refresh | `POST /oauth/token` |
| Current identity | `GET /oauth/userinfo` |

Request `offline_access` to receive a refresh token. Refresh tokens rotate on
every use: persist the replacement atomically and never present the old token
again. Reuse detection revokes the replacement lineage. ID tokens are RS256
and verified through the discovery document's `jwks_uri`.

Conversation ownership and tenant isolation are enforced by the server. A
client must never fetch all conversations and filter another user's data
locally. A conversation that does not exist and one owned by somebody else both
return `404` so identifiers cannot be probed.

## Endpoint summary

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/conversations?scope=&agent=&limit=` | List the caller's conversations, newest first |
| `POST` | `/v1/conversations` | Optionally claim an id before the first turn |
| `GET` | `/v1/conversations/{id}` | Read metadata and the complete ordered message history |
| `PATCH` | `/v1/conversations/{id}` | Rename a conversation |
| `PATCH` | `/v1/conversations/{id}/metadata` | Replace app-owned metadata |
| `DELETE` | `/v1/conversations/{id}` | Delete the conversation and message history |
| `POST` | `/v1/messages` | Run one turn; optionally persist and stream it |

The canonical machine-readable request and response schemas are in
[`openapi/libra-os-partner.v1.yaml`](../openapi/libra-os-partner.v1.yaml).

## Personal and organization scope

`scope` is the data membrane:

- `personal` uses the individual's private assistant and private grounding.
- `corporate` uses governed organization knowledge, employees, approvals, and
  audit controls.

Send an explicit scope on every Desk message. A new conversation takes its
scope from its first persisted turn. The list endpoint can filter it on the
server:

```http
GET /v1/conversations?scope=corporate&limit=50
```

Conversation list and detail responses include the effective scope. Do not
infer it from `project_id`, the selected employee, or the current screen.

## Conversations

### Create

Creating first is optional because `/v1/messages` auto-creates an unknown
`conversation_id`. Create explicitly when the client needs an addressable id or
metadata before the first turn:

```http
POST /v1/conversations
Content-Type: application/json

{
  "id": "b328425e-2d71-4ddd-a86d-c7c73de6db4e",
  "agent_id": "support-assistant",
  "metadata": { "surface": "android" }
}
```

`id` and `agent_id` are optional. Repeating the same id is idempotent and does
not overwrite the existing owner or metadata. Metadata keys beginning with
`nova_` are reserved and the serialized map is limited to 4 KB.

### List

```json
{
  "conversations": [
    {
      "id": "b328425e-2d71-4ddd-a86d-c7c73de6db4e",
      "agent_id": "support-assistant",
      "title": "PGWP options",
      "created_at": "2026-08-18T12:00:00Z",
      "last_active_at": "2026-08-18T12:03:00Z",
      "message_count": 2,
      "scope": "corporate"
    }
  ]
}
```

Supported query parameters:

- `scope=personal|corporate` selects the server-enforced data boundary.
- `agent=<id>` limits the list to one employee/persona.
- `limit=1..200` defaults to 50.

### Detail and ordering

`GET /v1/conversations/{id}` returns the summary plus `messages`:

```json
{
  "id": "b328425e-2d71-4ddd-a86d-c7c73de6db4e",
  "agent_id": "support-assistant",
  "title": "PGWP options",
  "created_at": "2026-08-18T12:00:00Z",
  "last_active_at": "2026-08-18T12:03:00Z",
  "message_count": 2,
  "scope": "corporate",
  "messages": [
    {
      "id": "39bd2d85-f118-4192-a1e8-e9c2c988cfcc",
      "role": "user",
      "content": "What are my options?",
      "timestamp": "2026-08-18T12:00:00Z",
      "seq": 1
    },
    {
      "id": "msg_01",
      "role": "assistant",
      "content": "…",
      "timestamp": "2026-08-18T12:00:02Z",
      "seq": 2
    }
  ]
}
```

Render messages in the order returned. `seq` is server-assigned, 1-based, and
monotonic; local timestamps are not an ordering authority.

## Send and stream a turn

```http
POST /v1/messages
Accept: text/event-stream
Content-Type: application/json
X-Protocol: ag-ui

{
  "model": "support-assistant",
  "messages": [{ "role": "user", "content": "What are my options?" }],
  "conversation_id": "b328425e-2d71-4ddd-a86d-c7c73de6db4e",
  "message_id": "39bd2d85-f118-4192-a1e8-e9c2c988cfcc",
  "scope": "corporate",
  "max_tokens": 1024,
  "stream": true,
  "metadata": { "agent_id": "support-assistant" }
}
```

Only the newest user turn needs to be sent. LibraOS reads prior history from
`conversation_id`. For Desk clients:

- `model` is required; set it to the selected employee/persona id.
- `metadata.agent_id` explicitly routes the employee that handles the turn.
- `conversation_id` persists the exchange and auto-creates the conversation.
- `message_id` is a fresh client-generated idempotency key for one logical
  user turn. Reuse the same value only when retrying that turn.
- `scope` is required by the product contract even though non-Desk compatibility
  clients may omit it.

For a non-streaming call, set `stream:false` and omit `X-Protocol`; the response
is an Anthropic-compatible `MessageResponse`. The actual provider model is also
reported in `X-Nova-Model-Used`; do not confuse the response's persona selector
with the model that ran.

### AG-UI events

With `X-Protocol: ag-ui`, each SSE frame contains a JSON object in `data:`. The
normal lifecycle is:

```text
RUN_STARTED
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT × N
TEXT_MESSAGE_END
RUN_FINISHED
```

`RUN_ERROR` replaces `RUN_FINISHED` on a run failure. Tool, state, and reasoning
events can appear between lifecycle frames. Unknown event types are ignored so
the protocol remains forward-compatible. The complete schema is
[`openapi/ag-ui-events.schema.json`](../openapi/ag-ui-events.schema.json).

LibraOS extensions use AG-UI's `CUSTOM` event:

```json
{
  "type": "CUSTOM",
  "name": "nova.citations",
  "value": { "citations": [] }
}
```

Web research sources use `name: "nova.search_sources"`. Render URLs from that
payload rather than treating model-written outlet names as verified links.
Structured citations in a non-streaming response are on a text block's
`citations` array.

Without the AG-UI header, streaming uses Anthropic's
`message_start → content_block_delta → message_stop` sequence. The TypeScript
client normalizes both dialects to AG-UI events.

## TypeScript example

```ts
import { LibraOSClient } from "@libraos/client";

const libraos = new LibraOSClient({ baseUrl, auth: oidc });
const conversationId = crypto.randomUUID();

for await (const event of libraos.streamMessage({
  model: "support-assistant",
  messages: [{ role: "user", content: "What are my options?" }],
  conversation_id: conversationId,
  message_id: crypto.randomUUID(),
  scope: "corporate",
  max_tokens: 1024,
  stream: true,
  metadata: { agent_id: "support-assistant" },
})) {
  if (event.type === "TEXT_MESSAGE_CONTENT") {
    process.stdout.write(event.delta);
  } else if (event.type === "CUSTOM" && event.name === "nova.citations") {
    renderCitations(event.value);
  }
}

const history = await libraos.getConversation(conversationId);
```

`LibraOSClient.listConversations({ scope: "corporate" })` applies the boundary at
the server. The client checks HTTP status before reading an SSE body and throws
`NovaApiError` for rejected streams.

## Disconnect recovery and idempotency

A dropped socket does not prove that the server failed. Recover in this order:

1. Read `GET /v1/conversations/{conversation_id}`.
2. Find the user message whose `id` equals the sent `message_id`.
3. If an assistant message follows it, replace the partial local answer with
   that persisted answer.
4. If the server has no record of the user message, retry using the same
   `message_id`.
5. If the user message exists but has no answer, show a recoverable error and
   avoid launching a concurrent retry.

Completed retries are idempotent: LibraOS replays the persisted answer instead
of running the model again. The reconcile-first flow still avoids racing a turn
that remains in flight. `/v1/messages` does not currently emit resumable SSE
`id:` fields, so `Last-Event-ID` is not a substitute for reconciliation today.

## Errors

| Status | Meaning | Client behavior |
|---|---|---|
| `400` | Invalid request or scope | Show the server validation message |
| `401` | Missing or expired token | Refresh once, then sign out |
| `403` | Agent/app entitlement or policy denial | Show the governed approval/permission path |
| `404` | Agent or conversation unavailable | Remove stale conversation navigation |
| `413` | Conversation metadata exceeds 4 KB | Ask the caller to reduce metadata |
| `422` | Output-contract validation failed | Show the validation failure |
| `429` | Rate limited | Honor `Retry-After` and back off |
| `503` | Agent or upstream unavailable | Retry with bounded backoff |

Every chat UI should distinguish loading, streaming, reconnecting, offline,
empty, and failed states.
