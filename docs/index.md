---
title: Nova OS SDK Documentation
---

# Nova OS SDK Documentation

Partner integration docs for [Nova OS](https://github.com/MeganovaAI/nova-os-sdk) — the agentic operating system that lets you build vertical AI products on a multi-model, multi-tenant runtime.

> ⚠️ **License Notice**
>
> The **Nova OS server** is provided for **evaluation and development use** under the Business Source License. Production deployments require a commercial license — contact contact@meganova.ai for pricing.
>
> The **SDK** (Python, CLI, OpenAPI) is **MIT-licensed** and free to use commercially.

## Start here

| Doc | What it covers |
|---|---|
| [Getting Started](getting-started.md) | Front-door table, 5-minute first call, three drop-in compat surfaces, scenario matrix |
| [Anthropic API Compatibility](anthropic-compat.md) | Endpoint-by-endpoint matrix, what's identical, what's extended, what's not implemented |
| [Multi-Model Routing](multi-model.md) | Three slots (answer / planner / skill), five-level cascade, fallback semantics |
| [Web Search Backends](web-search.md) | Five pluggable backends, cost-quality table, fallback chains, reformulator, recency intent |
| [Comparing Search Backends](comparing-search-backends.md) | Side-by-side pricing / latency / features for each backend vs the Anthropic Claude tool |
| [Custom Tools](custom-tools.md) | Mode A (SSE inline) + Mode B (webhook) end-to-end, HMAC signing, idempotency |
| [Deployment](deployment.md) | Self-hosted vs cloud, three deploy shapes, reverse-proxy templates, observability |
| [Scenarios](scenarios.md) | 10 lifecycle workflows traced end-to-end with wire-level detail |

## SDK reference

| Surface | Doc |
|---|---|
| Python SDK | [`python/README.md`](https://github.com/MeganovaAI/nova-os-sdk/blob/main/python/README.md) |
| CLI | [`cli/README.md`](https://github.com/MeganovaAI/nova-os-sdk/blob/main/cli/README.md) |
| OpenAPI spec | [`openapi/nova-os-partner.v1.yaml`](https://github.com/MeganovaAI/nova-os-sdk/blob/main/openapi/nova-os-partner.v1.yaml) |
| Worked examples | [`python/examples/`](https://github.com/MeganovaAI/nova-os-sdk/tree/main/python/examples) — 18 numbered examples covering every public surface |

## Server-side

For partners who need to operate Nova OS themselves:

| Doc | Where |
|---|---|
| Install Nova OS | [docs.meganova.ai/nova-os/install](https://docs.meganova.ai/nova-os/install) |
| Releases / cadence | [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases) |
| Anthropic SDK quickstart | [docs.meganova.ai/nova-os/anthropic-sdk-quickstart](https://docs.meganova.ai/nova-os/anthropic-sdk-quickstart) |
| Pre-built deploy stack | [`MeganovaAI/nova-os-stack`](https://github.com/MeganovaAI/nova-os-stack) — compose manifests + 8 companion apps |

## Status

**Python SDK 1.0.0** — Public API stable. PyPI: `pip install nova-os-sdk`.

**CLI 1.0.0** — Multi-arch binaries (`linux/darwin/windows × amd64/arm64`), cosign-signed, Docker image at `ghcr.io/meganovaai/nova-os-cli`.

**OpenAPI alpha.5** — Partner-facing API surface continuing to grow toward the v1 freeze. The Python SDK \`__version__\` is stable at 1.0.0; \`OPENAPI_VERSION\` tracks the spec separately.

**Server image** — `ghcr.io/meganovaai/nova-os:v0.1.5` (and `:latest`).

See [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases) for the cadence.

## Contributing

Issues and PRs welcome on the SDK side at [`MeganovaAI/nova-os-sdk`](https://github.com/MeganovaAI/nova-os-sdk). The Nova OS server itself is in a separate repository under a different license — see the notice above.

## Contact

- General SDK questions: open an issue on [`MeganovaAI/nova-os-sdk/issues`](https://github.com/MeganovaAI/nova-os-sdk/issues)
- Server-side issues: [`MeganovaAI/nova-os/issues`](https://github.com/MeganovaAI/nova-os/issues) (private repo — file at the SDK level if you don't have access)
- Commercial licensing: contact@meganova.ai
