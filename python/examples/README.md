# Nova OS SDK — worked examples

Each example is a runnable script. Set `NOVA_OS_URL` and `NOVA_OS_API_KEY`
env vars first.

```bash
pip install nova-os-sdk
export NOVA_OS_URL=https://nova.partner.com
export NOVA_OS_API_KEY=msk_live_...

python examples/00_quickstart.py
```

## Coming from Anthropic Managed Agents?

Nova OS's agent surface maps onto [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) but collapses the 5 concepts into 2 — there's no separate environment or session object.

| Anthropic Managed Agents | Nova OS SDK |
|---|---|
| `agents.create(model, system_prompt, tools, ...)` | `employees.create(id, model_config)` + `agents.create(id, type, owner_employee, instructions, ...)` — split so one employee can own many agents with shared model routing |
| `environments.create(...)` | Implicit — the Nova OS server is the runtime. Per-tenant filesystem ships as an opt-in agent flag (`filesystem.enabled: true`); six FS tools auto-register. |
| `sessions.create(agent_id)` | Implicit — observational memory is keyed on the `(API key, end_user, agent)` triple. Pass `X-End-User` for per-end-user isolation. |
| `sessions.events.send(...)` (SSE stream) | `messages.create(agent_id, messages=[...])` — sync or streaming via the SDK's `stream()` context manager |
| Steer/interrupt mid-run | Send another `messages.create()` to the same agent — observational memory threads it onto the same conversation |

Total to go from zero to a working digital agent: **3 SDK calls** (`00_quickstart.py`).

## Coming from the Claude Agent SDK?

The [Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python) is a different Anthropic-published library — it spawns the bundled `claude` CLI as a subprocess and drives a **local agent loop** (Read / Write / Bash / Edit + custom MCP tools) against `api.anthropic.com`. Different shape from Managed Agents, different shape from the Anthropic Messages SDK.

**It works against Nova OS unchanged.** The CLI inherits parent-process env when spawned, so `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` (set globally or via `ClaudeAgentOptions(env={...})`) reroute every call to your Nova OS instance:

```python
options = ClaudeAgentOptions(
    env={
        "ANTHROPIC_BASE_URL": "https://nova.your-company.example",
        "ANTHROPIC_API_KEY": "msk_live_...",
    },
    system_prompt="You are a helpful assistant.",
    max_turns=1,
)
async for message in query(prompt="...", options=options):
    ...
```

| Claude Agent SDK | Nova OS SDK |
|---|---|
| `query(prompt, options)` — AsyncIterator, one-shot | `c.messages.create(agent_id, messages)` — sync or streaming via `MessageStream` |
| `ClaudeSDKClient` — bidirectional / interruptible | `c.messages.create()` repeated against the same `agent_id`; observational memory threads conversation state automatically |
| `agents={"name": AgentDefinition(...)}` — declared per-options | `c.agents.create(id, type, owner_employee, instructions, ...)` — registered server-side, persisted across processes |
| Tools: built-in CLI set (Read/Bash/Edit/Write) + in-process MCP custom tools | Tools: server-side Nova OS skills + custom-tool callbacks (Mode A inline / Mode B webhook) |
| Permissions: `permission_mode` + `can_use_tool` per-tool callback | Permissions: JWT/API-key + agent-level firewall + opt-in custom-tool patterns |
| State: local session files (resume / fork / store) | State: server-side observational memory keyed on `(API key, end_user, agent)` |

**When to use which:**

- **Claude Agent SDK** when you want the local-CLI ergonomics — Read/Bash/Edit acting on the developer's own filesystem, in-process MCP servers, plan/acceptEdits permission modes. Scope is single-user, single-machine.
- **Nova OS SDK** when you want server-managed agents — multi-tenant, persisted, OIDC/SSO, RBAC, observational memory across sessions. Scope is the partner's user base.
- **Both together** is the killer pattern — write Claude Agent SDK code, redirect with two env vars, get the local-CLI dev ergonomics with the multi-tenant Nova OS backend. See `01b_claude_agent_sdk_drop_in.py`.

## Example index

| File | Surface |
|---|---|
| `00_quickstart.py` | **Start here.** Fastest path from zero to a digital agent — 3 SDK calls, side-by-side mapping to Anthropic Managed Agents Quickstart |
| `01_basic_chat.py` | Anthropic-compat hello world (Anthropic SDK drop-in, no agent setup) |
| `01b_claude_agent_sdk_drop_in.py` | Claude Agent SDK drop-in via env-var redirect — existing `query()` / `ClaudeSDKClient` code runs against Nova OS unchanged |
| `02_create_employee_and_agent.py` | Full lifecycle: employee → owned agent → first chat → cleanup |
| `04_custom_tool_inline.py` | Mode A (SSE inline) — partner intercepts `custom_tool_use` mid-stream |
| `05_custom_tool_webhook.py` | Mode B (webhook) — partner exposes a FastAPI endpoint |
| `06_multi_model_fallback.py` | Per-employee `model_config` cascade, observe fallback fields |
| `07_bundle_export_import.py` | Tenant onboarding via `.nova-bundle.zip` round-trip |
| `08_async_job_long_running.py` | Submit async job, poll status, receive final result |

**Skipped:** `03_upload_knowledge.py` — the `knowledge` resource is not yet
available server-side. This example will be added in a future release.

For full end-to-end vertical integrations (legaltech contract review,
healthcare clinical-note triage, finance 10-K diff) see [`../../examples/`](../../examples/).
