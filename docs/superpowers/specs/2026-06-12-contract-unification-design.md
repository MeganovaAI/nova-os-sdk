# Contract Unification — one LibraOS contract, web + iOS bindings

**Date:** 2026-06-12 · **Status:** Design (pre-implementation) · **Owner:** libraos-sdk
(contract source of truth)

**Scope (cross-repo):**
- `nova-os` — kernel; OIDC token endpoint (refresh grant **already shipped**; hardened in #653), the REST surfaces clients call.
- `libraos-sdk` — **source of truth**: OpenAPI spec + generated bindings + OIDC/AG-UI shared specs.
- `nova-ios` — iPhone client; retire its *assumed* `/api/v1`, adopt generated bindings + OIDC.
- `nova-os-employee-assistant` / `nova-os-school` — web verticals; consume the generated TS kit.

> **Internal design doc** — names internal surfaces and cross-repo architecture. Not for the
> published `docs/` site or partner distribution.

---

## 1. Problem

The same logical product — the digital-employee persona surfaced on **web** (`employee-ui`)
and **mobile** (`nova-ios` Assistant tab) over the `nova-os` kernel — is reached today through
**three divergent, partly-invented contracts**:

| Surface | Auth | API |
|---|---|---|
| `employee-ui` / `school-ui` (web) | OIDC | AG-UI / CopilotKit + `/v1` |
| `nova-ios` | **email/password** `login()` | **invented** `/api/v1` (`sessions`, `recording`, `briefing`) — its own spec says *"No API spec exists. This is an explicit assumption."* |
| `nova-os` (truth) | **OIDC PKCE** (`/oauth/*`; `nova-os-ios` client registered) | `/v1/messages`, `/agents/v1/*`, `/v1/managed/*`, OpenAPI partner spec, AG-UI |

Consequences: nova-ios is built on an unverified contract (compile/integration risk);
`employee-ui` has no shared client (it would fork `school-ui`'s 23k-LOC bespoke `api/`+`auth/`);
auth is inconsistent (password vs OIDC); and there is no single place a change to the wire
shape is made once.

## 2. The contract is THREE specs, not one

A single OpenAPI file cannot be the whole contract. The clients need three distinct things;
only the first exists today:

| Contract | Source of truth | Today |
|---|---|---|
| **REST data** (agents, messages, jobs, documents, sessions, knowledge) | `openapi/nova-os-partner.v1.yaml` (2,207 lines) | ✅ exists, rich |
| **Auth** (interactive login) | OIDC `/oauth/*` (Auth-Code + PKCE + refresh) — deliberately **not** in the OpenAPI spec (`bearerAuth` assumes a partner-minted JWT) | ⚠️ separate, undocumented in the SDK |
| **Streaming** (chat events) | AG-UI event shape | ⚠️ separate, no typed artifact |

**Unification model:** one REST spec **generates** both platform bindings; the two non-REST
contracts (OIDC flow, AG-UI events) are shared **specs/helpers**, not generated from OpenAPI.

```
libraos-sdk/openapi/nova-os-partner.v1.yaml   ── REST source of truth
        │  (codegen)
        ├── TS client-kit   →  employee-ui (web) + school-ui
        └── Swift NovaOSClient →  nova-ios   (replaces the "assumed" /api/v1)
  + shared OIDC PKCE+refresh flow  + shared AG-UI event types   (hand-authored specs)
```

## 3. Diff — nova-ios assumed `/api/v1` vs reality

| nova-ios assumes | Real LibraOS surface | Gap / action |
|---|---|---|
| `POST auth/login {email,password}` | OIDC `/oauth/authorize`+`/oauth/token` (PKCE; `nova-os-ios` + `novaos://oauth/callback` already registered) | **Replace** with Auth-Code+PKCE via `ASWebAuthenticationSession`. Isolated behind `AuthService`/`TokenProviding` → swappable. |
| `POST auth/refresh {refresh_token}` | `/oauth/token` grant=`refresh_token` | **Already shipped** (`nova-os` commit `3a5857a3`, rotating refresh gated on `offline_access`). Residual filled in `nova-os#653`: reuse-detection family revocation + discovery `grant_types_supported`. Keep the `refresh()` seam, re-point it. |
| `GET deployment` (capability catalogue) | — none — | **Net-new (small):** add a `deployment`/capabilities read, or configure client-side. |
| `POST sessions {matter,subject,mode,consent}` | `/v1/managed/sessions` (#185, generic) | **Partial:** real sessions exist but aren't recording/consent-shaped. Extend the session schema or wrap vertical-side (§4). |
| `POST sessions/{id}/recording` (media upload) | `/v1/managed/documents/upload` | **Divergent:** real is document-upload, not session-scoped media. Reconcile to a session-scoped upload. |
| `GET sessions/{id}/briefing` (202 polling) | `/v1/managed/agents/jobs` + `/jobs/{id}/stream` | **No bespoke endpoint:** the briefing is an async **job** running a report/summary persona over the transcript. Compose; don't invent. |
| *(future)* Assistant-tab chat | `/v1/messages` (Anthropic-shaped) + AG-UI | **Same as web** — build on `/v1/messages` + AG-UI, identical kit. |

## 4. Kernel-discipline decision (load-bearing)

**Recording → briefing is a vertical composition, not a kernel primitive.** It decomposes into
kernel primitives that already exist: `documents/upload` (capture the media/transcript) +
`agents/jobs` (run a briefing persona async) + a report. Therefore:

- The kernel does **not** grow bespoke `sessions/{id}/recording` / `briefing` endpoints.
- The recording→briefing **contract** is owned by a **vertical** (a recording companion or
  `nova-os-employee-assistant`), exactly like `promotion-svc`/`workflow-svc`.
- `nova-ios` **composes kernel primitives** (or calls the vertical service); it does not expect
  the kernel to speak "briefing."

This is the single decision that stops nova-ios's invented contract from leaking into the kernel
(per `nova-os` CLAUDE.md §"Kernel discipline" / #361: *provide the contract, partners build the world*).

## 5. Per-repo responsibilities

**`libraos-sdk` (owner)**
- Keep `openapi/nova-os-partner.v1.yaml` the REST truth; gap-fill the shapes both clients need
  (deployment/capabilities; confirm `sessions`, `documents/upload`, `agents/jobs`, `messages`).
- Add two hand-authored shared artifacts:
  - **`docs/oidc-client-flow.md`** — Auth-Code+PKCE+refresh sequence, client registration
    (`nova-os-ios`, web client ids), token storage guidance.
  - **`openapi/ag-ui-events.schema.json`** (or `.ts`) — typed AG-UI streaming event shape.
- Generate + publish the **TS client-kit** (REST via `openapi-typescript` + OIDC PKCE helper +
  AG-UI types) and the **Swift** model layer (REST DTOs from the spec).

**`nova-os` (kernel)**
- ~~Add `refresh_token` grant~~ — **already shipped** (`3a5857a3`, rotating refresh on
  `offline_access`). Residual hardening filled in `nova-os#653`: reuse-detection family
  revocation + discovery `grant_types_supported`. No further grant work.
- Confirm `/v1/managed/sessions`, `/v1/managed/documents/upload`, `/v1/managed/agents/jobs`,
  `/v1/messages` match the spec; add a small capabilities/`deployment` read if adopted
  (contract added in `libraos-sdk#34`; kernel endpoint still TODO).

**`nova-ios`**
- Replace `login(email,password)` with OIDC PKCE (`ASWebAuthenticationSession` → `/oauth/*`);
  re-point `refresh()` at `/oauth/token`. `TokenProviding` already abstracts this.
- Replace the *assumed* `DTO.*` wire types with Swift models generated from the OpenAPI spec for
  the overlapping surfaces (sessions, documents, jobs, messages).
- Re-map recording→briefing onto the §4 composition / vertical contract.
- (Future) Assistant tab → `/v1/messages` + AG-UI, same contract as web.

**`nova-os-employee-assistant` / `nova-os-school` (web verticals)**
- Consume the TS client-kit; retire `school-ui`'s bespoke `api/`+`auth/` in favor of it.
- Keep vertical pages/workflows/branding/connectors per-repo.

## 6. Build order (dependency-sorted)

1. ✅ **OIDC refresh hardening** (`nova-os#653`) — grant already shipped; this added
   reuse-detection + discovery advertisement. Unblocks durable web + mobile sessions.
2. ✅ **SDK truth** (`libraos-sdk#34`): OpenAPI gap-fill + `oidc-client-flow.md` + AG-UI event schema.
3. ✅ **TS kit generation** (`libraos-sdk#34`) → `employee-ui`/`school-ui` adopt it next (Phase 1 web).
4. **Swift realign**: OIDC PKCE + generated DTOs → retires nova-ios's *assumed* `/api/v1`.
5. **Recording→briefing vertical contract** (§4) → nova-ios V1 composes real primitives.
6. **Assistant tab** (web parity) — last, once kit + AG-UI are stable.

## 7. Open decisions

- **D1 — Capabilities discovery:** add a kernel `deployment`/capabilities endpoint, or have the
  client derive capabilities from config + which agents/personas the identity owns? *(lean: derive)*
- **D2 — Recording→briefing home:** a dedicated recording companion repo, or fold into
  `employee-assistant`? *(lean: dedicated, since nova-ios V1 is recording-first and not corporate-employee-specific)*
- **D3 — Swift codegen:** generate Swift from OpenAPI (`openapi-generator`) vs hand-write a thin
  layer matching the spec? *(lean: generate the DTOs, hand-write the `NovaOSClient` glue)*
- **D4 — Session schema:** extend the kernel `Session` (#185) with consent/recording fields, or
  keep those vertical-side and reference a generic session id? *(lean: vertical-side)*

## 8. Non-goals

- Modeling OIDC inside the OpenAPI partner spec (it stays a separate auth contract).
- A bespoke kernel recording/briefing surface (explicitly rejected, §4).
- Re-platforming nova-ios off Swift or employee-ui off React.
- Merging the verticals — each keeps its own pages/workflows/schema.

## 9. References

- `nova-os` CLAUDE.md §"Kernel discipline" (#361); `docs/research/technology/is-nova-os-a-kernel/`
- `nova-os` `docs/architecture/nova-os-is-a-kernel.md`
- `libraos-sdk/openapi/nova-os-partner.v1.yaml` (REST truth)
- `nova-ios` `docs/superpowers/specs/2026-06-11-nova-os-connectivity-design.md` (the *assumed* contract)
- `nova-os` branch `feat/oidc-ios-client`; `nova-os-school` branch `feat/i5-oidc-refresh`
- `nova-os-school/services/school-ui` (the built web reference to extract the TS kit from)
