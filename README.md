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
| [`ghcr.io/meganovaai/nova-os`](https://github.com/orgs/MeganovaAI/packages/container/package/nova-os) | Public, multi-arch Docker image of the server. `docker pull ghcr.io/meganovaai/nova-os:v0.1.4`. |
| [`MeganovaAI/nova-os-stack`](https://github.com/MeganovaAI/nova-os-stack) | Reference docker-compose manifests — core (Nova OS + Postgres + SurrealDB) plus 8 optional companion apps (LibreChat chat UI, SearXNG, crawl4ai, Firecrawl, Docling, FlashRank, Phoenix, Hermes). |
| [docs.meganova.ai/nova-os/install](https://docs.meganova.ai/nova-os/install) | Step-by-step install guide: prerequisites, env vars, smoke tests, reverse-proxy templates. |
| [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases) | Release notes + migration notes for each server version. |

If you only need to call a hosted Nova OS that someone else operates, skip this section — the SDK works against any reachable Nova OS endpoint.

## Two-tier client model

- **Anthropic-compat:** code targeting `anthropic.Anthropic(base_url=...)` works unchanged for the 1:1 surface.
- **Nova OS extended:** multi-model at agent + employee level, custom-tool webhook callbacks, portable employee bundles, async jobs.

## Status

**v0.9.0-rc1** — Public API frozen. Downstream consumers can integrate against this tag without chasing a moving target. `v1.0.0` ships when the cross-repo CI gate stays green and at least one partner has signaled "intent to validate" against this RC.

## License

MIT.
