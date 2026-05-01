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
