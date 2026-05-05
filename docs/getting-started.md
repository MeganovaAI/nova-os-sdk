# Getting Started

The front door for partners adopting Nova OS. Use the table below to jump to the doc that matches what you're trying to do — most adoption paths are 5-15 minutes.

## I want to…

| Goal | Path | Doc |
|---|---|---|
| **Run a Nova OS server locally** | Pull the public Docker image, set three env vars, smoke-test `/api/health` | [docs.meganova.ai/nova-os/install](https://docs.meganova.ai/nova-os/install) |
| **Point my existing Anthropic SDK at Nova OS** | Set `base_url` on `Anthropic(...)` — Messages API works unchanged | [`anthropic-compat.md`](anthropic-compat.md) |
| **Use the Claude Agent SDK against Nova OS** | Set `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` env to redirect the bundled CLI | [`python/examples/01b_claude_agent_sdk_drop_in.py`](../python/examples/01b_claude_agent_sdk_drop_in.py) |
| **Use the Nova OS native SDK** | `pip install nova-os-sdk`; `from nova_os import Client` | [`python/examples/00_quickstart.py`](../python/examples/00_quickstart.py) |
| **Manage employees / agents from the terminal** | Install `nova-os-cli`, set a profile, run `employees list` | [`cli/README.md`](../cli/README.md) |
| **Validate a folder of agent/employee definitions before deploy** | `nova-os-cli validate ./data/` — offline CI gate | [`cli/README.md` → validate](../cli/README.md#validate-offline-ci-gate) |
| **Sync a local folder of definitions to a server** | `nova-os-cli sync ./data/` (one-shot or `--watch`) | [`cli/README.md` → sync](../cli/README.md#sync-folder--server) |
| **Use multi-model fallbacks** | Per-call / per-skill / per-agent / per-employee / server-default cascade | [`multi-model.md`](multi-model.md) |
| **Add a custom tool with HTTP webhook fan-out** | Mode A (SSE inline) or Mode B (webhook) | [`custom-tools.md`](custom-tools.md) |
| **Bring my own search backend** | Ceramic, Tavily, Brave, Exa, SearXNG, MegaNova with fallback chains | [`web-search.md`](web-search.md) |
| **Deploy to production** | Reverse proxy, TLS, Postgres, scaling notes | [`deployment.md`](deployment.md) |
| **Pin a specific server version** | Track release tags + image digests | [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases) |

## 5-minute first call

The fastest path from zero to "I have a working Nova OS instance answering chat requests." Assumes Docker is installed.

### 1. Stand up the server

```bash
docker run -d --name nova-os -p 8900:8900 \
  -e NOVA_OS_DATABASE_URL="postgres://nova:secret@host.docker.internal:5432/nova_os" \
  -e NOVA_OS_JWT_SECRET="$(openssl rand -hex 32)" \
  -e NOVA_OS_ADMIN_EMAIL="admin@example.com" \
  -e NOVA_OS_ADMIN_PASSWORD="changeme-please-12chars" \
  -e OPENAI_API_KEY="msk_..." \
  ghcr.io/meganovaai/nova-os:v0.1.5
```

Defaults that "just work" against the MegaNova gateway: `OPENAI_API_BASE=https://api.meganova.ai`, `OPENAI_MODEL=gemini/gemini-2.5-flash`. Override either to use OpenAI direct or pick a different model.

`v0.1.5` and `:latest` track each other. For partner-validation builds, use `:v0.1.5-week-YYYY-MM-DD` weekly tags. See [releases](https://docs.meganova.ai/nova-os/releases) for the cadence.

### 2. Verify health

```bash
curl http://localhost:8900/api/health
# {"status":"ok","version":"v0.1.5","build_sha":"00ee9580..."}
```

### 3. First chat — pick your SDK surface

**Anthropic SDK (drop-in):**

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://localhost:8900", api_key="msk_...")
msg = client.messages.create(
    model="anthropic/claude-opus-4-7",
    max_tokens=256,
    messages=[{"role": "user", "content": "What is contract clause 7.3 about?"}],
)
print(msg.content[0].text)
```

**Nova OS native SDK:**

```python
from nova_os import Client

c = Client(base_url="http://localhost:8900", api_key="msk_...")
msg = await c.messages.create(
    agent_id="legal-assistant",
    end_user="demo-user",
    prompt="What is contract clause 7.3 about?",
)
print(msg.text)
```

**CLI:**

```bash
nova-os-cli config set local --url http://localhost:8900 --api-key-env NOVA_OS_API_KEY
nova-os-cli config default local
export NOVA_OS_API_KEY=msk_...

nova-os-cli messages send legal-assistant "What is contract clause 7.3 about?"
```

## Three drop-in compat surfaces

Existing partner code targeting any of these works against Nova OS with at most an env-var or constructor change:

| Surface | What it gives you | Redirect |
|---|---|---|
| **Anthropic Messages SDK** (`anthropic.Anthropic`) | The 1:1 Messages API + Managed Agents beta endpoints | `Anthropic(base_url="...")` |
| **Claude Agent SDK** (`claude_agent_sdk.query`) | Local agent loop ergonomics (Read/Bash/Edit + custom MCP tools) backed by Nova OS's multi-tenant runtime | `ANTHROPIC_BASE_URL` env |
| **Nova OS native** (`from nova_os import Client`) | The extended surface partners reach for once past hello-world: multi-model `model_config`, `output_type` validation, custom-tool webhook callbacks, portable employee bundles, async jobs | `Client(base_url="...")` |

The first two meet partners where they are. The third is the surface they grow into when their integration deepens.

## Scenario matrix

End-to-end paths for the most common partner tasks. Each row points at a worked example.

| Scenario | What it shows | Worked example |
|---|---|---|
| Hello-world chat | Bare `Anthropic(base_url=...)` round-trip | [`python/examples/01_basic_chat.py`](../python/examples/01_basic_chat.py) |
| Claude Agent SDK redirect | Subprocess CLI redirected to Nova OS | [`python/examples/01b_claude_agent_sdk_drop_in.py`](../python/examples/01b_claude_agent_sdk_drop_in.py) |
| Streaming chat | SSE event parsing + Mode A inline tool result | [`python/examples/02_streaming.py`](../python/examples/02_streaming.py) |
| Multi-model with fallback | Per-call model override + cascade resolution | [`python/examples/03_multi_model.py`](../python/examples/03_multi_model.py) |
| Structured output (`output_type`) | JSON Schema 2020-12 validation on assistant messages | [`python/examples/04_output_type.py`](../python/examples/04_output_type.py) |
| Mode A custom tool | SSE inline `tool_use` → `submit_tool_result` | [`python/examples/05_custom_tool_mode_a.py`](../python/examples/05_custom_tool_mode_a.py) |
| Mode B webhook custom tool | HMAC-signed webhook + idempotency dedup | [`python/examples/06_custom_tool_mode_b.py`](../python/examples/06_custom_tool_mode_b.py) |
| Async long-running job | Job submit + polling | [`python/examples/07_async_job.py`](../python/examples/07_async_job.py) |
| Persona discovery (boot-time) | `c.personas.list()` with `If-None-Match` ETag | [`python/examples/17_personas_discovery.py`](../python/examples/17_personas_discovery.py) |
| Folder-to-server sync | `nova-os-cli sync ./data/` | [`cli/README.md` → sync](../cli/README.md#sync-folder--server) |
| Webhook smoke test | Forge a Nova-OS-shaped signed POST to your handler | [`cli/README.md` → test-callback](../cli/README.md#test-callback-mode-b-webhook-smoke) |

## Auth resolution

For every CLI command and SDK call, credentials resolve in this order:

1. Explicit constructor args (`Client(base_url=..., api_key=...)`) or CLI flags (`--url`, `--api-key`)
2. Environment variables (`NOVA_OS_URL`, `NOVA_OS_API_KEY`)
3. Profile in `~/.nova-os/config.yaml` selected by `--profile` / `NOVA_OS_PROFILE`, falling back to `default:`

A partner running multiple environments (dev / staging / prod) keeps one profile per environment in `config.yaml` and switches via `--profile prod`.

## Next steps

- **Working in production?** [`deployment.md`](deployment.md) covers reverse-proxy templates, TLS, Postgres sizing, multi-replica deploys, and the SSE flag that's load-bearing for Cloudflare-fronted streaming.
- **Building a vertical product?** [`examples/legaltech/`](../examples/legaltech) is the canonical reference integration — EqualDocs's `legal-assistant` shape, validated end-to-end at 7/7 against the latest server build.
- **Running into an issue?** Open one at [`MeganovaAI/nova-os-sdk/issues`](https://github.com/MeganovaAI/nova-os-sdk/issues). Server-side issues live at [`MeganovaAI/nova-os/issues`](https://github.com/MeganovaAI/nova-os/issues).
