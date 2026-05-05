# Custom Tools

Nova OS supports two transport modes for partner-implemented tools: **Mode A (SSE inline)** and **Mode B (webhook)**. Same tool definition, same agent loop — different transport. Pick whichever matches your service shape.

## TL;DR

- **Mode A — SSE inline.** Partner holds an open streaming connection while the agent runs. Tool calls flow back as `custom_tool_use` events; partner submits results via `submit_tool_result(...)` on the same socket.
- **Mode B — Webhook.** Nova OS POSTs an HMAC-SHA256-signed JSON payload to a partner endpoint per tool call. Partner returns the result in the HTTP response. Idempotent via `tool_use_id` dedup.
- **Both modes are first-class** — declare them per-agent in `custom_tools[]`. Same input schema, same output contract.

## Mode comparison

| Concern | Mode A (inline) | Mode B (webhook) |
|---|---|---|
| **Transport** | SSE on `/v1/messages` (or `/v1/agents/.../chat`) | HTTP POST to partner-registered URL |
| **Partner shape** | Service holding a streaming connection | HTTP server (FastAPI / Flask / Lambda) |
| **Long tool runs** | Bad — connection held while tool runs | Good — connection released, async fan-out |
| **Auth** | Caller's bearer token | HMAC-SHA256 with shared secret |
| **Idempotency** | N/A (single-shot per stream) | Dedup by `tool_use_id` |
| **Best for** | Backend services with persistent processes; quick-result tools | Serverless; fire-and-forget; long-running tool work |

The two modes aren't mutually exclusive. A partner can register some tools as Mode A and others as Mode B on the same agent.

## Mode A — SSE inline

Nova OS pauses the agent mid-run when it wants to call a custom tool, emits a `custom_tool_use` event over the open SSE stream, and waits for the partner's `submit_tool_result(...)` over the same socket before continuing.

### When to pick Mode A

- The partner process is naturally long-lived (backend service, daemon)
- The tool is fast (sub-second to few-second) — connection time isn't a concern
- You don't want to expose a public webhook endpoint
- You want the simplest possible implementation

### Worked example

```python
import os
from typing import Any
from nova_os import Client


async def fetch_invoice(input: dict[str, Any]) -> str:
    invoice_id = input.get("invoice_id", "UNKNOWN")
    return f"Invoice {invoice_id}: status=paid, amount=$1,250.00"


TOOL_HANDLERS = {"fetch_invoice": fetch_invoice}


async def main():
    async with Client(base_url=..., api_key=...) as c:
        async with c.messages.stream(
            agent_id="invoice-bot",
            messages=[{"role": "user", "content": "Show me invoice INV-2026-042"}],
        ) as s:
            async for event in s:
                kind = event.get("type")

                if kind == "text_delta":
                    print(event.get("content", ""), end="", flush=True)

                elif kind == "custom_tool_use":
                    handler = TOOL_HANDLERS.get(event["name"])
                    if handler is None:
                        await s.submit_tool_result(
                            tool_use_id=event["id"],
                            content="tool not implemented",
                            is_error=True,
                        )
                        continue
                    result = await handler(event["input"])
                    await s.submit_tool_result(
                        tool_use_id=event["id"],
                        content=result,
                        is_error=False,
                    )

                elif kind == "message_stop":
                    break
```

Full example: [`python/examples/04_custom_tool_inline.py`](../python/examples/04_custom_tool_inline.py).

### Event sequence

```
client → server : POST /v1/messages (stream:true)
server → client : event: message_start
server → client : event: content_block_start (text)
server → client : event: text_delta
   ...                (model decides to call tool)
server → client : event: custom_tool_use
                  data: {"id": "tool_abc", "name": "fetch_invoice", "input": {...}}
client → server : POST /v1/messages/<msg_id>/tool_result
                  body: {"tool_use_id": "tool_abc", "content": "...", "is_error": false}
server → client : event: tool_result_received
server → client : event: text_delta (model continues)
   ...
server → client : event: message_stop
```

The SDK's `MessageStream.submit_tool_result(...)` wraps the POST round-trip and re-attaches to the original stream — your code sees one continuous event flow.

### Error handling

Set `is_error=True` to signal failure. The agent treats this as a recoverable error and may retry, try a different approach, or surface the failure to the user:

```python
await s.submit_tool_result(
    tool_use_id=event["id"],
    content="rate limited",
    is_error=True,
)
```

## Mode B — Webhook

Nova OS POSTs a signed JSON payload to a partner-registered URL whenever the agent calls a custom tool. Partner runs the tool and returns the result in the HTTP response.

### When to pick Mode B

- Partner is HTTP-server-shaped (FastAPI / Flask / Lambda / Cloudflare Workers)
- Tool runs are long enough that holding an SSE connection is impractical
- You want fire-and-forget for some tools (run async, ack the webhook fast)
- You want each tool's URL to live in a different service / process

### Webhook payload

```json
POST https://partner.example.com/nova/cb/tools/fetch_invoice

Headers:
  Content-Type: application/json
  X-Nova-Signature: t=1714867200,v1=<hex(hmac_sha256(secret, ts + "." + tool_use_id + "." + body))>
  X-Nova-Tool-Use-Id: toolu_abc123
  X-Nova-Agent-Id: invoice-bot
  X-Nova-Employee-Id: legal-team

Body:
{
  "tool_use_id": "toolu_abc123",
  "tool": "fetch_invoice",
  "input": {"invoice_id": "INV-2026-042"},
  "agent_id": "invoice-bot",
  "employee_id": "legal-team",
  "session_id": "sess_xyz",
  "ts": 1714867200
}
```

### Expected response

```json
HTTP/1.1 200 OK
Content-Type: application/json

{"output": "Invoice INV-2026-042: status=paid", "is_error": false}
```

Or for errors:

```json
{"output": "rate limited by ERP", "is_error": true}
```

### Worked example (FastAPI)

```python
import os
from fastapi import FastAPI
from nova_os.callbacks import WebhookRouter

router = WebhookRouter(secret=os.environ["NOVA_CB_SECRET"])


@router.tool("fetch_invoice")
async def fetch_invoice(input: dict, ctx: dict) -> str:
    invoice_id = input.get("invoice_id", "UNKNOWN")
    agent_id = ctx.get("agent_id", "?")
    # In production: query your DB / ERP.
    return f"Invoice {invoice_id}: status=paid"


@router.tool("check_eligibility")
async def check_eligibility(input: dict, ctx: dict) -> dict:
    client_id = input.get("client_id")
    return {"eligible": True, "reason": "All criteria met", "client_id": client_id}


app = FastAPI()
app.include_router(router.fastapi_router(), prefix="/nova/cb")
```

`WebhookRouter` handles:
- HMAC-SHA256 signature verification (rejects with 401 on mismatch)
- Idempotency dedup by `tool_use_id` (skips duplicate deliveries — Nova OS retries on transient failures)
- Replay-window enforcement (5min default — rejects requests with `t` outside the window)
- Auto-serialisation of dict / str / list returns to JSON

Full example: [`python/examples/05_custom_tool_webhook.py`](../python/examples/05_custom_tool_webhook.py).

### Signature scheme

```
t=<unix_ts>,v1=<hex(hmac_sha256(secret, ts + "." + tool_use_id + "." + body))>
```

Three components separated by `.`:

1. **Timestamp** (`ts`) — Unix seconds. Nova OS rejects deliveries with `|now - ts| > 300s` (5min replay window). Partners must verify the same window.
2. **`tool_use_id`** — pins the signature to a specific tool invocation. Replaying the body alone won't pass verification for a different `tool_use_id`.
3. **Body** — the raw JSON body bytes (no whitespace normalization).

### Idempotency dedup

Nova OS may retry webhook deliveries on transient network failures. The same `tool_use_id` may arrive 1-3 times. Partners should dedup:

```python
# WebhookRouter does this for you:
@router.tool("fetch_invoice")
async def fetch_invoice(input, ctx):
    # Already deduped by tool_use_id before reaching this fn.
    ...
```

Or manually (DIY router):

```python
seen_ids = set()
async def handle(req):
    tool_use_id = req.headers["X-Nova-Tool-Use-Id"]
    if tool_use_id in seen_ids:
        return {"output": cached_result_for(tool_use_id), "is_error": False}
    seen_ids.add(tool_use_id)
    ...
```

In production, use Redis / your DB / a TTL cache — in-process sets don't survive restarts.

### Smoke test

Forge a Nova-OS-shaped signed POST to your handler before exposing it to live traffic:

```bash
export NOVA_CB_SECRET=your-shared-hmac-secret
nova-os-cli test-callback \
  --target https://partner.example.com/nova/cb \
  --tool fetch_invoice \
  --input '{"invoice_id":"INV-9912"}'
```

Test idempotency dedup with `--repeat 3 --tool-use-id toolu_dedupe_test` — your handler should run exactly once.

## Tool definition (server-side)

Both modes use the same agent-level tool definition:

```python
await c.agents.create(
    id="invoice-bot",
    type="conversational",
    custom_tools=[
        {
            "name": "fetch_invoice",
            "description": "Fetch invoice details by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Invoice identifier"},
                },
                "required": ["invoice_id"],
            },
            # Mode B: register a callback URL.
            # Omit `callback` to use Mode A (SSE inline).
            "callback": {
                "url": "https://partner.example.com/nova/cb/tools/fetch_invoice",
                "auth": {"type": "hmac_sha256", "secret_ref": "partner_webhook_secret"},
                "timeout_sec": 30,
                "retry": {"max_attempts": 3, "backoff": "exponential"},
            },
        },
    ],
)
```

Without `callback`, the tool runs in Mode A (SSE inline). With `callback`, Mode B (webhook).

### Input schema gotcha (Vertex AI)

If you declare `type: array` in the schema **without** `items`, Nova OS validation rejects the agent on save. This catches a class of failure where Vertex AI strictly enforces JSON Schema and returns 400 at chat time:

```python
# ✗ Rejected at validation:
"input_schema": {"type": "object", "properties": {"ids": {"type": "array"}}}

# ✓ Accepted:
"input_schema": {"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string"}}}}

# ✓ Also accepted (catch-all):
"input_schema": {"type": "object", "properties": {"ids": {"type": "array", "items": {}}}}
```

The CLI's `nova-os-cli validate ./data/` runs this rule offline, before deploy.

## Picking between Mode A and Mode B

| Your situation | Pick |
|---|---|
| Backend service that already holds long-lived connections | Mode A |
| Serverless (Lambda / Cloudflare Workers) | Mode B |
| Tool runs in <1s, partner is HTTP-server-shaped | Either — Mode A is slightly simpler |
| Tool runs in 30s+ | Mode B (don't hold SSE for 30s) |
| Tool runs are fire-and-forget (e.g., kick off a job) | Mode B with `is_error: false` returned immediately |
| Multi-tenant SaaS where tools live in different services | Mode B (each callback URL can point at a different service) |
| Want to test before exposing a public endpoint | Mode A (no public URL needed) |

## Mode B retries + dispatch

When Nova OS POSTs to a partner endpoint and gets a non-2xx response or timeout:

| Response | Action |
|---|---|
| `200 OK` with `is_error: false` | Use result, continue agent loop |
| `200 OK` with `is_error: true` | Surface to agent as recoverable error |
| `4xx` (4xx body) | Surface to agent as fatal error — don't retry (it'd fail the same way) |
| `5xx` or network timeout | Retry with exponential backoff (max 3 by default) |
| Final retry failed | Surface to agent as upstream-error |

Configure per-tool via the `retry` block on the callback:

```python
"callback": {
    "url": "...",
    "auth": {...},
    "retry": {
        "max_attempts": 5,
        "backoff": "exponential",
    },
}
```

## See also

- [`anthropic-compat.md`](anthropic-compat.md) — how custom tools surface in the Anthropic SDK
- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
- [`python/examples/04_custom_tool_inline.py`](../python/examples/04_custom_tool_inline.py) — Mode A worked example
- [`python/examples/05_custom_tool_webhook.py`](../python/examples/05_custom_tool_webhook.py) — Mode B worked example
- [`cli/README.md` → test-callback](../cli/README.md#test-callback-mode-b-webhook-smoke) — webhook smoke-test flow
