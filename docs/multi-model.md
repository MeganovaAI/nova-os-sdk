# Multi-Model Routing

Nova OS routes each LLM call through a five-level cascade. The most-specific level wins. This lets a partner declare "use Opus for the answer, Flash for skill steps, Haiku for the planner" once at the employee level and let everything below inherit, while still being able to override per-call when needed.

## TL;DR

- **Three slots:** `answer`, `planner`, `skill`. Each is independent.
- **Five resolution levels:** per-call → per-skill → per-agent → per-employee → server default. Most-specific wins.
- **Each slot carries a fallback chain** — Nova OS auto-promotes on rate-limit / 5xx / vendor outage / Vertex 400 schema-error.
- **Model shape:** `<vendor>/<model>` (e.g. `anthropic/claude-opus-4-7`). Bare names get a 400.
- **Default since v0.1.5 (2026-05-05):** `gemini/gemini-2.5-flash`. Override via per-level config or `OPENAI_MODEL` env.

## The three slots

Different parts of an agent run want different cost/quality tradeoffs:

| Slot | What it serves | Typical pick |
|---|---|---|
| **`answer`** | Main chat synthesis, report executive summary, persona answer synthesis — anything the user reads | Premium model (Opus, GPT-5, Gemini Pro) |
| **`planner`** | Brain DAG planning, intent classification, skill selection — internal reasoning the user never sees | Cheap-fast model (Haiku, Flash, GPT-mini) or a local Qwen |
| **`skill`** | Skill agents + report sections (outline, per-section, timeline, risk matrix) — high-throughput internal work | Cheap-fast model (Flash, Haiku) |

A typical production setup runs `answer` on a premium Anthropic model and pins `planner` + `skill` on Flash. That single split cuts report generation cost roughly six-fold while keeping reader-facing prose at premium quality.

## Resolution cascade

For every LLM call, Nova OS walks from most-specific to least-specific until it finds a non-empty value:

```
per-call (request body)
   └─ per-skill (skill agent's model_config)
        └─ per-agent (agent.model_config)
             └─ per-employee (employee.model_config — cascades to all owned agents)
                  └─ server default (NOVA_OS_BRAIN_MODEL / NOVA_OS_SKILL_MODEL / OPENAI_MODEL env)
```

Each level may set any subset of slots. Unset slots fall through. Practical example:

```python
# Server defaults (env vars set at boot):
#   OPENAI_MODEL              = gemini/gemini-2.5-flash         # answer
#   NOVA_OS_SKILL_MODEL       = gemini/gemini-2.5-flash         # skill
#   NOVA_OS_BRAIN_MODEL       = anthropic/claude-haiku-4-5      # planner

# Employee overrides answer only:
employee.model_config = {
    "answer": {"primary": "anthropic/claude-opus-4-7"},
}

# Agent under that employee overrides skill:
agent.model_config = {
    "skill": {"primary": "openai/gpt-5-mini"},
}

# Per-call request overrides answer:
client.messages.create(model="gemini/gemini-2.5-pro", ...)
```

For this call, the resolved selections are:
- `answer` → `gemini/gemini-2.5-pro` (per-call wins)
- `planner` → `anthropic/claude-haiku-4-5` (server default; nothing overrode)
- `skill` → `openai/gpt-5-mini` (agent override wins)

## Fallback chains

Each slot has both a `primary` and an optional ordered `fallback[]`. Nova OS automatically promotes the next healthy fallback when the primary fails:

```python
employee.model_config = {
    "answer": {
        "primary": "anthropic/claude-opus-4-7",
        "fallback": [
            "gemini/gemini-2.5-pro",      # 1st fallback — tried first
            "openai/gpt-5",               # 2nd fallback — only if Gemini also fails
        ],
    },
}
```

**Failure conditions that trigger fallback:**

| Condition | Action |
|---|---|
| HTTP `429` rate limit | Promote next fallback. Don't retry primary on same call. |
| HTTP `503` / upstream timeout | Promote next fallback. |
| Provider billing exhaustion (`quota_exceeded`) | Promote next fallback. |
| Vertex AI `400` schema error (`type:array` without `items`) | Treated as primary failure on this call (it's deterministic per payload — retry won't help). |
| HTTP `400` malformed request | **Don't fallback** — surface the error. The fallback model would fail the same way. |
| HTTP `401`/`403` auth | **Don't fallback** — surface the error. |

The response includes `model_used` and `fallback_triggered` fields so partners can observe which tier served the request:

```python
resp = await c.messages.create(agent_id="legal-assistant", messages=[...])
print(resp["model_used"])           # e.g. "gemini/gemini-2.5-pro"
print(resp["fallback_triggered"])   # True
```

## Setting model_config

### Per-employee (the common case)

```python
async with Client(base_url=..., api_key=...) as c:
    await c.employees.create(
        id="legal-team",
        display_name="Legal Team",
        model_config={
            "answer":  {"primary": "anthropic/claude-opus-4-7", "fallback": ["gemini/gemini-2.5-pro"]},
            "planner": {"primary": "anthropic/claude-haiku-4-5"},
            "skill":   {"primary": "gemini/gemini-2.5-flash"},
        },
    )
```

All agents owned by `legal-team` inherit this cascade unless they override individual slots.

### Per-agent

```python
await c.agents.create(
    id="contract-reviewer",
    type="skill",
    owner_employee="legal-team",
    model_config={
        "answer": {"primary": "openai/gpt-5"},   # only override answer
    },
)
```

Inherits `planner` and `skill` from the employee.

### Per-call

Anthropic SDK shape:

```python
client.messages.create(
    model="gemini/gemini-2.5-pro",
    messages=[...],
)
```

Nova OS native shape:

```python
await c.messages.create(
    agent_id="contract-reviewer",
    model="gemini/gemini-2.5-pro",
    messages=[...],
)
```

Per-call wins over every other level.

### Server default (operators only)

| Env var | Slot | Default | Notes |
|---|---|---|---|
| `OPENAI_MODEL` | `answer` | `gemini/gemini-2.5-flash` (since v0.1.5 force-update on 2026-05-05) | Gateway-safe per `validateModelShape`. |
| `NOVA_OS_BRAIN_MODEL` | `planner` | varies by deployment | Often a local Qwen via vLLM, or Haiku. |
| `NOVA_OS_PLANNER_API_BASE` | `planner` (URL) | unset | When set, `planner` calls hit this URL instead of the model gateway. |
| `NOVA_OS_SKILL_MODEL` | `skill` | `gemini/gemini-2.5-flash` | Cheap-fast tier. |
| `NOVA_OS_MEMORY_WORKER_MODEL` | memory worker | falls back to `OPENAI_MODEL` | Observer/Reflector LLM. |

These are operator-set; partners typically don't touch them.

## Model identifier requirement: `<vendor>/<model>`

Every model identifier must carry a vendor prefix. This is gateway-safe per `validateModelShape` ([`#93`](https://github.com/MeganovaAI/nova-os/issues/93)):

| Vendor prefix | Routes to |
|---|---|
| `anthropic/` | Anthropic Messages API direct |
| `openai/` | OpenAI Chat Completions (or any OpenAI-compatible gateway via `OPENAI_API_BASE`) |
| `gemini/` | Google Vertex AI (or MegaNova gateway routing) |
| `nebula/` | NebulaBlock |

**Bare names like `gpt-4o` or `claude-opus-4-7` get rejected at validation.** The default-value fix in [`#197`](https://github.com/MeganovaAI/nova-os/issues/197) / [`#198`](https://github.com/MeganovaAI/nova-os/pull/198) makes the boot-time default (`OPENAI_MODEL`) gateway-safe; per-level overrides must follow the same shape.

## Inspecting which model served a request

Two channels:

**1. Response body** (Nova OS native + Managed Agents):
```python
resp = await c.messages.create(...)
print(resp["model_used"], resp["fallback_triggered"])
```

**2. Response headers** (planned — `X-Nova-Model-Used` / `X-Nova-Model-Fallback-Triggered`):
Tracked at [`MeganovaAI/nova-os` issue tracker](https://github.com/MeganovaAI/nova-os/issues). Until shipped, use the body fields.

**3. Server logs:**
```
planner_decision skills=[draft] count=1 ... model=anthropic/claude-haiku-4-5
skill_completed name=section model=gemini/gemini-2.5-flash duration=1240ms
```
`grep` on `model=` to track per-skill model selection in production.

## Common patterns

### Cost-optimized partner deployment

```python
employee.model_config = {
    "answer":  {"primary": "anthropic/claude-opus-4-7", "fallback": ["gemini/gemini-2.5-pro"]},
    "planner": {"primary": "anthropic/claude-haiku-4-5"},
    "skill":   {"primary": "gemini/gemini-2.5-flash"},
}
```

Premium for reader-facing answers, mid-tier for planning, cheap-fast for high-throughput skill calls. ~6× cost reduction vs running Opus across all three slots.

### High-availability dual-vendor

```python
employee.model_config = {
    "answer": {
        "primary": "anthropic/claude-opus-4-7",
        "fallback": ["openai/gpt-5", "gemini/gemini-2.5-pro"],
    },
}
```

If Anthropic rate-limits or quota-exhausts, OpenAI takes over. If both fail, Gemini.

### A/B testing a new model

Override per-call for the experiment:

```python
# Bucket 50% of users onto gpt-5 via per-call override, leave the rest on the default.
model = "openai/gpt-5" if user_id % 2 == 0 else None
client.messages.create(model=model, ...)
```

`None` (or omitting `model`) falls through to the cascade.

## See also

- [`anthropic-compat.md`](anthropic-compat.md) — model parameter on `/v1/messages` endpoint
- [`web-search.md`](web-search.md) — backend selection (parallel concept for search)
- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
- [`python/examples/06_multi_model_fallback.py`](../python/examples/06_multi_model_fallback.py) — worked example
