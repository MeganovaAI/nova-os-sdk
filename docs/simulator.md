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
pip install libraos-sdk
```

### 3. Run a single archetype

```python
from libraos import Client, Archetype

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
`python/libraos/simulator/archetype.schema.json`; minimum required fields:

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
- `drift_alert_threshold` — float `0.0`–`1.0`; persona-drift alert threshold for this archetype (default `0.15`). See [Threshold tuning](#threshold-tuning)
- `drift_probes` — list of probe questions for drift `probe_mode="active"`. See [Active probe injection](#optional-active-probe-injection)

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
- `drift: DriftMetric | None` — persona-drift measurement, see [Persona drift](#persona-drift). `None` only when monitoring was disabled

**Runtime errors are returned as data, not raised.** The simulator catches
target / simulator failures and surfaces them via `outcome="error"`. Partners
inspect `outcome_reason` + `error` to decide how to handle a failed
simulation.

Exceptions that DO raise (before any `/chat` call):

- `ArchetypeValidationError` — archetype YAML/dict failed schema validation
- `AuthenticationError` — invalid `api_key`
- `EvalInstanceUnreachableError` — eval-instance health check failed

## Persona drift

`simulate()` tells you what the **agent** did. It does not tell you whether the
synthetic customer was still the customer you authored. Kenneth Li's
persona-drift work ([arXiv 2402.10962](https://arxiv.org/html/2402.10962v1))
shows that an LLM told to hold a persona decays toward its default assistant
behaviour within roughly eight turns, as attention on the system prompt fades.
On a 10-turn archetype that is not a corner case — it is the second half of
every run.

The failure is silent and it inverts your result. A run can match its
`success_signal` on turn 8 while the simulator stopped playing a guarded
applicant on turn 5 and started volunteering everything. The outcome says
`success`; what you actually measured was your agent against a different,
easier persona. **Drift is a validity check on the evaluation, not a score for
the agent under test.**

Every `simulate()` call now measures it. Scoring is deterministic, runs offline,
and costs no extra model calls.

```python
result = c.simulate(target_agent_id="legal-assistant", archetype=archetype)

print(result.drift.score)            # 0.0 = perfect retention, 1.0 = complete drift
print(result.drift.alert_triggered)  # score > threshold
print(result.drift.threshold)        # 0.15 default; archetype can override

for t in result.drift.per_turn:
    if t.score:
        print(t.turn_index, round(t.score, 2), t.evidence)
# 8 0.84 ["assistant-service marker: 'is there anything else i can help'"]
```

### Reading the result

| field | meaning |
| --- | --- |
| `score` | aggregate drift, `0.0`–`1.0` |
| `threshold` / `alert_triggered` | the threshold applied, and `score > threshold` |
| `per_turn` | one `DriftTurn` per probe point: `score`, `components`, `evidence`, `excerpt` |
| `first_drift_turn_index` | transcript index where drift first became visible — plot this across a corpus to get your own version of Li's decay curve |
| `baseline_turn_index` | the in-character turn everything was compared against |
| `measured` | **check this before aggregating.** A run too short to score still returns a `DriftMetric` with `score=0.0`; that zero means *not measured*, not *no drift* |

```python
scored = [r.drift.score for r in results if r.drift and r.drift.measured]
```

### Any transcript, not just simulator output

`measure_drift` is a pure function. Point it at archived transcripts, at another
harness's logs, at a hand-written conversation — anything with two speakers.

```python
drift = c.measure_drift(
    transcript=[
        {"role": "user", "content": "I need help with my permit."},
        {"role": "assistant", "content": "When does it expire?"},
        {"role": "user", "content": "As an AI language model, I don't have a permit."},
    ],
    archetype=archetype,          # Archetype | dict | path to YAML
    method="kenneth-li-probe",
)
```

Accepted shapes: a `SimulationResult`, a list of `Turn`, `{"role", "content"}`
dicts (Anthropic content blocks included), `(role, content)` pairs, objects with
`.role`/`.content`, or a bare list of strings assumed to alternate persona-first.

The persona side is resolved from the role names — `simulator`, `persona`,
`customer`, `applicant`, `patient`, then `user`. For anything else, name it:
`persona_role="client"`. If the persona side cannot be identified the call
raises rather than guessing, because scoring the wrong speaker silently would be
worse than failing.

> **One case auto-detection cannot get right.** In a bare `user`/`assistant`
> log, `user` is assumed to be the persona. That is correct for a log recorded
> from the target agent's point of view and **wrong** for one recorded from the
> persona-playing model's own point of view, where the persona is the
> `assistant` — and nothing in the data distinguishes them. Pass
> `persona_role="assistant"` for the latter, and check
> `drift.notes["persona_role"]` to confirm which side was scored.

### Streaming: `drift_alert`

The streaming variant emits **one** `drift_alert` event the first time the
running score crosses the threshold mid-loop, so a long or expensive run can be
cut short as soon as the persona is gone.

```python
for event in c.simulate(target, archetype, max_turns=20, stream=True):
    if event.kind == "drift_alert":
        print(f"persona lost at turn {event.turn_index}: {event.drift.score:.2f}")
        break   # transient simulator agent is still cleaned up
    elif event.kind == "outcome":
        print(event.outcome.outcome, event.outcome.drift.score)
```

> **Upgrade note.** `drift_alert` is a new `TurnEvent.kind`. It only ever fires
> on a drifted run, so consumers that ignore unknown kinds are unaffected — but
> code asserting an exhaustive set of kinds must add it, or opt out with
> `drift=DriftOptions(alert=False)`.

### Threshold tuning

Default is `0.15`. Set it per-archetype in the YAML, per-call with
`DriftOptions(threshold=...)`, or leave it alone.

```yaml
drift_alert_threshold: 0.10   # tighter than the 0.15 default
```

Precedence: `DriftOptions(threshold=...)` → `archetype.drift_alert_threshold` →
`0.15`.

Pick it from **what the archetype's hidden facts are for**, not from taste:

- **`0.05`–`0.10` — the disclosure gradient IS the test.** The archetype exists
  to check whether the agent asks the right questions in the right order, so a
  simulator that starts volunteering has destroyed the experiment even if the
  register never slips. `examples/simulator/legal-immigration-pgwp.yaml` ships
  at `0.10` for exactly this reason. Expect occasional alerts on runs a human
  would pass; that is the correct trade at this setting.
- **`0.15` (default) — general multi-turn behaviour.** Tuned so a single
  markdown-formatted turn or one stray "I suggest…" never alerts, while any
  outright character break always does.
- **`0.25`–`0.40` — long runs, or `open` personas.** Above ~15 turns some
  register decay is unavoidable with current models; raise the floor rather than
  drown in alerts. Same for `open` archetypes, where you are grading answer
  quality and the persona is scaffolding.
- **Never `0.0`.** It alerts on the weakest signal the scorer emits, including
  a customer who bullet-points their documents.

Calibrate against your own corpus before trusting any number: run 20 archetypes
you consider clean, look at the score distribution, and set the threshold above
its tail. `per_turn[].evidence` names the exact phrase that fired, so
disagreements are cheap to adjudicate.

Two other knobs:

- `DriftOptions(probe_every=N)` — how often the persona is scored. Default `2`
  means half its turns are sampled; `1` scores every turn (more sensitive, more
  exposed to lexical false positives).
- `DriftOptions(enabled=False)` — turn measurement off entirely.

### Optional: active probe injection

By default the metric reads the persona's own turns — zero extra calls. Li's
method probes the persona directly, which the SDK supports opt-in:

```python
result = c.simulate(target, archetype, drift=DriftOptions(probe_mode="active"))
```

At each cadence point the simulator is asked one out-of-band question. **The
probe never reaches the target agent and is never replayed into the persona's
own history** — measuring must not alter the trajectory being graded. The answer
*is* appended to `result.transcript`, tagged `metadata["drift_probe"] = True`,
so the score stays reproducible offline from the stored result.

Cost: one extra simulator call per probe, accumulated into the `simulator_*`
token counters. Two consequences to plan for: the transcript no longer strictly
alternates simulator/target, and probe turns are not emitted as stream events.

Supply probes per archetype, or let the SDK use its built-ins:

```yaml
drift_probes:
  - "Before we carry on — in your own words, who are you and what brought you here?"
  - "Is there anything on your mind you have not mentioned yet?"
```

Keep them **persona-agnostic**. A probe that restates the description re-primes
the model's attention on the persona and erases the drift you are trying to
measure — the built-in set is deliberately generic for this reason.

### What the metric detects — and what it does not

Scoring is lexical and deterministic, so it can run in CI with no model and no
server. Each probe point is scored on four signals combined with a noisy-OR;
the transcript score is `0.5 * max(per-turn) + 0.5 * mean(per-turn)`, which
guarantees that **any single complete character break scores ≥ 0.5 no matter how
long the run is**. A plain mean would dilute one break in a 20-probe run to
0.05 — the exact failure this metric exists to catch.

| signal | weight | fires on |
| --- | --- | --- |
| `character_break` | 1.0 | model self-reference ("as an AI", "my system prompt") at 1.0; assistant-service framing ("how can I help you") at 0.8 |
| `disposition_violation` | 0.9 | behaviour contradicting `disclosure_willingness` + `hidden_facts` |
| `advisory_inversion` | 0.6 | the help-seeker giving advice, gated on second-person dominance |
| `format_break` | 0.2 | markdown structure the simulator prompt forbids |

`disposition_violation` is direction-sensitive, which is the part worth
understanding before you read a score:

- `cautious` — disclosure is drift only when *volunteered*; answering a direct
  question is exactly what the archetype asks for and scores zero.
- `guarded` — disclosure must be both prompted *and* preceded by sustained
  questioning; a fact dumped on the first question is drift.
- `open` — disclosure is never drift. The inverse is: an open persona that turns
  evasive has drifted.

**Not detected.** Treat a low score as "no drift *of the kinds this detects*",
not as proof of persona fidelity:

- semantic drift that preserves register — a persona that still sounds like a
  customer but contradicts its own biography, dates, or stated goal
- paraphrased hidden-fact leakage that shares few surface tokens with the
  archetype text (detection needs ≥60% content-word overlap)
- tone, affect, and emotional-stance drift
- non-English transcripts — the marker sets and stopword list are English-only,
  so a Punjabi or Mandarin persona will under-score
- drift on turns the cadence did not sample (use `probe_every=1` for full
  coverage)

A model-graded method can be added under a new `method=` identifier without
changing any existing signature; `method` is recorded on every `DriftMetric` so
stored results stay attributable.

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
- **Model-graded persona-drift scoring** — the shipped metric (see
  [Persona drift](#persona-drift)) is deterministic and lexical so it can run in
  CI offline. It does not catch semantic drift that preserves register, and it
  is English-only. An LLM-judge method would, at the cost of a model call per
  probe; it would register under a new `method=` identifier.
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

Full API: `python/libraos/simulator/`. Public entry points:

- `libraos.Client.simulate(target_agent_id, archetype, *, stream=False, max_turns=10, simulator_model="anthropic/claude-haiku-4-5", simulator_system_prompt=None, metadata=None, target_api_key=None, target_model=None, drift=None) -> SimulationResult | Iterator[TurnEvent]`
- `libraos.Client.async_simulate(...) -> SimulationResult` (async variant for partners already in an event loop)
- `libraos.Client.measure_drift(transcript, archetype, *, method="kenneth-li-probe", threshold=None, probe_every=2, persona_role=None) -> DriftMetric` — standalone, offline, no HTTP call
- `libraos.measure_drift(...)` — the same function, importable without a client
- `libraos.DriftOptions` — per-call drift config (`enabled`, `probe_every`, `threshold`, `method`, `probe_mode`, `probes`, `alert`)
- `libraos.DriftMetric` / `libraos.DriftTurn` — result types
- `libraos.Archetype` — Pydantic model + JSON Schema for archetype YAML
- `libraos.Archetype.from_yaml_path(path)` / `from_dict(d)` — loaders with validation

## Work-product evaluation (rubric grading)

Where `simulate()` scores a *trajectory* (multi-turn behaviour), `evaluate()`
scores a *static work product* against a checklist — the Harvey LAB rubric
shape. A rubric case pairs an instruction + matter with a list of pass/fail
criteria; grading uses the **Harvey 100% threshold** (`task_passed` is true only
when every *required* criterion passes).

```python
from libraos import Client, RubricCase

case = RubricCase.from_yaml_path("examples/rubrics/legal-vendor-msa-review.yaml")
c = Client(base_url="https://nova-eval.partner.com", api_key="…", timeout=280)

result = c.evaluate(target_agent_id="legal-assistant", case=case)
print(result.task_passed)   # False — a required criterion missed
print(result.pass_rate)     # 0.80 — 4/5 criteria (soft signal, includes optional)
for cr in result.criteria:
    print(cr.passed, cr.required, cr.criterion)
```

Under the hood `evaluate()` makes two calls: it asks the **target** agent to
produce the work product, then asks a **judge** agent for a PASS/FAIL verdict
on each criterion. Point the judge at a stronger model with `judge_agent_id=` /
`judge_model=` if you want producer and grader separated.

**Timeout:** work-product generation on a planner agent can take minutes — set
`Client(..., timeout=280)` (see the multi-agent note above).

**Rubric YAML** (`RubricCase`):

```yaml
case_id: my-case-v1
practice_area: commercial-contracts
instruction: |
  Review the MSA and identify every issue a senior lawyer would flag.
matter:
  context: |            # v1 passes context (and doc paths, as references) inline;
    Section 8 …         # binary document upload is a follow-up.
expected_work_product_shape: legal-memo   # or redline | recommendation-letter | intake-form | other
rubric:
  - criterion: "flags the uncapped liability in Section 8"
    required: true
  - criterion: "notes the auto-renewal window"
    required: false      # at least one criterion must be required
```

Load a directory of cases with `load_rubric_pack("examples/rubrics")`.

### Composing trajectory + work-product evals

```python
sim = c.simulate(target, archetype, max_turns=10)          # how it behaves
rubrics = [c.evaluate(target, case) for case in load_rubric_pack("immigration")]  # what it produces
passed = sum(r.task_passed for r in rubrics) / len(rubrics)
print(f"trajectory={sim.outcome}  rubric pass rate={passed:.0%}")
```

## Authoring a vertical pack

A **pack** lets a vertical keep its own archetype + rubric catalog in its own
repo, without forking the SDK or bloating `examples/`. Layout:

```
my-pack/
├── pack.yaml          # name, version, requires_sdk
├── archetypes/*.yaml  # loaded as Archetype
├── rubrics/*.yaml     # loaded as RubricCase
└── compliance/
    └── overlay.yaml   # optional: vertical-specific archetype fields
```

```python
from libraos.simulator import load_pack, detect_pack_collisions

pack = load_pack(path="./my-pack")             # local dir
# pack = load_pack(name="equaldocs-immigration")  # pip-installed (entry point)
# pack = load_pack(git="https://github.com/EqualDocs/immigration-pack")

pack.archetypes                 # ['reference-applicant', ...]
archetype = pack.get("reference-applicant")     # validated Archetype
pack.get_extensions("reference-applicant")      # {'jurisdiction': 'ON', ...}
rubric = pack.get_rubric("reference-msa-review")

# refuse ambiguous ids when merging multiple verticals
detect_pack_collisions([pack_a, pack_b])        # {'pgwp-applicant': ['a', 'b']}
```

### Extension fields (the anti-bloat primitive)

The base `Archetype` schema is strict (`extra="forbid"`) and vertical-agnostic.
A pack declares its own fields in `compliance/overlay.yaml`; loading validates
each archetype against **base + overlay**, and the extra values are read via
`pack.get_extensions(name)` — the base archetype stays clean, so the SDK schema
never grows a field per vertical.

```yaml
# compliance/overlay.yaml
extension_fields:
  required:
    - jurisdiction:
        type: string
        enum: ["ON", "QC", "BC", "AB"]   # ⚠ quote these — YAML parses ON/OFF/YES/NO as booleans
  optional:
    - retainer_template_ref:
        type: string
        pattern: '^retainer-v\d+$'
```

Supported overlay checks: `type` (string / boolean / integer / number),
`enum`, `pattern`. A `requires_sdk: ">=1.0.0"` in `pack.yaml` is enforced at
load time against the installed SDK version.

> **YAML boolean gotcha:** unquoted `ON` / `OFF` / `YES` / `NO` parse as
> booleans under YAML 1.1. Quote string enum values (e.g. Canadian provinces
> `"ON"`) in both the overlay and the archetypes, or they'll fail the string
> check. The reference pack under `examples/simulator/reference-pack/` shows the
> correct quoting.

See `examples/simulator/reference-pack/` for a complete working pack.
