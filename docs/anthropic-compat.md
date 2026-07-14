# Anthropic API Compatibility

Endpoint-by-endpoint compatibility coverage. This doc is the source of truth for "what works against `anthropic.Anthropic(base_url=...)` unchanged, what's extended, what's not implemented." For the use-case-driven walkthrough, see [`docs.meganova.ai/nova-os/anthropic-sdk-quickstart`](https://docs.meganova.ai/nova-os/anthropic-sdk-quickstart).

## TL;DR

The Messages API is 1:1 compatible. The Managed Agents beta API is implemented behind the official beta header. The Claude Agent SDK works via env-var redirect.

## Three drop-in surfaces

| Surface | Constructor / env | What you get | Best when |
|---|---|---|---|
| **Anthropic Messages SDK** | `Anthropic(base_url="...")` | `client.messages.*`, `client.beta.agents.*`, `client.beta.sessions.*` | You already have `anthropic`-SDK code — change one line |
| **Claude Agent SDK** | `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` env | Local agent loop ergonomics (Read/Bash/Edit + custom MCP tools) backed by LibraOS's multi-tenant runtime | You want autonomous agent loops with the Anthropic UX |
| **LibraOS native** | `from nova_os import Client` | Multi-model `model_config` cascade, `output_type` validation, custom-tool webhook callbacks, portable employee bundles, async jobs | You're past hello-world and want LibraOS's extensions |

The first two meet partners where they are. The third is the surface they grow into.

## Auth headers

Both Anthropic header shapes are accepted:

| Env var | Header sent | Used by |
|---|---|---|
| `ANTHROPIC_API_KEY` | `x-api-key: <jwt>` | `Anthropic(api_key="...")` (default) |
| `ANTHROPIC_AUTH_TOKEN` | `Authorization: Bearer <jwt>` | `claude-agent-sdk` (its bundled CLI requires this form) |

If both are set, `Authorization: Bearer` wins. Set one and forget.

> **No `/v1` suffix on `ANTHROPIC_BASE_URL`.** The Anthropic SDK appends `/v1/messages` itself. `ANTHROPIC_BASE_URL=https://nova-os/v1` produces `/v1/v1/messages` → 405 Method Not Allowed.

## Endpoint matrix

| Anthropic endpoint | LibraOS path | Status | Notes |
|---|---|---|---|
| `POST /v1/messages` | `POST /v1/messages` | ✅ 1:1 | Drop-in. Streaming SSE matches upstream event sequence. |
| `POST /v1/messages` (streaming) | same, `stream: true` | ✅ 1:1 | `message_start` → `content_block_delta*` → `message_stop` event sequence. |
| `POST /v1/messages/count_tokens` | `POST /v1/messages/count_tokens` | ✅ 1:1 | Same request shape, returns `{input_tokens: N}`. |
| `POST /v1/messages/batches` | — | 🚫 Not implemented | Use synchronous `messages.create` or async `c.jobs.create` instead. |
| `POST /v1/agents` | `POST /v1/agents` | ✅ Beta | Requires `anthropic-beta: managed-agents-2026-04-01` header. |
| `GET /v1/agents` | `GET /v1/agents` | ✅ Beta | Same pagination shape. |
| `GET /v1/agents/{id}` | same | ✅ Beta | |
| `POST /v1/agents/{id}` (update) | same | ✅ Beta | |
| `DELETE /v1/agents/{id}` | same | ✅ Beta | |
| `POST /v1/agents/{id}/messages` | `POST /v1/agents/{id}/chat` | ✅ Beta | Path differs: Anthropic spec calls it `messages`, LibraOS calls it `chat`. SDK consumers using `client.beta.agents.messages.create(agent_id=..., ...)` work unchanged because the SDK constructs the path from operation, not URL. |
| `POST /v1/sessions` | `POST /v1/sessions` | ✅ Beta | |
| `GET /v1/sessions/{id}` | same | ✅ Beta | |
| `DELETE /v1/sessions/{id}` | same | ✅ Beta | |
| `POST /v1/sessions/{id}/fork` | same | ⚠️ Stubbed | Server returns the parent session; full implementation is in [`MeganovaAI/nova-os#185`](https://github.com/MeganovaAI/nova-os/issues/185) follow-up. |
| `POST /v1/files` | — | 🚫 Not implemented | Use `c.documents` (Nova-OS-native partner-prefix) for file uploads. |
| `POST /v1/admin/*` | — | 🚫 Not implemented | Use `c.users` / `c.settings` (Nova-OS-native partner-prefix) instead. |

The "Beta" rows require the `anthropic-beta: managed-agents-2026-04-01` header. The Anthropic SDK adds this when you use `client.beta.agents.*` or pass `default_headers={"anthropic-beta": "managed-agents-2026-04-01"}` to the constructor.

## Per-endpoint detail

### `POST /v1/messages`

The bare Messages API. Compatible with both `client.messages.create(...)` and `client.messages.stream(...)`.

```python
from anthropic import Anthropic

client = Anthropic(base_url="https://nova-os.your-company.example", api_key="<jwt>")

msg = client.messages.create(
    model="anthropic/claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarize clause 7.3."}],
)
print(msg.content[0].text)
```

**What's identical:**
- Request body shape (`model`, `messages`, `max_tokens`, `system`, `stop_sequences`, `temperature`, `top_p`, `top_k`, `tools`, `tool_choice`, `metadata`)
- Response shape (`id`, `type`, `role`, `content`, `model`, `stop_reason`, `usage`)
- Streaming SSE event sequence (`message_start` → `content_block_start` → `content_block_delta*` → `content_block_stop` → `message_delta` → `message_stop`)
- `Anthropic-Version: 2023-06-01` (SDK sends; server accepts)
- Tool use loop (`tool_use` content block → caller submits `tool_result` → server completes)

**What LibraOS extends (transparent if unused):**
- `model` accepts `<vendor>/<model>` prefix to route across providers (`anthropic/...`, `openai/...`, `gemini/...`). Bare model names without a prefix are rejected at validation; default model is `gemini/gemini-2.5-flash` if unset.
- `metadata.nova_*` fields surface Nova-OS-specific signals on responses (e.g., `nova_route_hint` for the brain dispatch contract). Anthropic-only consumers ignore these freely.

**Gotchas:**
- Bare model names (`gpt-4o`, `claude-opus-4-7` without a `<vendor>/` prefix) get a 400. The default-model server-side fix ([`#197`](https://github.com/MeganovaAI/nova-os/issues/197) / [`#198`](https://github.com/MeganovaAI/nova-os/pull/198)) prefixes the boot-time default for you.
- The MegaNova gateway returns "unable to reach upstream endpoints" 400s on Vertex-routed Gemini calls if a tool's `parameters.properties.X.items` is missing while `type:array` is set — that's Vertex strictly enforcing JSON Schema, not a transient. See [`#731 in mega-nova-api`](https://github.com/MeganovaAI/mega-nova-api/issues/731) for the root-cause pattern.

### `POST /v1/agents` and friends (Managed Agents beta)

```python
client = Anthropic(
    base_url="https://nova-os.your-company.example",
    api_key="<jwt>",
    default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
)

agent = client.beta.agents.create(
    name="legal-assistant",
    model="anthropic/claude-opus-4-7",
    instructions="You answer questions about contracts.",
)

session = client.beta.sessions.create(agent_id=agent.id)
reply = client.beta.agents.messages.create(
    agent_id=agent.id,
    session_id=session.id,
    messages=[{"role": "user", "content": "What's clause 7.3 about?"}],
)
```

**What's identical:**
- Lifecycle ops on agents and sessions (create/list/get/update/delete)
- The beta header gate (`anthropic-beta: managed-agents-2026-04-01`)
- Request bodies for agent + session creation (apart from Nova-OS-only optional fields like `model_config`)

**What LibraOS extends:**
- `model_config` field on agents — declares per-tier (answer / skill / brain / memory_worker) model selections with fallback chains. See [`multi-model.md`](multi-model.md).
- `output_type` field on agents — JSON Schema 2020-12 contract for response validation. Three violation modes: `error` / `log` / `repair`.
- `custom_tools` field on agents — Mode A (SSE inline) and Mode B (webhook) custom-tool registration. See [`custom-tools.md`](custom-tools.md).
- `web_search_config` field on agents — backend selection, fallback chain, reformulator toggle, recency-intent escalation. See [`web-search.md`](web-search.md).
- `route_templates` field on agents — partner-registered URL templates that brain dispatch can fill into `route_hint` responses.

**Gotchas:**
- The `messages` operation on an agent maps to `POST /v1/agents/{id}/chat` (not `/messages`). The SDK constructs the URL from the operation, so `client.beta.agents.messages.create(...)` works as expected.
- `426 Upgrade Required` if you call `/v1/agents` or `/v1/sessions` without the beta header. Add it.

### `POST /v1/messages` (Claude Agent SDK)

The Claude Agent SDK runs a bundled CLI subprocess that hits `/v1/messages` (no Managed Agents beta surface). Set env vars before constructing the SDK client:

```python
import os
os.environ["ANTHROPIC_BASE_URL"] = "https://nova-os.your-company.example"
os.environ["ANTHROPIC_AUTH_TOKEN"] = "<jwt>"   # CLI requires AUTH_TOKEN, not API_KEY

from claude_agent_sdk import query, ClaudeAgentOptions

async def run():
    async for msg in query(
        prompt="Draft a Bill 96 compliance review for Quebec.",
        options=ClaudeAgentOptions(),
    ):
        print(msg)
```

The bundled `claude` CLI binary inherits `os.environ` from the parent process — setting once at the top of the script propagates correctly.

## Differences worth knowing

### Tool use schemas

Anthropic accepts `type: "array"` without an `items` schema; Vertex (which LibraOS may route to) strictly enforces it and returns 400. Always declare `items` on array tool params, even when `items: {}` is the only constraint.

### Model identifier prefixes

Anthropic uses bare model names (`claude-opus-4-7`); LibraOS requires `<vendor>/<model>` (`anthropic/claude-opus-4-7`) for gateway-safe routing. The default has been gateway-safe since the 2026-05-05 v0.1.5 force-update.

| You write | Anthropic accepts | LibraOS accepts |
|---|---|---|
| `claude-opus-4-7` | ✅ | ❌ — 400 at validation |
| `anthropic/claude-opus-4-7` | ✅ (passes through) | ✅ — routes to Anthropic |
| `gemini/gemini-2.5-flash` | N/A | ✅ — routes to Gemini |
| `openai/gpt-5` | N/A | ✅ — routes to OpenAI |

### Streaming events

Identical event shapes. LibraOS may insert one extra event class — `route_hint` — between `agent_execution` and `content`/`done` when the agent emits a brain-dispatch hint. Consumers that don't recognize the event type ignore it (per Anthropic SDK's tolerant parser).

### Response IDs

`msg.id` is a Nova-OS-namespaced ID (`msg_nova_<ulid>`), not an Anthropic-shape ID (`msg_<ulid>`). Code that string-matches the prefix needs to handle both shapes; code that treats it opaquely (most code) works fine.

### What's not implemented

- **Message Batches API** (`POST /v1/messages/batches`) — use synchronous `messages.create` or `c.jobs.create` for async.
- **Files API** (`POST /v1/files`) — use `c.documents` (Nova-OS-native partner-prefix) for file uploads.
- **Admin API** (`POST /v1/admin/*`) — use `c.users` / `c.settings` (Nova-OS-native partner-prefix) instead.
- **Vertex AI direct mode** — LibraOS itself routes to Vertex when configured; partners don't talk Vertex protocol directly.

## Verifying compatibility

The SDK ships a recorded-fixture test (`python/tests/test_anthropic_fixture.py`) that replays a captured Anthropic-shaped request against LibraOS and asserts the response matches. Run as part of the SDK test suite.

For your own verification:

```python
# 1. Health check
curl https://nova-os.your-company.example/api/health
# {"status":"ok","agents_available":67,"agents_registered":67,"circuit_breakers_open":0}

# 2. Bare Messages API
python python/examples/01_basic_chat.py

# 3. Claude Agent SDK redirect
python python/examples/01b_claude_agent_sdk_drop_in.py
```

If both examples succeed, your gateway is Anthropic-compat ready.

## See also

- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
- [`multi-model.md`](multi-model.md) — per-call / per-skill / per-agent / per-employee / server-default cascade
- [`custom-tools.md`](custom-tools.md) — Mode A (SSE inline) and Mode B (webhook) end-to-end
- [`web-search.md`](web-search.md) — pluggable backends + `web_search_config`
- [Anthropic SDK quickstart on docs.meganova.ai](https://docs.meganova.ai/nova-os/anthropic-sdk-quickstart) — patterns A-D walkthrough
