# Nova OS SDK

Partner integration SDK for **Nova OS** — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

This repo ships:

- **OpenAPI spec** (`openapi/nova-os-partner.v1.yaml`) — source of truth for the partner-facing API surface.
- **CLI** (`cli/`) — single static Go binary for sync, validate, test-callback, export/import.
- **Python SDK** (`python/`) — reference client library, published to PyPI as `nova-os-sdk`.
- **Docs** (`docs/`) — getting started, Anthropic compatibility, multi-model, web-search, custom tools.
- **Examples** (`examples/`) — worked partner integrations (legaltech, healthcare, finance).

## Two-tier client model

- **Anthropic-compat:** code targeting `anthropic.Anthropic(base_url=...)` works unchanged for the 1:1 surface.
- **Nova OS extended:** multi-model at agent + employee level, custom-tool webhook callbacks, portable employee bundles, async jobs.

## Status

Pre-1.0 — the API surface is being stabilized. Watch this repo's releases for the `v0.9.0-rc` API freeze tag, after which the public Python and CLI surfaces are locked for `v1.0.0`.

## License

MIT.
