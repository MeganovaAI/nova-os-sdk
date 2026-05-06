# Comparing Search Backends

A side-by-side comparison of the five `web_search_config` backends Nova OS supports, plus the Anthropic Claude web search tool for partners weighing whether to use the model-driven path instead. Public-source data only; vendor pricing changes — verify against each vendor's docs before committing to a budget.

## At a glance

| Option | Layer | Cost (per query) | Bundled extraction | Citations | Domain allow/block | Geo localization |
|---|---|---|---|---|---|---|
| `meganova` | SDK backend | 50/day free + $0.002/group overage | ✅ | ✗ (URLs returned, partner cites) | ✗ | ✗ |
| `tavily` | SDK backend | Paid tier with monthly free quota | ✅ | ✗ (URLs + snippets) | Per-call `include_domains` | ✗ |
| `brave` | SDK backend | Free tier + per-CPM paid | ✗ (keyword-only) | ✗ | ✗ | ✗ |
| `exa` | SDK backend | Paid per-query | ✗ (keyword + neural) | ✗ | ✗ | ✗ |
| `searxng` | SDK backend | Free (self-hosted) | ✗ | ✗ | ✗ | ✗ |
| Anthropic Claude web search | Tool inside Messages API | $0.01/query + token costs | ✗ (URLs returned) | ✅ Always-on, structured | ✅ `allowed_domains` / `blocked_domains` | ✅ `user_location` |

Verify exact pricing/limits on each vendor's docs:
- MegaNova — [docs.meganova.ai/api-reference/platform-api/search](https://docs.meganova.ai/api-reference/platform-api/search)
- Tavily — [docs.tavily.com](https://docs.tavily.com)
- Brave Search API — [api.search.brave.com](https://api.search.brave.com)
- Exa — [docs.exa.ai](https://docs.exa.ai)
- SearXNG — [docs.searxng.org](https://docs.searxng.org)
- Anthropic Claude web search — [platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)

## SDK backend vs Claude tool — the layer matters

These aren't direct substitutes. They sit at different layers:

| Aspect | SDK backend (`web_search_config`) | Anthropic Claude tool |
|---|---|---|
| **Where it runs** | The deep-research skill calls the backend programmatically | Tool injected into the Messages API; Claude decides when to invoke |
| **Who decides to search** | Caller code / agent definition | Claude (model-driven) |
| **Returns what** | Ranked passages your code consumes | `web_search_tool_result` content blocks woven into Claude's reply |
| **Citations** | Partner generates from the returned URLs | Always-on, structured, with `cited_text` + `encrypted_index` |
| **Cross-vendor** | Works against any LLM you route to | Anthropic-routed models only |
| **Cost shape** | Per-query backend fee | Per-query tool fee + token costs (search results count as input tokens) |

The SDK backends are for partners who want **programmable, model-agnostic search** — pin a backend per persona, control the fallback chain, run the same search regardless of which LLM family the agent uses.

The Claude tool is for partners who want **the model to handle search end-to-end** — Claude decides when to query, the response includes citations automatically, and you don't write the orchestration code. Trade-off: Anthropic-only and roughly 5× the per-query cost.

You can use both in the same deployment: the deep-research skill uses an SDK backend for structured retrieval, and you give Claude the web search tool separately for ad-hoc lookups during synthesis.

## Bundled extraction vs keyword-only

A real-cost factor that the per-query price hides: whether the backend returns full page content or just URLs.

- **Bundled extraction** (`tavily`, `meganova`): one API call returns search + extracted page text. The deep-research skill consumes it directly.
- **Keyword-only** (`brave`, `exa`, `searxng`): the backend returns URLs and snippets; the partner / skill follows up with separate fetches via Firecrawl / crawl4ai / similar to get full page text.

If you're doing multi-aspect research with N hits per query, keyword-only multiplies your fetch cost: 1 search + N fetches at ~5-15 seconds and per-fetch fees, vs 1 search-with-extraction call. For partners on a tight latency or cost budget, prefer bundled-extraction backends.

## Latency expectations

| Option | P50 (verified) | Notes |
|---|---|---|
| `meganova` | 1-3s plain, 3-10s with `enrich=true` | P95 with `enrich`: ~15s |
| `tavily` | Sub-second to low single-digit | Vendor-published; varies with depth |
| `brave` | Sub-second | Keyword backend, fast |
| `exa` | Low single-digit | Neural ranking adds time |
| `searxng` | Variable | Aggregator latency = slowest underlying source |
| Anthropic Claude tool | Adds search round-trip + token streaming | "Pause while search executes" per Anthropic docs |

`meganova`'s latency table is the only one with public P50/P95 numbers from a vendor doc — others are general industry expectations.

## Which to pick

```
Are you running on Anthropic-routed models exclusively?
├── No → SDK backend (vendor-agnostic)
└── Yes → Continue ↓

Do you want Claude to decide when to search?
├── Yes → Claude web search tool
└── No → SDK backend ↓

Is cost the dominant constraint?
├── Yes, plus you're below $0.002/query budget → meganova (free tier first, $0.002 overage)
├── Yes, plus you can self-host → searxng
└── No → next question

Do you need bundled extraction (search + page text in one call)?
├── Yes → meganova or tavily
└── No → next question

Do you need privacy-first or no third-party dependency?
├── Yes → brave (privacy-first) or searxng (self-hosted)
└── No → next question

Is the workload technical / academic / paraphrased queries?
├── Yes → exa (neural ranking helps)
└── No → tavily (most reliable for current events)
```

## Three concrete partner patterns

### Cost-conscious general-purpose

```yaml
web_search_config:
  primary_backend: meganova   # 50/day free + $0.002/group overage; extraction included
  fallback_chain: [brave]     # cheap keyword fallback when MegaNova quota exhausts
  reformulator: true
```

Free tier covers low-volume tenants; overage is the cheapest paid extraction-included option in the table.

### Premium current-events

```yaml
web_search_config:
  primary_backend: tavily
  fallback_chain: [exa]       # exa for technical follow-ups
  reformulator: false         # tavily handles reformulation internally
```

Pay for Tavily on the freshness-dominant majority; fall through to Exa for the long tail.

### Anthropic-only deployment with model-driven search

```python
# In the partner backend code:
client = Anthropic(base_url="https://nova-os.your-company.example", api_key="<jwt>")

response = client.messages.create(
    model="anthropic/claude-opus-4-7",
    max_tokens=4096,
    messages=[{"role": "user", "content": "What's the latest on Bill 96?"}],
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
)
# Claude decides when to search; results stream back with citations.
```

Skip `web_search_config` entirely; let Claude orchestrate.

## Caveats

- **Vendor pricing changes.** All numbers in this doc were captured at the time of writing. Verify against each vendor's docs before committing to a partner-tier price.
- **Per-query is not per-call.** Some backends bill "groups" (multi-aspect deep research counts as one); some bill per individual search. Read the vendor's billing-unit definition.
- **Free tiers are real but rate-limited.** Don't size capacity assuming the free tier scales — per-key concurrency caps usually kick in first.
- **The Anthropic Claude tool requires admin enablement** in the Claude Console (per their docs). It's not on by default.

## See also

- [`web-search.md`](web-search.md) — full reference for the SDK's `web_search_config`
- [`anthropic-compat.md`](anthropic-compat.md) — Claude tool integration via the Messages API
- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
