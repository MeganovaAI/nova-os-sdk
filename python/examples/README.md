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

## Example index

| File | Surface |
|---|---|
| `00_quickstart.py` | **Start here.** Fastest path from zero to a digital agent — 3 SDK calls, side-by-side mapping to Anthropic Managed Agents Quickstart |
| `01_basic_chat.py` | Anthropic-compat hello world (Anthropic SDK drop-in, no agent setup) |
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
