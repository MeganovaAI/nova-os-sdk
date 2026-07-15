# libraos-adk (Python)

**LibraOS Agent Development Kit** — author agents in code, run them on the
**LibraOS managed stack** (hosted, governed execution). Python sibling of
[`@libraos/adk`](../adk); companion to the [`libraos`](../../python) client.

> **Status: v1 scaffold (alpha).** Authoring API + CLI shape are stable. `run`
> targets the durable **jobs** surface that works today; the exact wire shapes
> and the in-process custom-tool round-trip are being finalized — see the design
> docs in `libraos/libraos` (`docs/design/agent-sdk-rfc.md`) and issues #840–#842.

## Install

```bash
pip install libraos-adk
```

## Author an agent

```python
# agent.py
from libraos_adk import define_agent, tool

def lookup_order(args):
    return my_db.orders.get(args["orderId"])   # in-process (v2)

agent = define_agent(
    "refund-copilot",
    model="libraos/brain",                      # or "anthropic/claude-opus-4-8", "openai/…", "gemini/…"
    system="You handle refund requests…",
    skills=["docx", "xlsx"],                    # LibraOS server-side skills
    knowledge=["collection:refunds"],           # declarative RAG binding
    memory="per-user",                          # governed cross-session memory
    guardrails={"pii_redactor": True},
    tools=[
        tool(
            "lookup_order",
            {"type": "object", "properties": {"orderId": {"type": "string"}}, "required": ["orderId"]},
            lookup_order,
        )
    ],
)
```

## Deploy + run

```bash
export LIBRAOS_BASE_URL=https://your-libraos.example.com
export LIBRAOS_API_KEY=…

adk deploy agent.py                          # upserts the agent on /v1/agents
adk run refund-copilot "refund order 8842"   # runs on the stack, streaming events
```

## Programmatic API

```python
from libraos_adk import LibraAdk
from agent import agent

adk = LibraAdk()                              # reads LIBRAOS_BASE_URL / LIBRAOS_API_KEY
adk.deploy(agent)
adk.run("refund-copilot", "refund order 8842", on_event=lambda e: print(e.get("type"), e))
```

## What runs where

You author + deploy the agent and (optionally) supply your own tools. **LibraOS
runs everything else** — the agent loop, server-side skills, RAG, memory — and
enforces governance a dev-hosted framework can't: signed tenant/app identity, a
capability membrane, a live kill-switch + firewall, a human-approval queue for
side-effecting tools, and append-only audit trails.

## Custom tools: two models

- **Webhook (works today):** `tool(name, schema, webhook_url="https://…")` — LibraOS HMAC-POSTs the tool call to your endpoint.
- **In-process (v2):** `tool(name, schema, handler)` — the agent pauses, your `handler` answers over the stream, the run resumes (needs libraos/libraos#842).

## Roadmap

- **v1 (now):** authoring + deploy + run over the jobs surface; webhook tools; full governance.
- **v2:** session-based runs + live streaming + in-process tools (Anthropic-Managed-Agents wire-compatible).
- **v3:** agent versioning/pinning, MCP client, scheduled deployments.
