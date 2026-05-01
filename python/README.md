# nova-os-sdk

Python reference SDK for **Nova OS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

This is the Python client published to PyPI as `nova-os-sdk`. It wraps an OpenAPI-generated client (under `nova_os._generated/`) with ergonomic Anthropic-compatible and Nova OS extended surfaces.

Status: pre-1.0 — the API surface is being stabilized. Watch this repo's releases for the `v0.9.0-rc` API freeze tag, after which the public Python surface is locked for `v1.0.0`.

## Install

```bash
pip install nova-os-sdk
```

## Quick start

```python
import nova_os

# Async (recommended)
c = nova_os.Client(base_url="https://nova.partner.com", api_key="...")

# List all agents (auto-paginating async iterator)
agents = [a async for a in c.agents.list()]

# Create an agent
agent = await c.agents.create(id="marketing-assistant", type="skill")

# Send a message (non-streaming)
resp = await c.messages.create(
    agent_id="marketing-assistant",
    messages=[{"role": "user", "content": "Hello"}],
)

# Submit a long-running job
job = await c.jobs.create(
    "marketing-assistant",
    messages=[{"role": "user", "content": "Write a full market report"}],
)
# Poll until done
import asyncio
while (job := await c.jobs.get(job["job_id"]))["status"] not in ("completed", "failed"):
    await asyncio.sleep(2)

# Sync mirror — for scripts and notebooks (not inside async handlers)
sync_agents = c.sync.agents.list()          # returns a plain list
agent = c.sync.agents.create(id="foo", type="skill")
agent = c.sync.agents.get("marketing-assistant")
```

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
| `c.messages` | `create` (streaming in Phase 3.2) |
| `c.jobs` | `create`, `get`, `cancel`, `list` |

## Development

```bash
cd python
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT.
