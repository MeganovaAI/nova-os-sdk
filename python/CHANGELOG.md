# Changelog

All notable changes to `nova-os-sdk` (Python) will be documented in this file.

## [Unreleased] — towards 1.1.0

Python SDK changes since `1.0.0`. Targets a `1.1.0` minor cut once the partner-prefix wave settles. The OpenAPI spec advanced through `1.0.0-alpha.3` → `1.0.0-alpha.4` → `1.0.0-alpha.5` to declare new server endpoints the SDK now wraps. For Nova OS **server-side** release notes that pair with this SDK release, see [docs.meganova.ai/nova-os/releases](https://docs.meganova.ai/nova-os/releases).

### Added

- **`c.documents`** — partner-prefix CRUD wrapper for `/v1/managed/documents`. OpenAPI alpha.3.
- **`c.knowledge`** — partner-prefix wrapper for `/v1/managed/knowledge`. OpenAPI alpha.3.
- **`c.hooks`** — partner-prefix CRUD for lifecycle-hook subscriptions under `/v1/managed/hooks`. OpenAPI alpha.3. First slice is in-memory on the server; persistence + bus bridge tracked for a follow-up.
- **`c.filesystem`** — partner-prefix wrapper for `/v1/managed/filesystem`. OpenAPI alpha.3. `POST /provision` endpoint deferred to a follow-up.
- **`c.users`** + **`c.settings`** — partner-prefix wrappers for `/v1/managed/users` and `/v1/managed/settings`. OpenAPI alpha.3.
- **`c.sessions`** — partner-prefix wrapper for `/v1/managed/sessions`. OpenAPI alpha.4. Currently `create` + `get`; `list` / `delete` / `fork` tracked for a follow-up.
- **`c.personas`** — boot-time persona-contract surface (`GET /agents/v1/personas` + `:id`) with `If-None-Match` ETag round-trip and `PersonaNotFound` typed error. OpenAPI alpha.5. Closes [`nova-os-sdk#14`](https://github.com/MeganovaAI/nova-os-sdk/issues/14).
- **`PersonaNotFound`** typed error — subclass of `NotFoundError`, raised by `c.personas.get(persona_id)` on a 404 with the persona-envelope shape `{"error": "persona not found", "id": ...}`. `parse_error_response` detects the envelope.
- Examples 16 (sessions), 17 (personas discovery), and 18 (custom persona + `output_type.persist_fields` slot collection across sync + streaming) under `python/examples/`.

### Fixed

- **Codegen-python CI gate unblocked** ([`nova-os-sdk#15`](https://github.com/MeganovaAI/nova-os-sdk/issues/15)). `openapi-python-client` 0.28.3 had been crashing on every push since `AgentCreate` landed as `allOf: [Agent]`, leaving `_generated/` permanently stale. Flattened `AgentCreate` to a duplicated property block (wire shape unchanged) and loosened `Agent.route_templates` from `additionalProperties: {type: string}` to `additionalProperties: true`. Codegen now produces full output for all 8 alpha.3-alpha.5 resources (`documents`, `filesystem`, `hooks`, `knowledge`, `personas`, `sessions`, `settings`, `users`) — previously these endpoints were declared in OpenAPI but never auto-generated, so `_generated/` only carried the v0.9.0 surface. Hand-written `nova_os/resources/*.py` public API unaffected; partner code keeps working.

## [1.0.0] — 2026-05-02

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
