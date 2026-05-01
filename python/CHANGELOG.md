# Changelog

All notable changes to `nova-os-sdk` (Python) will be documented in this file.

## [1.0.0] — TBD (drafted)

**Public API stable.** First stable release of the v1.x line. **No breaking changes from `v0.9.0rc1`** — upgrade is `pip install --upgrade nova-os-sdk`.

See [`docs/release-notes/v1.0.0.md`](../docs/release-notes/v1.0.0.md) for the comprehensive release notes.

### Added since v0.9.0rc1

- `release.yml` extended with `build-cli` job — multi-arch CLI binaries (linux/darwin/windows × amd64/arm64), cosign keyless signing, Docker image at `ghcr.io/meganovaai/nova-os-cli`. Multi-arch manifest covers `linux/amd64` + `linux/arm64`.
- CLI surface complete: `employees`, `agents`, `jobs`, `messages` (via SDK), `sync` (one-shot + `--watch`), `validate` (with Vertex schema-bug guardrail), `test-callback` (Mode B webhook smoke), `config` (profile management), `version` (with embedded build metadata).

### Unchanged from v0.9.0rc1

Every Python public surface, including the wire formats for HMAC signing, SSE event names, and OpenAPI request/response shapes. `v1.0.0` is functionally identical at the Python API layer — the additions are CLI + release pipeline.

### Still deferred to v1.1+

- `c.knowledge` resource (depends on a future server-side endpoint)
- `c.settings` resource (admin-only)
- `nova-os-cli logs` subcommand
- `nova-os-cli sync --prune` (destructive sync)
- TypeScript / Rust / Go-direct client SDKs — codegen from `openapi/nova-os-partner.v1.yaml` if needed

## [0.9.0rc1] — 2026-05-01

**API freeze candidate.** Public surface is locked for `v1.0.0`. Downstream
consumers can integrate against this tag.

### Added

- `nova_os.Client(base_url, api_key)` — async-first with `.sync` proxy mirror
- 4 resources: `agents`, `employees`, `messages`, `jobs` — CRUD + auto-paginating `list()`
- `c.messages.stream(...)` — async context manager + Mode A `submit_tool_result`
- `nova_os.callbacks.WebhookRouter` — Mode B HMAC verification + idempotency dedup
- FastAPI / Flask / AWS Lambda integration mounts (lazy-imported)
- `nova_os.AnthropicCompatClient(...)` — drop-in factory pre-configured for Nova OS's `/v1/managed` path
- Recorded fixture test proving Anthropic SDK round-trips against Nova OS-shaped responses
- Typed error hierarchy: `VertexSchemaError`, `BillingError`, `RateLimitedError`, `NotFoundError`, etc.
- `Idempotency-Key` kwarg on POST resource methods
- 7 worked examples in `python/examples/`
- `.github/workflows/release.yml` — builds sdist + wheel on tag push, publishes GitHub Release, conditionally uploads to PyPI

### Pending for v1.0.0

- `knowledge` resource (depends on a future Nova OS server-side endpoint)
- Bundle import via partner-side helpers (export side already works via raw HTTP)
- Per-skill model override (`agent.skills[].model`)
- Full PyPI publish (workflow ready; `PYPI_API_TOKEN` secret must be configured to fire)
