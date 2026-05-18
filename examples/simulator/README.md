# Synthetic customer archetypes

Reference archetypes for the synthetic-customer simulator pattern. Each
archetype simulates a customer with hidden information that a target
AI agent must elicit through appropriate questioning.

## Quickstart

```python
from nova_os import Archetype
a = Archetype.from_yaml_path("examples/simulator/legal-immigration-pgwp.yaml")
print(a.name, a.disclosure_willingness)
```

## Archetypes shipped

| File | Vertical | Disclosure | Tests |
|---|---|---|---|
| `legal-immigration-pgwp.yaml` | Legal — Canadian immigration | cautious | intake matching with information asymmetry |
| `legal-vendor-msa-review.yaml` | Legal — contract review | guarded | multi-turn redline identification under hidden constraints |
| `medical-patient-with-hidden-history.yaml` | Medical — triage | cautious | targeted history-question elicitation |

## Running the example

The `run_eval.py` script in this directory runs all three example
archetypes against a target agent. It uses the two-instance pattern:
point it at an evaluation `nova-os` instance (separate from production),
not at production.

See the [nova-os-stack](https://github.com/MeganovaAI/nova-os-stack)
repo for the `docker-compose.eval.yaml` template that brings up the
eval instance.

### Quickstart

```bash
# 1. Bring up the eval nova-os instance per the nova-os-stack README
#    (results in nova-os listening on port 8901 with its own database
#    and gateway key).

# 2. Set env + run.
export EVAL_NOVA_BASE_URL=http://localhost:8901
export EVAL_NOVA_API_KEY=<your eval JWT or agent key>
export EVAL_TARGET_AGENT_ID=default      # optional; defaults to "default"
python examples/simulator/run_eval.py
```

Output:

- Live turn-by-turn events streamed to stdout (one line per
  simulator / target utterance).
- Per-archetype JSON transcript in `./output/<archetype>.json`
  containing the full transcript, outcome, evaluation signals,
  duration, and token usage.
- A final summary table with per-archetype outcome / turn count /
  duration / success-signal-matched.
- Exit code `0` if every archetype terminated cleanly (any outcome
  other than `"error"`); `1` if any archetype errored.

## Authoring custom archetypes

Make hidden facts consequence-bearing and specific — "I would be embarrassed
to mention this unprompted" framing keeps the simulator from leaking the
fact in turn 1. Use `disclosure_willingness: guarded` when leak-cost is
high; `cautious` is the leak-prone mid-tier.

See `python/nova_os/simulator/archetype.py` for the full schema.
