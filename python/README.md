# nova-os-sdk

Python reference SDK for **Nova OS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

Published to PyPI as `nova-os-sdk`. Status: **v0.9.0-rc1** — public API frozen for `v1.0.0`.

## Install

```bash
pip install nova-os-sdk
# Optional — for Anthropic SDK drop-in compatibility
pip install anthropic
```

## Usage

```python
from nova_os import Client, AnthropicCompatClient, WebhookRouter

# Nova OS extended client (multi-model, employees, bundles, async jobs, ...)
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
    model="anthropic/claude-opus-4-7",
    messages=[{"role": "user", "content": "hello"}],
    max_tokens=256,
)

# Mode B custom-tool webhook router (FastAPI mount shown; Flask/Lambda also supported)
router = WebhookRouter(secret="...")
@router.tool("fetch_invoice")
async def fetch_invoice(input, ctx): ...
app.include_router(router.fastapi_router(), prefix="/nova/cb")
```

See `python/examples/` for 7 worked examples covering every public surface.

## Model names — vendor prefix required for the gateway

When Nova OS routes through the MegaNova gateway (the default for cloud + most self-hosted deployments), every model name MUST carry a `<vendor>/` prefix:

| Right | Wrong (returns `model_not_found`) |
|---|---|
| `anthropic/claude-opus-4-7` | `claude-opus-4-7` |
| `anthropic/claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `anthropic/claude-haiku-4-5-20251001` | `claude-haiku-4-5-20251001` |
| `gemini/gemini-3-pro-preview` | `gemini-3-pro-preview` |
| `openai/gpt-5` | `gpt-5` |

This applies to:
- The `model=` arg on `c.messages.create(...)` and `c.jobs.create(...)`
- `model_config.{answer,planner,skill}.primary` in agent + employee YAML
- The `model:` field in agent markdown frontmatter

**For partners using the Anthropic SDK directly:** the SDK's natural default (`claude-opus-4-7` without prefix) won't resolve through the gateway. Either pin to a prefixed model in your config (`ANTHROPIC_HIGH_MODEL=anthropic/claude-opus-4-7`) or add a translation layer that prefixes bare Anthropic model names with `anthropic/` when routing through Nova OS.

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

This is a pre-existing constraint of the underlying Anthropic API; Nova OS forwards what it receives. Partner-defined custom tools (Mode B via `WebhookRouter`) emit `custom_tool_use` events normally.

**Workaround for partners on v1.0.0:** inspect `MessageResponse.content` after the stream completes for `server_tool_use` blocks; OR use the non-streaming `messages.create` path when discrete tool observability matters.

Tracking [`MeganovaAI/nova-os-sdk#10`](https://github.com/MeganovaAI/nova-os-sdk/issues/10) for v1.1 — adds gateway-side synthetic event emission so audit hooks Just Work for server-side tools.

## Error handling

```python
from nova_os import (
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

| Resource | Endpoints |
|----------|-----------|
| `c.agents` | `create`, `get`, `update`, `delete`, `list` |
| `c.employees` | `create`, `get`, `update`, `delete`, `list` |
| `c.messages` | `create` (streaming via `stream()` context manager) |
| `c.jobs` | `create`, `get`, `cancel`, `list` |

## Sync mirror

```python
# For scripts and notebooks — not inside async handlers
sync_agents = c.sync.agents.list()          # returns a plain list
agent = c.sync.agents.create(id="foo", type="skill")
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
