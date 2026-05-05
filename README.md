# Nova OS SDK

Partner integration SDK for **Nova OS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

This repo ships:

- **OpenAPI spec** (`openapi/nova-os-partner.v1.yaml`) — source of truth for the partner-facing API surface.
- **CLI** (`cli/`) — single static Go binary for sync, validate, test-callback, export/import.
- **Python SDK** (`python/`) — reference client library, published to PyPI as `nova-os-sdk`.
- **Docs** (`docs/`) — getting started, Anthropic compatibility, multi-model, web-search, custom tools.
- **Examples** (`examples/`) — worked partner integrations (legaltech, healthcare, finance).

## Install

| Surface | Command |
|---|---|
| Python SDK | `pip install nova-os-sdk` |
| CLI binary | `curl -L $(release_url)/nova-os-cli_linux_amd64.tar.gz \| tar -xz` |
| CLI Docker | `docker pull ghcr.io/meganovaai/nova-os-cli:latest` |

See `python/README.md` and `cli/README.md` for usage details.

## Self-hosting the Nova OS server

The SDK targets a running Nova OS server. To stand one up yourself:

| Resource | What it is |
|---|---|
| [`ghcr.io/meganovaai/nova-os`](https://github.com/orgs/MeganovaAI/packages/container/package/nova-os) | Public, multi-arch Docker image of the server. `docker pull ghcr.io/meganovaai/nova-os:v0.1.5`. |
| [`MeganovaAI/nova-os-stack`](https://github.com/MeganovaAI/nova-os-stack) | Reference docker-compose manifests — core (Nova OS + Postgres + SurrealDB) plus 8 optional companion apps (LibreChat chat UI, SearXNG, crawl4ai, Firecrawl, Docling, FlashRank, Phoenix, Hermes). |
| [docs.meganova.ai/nova-os/install](https://docs.meganova.ai/nova-os/install) | Step-by-step install guide: prerequisites, env vars, smoke tests, reverse-proxy templates. |
| [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases) | Release notes + migration notes for each server version. |

### One-liner evaluation

Smallest possible local instance — single container, ephemeral state, fine for a kick-the-tires evaluation. **Not for production**:

```bash
docker run --rm -p 8900:8900 \
  -e NOVA_OS_PUBLIC_URL=http://localhost:8900 \
  -e NOVA_OS_ADMIN_EMAIL=admin@example.com \
  -e NOVA_OS_ADMIN_PASSWORD=$(openssl rand -hex 16) \
  -e NOVA_OS_DATABASE_URL=sqlite:///tmp/nova.db \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  ghcr.io/meganovaai/nova-os:v0.1.5
```

Then point the SDK at it:

```python
from nova_os import AnthropicCompatClient

client = AnthropicCompatClient(base_url="http://localhost:8900", api_key="msk_eval_...")
msg = client.messages.create(
    model="anthropic/claude-opus-4-7",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello, Nova OS!"}],
)
```

For anything beyond evaluation (real Postgres, SurrealDB knowledge store, companion apps, TLS, OIDC) use the `MeganovaAI/nova-os-stack` manifests linked above and follow [docs.meganova.ai/nova-os/install](https://docs.meganova.ai/nova-os/install).

If you only need to call a hosted Nova OS that someone else operates, skip this section — the SDK works against any reachable Nova OS endpoint.

## Three drop-in compat surfaces

Existing partner code targeting any of the three Anthropic-published Python entry points works against Nova OS with at most an env-var or constructor change:

- **Anthropic Messages SDK** (`anthropic.Anthropic(base_url=...)`) — set `base_url` to your Nova OS instance. The 1:1 Messages-API surface plus the Managed Agents beta endpoints (`/v1/agents`, `/v1/sessions`, `/v1/messages` behind the `anthropic-beta: managed-agents-2026-04-01` header) work unchanged. See [`python/examples/01_basic_chat.py`](python/examples/01_basic_chat.py).
- **Claude Agent SDK** (`claude_agent_sdk.query` / `ClaudeSDKClient`) — set `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` (or `ClaudeAgentOptions(env={...})`) to redirect the bundled CLI subprocess to Nova OS. Local agent loop ergonomics (Read/Bash/Edit + custom MCP tools) backed by Nova OS's multi-tenant runtime instead of `api.anthropic.com`. See [`python/examples/01b_claude_agent_sdk_drop_in.py`](python/examples/01b_claude_agent_sdk_drop_in.py).
- **Nova OS native** (`from nova_os import Client`) — the extended surface partners reach for once they're past hello-world: multi-model `model_config` cascade at employee + agent level, structured-output `output_type` validation, custom-tool webhook callbacks (Mode A inline / Mode B webhook), portable employee bundles, async jobs. See [`python/examples/00_quickstart.py`](python/examples/00_quickstart.py).

The first two are about meeting partners where they are. The third is the surface they grow into when their integration deepens.

## Status

**v0.9.0-rc1** — Public API frozen. Downstream consumers can integrate against this tag without chasing a moving target. `v1.0.0` ships when the cross-repo CI gate stays green and at least one partner has signaled "intent to validate" against this RC.

## License

MIT.
