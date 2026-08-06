# libraos-sdk

Python reference SDK for **LibraOS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

Published to PyPI as `libraos-sdk`. Status: **v1.1.1** — stable; the public API has been frozen since `v1.0.0`.

- [Source](https://github.com/libraos/sdk) · [Issues](https://github.com/libraos/sdk/issues) · [Changelog](https://github.com/libraos/sdk/blob/main/python/CHANGELOG.md) · [Docs](https://libraos.com/docs/)

## Install

```bash
pip install libraos-sdk
# Optional — for Anthropic SDK drop-in compatibility
pip install anthropic
```

## Usage

```python
from libraos import Client, AnthropicCompatClient, WebhookRouter

# LibraOS extended client (multi-model, employees, bundles, async jobs, ...)
async with Client(base_url="https://nova.partner.com", api_key="...") as c:
    agents = [a async for a in c.agents.list()]
    msg = await c.messages.create(
        agent_id="...",
        messages=[{"role": "user", "content": "hi"}],
    )

# Drop-in Anthropic SDK compat — partners using the Anthropic SDK
# can switch base_url and ship without any other code changes.
client = AnthropicCompatClient(base_url="https://nova.partner.com", api_key="...")
msg = client.messages.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[{"role": "user", "content": "hello"}],
    max_tokens=256,
)

# Mode B custom-tool webhook router (FastAPI mount shown; Flask/Lambda also supported)
router = WebhookRouter(secret="...")
@router.tool("fetch_invoice")
async def fetch_invoice(input, ctx): ...
app.include_router(router.fastapi_router(), prefix="/nova/cb")
```

See [`python/examples/`](https://github.com/libraos/sdk/tree/main/python/examples) on GitHub for 20 worked examples covering every public surface, and
[`examples/simulator/`](https://github.com/libraos/sdk/tree/main/examples/simulator) for end-to-end synthetic-customer evaluation runs. The examples are not
shipped inside the installed package — they are scripts to read and copy, not importable modules.

## Synthetic-customer simulator

`client.simulate()` runs a **synthetic customer** against one of your agents and
tells you whether the agent got the job done. An *archetype* describes the
persona the simulator plays — including facts the customer will **not** volunteer
— so you can answer questions like "can this agent handle a customer who
withholds information?"

```python
from libraos import Client

client = Client(base_url="https://nova-eval.partner.com", api_key="...")

result = client.simulate(
    target_agent_id="intake-bot",
    archetype={
        "name": "cautious-applicant",
        "description": "Applicant with a prior visa refusal they are reluctant to raise.",
        "hidden_facts": [
            "visitor visa refused in 2024 — only admits it when asked directly",
            "partner holds a Brazilian passport — only mentions it when asked about family",
        ],
        "disclosure_willingness": "cautious",
        "success_signal": "lawyer matched for immigration with common-law representation",
        "failure_signals": ["lawyer not matched after 10 turns"],
        "termination_conditions": {"max_turns": 10},
    },
)

print(result.outcome)         # "success" | "failure" | "timeout" | "error"
print(result.outcome_reason)  # e.g. "success_signal_matched", "max_turns_reached: 10"
for turn in result.transcript:
    print(f"{turn.role}: {turn.content}")
```

`archetype=` accepts a plain dict (as above), an `Archetype` instance, or a path
to a YAML file — `Archetype.from_dict(...)` / `Archetype.from_yaml_path(...)`.
All three run the full validation chain and raise `ArchetypeValidationError`
with a field path and a human-readable reason, before any call is made.

### Archetype fields

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Lowercase kebab-case identifier. |
| `description` | yes | Who the customer is. |
| `hidden_facts` | yes | Facts the synthetic customer will not volunteer unless drawn out. |
| `disclosure_willingness` | yes | `open` / `cautious` / `guarded` — how readily hidden facts come out. |
| `success_signal` | yes | Defines what passing means. Prefix with `re:` for a regex. |
| `failure_signals` | no | Signals that end the run as a failure. |
| `termination_conditions` | no | `max_turns` (default 10), `success_signal_in_target_response`, `failure_signal_match` (`any` / `all`). |
| `language_register`, `demographic` | no | Flavour for the simulator persona. |
| `model_override` | no | Gateway-prefixed model for the simulator side (default `anthropic/claude-haiku-4-5`). |

### What you get back

`SimulationResult` is a frozen dataclass: `transcript` (a list of `Turn`, each
with `role` — `"simulator"` or `"target"` — plus `content`, `timestamp`,
`metadata`), `outcome`, `outcome_reason`, `evaluation_signals`
(`success_signal_match`, `failure_signal_matches`, `turn_count`), `duration_ms`,
`tokens_used`, and `error`.

### Streaming and async

Pass `stream=True` to watch a run live — an iterator of `TurnEvent`, one event
per turn plus a final `outcome` event. The outcome event **always** fires, even
on error, timeout, or cancellation; failures arrive as events rather than raised
exceptions:

```python
from libraos.simulator import TurnEvent

for event in client.simulate("intake-bot", archetype, stream=True):
    if event.kind in ("simulator_turn", "target_turn"):
        print(f"{event.role}: {event.content}")
    elif event.kind == "outcome":
        print(event.outcome.outcome, event.outcome.outcome_reason)
```

`client.async_simulate(...)` is the async variant — `await` it for a
`SimulationResult`, or iterate it with `async for` when `stream=True`.

> **Run evaluations against a separate instance.** `simulate()` generates real
> traffic; pointing it at production accumulates eval rows in the production
> `call_log`. The recommended setup is a sibling LibraOS instance with its own
> database and empty knowledge collections.

A full CI-ready runner — loads every archetype in a directory, streams turns,
writes JSON transcripts, exits non-zero on error — is at
[`examples/simulator/run_eval.py`](https://github.com/libraos/sdk/tree/main/examples/simulator).

## Model names — vendor prefix required for the gateway

When LibraOS routes through the MegaNova gateway (the default for cloud + most self-hosted deployments), every model name MUST carry a `<vendor>/` prefix:

| Right | Wrong (returns `model_not_found`) |
|---|---|
| `Qwen/Qwen3.6-35B-A3B` | `Qwen3.6-35B-A3B` |
| `anthropic/claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `anthropic/claude-haiku-4-5-20251001` | `claude-haiku-4-5-20251001` |
| `openai/gpt-5` | `gpt-5` |

This applies to:
- The `model=` arg on `c.messages.create(...)` and `c.jobs.create(...)`
- `model_config.{answer,planner,skill}.primary` in agent + employee YAML
- The `model:` field in agent markdown frontmatter

**For partners using the Anthropic SDK directly:** the SDK's natural default (`claude-opus-4-7` without prefix) won't resolve through the gateway. Either pin to a gateway-safe prefixed model in your config (for example, `ANTHROPIC_HIGH_MODEL=Qwen/Qwen3.6-35B-A3B`) or add a translation layer that prefixes bare Anthropic model names with `anthropic/` when routing through LibraOS.

The `agent_inference_model` and `ollama_embed_model` settings are exempt — they route to a local Ollama and use `<tag>:<version>` shape (e.g. `gemma4:e4b`).

To list all registered models (catalog discovery):

```python
# Direct gateway query, requires a gateway-scoped key
import httpx
r = httpx.get("https://nova.partner.com/v1/models", headers={"Authorization": f"Bearer {api_key}"})
print([m["id"] for m in r.json()["data"]])
```

## Server-side tool observability — known v1.0.0 limitation

Anthropic-provided server-side tools (`web_search_20250305`, `code_execution_20250522`, etc.) execute on Anthropic's infrastructure and DO NOT emit discrete `content_block_start` / `content_block_stop` events on the SSE stream. Audit hooks that fire on `content_block_stop` for `tool_use` blocks won't see these invocations.

**Visible:** the model's text response references the search; `MessageResponse.content[]` (non-streaming) contains `server_tool_use` blocks.
**Not visible:** discrete tool-invocation events on the streaming path. Affects observability hooks that watch the SSE stream for `tool_use` events.

This is a pre-existing constraint of the underlying Anthropic API; LibraOS forwards what it receives. Partner-defined custom tools (Mode B via `WebhookRouter`) emit `custom_tool_use` events normally.

**Workaround for partners on v1.0.0:** inspect `MessageResponse.content` after the stream completes for `server_tool_use` blocks; OR use the non-streaming `messages.create` path when discrete tool observability matters.

Tracking [`libraos/sdk#10`](https://github.com/libraos/sdk/issues/10) for v1.1 — adds gateway-side synthetic event emission so audit hooks Just Work for server-side tools.

## Error handling

```python
from libraos import (
    NovaOSError,
    NotFoundError,
    RateLimitedError,
    BillingError,
    VertexSchemaError,
)

try:
    agent = await c.agents.get("does-not-exist")
except NotFoundError:
    print("agent not found")
except RateLimitedError as e:
    print(f"rate limited — retry after {e.retry_after}s")
except BillingError as e:
    print(f"billing issue: {e.code}")
except VertexSchemaError as e:
    # Deterministic schema bug — do NOT retry, fix the tool schema
    print(f"Vertex schema error on tool={e.tool_name} param={e.parameter_path}")
    print(f"Hint: {e.fix_hint}")
```

## Idempotency

Pass `idempotency_key=` to any `create()` call to safely retry on network failure:

```python
agent = await c.agents.create(
    id="marketing-assistant",
    type="skill",
    idempotency_key="create-marketing-agent-v1",
)
```

## Resources

All twelve resources are bound on the client, and their methods are `async`
(`c.messages.stream()` returns an async context manager rather than a coroutine).
The [sync mirror](#sync-mirror) currently covers `agents`, `employees`, `messages`
and `jobs` only — reach the other eight through the async surface.

| Resource | Endpoints | What it's for |
|----------|-----------|---------------|
| `c.agents` | `create`, `get`, `update`, `delete`, `list` | Agent definitions — the things you send messages to. |
| `c.employees` | `create`, `get`, `update`, `delete`, `list` | Model-routing owners; one employee can own many agents. |
| `c.messages` | `create`, `stream` | Send a turn; `stream` returns an SSE context manager. |
| `c.jobs` | `create`, `get`, `cancel`, `list` | Long-running async work. |
| `c.documents` | `upload`, `list`, `delete` | Upload documents; auto-indexed on upload, then referenced by `document_id`. |
| `c.knowledge` | `search`, `ingest`, `collections` | Hybrid search + ingest over knowledge collections. Collections are scoped by API-key auth — you cannot read another tenant's collection regardless of name; `search` defaults to the caller's own collection. |
| `c.hooks` | `create`, `get`, `delete`, `list` | Register webhook subscriptions for platform events. |
| `c.filesystem` | `list`, `read`, `write`, `delete` | Per-tenant/session agent workspace (`tenant_id` + `session_id` scoped). |
| `c.users` | `create`, `get`, `delete`, `list` | Tenant user administration. |
| `c.settings` | `all`, `get`, `put` | Read/write platform settings (heterogeneously typed values). |
| `c.sessions` | `create`, `get` | Explicit sessions bound to an agent, with an optional session-default model. |
| `c.personas` | `list`, `get` | Persona manifest discovery; `list` accepts `if_none_match` and returns `None` on a 304. |

Knowledge search, the most commonly looked-for surface:

```python
collections = await c.knowledge.collections()
hits = await c.knowledge.search(query="refund policy", collection=collections[0])
```

## Sync mirror

```python
# For scripts and notebooks — not inside async handlers
sync_agents = c.sync.agents.list()          # returns a plain list
agent = c.sync.agents.create(id="foo", type="skill")
```

## Streaming

`c.messages.stream()` opens an SSE connection and returns an async context manager:

```python
async with c.messages.stream(
    agent_id="invoice-bot",
    messages=[{"role": "user", "content": "Process invoice INV-9912"}],
) as stream:
    async for event in stream:
        if event["event"] == "text":
            print(event["data"]["content"], end="", flush=True)
        elif event["event"] == "done":
            print()  # newline at end
```

**Mode A — custom-tool inline** (intercept the LLM tool call, compute result, resume):

```python
async with c.messages.stream(
    agent_id="invoice-bot",
    messages=[{"role": "user", "content": "Fetch invoice INV-9912"}],
    message_id="my-request-id",  # required for submit_tool_result before done
) as stream:
    async for event in stream:
        if event["event"] == "custom_tool_use":
            result = await my_invoice_lookup(event["data"]["input"]["invoice_id"])
            await stream.submit_tool_result(event["data"]["id"], result)
```

## Webhook router (Mode B)

`WebhookRouter` receives LibraOS custom-tool dispatches on your HTTP endpoint, verifies the HMAC-SHA256 signature, dedupes by idempotency key, and dispatches to registered handlers:

```python
from libraos import WebhookRouter

router = WebhookRouter(secret="your-webhook-secret")

@router.tool("fetch_invoice")
async def fetch_invoice(input: dict, ctx: dict) -> str:
    invoice = await db.get_invoice(input["invoice_id"])
    return f"Invoice {invoice.id}: ${invoice.amount}"
```

**FastAPI mount:**

```python
from fastapi import FastAPI

app = FastAPI()
app.include_router(router.fastapi_router(), prefix="/nova/callbacks")
```

**Flask mount:**

```python
from flask import Flask

app = Flask(__name__)
app.register_blueprint(router.flask_blueprint(), url_prefix="/nova/callbacks")
```

**AWS Lambda mount:**

```python
handler = router.aws_lambda_handler()  # pass to Lambda runtime
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Development

```bash
cd python
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT.
