# Nova OS SDK — worked examples

Each example is a runnable script. Set `NOVA_OS_URL` and `NOVA_OS_API_KEY`
env vars first.

```bash
pip install nova-os-sdk
export NOVA_OS_URL=https://nova.partner.com
export NOVA_OS_API_KEY=msk_live_...

python examples/01_basic_chat.py
```

| File | Surface |
|---|---|
| `01_basic_chat.py` | Anthropic-compat hello world |
| `02_create_employee_and_agent.py` | Full lifecycle: employee → owned agent → first chat |
| `04_custom_tool_inline.py` | Mode A (SSE inline) — partner intercepts `custom_tool_use` mid-stream |
| `05_custom_tool_webhook.py` | Mode B (webhook) — partner exposes a FastAPI endpoint |
| `06_multi_model_fallback.py` | Per-employee `model_config` cascade, observe fallback fields |
| `07_bundle_export_import.py` | Tenant onboarding via `.nova-bundle.zip` round-trip |
| `08_async_job_long_running.py` | Submit async job, poll status, receive final result |

**Skipped:** `03_upload_knowledge.py` — the `knowledge` resource is not yet
available server-side. This example will be added in a future release.
