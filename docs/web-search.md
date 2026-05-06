# Web Search Backends

Nova OS ships pluggable web-search with fallback chains. Six backends out of the box; partners pick per-persona via `web_search_config`. The configuration is resolved per-invocation, so a partner can run different personas on different backends in the same deployment.

## TL;DR

- **Six backends:** `ceramic`, `tavily`, `brave`, `exa`, `searxng`, `meganova`. Plus `auto` for server-default order.
- **Fallback chain** wraps the primary in a `FallbackSearcher` that promotes on empty / error / off-topic results.
- **Reformulator** wraps keyword backends with an LLM rewrite step (lifts Ceramic 42→70% on broad queries).
- **Recency-intent escalator** detects "latest", "today", "this week" markers and biases results toward fresh sources.
- **Per-call resolution** since [`#200`](https://github.com/MeganovaAI/nova-os/issues/200) — `web_search_config` on the persona is read at invocation, not boot.

## Backend selection

| Backend | Type | When to pick |
|---|---|---|
| `ceramic` | Bundled extraction | Default — combines retrieval + page extraction in one call. Best signal-to-noise for broad queries when paired with reformulator. |
| `tavily` | Bundled extraction | Most reliable for current-events queries. Native answer/snippet quality. Costs more than keyword backends. |
| `brave` | Keyword | Privacy-first, decent freshness, no LLM-fluff. Pair with reformulator. |
| `exa` | Keyword + neural | Strong on technical / academic queries. Neural ranking helps for paraphrased queries. |
| `searxng` | Keyword aggregator | Self-hosted; aggregates Google / Bing / others. Good when partners want no third-party search dependency. |
| `meganova` | Bundled extraction | MegaNova's managed search API — natural-language query → ranked results with optional full-page text extraction in one round-trip. See [meganova.ai/web-search](https://www.meganova.ai/web-search). |
| `auto` | (alias) | Falls through to server's `DefaultSearcher()` priority: Ceramic → Tavily → Brave → Exa → SearXNG with reformulator + Tavily-fallback wrappers. |

`auto` is the right pick if you don't have a specific reason to override; the default order is tuned against operator experience.

## Cost-quality table

Order of magnitude per 1K queries. Exact pricing varies by tier, region, and contract — treat as relative.

| Backend | Cost | Quality | Best for |
|---|---|---|---|
| `meganova` | 50/day free + $0.002/group overage | Natural-language + extraction in one call | Cost-conscious general-purpose; one-call extraction (no separate fetcher) |
| `searxng` | Free (self-hosted) | Variable (depends on aggregated sources) | Air-gap deployments |
| `brave` | Low | Good | Privacy-first, day-to-day queries |
| `ceramic` | Mid | Good | Broad queries, especially with reformulator |
| `exa` | Mid | High on technical | Engineering / research queries |
| `tavily` | High | Highest | Current-events queries, when freshness matters |

A common partner pattern: `tavily` primary with `brave` fallback. Pays for Tavily on most queries, falls through to free Brave if Tavily quota exhausts.

### MegaNova backend specifics

Concrete numbers from the [API reference](https://docs.meganova.ai/api-reference/platform-api/search):

| Concern | Value |
|---|---|
| Endpoint | `POST https://api.meganova.ai/v1/serverless/search` |
| Free quota | 50 prompt-groups per day, per key |
| Overage | `$0.002 per group` (a "group" is all sub-calls sharing the same `X-Request-Group-Id`) |
| Tier requirement | `ENGINEER_TIER_2` — auto-granted on first $1 deposit; returns 403 below tier |
| Per-key RPS | 10 req/s |
| Per-key concurrency | 20 (paid) / 50 (enterprise) |
| Latency (`enrich=false`) | 1–3 s P50 |
| Latency (`enrich=true`) | 3–10 s P50, 15 s P95 |
| `max_results` cap | 20 |
| Failure mode | 5xx when all upstream sources exhausted — **not charged** |

A "group" is the billing unit — Nova OS sends a single `X-Request-Group-Id` per persona invocation, so multi-aspect deep research counts as one group regardless of how many sub-queries fan out. Personas configured with high `max_results` and `enrich: true` should plan for the 3-10s P50 latency; pair with `reformulator: false` since MegaNova handles reformulation internally.

## Configuration

`web_search_config` lives on the persona / agent definition. Field names changed in [`#212`](https://github.com/MeganovaAI/nova-os/pull/212) — `backend` → `primary_backend`, `fallback` → `fallback_chain`. Old names are no longer accepted server-side.

### YAML (in `data/agents/<persona>.md` frontmatter)

```yaml
---
id: legal-research-agent
type: skill
owner_employee: legal-team
web_search_config:
  primary_backend: tavily
  fallback_chain: [brave, searxng]
  reformulator: true
  recency_terms: ["court ruling", "amendment", "regulation"]
---
```

### SDK (Python)

```python
from nova_os import Client

async with Client(base_url=..., api_key=...) as c:
    await c.agents.create(
        id="legal-research-agent",
        type="skill",
        owner_employee="legal-team",
        web_search_config={
            "primary_backend": "tavily",
            "fallback_chain": ["brave", "searxng"],
            "reformulator": True,
            "recency_terms": ["court ruling", "amendment", "regulation"],
        },
    )
```

### Field reference

| Field | Type | Default | Notes |
|---|---|---|---|
| `primary_backend` | enum | `auto` | One of `ceramic` / `tavily` / `brave` / `exa` / `searxng` / `meganova` / `auto`. |
| `fallback_chain` | array | `[]` | Ordered list. Wraps the primary in a `FallbackSearcher` whose `Name()` renders as `primary→fallback1→fallback2`. |
| `reformulator` | bool | `true` | LLM-wrap the search call. Only applied to keyword backends (ceramic / searxng / exa); bundled-extraction backends ignore it. |
| `recency_terms` | array | `[]` | Custom recency markers for the recency-intent escalator. Default markers (`latest`, `today`, `this week`, `recent`) always apply. |

## Fallback chain semantics

`FallbackSearcher` wraps a primary + N fallbacks. Promotion conditions:

| Condition | Action |
|---|---|
| Primary returns empty results | Try next fallback. |
| Primary returns HTTP 5xx / timeout | Try next fallback. |
| Primary returns HTTP 429 rate limit | Try next fallback. |
| Primary's results judged off-topic by reformulator (when enabled) | Try next fallback. |
| All backends fail | Return empty result set. |

The runtime `Name()` of a chained searcher renders as `primary→fallback1→...`. Operators see this in logs:

```
deep_research: per-call backend=tavily→brave (from persona web_search_config; defaultBackend=ceramic+reformulate→tavily→tavily)
```

## Per-call resolution

Before [`#200`](https://github.com/MeganovaAI/nova-os/issues/200) / [`#212`](https://github.com/MeganovaAI/nova-os/pull/212), the search backend was captured at boot time and the persona-level `web_search_config` was silently ignored on `skill_deep_research`. Post-fix:

- Every invocation reads `searchctx.WebSearchConfigFromContext(ctx)`.
- When persona config is set, builds a per-call searcher via `BuildSearcherWithFallback`.
- Falls back to the boot-time env-built default when context is empty (preserves zero-config behavior).
- Goroutines see their own per-call resolved values (race-safe — searcher passed as method parameter, not struct mutation).

This means a single Nova OS deployment can run different personas on different backends concurrently. The persona's YAML is the source of truth; partners don't need to restart the server to change a backend.

## Reformulator

When `reformulator: true` (default for keyword backends), each search call wraps the keyword query with an LLM rewrite step:

1. Original user query → LLM → reformulated query
2. Reformulated query → backend → results
3. (Optionally) results filtered by topical relevance

Empirical lift on Ceramic: **42% → 70%** on broad partner queries. The cost is one cheap-tier LLM call per search (typically Flash, ~$0.0001).

Reformulator is **only applied to keyword backends** (`ceramic`, `searxng`, `exa`). Bundled-extraction backends (`tavily`, `brave`, `meganova`) handle reformulation internally.

Disable per-persona when:
- The query domain is so narrow the LLM rewrite hurts more than helps
- Latency budget is tight (reformulation adds ~500ms)
- Cost matters and the lift isn't worth the per-search LLM call

```yaml
web_search_config:
  primary_backend: ceramic
  reformulator: false   # raw query straight to backend
```

## Recency-intent escalator

Partners' users often ask "what's the latest…" or "recent changes to…" — queries where freshness matters more than breadth. The recency-intent escalator detects these markers and:

1. Biases backend ordering toward fresher sources (Tavily over Ceramic on recency-tagged queries)
2. Adds a date-filter parameter to keyword-backend searches
3. Boosts ranking of results from the past N days (default 30)

**Default markers** (always applied): `latest`, `today`, `this week`, `recent`, `recently`, `now`.

**Custom markers** (per-persona): add domain-specific phrases via `recency_terms`:

```yaml
web_search_config:
  primary_backend: tavily
  recency_terms: ["court ruling", "amendment", "regulation", "Bill 96 update"]
```

A query mentioning "Bill 96 update" then biases toward fresh sources without the user having to spell out "latest."

## Common patterns

### Cost-optimized partner (free-tier-first)

```yaml
web_search_config:
  primary_backend: meganova   # 50/day free + $0.002 overage, extraction included
  fallback_chain: [brave]     # cheap fallback when MegaNova quota exhausts
  reformulator: true
  recency_terms: ["court ruling", "amendment"]
```

The MegaNova backend bundles search + page extraction in one call, so the persona doesn't need a separate fetcher (similar to Tavily, but at a different price point). `recency_terms` example shown is for a legaltech partner; adjust for your domain.

### Air-gap deployment

```yaml
web_search_config:
  primary_backend: searxng    # self-hosted, no third-party dependency
  fallback_chain: []          # no escape from the air-gap
  reformulator: false         # avoids LLM-call for query rewrite (still hits the air-gap LLM, but...)
```

### Highest-quality current-events

```yaml
web_search_config:
  primary_backend: tavily
  fallback_chain: [exa]       # exa for technical follow-ups
  reformulator: false         # Tavily handles this internally
```

### Per-tenant override

The `web_search_config` is on the agent / persona definition, so partners running multi-tenant deployments can give different tenants different backends by per-tenant agent overrides:

```python
# Tenant A — premium tier — full Tavily
await c.agents.update(
    id="legal-research-agent-tenant-a",
    web_search_config={"primary_backend": "tavily", "fallback_chain": ["brave"]},
)

# Tenant B — free tier — Brave only
await c.agents.update(
    id="legal-research-agent-tenant-b",
    web_search_config={"primary_backend": "brave"},
)
```

## Required env vars (operator-side)

Each backend needs its own credential. Set as Nova OS env vars:

| Backend | Env var | Notes |
|---|---|---|
| `tavily` | `TAVILY_API_KEY` | Required for `tavily` primary or fallback. |
| `brave` | `BRAVE_API_KEY` | Required for `brave` primary or fallback. |
| `exa` | `EXA_API_KEY` | Required for `exa` primary or fallback. |
| `meganova` | `MEGANOVA_CLOUD_KEY` (or `MEGANOVA_API_KEY` alias) | Required for `meganova` primary. The alias was added in [`#214`](https://github.com/MeganovaAI/nova-os/issues/214) / [`#215`](https://github.com/MeganovaAI/nova-os/pull/215); both forms accepted, `CLOUD_KEY` is canonical. Sent as `Authorization: Bearer <sk-...>` to the upstream API at `https://api.meganova.ai/v1/serverless/search`. Engineer Tier 2 required (auto-granted on first $1 deposit) — calls return 403 below tier. Service product page: [meganova.ai/web-search](https://www.meganova.ai/web-search); API reference: [docs.meganova.ai/api-reference/platform-api/search](https://docs.meganova.ai/api-reference/platform-api/search). |
| `searxng` | `SEARXNG_URL` | Self-hosted SearXNG instance URL. No API key. |
| `ceramic` | (none) | Built-in to the server. |

If a persona declares `primary_backend: tavily` but `TAVILY_API_KEY` is unset, the server logs a warn and falls through to boot defaults:

```
deep_research: persona declared web_search_config.primary_backend=tavily but BuildSearcherWithFallback returned nil — using default backend=ceramic+reformulate→tavily→tavily
```

## See also

- [`anthropic-compat.md`](anthropic-compat.md) — `web_search_config` field on the agent endpoint
- [`multi-model.md`](multi-model.md) — parallel concept for LLM model selection
- [Web search resolver design](https://github.com/MeganovaAI/nova-os/blob/master/docs/superpowers/specs/2026-05-05-web-search-config-resolver-design.md) — server-side architecture
- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
