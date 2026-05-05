# Changelog

All notable changes to `nova-os-sdk` (Python) will be documented in this file.

## [Unreleased] — towards 1.1.0

Tracks Python surface added since `1.0.0`. Targets a `1.1.0` minor cut once the partner-prefix wave settles. The OpenAPI spec advanced through `1.0.0-alpha.3` → `1.0.0-alpha.4` → `1.0.0-alpha.5` to declare the new server endpoints; the matching server build is `ghcr.io/meganovaai/nova-os:v0.1.5-week-2026-05-09` (round-5 in-week force-update on 2026-05-05).

### Added

- **`c.documents`** — partner-prefix CRUD wrapper for `/v1/managed/documents` (lockstep with `MeganovaAI/nova-os#175` / PR #189). OpenAPI alpha.3.
- **`c.knowledge`** — partner-prefix wrapper for `/v1/managed/knowledge` (lockstep with `#176` / PR #190). OpenAPI alpha.3.
- **`c.hooks`** — partner-prefix CRUD for lifecycle-hook subscriptions under `/v1/managed/hooks` (lockstep with `#177` / PR #193). OpenAPI alpha.3. First slice is in-memory on the server; persistence + bus bridge tracked for a follow-up.
- **`c.filesystem`** — partner-prefix wrapper for `/v1/managed/filesystem` (lockstep with `#178` / PR #192). OpenAPI alpha.3. `POST /provision` endpoint deferred to a follow-up.
- **`c.users`** + **`c.settings`** — partner-prefix wrappers for `/v1/managed/users` and `/v1/managed/settings` (lockstep with `#179` / PR #191). OpenAPI alpha.3.
- **`c.sessions`** — partner-prefix wrapper for `/v1/managed/sessions` (lockstep with `#185` / PR #194). OpenAPI alpha.4. Currently `create` + `get`; `list` / `delete` / `fork` tracked for a follow-up.
- **`c.personas`** — boot-time persona-contract surface (`GET /agents/v1/personas` + `:id`) with `If-None-Match` ETag round-trip and `PersonaNotFound` typed error (lockstep with `#187`). OpenAPI alpha.5. Closes `nova-os-sdk#14`.
- **`PersonaNotFound`** typed error — subclass of `NotFoundError`, raised by `c.personas.get(persona_id)` on a 404 with the persona-envelope shape `{"error": "persona not found", "id": ...}`. `parse_error_response` detects the envelope.
- Examples 16 (sessions) + 17 (personas discovery) under `python/examples/`.

### Server-side notes for partners

- `OPENAI_MODEL` now defaults to `gemini/gemini-2.5-flash` server-side (`nova-os#197` / PR #198). Partners running `docker run ghcr.io/meganovaai/nova-os` against the MegaNova gateway with no env var no longer hit the bare-`gpt-4o` 404 on first chat. Override via `-e OPENAI_MODEL=<vendor>/<model>` still wins. Default is gateway-safe per `validateModelShape` (`<provider>/<model>`).

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
