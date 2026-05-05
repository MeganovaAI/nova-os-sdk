# Nova OS SDK improvement pass — design

**Status:** approved 2026-05-05; issues filed; examples shipped; spec captured for reference.
**Tracking:** [`MeganovaAI/nova-os#123`](https://github.com/MeganovaAI/nova-os/issues/123) (epic).

## Goal

Compare the Nova OS Python SDK against Anthropic's three Python entry points (`anthropic.Anthropic`, Claude Agent SDK, Managed Agents API) and Nova OS's own server-side surface, identify gaps, file the gaps that are server-side as issues, and ship the gaps that are SDK-side as examples.

## Non-goals

- Implementing any of the server-side gaps. Those are filed as issues; they ship in their own cycles.
- Adding new SDK *resources* (e.g. `c.documents`, `c.knowledge`). The SDK matches the partner OpenAPI exhaustively today; the gap is in the partner OpenAPI itself, not in the client. Adding client surface ahead of contract would create drift.
- Refactoring the existing resource modules. They follow a clean pattern (`Resource` base + per-resource module).

## Findings (the comparison)

### 1. Python SDK matches partner OpenAPI exhaustively

| OpenAPI tag group | Python resource | CLI subcommand |
|---|---|---|
| `agents` (4 paths) | `c.agents` | `nova-os-cli agents …` |
| `employees` (4 paths) | `c.employees` | `nova-os-cli employees …` |
| `messages` (3 paths inc. custom-tool-results) | `c.messages` (`.create`, `.stream`, `.submit_tool_result`) | (none — see issue) |
| `jobs` (3 paths inc. stream) | `c.jobs` | `nova-os-cli jobs …` |

**No SDK-side gap.** The pre-investigation hypothesis ("missing client resources") was wrong.

### 2. Server has features not in the partner OpenAPI

These ship server-side but the partner contract doesn't declare them. SDK can't expose them cleanly without contract drift.

| Feature | Server release | Issue |
|---|---|---|
| `documents` resource (upload/list/get/delete) | v0.1.4 (Super Nova auto-indexing) | [#175](https://github.com/MeganovaAI/nova-os/issues/175) |
| `knowledge` resource (search/ingest/collections) | v0.1.2 / v0.1.4 | [#176](https://github.com/MeganovaAI/nova-os/issues/176) |
| `hooks` resource (9 lifecycle events) | v0.1.4 | [#177](https://github.com/MeganovaAI/nova-os/issues/177) |
| `filesystem` ops (per-tenant FS) | v0.1.4 | [#178](https://github.com/MeganovaAI/nova-os/issues/178) |
| `users` + `settings` admin endpoints | pre-v0.1.0 | [#179](https://github.com/MeganovaAI/nova-os/issues/179) |
| `output_type` field on `AgentCreate` / `AgentUpdate` | v0.1.4 | [#180](https://github.com/MeganovaAI/nova-os/issues/180) |
| `route_templates` field + `route_hint` event | v0.1.5 | [#181](https://github.com/MeganovaAI/nova-os/issues/181) |

### 3. Anthropic-parity feature gaps (server work)

Comparing against Claude Agent SDK and Managed Agents:

| Anthropic surface | Nova OS state | Issue |
|---|---|---|
| In-process MCP custom tools | Mode A (SSE inline) + Mode B (webhook); no in-process | [#182](https://github.com/MeganovaAI/nova-os/issues/182) |
| 6 `permission_mode` values | Binary firewall + custom-tool callbacks | [#183](https://github.com/MeganovaAI/nova-os/issues/183) |
| Plan mode (return plan, no exec) | None | [#184](https://github.com/MeganovaAI/nova-os/issues/184) |
| Explicit `Session` resource | Implicit via `(API key, end_user, agent)` triple | [#185](https://github.com/MeganovaAI/nova-os/issues/185) |
| Steer + interrupt API | None | [#186](https://github.com/MeganovaAI/nova-os/issues/186) |
| Streaming partial chunks | Partial; existing [#99](https://github.com/MeganovaAI/nova-os/issues/99) covers tool_use/thinking buffering | (linked) |

### 4. SDK-side example gaps for already-shipped features

| Feature | Status before | Action |
|---|---|---|
| `c.messages.stream(...)` | Shipped; only buried use was inside a stale-comment `04_custom_tool_inline.py` | Refresh `04` to use it directly; new `09_streaming_messages.py` for the no-tool case |
| `idempotency_key=` on `create()` | Shipped on every resource; no example | New `10_idempotency.py` |
| Auto-pagination on `list()` | Shipped (cursor + has_more handled internally); no example | New `11_pagination.py` |

### 5. CLI gaps

CLI is mature (`agents`, `employees`, `jobs`, `config`, `sync`, `validate`, `test-callback`, `version`). Two gaps:

- No `messages` subcommand (smoke-test path partners reach for first when the gateway misbehaves)
- `sync --prune` declared "Coming soon" but not tracked

Filed as [`MeganovaAI/nova-os-sdk#13`](https://github.com/MeganovaAI/nova-os-sdk/issues/13).

## What ships in this design

### Issues filed (13)

12 on `MeganovaAI/nova-os` (#175–#186), 1 on `MeganovaAI/nova-os-sdk` (#13). Each issue describes:
- The gap (with link to the release notes / changelog evidence)
- Why partners need it (concrete scenarios, not abstract parity)
- Suggested OpenAPI / SDK shape (so the implementer doesn't start from blank)
- Scope estimate (OpenAPI-only vs server work vs SDK work)

The four large parity issues (#182 in-process MCP, #183 permission_mode, #185 Session, #186 steer/interrupt) explicitly note they're larger than the OpenAPI-only ones and need their own design cycles when scheduled.

### Examples shipped (4)

```
python/examples/
  04_custom_tool_inline.py         REFRESHED — uses c.messages.stream() directly
  09_streaming_messages.py         NEW — token-on-the-wire chat UI pattern
  10_idempotency.py                NEW — retry-safe create() with idempotency_key
  11_pagination.py                 NEW — async for x in c.agents.list()
```

`python/examples/README.md` index updated with all three new entries.

## Decisions

### "Add missing client resources to the SDK now" — rejected

Investigated, then rejected. The SDK matches the partner OpenAPI exhaustively. Adding `c.documents` / `c.knowledge` / `c.hooks` / `c.filesystem` / `c.users` / `c.settings` ahead of OpenAPI declaration would either:
- Create drift (SDK calls fields the spec doesn't declare → typed clients in other languages can't call them)
- Force SDK changes to revert when the OpenAPI lands (server may pick different field names)

Right path: file issues against the OpenAPI, regenerate the SDK once they land. The SDK's existing resource pattern (`Resource` base + per-tag module) makes regeneration mechanical.

### "Refresh `04_custom_tool_inline.py` vs add a new example" — refresh

The existing file had a stale docstring claiming `c.messages.stream()` would be available "in the next SDK release" — that release shipped. Leaving it as-is would propagate confusion. Refresh in place; partners reading numbered examples in order get the right pattern.

### "Decompose the 12 nova-os issues into one per resource vs one per concern" — one per resource

Each of the OpenAPI-expansion issues (#175–#179) is one resource. Allows the server team to assign + ship them independently. Bundling into one mega-issue would force serial work and slower partner unblocks.

### "Examples 03 — fill it now or wait for #176?" — wait

`python/examples/03_upload_knowledge.py` is intentionally absent because the knowledge resource isn't in OpenAPI. Once #176 ships, regenerate SDK + add the example. Filling it now would be against the contract.

## Risks

- **Issue triage load.** 12 issues land on `nova-os` at once. Mitigated by linking each to the existing epic #123 so the server team can prioritise within an existing tracked initiative rather than treating them as net-new scope.
- **Documentation drift.** The new examples (09, 10, 11) demonstrate features that the partner-facing docs.meganova.ai doesn't yet describe. Follow-up: surface streaming/idempotency/pagination on the docs site (`docs/nova-os/anthropic-sdk-quickstart.md` is the natural home). Not in this design's scope.
- **Stale-docstring repeat risk.** `04_custom_tool_inline.py` had a stale "future API" comment for an unknown duration. To prevent recurrence: when the SDK ships a new top-level method, the same commit should land an example that exercises it. Convention only; no enforcement plumbing in this design.

## What this design does NOT cover

- Implementation of any of the 12 nova-os issues. Each gets its own design cycle when scheduled.
- TypeScript / Go SDK example parity (TS / Go SDKs are out-of-scope for v1 per the SDK README).
- A `Session` SDK surface (waits on #185).
- A `c.users.create()` / `c.settings.put()` SDK surface (waits on #179).
- Any change to the public API of existing resources (`agents`, `employees`, `messages`, `jobs`).

## Acceptance

- [x] 12 issues filed on `MeganovaAI/nova-os` (#175–#186), each linked to epic #123
- [x] 1 issue filed on `MeganovaAI/nova-os-sdk` (#13)
- [x] `04_custom_tool_inline.py` refreshed to use `c.messages.stream()` directly
- [x] `09_streaming_messages.py`, `10_idempotency.py`, `11_pagination.py` added
- [x] `python/examples/README.md` index updated
- [x] All 12 example files pass `ast.parse()`
- [x] Spec doc committed to `docs/superpowers/specs/`

## Follow-up

Once any of #175–#186 lands, the corresponding SDK regen + example pair is mechanical. The first one most likely to land is #180 (`output_type` OpenAPI declaration — pure spec change, server already accepts the field) — that unblocks the three vertical examples (`legaltech`, `healthcare`, `finance`) that already use the field.
