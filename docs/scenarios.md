# Scenarios

Ten end-to-end partner workflows. Each scenario shows what happens from the user's perspective, what flows on the wire, and which surface (UI / shared folder / SDK / CLI) is the right entry point.

| # | Scenario | Lifecycle phase | Primary surface |
|---|---|---|---|
| 1 | [Partner onboarding — create employee + agent](#1-partner-onboarding) | Setup | Shared folder + CLI sync |
| 2 | [Knowledge upload + first retrieval](#2-knowledge-upload--first-retrieval) | Setup | SDK |
| 3 | [End-user's first chat](#3-end-users-first-chat) | Runtime | SDK / Anthropic SDK |
| 4 | [Custom tool — Mode A (SSE inline)](#4-custom-tool--mode-a-sse-inline) | Runtime | SDK |
| 5 | [Custom tool — Mode B (webhook)](#5-custom-tool--mode-b-webhook) | Runtime | SDK + partner HTTP server |
| 6 | [Multi-model fallback fires under load](#6-multi-model-fallback-fires-under-load) | Runtime | (transparent) |
| 7 | [Long-running async job](#7-long-running-async-job) | Runtime | SDK |
| 8 | [Persona update — git → live](#8-persona-update--git--live) | Iteration | Shared folder + CLI sync |
| 9 | [Lifecycle hook subscription](#9-lifecycle-hook-subscription) | Iteration | SDK |
| 10 | [Bundle export → import across instances](#10-bundle-export--import-across-instances) | Migration | SDK / CLI |

---

## 1. Partner onboarding

**Goal:** A new partner stands up an employee + one agent, validates locally, and syncs to a running Nova OS instance.

**What the user does:**
- Drops `data/employees/<id>.md` and `data/agents/<id>.md` files in their git repo
- Runs `nova-os-cli validate ./data/` as a CI gate
- Runs `nova-os-cli sync ./data/` to push to the server

**What flows on the wire:**

```
$ nova-os-cli validate ./data/
✓ data/employees/legal-team.md         frontmatter / model_shape / vertex-array OK
✓ data/agents/legal-assistant.md       frontmatter / model_shape / route_templates OK
0 errors

$ nova-os-cli sync ./data/
PLAN
  CREATE employee  legal-team
  CREATE agent     legal-assistant       (owner_employee=legal-team)
APPLY
  POST /v1/managed/employees       → 201
  POST /v1/managed/agents          → 201
```

**Surface choice:**
- **Shared folder + CLI sync** is the production-grade path. Folders are git-diffable; sync is idempotent and supports `--watch` for live development.
- **Dashboard UI** works for ad-hoc edits but loses git history.
- **SDK direct** (`c.employees.create(...)`) works for programmatic provisioning (e.g., one-employee-per-tenant in multi-tenant SaaS).

**Worked example:** [`02_create_employee_and_agent.py`](../python/examples/02_create_employee_and_agent.py).

---

## 2. Knowledge upload + first retrieval

**Goal:** Partner uploads a corpus of documents (contracts, regulations, FAQs) and verifies the agent retrieves from them at chat time.

**What flows on the wire:**

```
# Ingest
POST /v1/managed/knowledge/ingest
  body: {"content": "...", "title": "Quebec Bill 96 ...", "collection": "case-law"}
  → 201 {"document_id": "doc_abc"}

# At chat time, agent retrieves automatically when knowledge_bindings is set:
POST /v1/messages
  body: {"agent_id": "legal-assistant", "messages": [...], ...}
  ⇒ server-side retrieval enriches context with collection="case-law" passages
  → 200 {"content": [...], "model_used": "anthropic/claude-opus-4-7", ...}
```

**Surface choice:**
- **SDK** for partner backends ingesting at scale.
- **CLI** for one-off ingestion: `nova-os-cli knowledge ingest -f document.md --collection case-law`.
- **Dashboard UI** for ad-hoc partner-internal review.

**Verification:** Run `nova-os-cli knowledge search "Bill 96 termination" --collection case-law --top-k 3`. If your ingest succeeded, ranked passages come back.

**Worked example:** [`03_upload_knowledge.py`](../python/examples/03_upload_knowledge.py).

---

## 3. End-user's first chat

**Goal:** End-user (a person logged into the partner's product) sends a question and gets a response.

**What flows on the wire (Anthropic SDK pattern):**

```
1. Partner backend authenticates the end-user (their own auth — JWT, session cookie, etc.)
2. Partner backend calls Nova OS:

   POST /v1/messages
     headers: x-api-key: <partner JWT for Nova OS>
     body: {
       "model": "anthropic/claude-opus-4-7",
       "messages": [{"role": "user", "content": "What's clause 7.3 about?"}],
       "metadata": {"end_user_id": "user_42"}
     }

3. Nova OS:
   - Resolves model via cascade (per-call → per-skill → per-agent → per-employee → server-default)
   - Retrieves relevant knowledge if knowledge_bindings is set
   - Calls upstream LLM (Anthropic / OpenAI / Vertex / NebulaBlock)
   - Returns the assembled response

   → 200 {"content": [{"type": "text", "text": "Clause 7.3 covers..."}], "model_used": "anthropic/claude-opus-4-7", ...}

4. Partner backend renders the response in their UI.
```

**Surface choice:**
- **Anthropic SDK** if the partner already has Anthropic-SDK code — change `base_url` only.
- **Nova OS native SDK** for partners who want extensions (multi-model, output_type, custom tools).

**Worked example:** [`01_basic_chat.py`](../python/examples/01_basic_chat.py).

---

## 4. Custom tool — Mode A (SSE inline)

**Goal:** Agent calls a partner-implemented function mid-run; the result flows back over the same streaming connection.

**What the user sees:** Streamed text, brief pause when the agent calls `fetch_invoice`, then text continues with the invoice details inline.

**What flows on the wire:**

```
client → server : POST /v1/messages (stream:true)
server → client : event: text_delta ("Looking up invoice INV-2026-042...")
server → client : event: custom_tool_use
                  data: {"id": "tool_abc", "name": "fetch_invoice", "input": {"invoice_id": "INV-2026-042"}}
                  ⇒ partner runs fetch_invoice locally
client → server : POST /v1/messages/<msg_id>/tool_result
                  body: {"tool_use_id": "tool_abc", "content": "Invoice ... status=paid", "is_error": false}
server → client : event: tool_result_received
server → client : event: text_delta ("Invoice INV-2026-042 is paid, due 2026-03-31...")
server → client : event: message_stop
```

**Surface choice:** Mode A. Pick this when the partner is a backend service holding a long connection and the tool is fast.

**Worked example:** [`04_custom_tool_inline.py`](../python/examples/04_custom_tool_inline.py). See [`custom-tools.md`](custom-tools.md) for picking between Mode A and Mode B.

---

## 5. Custom tool — Mode B (webhook)

**Goal:** Agent calls a partner-implemented function via a signed webhook; the partner returns the result in the HTTP response.

**What flows on the wire:**

```
1. Agent run starts: POST /v1/messages (server-side)
2. Mid-run, agent decides to call fetch_invoice. Nova OS:

   POST https://partner.example.com/nova/cb/tools/fetch_invoice
     headers: X-Nova-Signature: t=<ts>,v1=<hmac_sha256(secret, ts.tool_use_id.body)>
              X-Nova-Tool-Use-Id: toolu_abc
              X-Nova-Agent-Id: invoice-bot
     body: {"tool_use_id": "toolu_abc", "tool": "fetch_invoice", "input": {...}, ...}

3. Partner WebhookRouter:
   - Verifies HMAC + timestamp window (5min replay window)
   - Dedupes by tool_use_id
   - Runs the registered handler
   - Returns: {"output": "Invoice ... status=paid", "is_error": false}

4. Nova OS:
   - Continues the agent loop with the tool result
   - Returns final assembled response to the original /v1/messages caller
```

**Surface choice:** Mode B. Pick this when the partner is HTTP-server-shaped (FastAPI / Lambda / Cloudflare Workers) or the tool runs are long enough that holding an SSE connection is impractical.

**Worked example:** [`05_custom_tool_webhook.py`](../python/examples/05_custom_tool_webhook.py).

---

## 6. Multi-model fallback fires under load

**Goal:** Primary model is rate-limited; Nova OS automatically promotes the next fallback so the user's request still succeeds.

**What flows on the wire (transparent to the partner):**

```
Employee model_config:
  answer:
    primary: anthropic/claude-opus-4-7
    fallback: [gemini/gemini-2.5-pro, openai/gpt-5]

Request comes in:
  1. Nova OS calls anthropic/claude-opus-4-7
     → 429 rate limit
  2. Nova OS catches it, calls gemini/gemini-2.5-pro instead
     → 200 OK
  3. Response includes model_used: "gemini/gemini-2.5-pro" + fallback_triggered: true
```

**What the partner observes:**

```python
resp = await c.messages.create(agent_id="legal-assistant", messages=[...])
print(resp["model_used"])           # "gemini/gemini-2.5-pro"
print(resp["fallback_triggered"])   # True
```

The end-user's chat experience is unaffected — they get a response on the same SSE stream, slightly later than the primary would have served. Partner observability dashboards can grep `fallback_triggered=true` to track upstream provider health.

**Surface choice:** Transparent. No partner code change needed beyond declaring the fallback chain in `model_config`.

**Worked example:** [`06_multi_model_fallback.py`](../python/examples/06_multi_model_fallback.py). See [`multi-model.md`](multi-model.md).

---

## 7. Long-running async job

**Goal:** Partner submits a job that takes 5-20 minutes (e.g., cross-document analysis), polls for completion, retrieves the result.

**What flows on the wire:**

```
1. Submit:
   POST /v1/managed/jobs
     body: {"agent_id": "report-builder", "input": {...}, "callback_url": "https://partner.example/cb/job-done"}
     → 202 {"job_id": "job_xyz", "status": "queued"}

2. Poll (or wait for callback):
   GET /v1/managed/jobs/job_xyz
     → 200 {"status": "running", "progress": 0.42}
   ...
   GET /v1/managed/jobs/job_xyz
     → 200 {"status": "completed", "result": {...}}

3. (Optional) callback fires when job completes:
   POST https://partner.example/cb/job-done
     body: {"job_id": "job_xyz", "status": "completed"}
```

**Surface choice:**
- **SDK with polling** for partners who don't want to expose a public callback endpoint.
- **SDK with callback URL** for partners who do — eliminates polling overhead.
- **`/v1/managed/jobs/<id>/stream`** for partners who want progress events live.

**Worked example:** [`08_async_job_long_running.py`](../python/examples/08_async_job_long_running.py).

---

## 8. Persona update — git → live

**Goal:** Partner edits an agent's system prompt or `model_config` in their git repo; changes propagate to the running Nova OS instance.

**What the user does:**

```bash
# Edit the file:
$ vim data/agents/legal-assistant.md
# (change system_prompt, save)

$ git diff data/agents/legal-assistant.md
-system_prompt: "You answer questions about contracts."
+system_prompt: "You answer questions about contracts and cite the relevant clause."

# Push to running Nova OS:
$ nova-os-cli sync ./data/
PLAN
  UPDATE agent legal-assistant
APPLY
  PUT /v1/managed/agents/legal-assistant → 200

# Or live-reload during development:
$ nova-os-cli sync --watch ./data/
[watching ./data/ for changes...]
```

The change is hot — next chat request uses the new prompt without restarting Nova OS.

**Surface choice:**
- **Shared folder + CLI sync** is the production-grade path. Git history captures every change.
- **Dashboard UI** edits work but bypass version control.

For partners who maintain agents YAML in git, the discipline is:
1. PR review on YAML changes
2. CI runs `nova-os-cli validate ./data/` (pre-deploy gate)
3. Post-merge, CI runs `nova-os-cli sync ./data/` against staging, then production

---

## 9. Lifecycle hook subscription

**Goal:** Partner subscribes to canonical agent-loop events (e.g., `tool_use_start`, `agent_completed`, `output_violation`) for observability or downstream automation.

**What flows on the wire:**

```python
# Partner registers a hook:
await c.hooks.create(
    event="agent_completed",
    url="https://partner.example/hooks/audit",
    auth={"type": "hmac_sha256", "secret_ref": "audit_hook_secret"},
)

# Now, every time an agent run completes, Nova OS POSTs:
POST https://partner.example/hooks/audit
  headers: X-Nova-Signature: t=<ts>,v1=<hmac>
  body: {
    "event": "agent_completed",
    "agent_id": "legal-assistant",
    "session_id": "sess_xyz",
    "duration_ms": 2840,
    "model_used": "anthropic/claude-opus-4-7",
    "tokens": {"input": 1024, "output": 512},
  }
```

**Available events** (canonical agent-loop signals):

| Event | When it fires |
|---|---|
| `agent_started` | Agent run begins |
| `agent_completed` | Agent run ends (success or error) |
| `tool_use_start` | Custom tool call begins |
| `tool_use_complete` | Custom tool call returns |
| `output_violation` | `output_type` validation failed (when `violation_mode: log` or `repair`) |
| `route_hint_emitted` | Brain dispatch contract emits a route_hint |

**Surface choice:** SDK. The first server-side slice ([`#177`](https://github.com/MeganovaAI/nova-os/issues/177)) lives in-memory; persistence + bus bridge tracked for a follow-up. Partners running multi-replica should pin to a single replica until persistence ships, or accept that subscriptions don't propagate across replicas.

**Worked example:** [`13_hooks_subscribe.py`](../python/examples/13_hooks_subscribe.py).

---

## 10. Bundle export → import across instances

**Goal:** Partner exports an employee + all owned agents + knowledge collections as a single `.nova-bundle.zip`, imports on another Nova OS instance (e.g., staging → prod, or migrating between regions).

**What flows on the wire:**

```python
# Source instance:
src = Client(base_url="https://nova-staging.example", api_key="...")
bundle_bytes = await src.employees.export_bundle("legal-team")   # → bytes

with open("legal-team.nova-bundle.zip", "wb") as f:
    f.write(bundle_bytes)

# Target instance:
tgt = Client(base_url="https://nova-prod.example", api_key="...")
with open("legal-team.nova-bundle.zip", "rb") as f:
    result = await tgt.employees.import_bundle(f.read())

print(result)
# {
#   "employee_id": "legal-team",
#   "agents_imported": ["legal-assistant", "contract-reviewer"],
#   "knowledge_collections_imported": ["case-law", "regulations"],
#   "skipped": []
# }
```

The bundle contains:
- The employee definition
- All owned agents
- Knowledge collections referenced by `knowledge_bindings`
- Document content for those collections (vector embeddings rebuilt on import)
- `model_config`, `web_search_config`, `custom_tools`, `route_templates` — all preserved

**Surface choice:** SDK. The bytes shape (no path coupling) makes it composable: partners can tar / encrypt / sign / version the bundle as part of their deploy pipeline.

The CLI doesn't currently wrap this; if partners want a one-liner, they can do `python -c "...export_bundle..." | scp ...` or use the SDK from a small script.

**Worked example:** [`07_bundle_export_import.py`](../python/examples/07_bundle_export_import.py).

---

## See also

- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
- [`anthropic-compat.md`](anthropic-compat.md) — endpoint-by-endpoint compat coverage
- [`multi-model.md`](multi-model.md) — model resolution cascade
- [`web-search.md`](web-search.md) — pluggable backends
- [`custom-tools.md`](custom-tools.md) — Mode A and Mode B
- [`deployment.md`](deployment.md) — production deploy shapes
