# Nova OS SDK

Partner integration SDK for [Nova OS](https://github.com/MeganovaAI/nova-os).

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

Pre-1.0. See [MeganovaAI/nova-os#123](https://github.com/MeganovaAI/nova-os/issues/123) for the implementation epic.

## License

MIT.
