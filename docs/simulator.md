# Synthetic-customer simulator

Multi-turn evaluation pattern for production agents. The SDK ships a simulator
that plays the customer side of a chat, driven by a partner-supplied archetype
YAML. Each archetype describes a customer with hidden facts the target agent
must elicit through appropriate questioning — testing whether the agent
behaves correctly under realistic information asymmetry.

## When to use

- You're shipping a production agent (legal intake, clinical triage, customer
  service, sales, HR, tutoring) that interacts with end users across multiple
  turns
- You want repeatable, scenario-driven evaluation runs that don't depend on
  real customer traffic
- You need to detect regressions when prompting, tools, or model choice
  change

## Quickstart

### 1. Spin up an evaluation `nova-os` instance

Keep evaluation traffic OFF your production database, gateway key, and
audit log. Use the [nova-os-stack](https://github.com/MeganovaAI/nova-os-stack)
`docker-compose.eval.yaml` template:

```bash
git clone https://github.com/MeganovaAI/nova-os-stack
cd nova-os-stack
cp .env.eval.example .env.eval
# edit .env.eval — set EVAL_PG_PASSWORD, EVAL_JWT_SECRET, EVAL_ADMIN_PASSWORD,
# EVAL_OPENAI_API_KEY (recommend a low-limit prepaid key for safety)
docker-compose -f docker-compose.eval.yaml --env-file .env.eval up -d
curl http://localhost:8901/health    # confirm
```

### 2. Install the SDK

```bash
pip install nova-os
```

### 3. Run a single archetype

```python
from nova_os import Client, Archetype

eval_client = Client(base_url="http://localhost:8901", api_key="<eval-jwt>")

archetype = Archetype.from_yaml_path("path/to/your-archetype.yaml")
result = eval_client.simulate(
    target_agent_id="default",
    archetype=archetype,
    max_turns=10,
)
print(result.outcome, result.outcome_reason)
for turn in result.transcript:
    print(f"{turn.role}: {turn.content[:80]}")
```

### 4. Stream live turn events

```python
for event in eval_client.simulate(
    target_agent_id="default",
    archetype=archetype,
    max_turns=10,
    stream=True,
):
    if event.kind in ("simulator_turn", "target_turn"):
        print(f"{event.role}: {event.content}")
    elif event.kind == "outcome":
        print(f"Outcome: {event.outcome.outcome}")
```

### 5. Run the bundled example

The SDK ships a runnable CI-shaped example at `examples/simulator/run_eval.py`
that loads all three reference archetypes, runs them streaming, and writes
per-archetype JSON transcripts.

```bash
export EVAL_NOVA_BASE_URL=http://localhost:8901
export EVAL_NOVA_API_KEY=<eval-jwt>
export EVAL_TARGET_AGENT_ID=default
python examples/simulator/run_eval.py
```

## Writing your own archetype

An archetype is a YAML file describing a customer. The full schema lives at
`python/nova_os/simulator/archetype.schema.json`; minimum required fields:

```yaml
name: my-customer-archetype          # lowercase-kebab, unique per catalog
description: |
  Short description of who the customer is and what they're trying to do.
  Used to construct the simulator's system prompt.
hidden_facts:                         # >=1; do NOT volunteer; surface on direct question
  - "fact-1 the agent should elicit"
  - "fact-2 with framing of how it would naturally come up"
disclosure_willingness: cautious      # open | cautious | guarded
success_signal: "string the target agent should produce"
```

Optional fields:

- `language_register` — freeform string (e.g. `english_with_occasional_punjabi`)
- `demographic` — object with whatever shape makes sense for the vertical
- `failure_signals` — list of strings; matched against transcript per `failure_signal_match` rule
- `termination_conditions` — `{max_turns, success_signal_in_target_response, failure_signal_match}`
- `model_override` — gateway model shape (`<provider>/<name>`); wins over the SDK call's `simulator_model` arg

Three reference archetypes ship under `examples/simulator/`:

- `legal-immigration-pgwp.yaml` — legal intake under information asymmetry
- `legal-vendor-msa-review.yaml` — contract review with hidden constraints
- `medical-patient-with-hidden-history.yaml` — clinical triage with hidden risk factors

### Authoring guide — keep hidden facts hidden

The simulator may leak hidden facts even with the load-bearing "do NOT
volunteer" instruction in the system prompt — current LLMs sometimes summarize
strong system instructions into the response. Mitigations, cheapest to
most-invasive:

1. **Frame hidden facts as consequence-bearing.** "I would be embarrassed
   to mention this unprompted" framing keeps the simulator more reliably
   reticent than a bare statement.
2. **Use `disclosure_willingness: guarded`** for archetypes where leak is
   high-cost; `cautious` is the leak-prone mid-tier.
3. **Validate transcripts post-hoc.** For high-stakes evaluation, partners
   should check the simulator's adherence rather than trusting it blindly —
   the transcript JSON has the full conversation for this.
4. **Use `disclosure_willingness: open`** for archetypes where leak is
   acceptable (you're testing the agent's response quality, not its question
   sequence).

## Signal matching syntax

`success_signal` and `failure_signals` use substring matching (case-
insensitive) by default. For partners who need regex:

```yaml
success_signal: "re:lawyer matched.*(common-law|spousal)"
failure_signals:
  - "re:(refuse|decline) (the|all) redline"
  - "I give up"   # plain substring; case-insensitive
```

Regex syntax is validated at archetype-load time — a malformed pattern
raises `ArchetypeValidationError` before any `/chat` call.

## Outcome model

`simulate()` returns a `SimulationResult` with:

- `outcome: Literal["success", "failure", "timeout", "error"]`
- `outcome_reason: str` — e.g. `"success_signal_matched"`, `"max_turns_reached: 10"`, `"target_agent_error: HTTP 503"`
- `transcript: list[Turn]` — alternating simulator + target turns
- `evaluation_signals: dict[str, Any]` — `success_signal_match`, `failure_signal_matches`, `turn_count`
- `duration_ms: int`
- `tokens_used: dict[str, int]` — best-effort per-side input/output counts
- `error: str | None` — populated when `outcome == "error"`

**Runtime errors are returned as data, not raised.** The simulator catches
target / simulator failures and surfaces them via `outcome="error"`. Partners
inspect `outcome_reason` + `error` to decide how to handle a failed
simulation.

Exceptions that DO raise (before any `/chat` call):

- `ArchetypeValidationError` — archetype YAML/dict failed schema validation
- `AuthenticationError` — invalid `api_key`
- `EvalInstanceUnreachableError` — eval-instance health check failed

## Termination order

Per turn, after the target agent's response, the simulator checks
termination in exactly this order:

1. `success_signal` matched in target's response → `outcome="success"`
2. `failure_signals` matched in transcript (per `failure_signal_match: any|all`) → `outcome="failure"`
3. `max_turns` reached → `outcome="timeout"`

The first match wins.

## Two-instance pattern: why a separate `nova-os`

Running `simulate()` against your PRODUCTION nova-os instance pollutes:

- **`call_log`** — evaluation traffic shows up alongside real customer calls
- **`persist_fields`** — slot state is written/updated for synthetic conversations
- **`firewall_events`** — synthetic prompts trigger guardrails the same as real
- **Gateway cost** — eval LLM calls are billed to your production gateway key
- **Knowledge collections** — agents may retrieve from your production set
- **Per-user filesystem** — synthetic users get their own `users/<id>/` dirs
- **Audit log** — synthetic activity is preserved in your audit trail
- **Observation memory** — eval conversations may accumulate in observed memory

A second `nova-os` instance with its own PG database, gateway key, and
data volume cleanly segregates all of this — at the cost of one extra
process (~57 MB binary, smallest VM tier on any major cloud).

See [nova-os-stack/docker-compose.eval.yaml](https://github.com/MeganovaAI/nova-os-stack/blob/main/docker-compose.eval.yaml)
for the template.

## Tradeoffs vs single-turn rubric evaluation

- **Single-turn rubric evaluation** (e.g. Harvey AI's open Legal Agent
  Benchmark, BigLaw Bench) — partner ships an instruction + materials; agent
  produces work product; binary rubric grade. Best for evaluating answer
  quality on tasks where the question is well-formed.
- **Multi-turn synthetic-customer simulation** (what this SDK ships) —
  partner ships an archetype; simulator plays the customer; transcript
  captures the conversation. Best for evaluating the agent's question
  sequence, information elicitation, and ability to handle disclosure
  gradients.

The two patterns are complementary, not competing. Production agent
evaluation typically benefits from both.

## What's NOT shipped in v1

- **Multi-simulator N-way conversations** — only 2-party (simulator + target). 3-party (e.g. simulator + target + arbiter) is future SDK work.
- **Real-time HITL** overriding the simulator mid-conversation — out of scope.
- **LLM-authored archetypes** — partner supplies the YAML.
- **Archetype marketplace / leaderboards** — partner-side concern.
- **Persona-drift-aware scoring** — research-grade analysis on top of the
  transcript; partners run their own post-hoc.
- **Cost-budget enforcement inside the loop** — handled by the eval-instance
  gateway key's prepaid limit (see two-instance pattern above).
- **Multi-turn turn-by-turn rubric grading** — transcript is returned; partner
  runs whatever grading they want post-hoc.

## Troubleshooting

### Simulator volunteers hidden facts in turn 1

The "do NOT volunteer" instruction is load-bearing but not perfect with
current LLMs. See [Authoring guide — keep hidden facts hidden](#authoring-guide--keep-hidden-facts-hidden).

### `EvalInstanceUnreachableError` on first call

The eval instance isn't reachable at the configured `base_url`. Check:

- Is `docker-compose -f docker-compose.eval.yaml up -d` running?
- Does `curl http://<eval-base-url>/health` succeed?
- Is `EVAL_NOVA_API_KEY` set and valid for the eval instance (not production)?

### `outcome="error"` with `outcome_reason="target_agent_error: HTTP 404"`

Target agent doesn't exist on the eval instance. Either register it
(`POST /v1/agents`) or seed the eval instance with the agents you want to
evaluate. The eval instance starts empty — fixtures don't carry over from
production.

### `outcome="error"` with `outcome_reason="simulator_error: ..."`

Simulator LLM call failed twice (1 retry + 1 attempt). Check the
simulator's configured model is reachable via the eval gateway key. Default
simulator model is `anthropic/claude-haiku-4-5` — if that's not on your
gateway, set `simulator_model="..."` on the `simulate()` call or in the
archetype's `model_override`.

## API reference

Full API: `python/nova_os/simulator/`. Public entry points:

- `nova_os.Client.simulate(target_agent_id, archetype, *, stream=False, max_turns=10, simulator_model="anthropic/claude-haiku-4-5", simulator_system_prompt=None, metadata=None, target_api_key=None) -> SimulationResult | Iterator[TurnEvent]`
- `nova_os.Client.async_simulate(...) -> SimulationResult` (async variant for partners already in an event loop)
- `nova_os.Archetype` — Pydantic model + JSON Schema for archetype YAML
- `nova_os.Archetype.from_yaml_path(path)` / `from_dict(d)` — loaders with validation
