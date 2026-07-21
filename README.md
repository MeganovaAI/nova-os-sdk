# LibraOS SDK

Partner integration SDK for **LibraOS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

This repo ships:

- **OpenAPI spec** (`openapi/nova-os-partner.v1.yaml`) — source of truth for the partner-facing API surface.
- **CLI** (`cli/`) — single static Go binary for sync, validate, test-callback, export/import.
- **Python SDK** (`python/`) — reference client library, published to PyPI as `libraos-sdk`.
- **Docs** (`docs/`) — getting started, Anthropic compatibility, multi-model, web-search, custom tools.
- **Examples** (`examples/`) — worked partner integrations (legaltech, healthcare, finance).

## Install

| Surface | Command |
|---|---|
| Python SDK | `pip install libraos-sdk` |
| CLI binary | `curl -L $(release_url)/nova-os-cli_linux_amd64.tar.gz \| tar -xz` |
| CLI Docker | `docker pull ghcr.io/meganovaai/nova-os-cli:latest` |

See `python/README.md` and `cli/README.md` for usage details.

## Self-hosting the LibraOS server

The SDK targets a running LibraOS server. To stand one up yourself:

| Resource | What it is |
|---|---|
| [`ghcr.io/libraos/libraos`](https://github.com/orgs/libraos/packages/container/package/libraos) | Public, multi-arch Docker image of the server. `docker pull ghcr.io/libraos/libraos:v0.1.14-week-2026-07-20`. |
| [[`libraos/stack`](https://github.com/libraos/stack)](https://github.com/libraos/stack) | Reference docker-compose manifests — core (LibraOS + Postgres + SurrealDB) plus 8 optional companion apps (LibreChat chat UI, SearXNG, crawl4ai, Firecrawl, Docling, FlashRank, Phoenix, Hermes). |
| [docs.libraos.com/install](https://docs.libraos.com/install) | Step-by-step install guide: prerequisites, env vars, smoke tests, reverse-proxy templates. |
| [docs.libraos.com/releases](https://docs.libraos.com/releases) | Release notes + migration notes for each server version. |

### Minimal local evaluation

Smallest practical local instance — LibraOS plus a disposable Postgres. **Not for production**:

```bash
docker network create nova-os-eval
docker run --rm -d --name nova-os-pg --network nova-os-eval \
  -e POSTGRES_USER=nova \
  -e POSTGRES_PASSWORD=nova \
  -e POSTGRES_DB=nova_os \
  postgres:16
docker run --rm --network nova-os-eval -p 8900:8900 \
  -e NOVA_OS_PUBLIC_URL=http://localhost:8900 \
  -e NOVA_OS_ADMIN_EMAIL=admin@example.com \
  -e NOVA_OS_ADMIN_PASSWORD=$(openssl rand -hex 16) \
  -e NOVA_OS_DATABASE_URL='postgres://nova:nova@nova-os-pg:5432/nova_os?sslmode=disable' \
  -e OPENAI_API_BASE=http://your-vllm-host:8000/v1 \
  -e OPENAI_API_KEY=local \
  ghcr.io/libraos/libraos:v0.1.14-week-2026-07-20
```

The server runs against **any OpenAI-compatible endpoint** — a local vLLM/Ollama
for a fully self-hosted, air-gapped deployment (shown above), or a hosted
provider. To use hosted Claude instead, drop the `OPENAI_*` vars and set
`ANTHROPIC_API_KEY` — it is optional, not required.

```
```

Then point the SDK at it:

```python
from libraos import AnthropicCompatClient

client = AnthropicCompatClient(base_url="http://localhost:8900", api_key="msk_eval_...")
msg = client.messages.create(
    model="Qwen/Qwen3.6-35B-A3B",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello, LibraOS!"}],
)
```

For anything beyond evaluation (real Postgres, SurrealDB knowledge store, companion apps, TLS, OIDC) use the [`libraos/stack`](https://github.com/libraos/stack) manifests linked above and follow [docs.libraos.com/install](https://docs.libraos.com/install).

If you only need to call a hosted LibraOS that someone else operates, skip this section — the SDK works against any reachable LibraOS endpoint.

## Three drop-in compat surfaces

Existing partner code targeting any of the three Anthropic-published Python entry points works against LibraOS with at most an env-var or constructor change:

- **Anthropic Messages SDK** (`anthropic.Anthropic(base_url=...)`) — set `base_url` to your LibraOS instance. The 1:1 Messages-API surface plus the Managed Agents beta endpoints (`/v1/agents`, `/v1/sessions`, `/v1/messages` behind the `anthropic-beta: managed-agents-2026-04-01` header) work unchanged. See [`python/examples/01_basic_chat.py`](python/examples/01_basic_chat.py).
- **Claude Agent SDK** (`claude_agent_sdk.query` / `ClaudeSDKClient`) — set `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` (or `ClaudeAgentOptions(env={...})`) to redirect the bundled CLI subprocess to LibraOS. Local agent loop ergonomics (Read/Bash/Edit + custom MCP tools) backed by LibraOS's multi-tenant runtime instead of `api.anthropic.com`. See [`python/examples/01b_claude_agent_sdk_drop_in.py`](python/examples/01b_claude_agent_sdk_drop_in.py).
- **LibraOS native** (`from libraos import Client`) — the extended surface partners reach for once they're past hello-world: multi-model `model_config` cascade at employee + agent level, structured-output `output_type` validation, custom-tool webhook callbacks (Mode A inline / Mode B webhook), portable employee bundles, async jobs. See [`python/examples/00_quickstart.py`](python/examples/00_quickstart.py).

The first two are about meeting partners where they are. The third is the surface they grow into when their integration deepens.

## Status

**v0.9.0-rc1** — Public API frozen. Downstream consumers can integrate against this tag without chasing a moving target. `v1.0.0` ships when the cross-repo CI gate stays green and at least one partner has signaled "intent to validate" against this RC.

## License

> ⚠️ **License Notice**
>
> The **LibraOS server** is provided for **evaluation and development use** under the Business Source License. Production deployments require a commercial license — contact contact@meganova.ai for pricing.
>
> The **SDK in this repository** (Python, CLI, OpenAPI) is **MIT-licensed** and free to use commercially.
