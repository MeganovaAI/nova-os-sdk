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

## Authoring custom archetypes

Make hidden facts consequence-bearing and specific — "I would be embarrassed
to mention this unprompted" framing keeps the simulator from leaking the
fact in turn 1. Use `disclosure_willingness: guarded` when leak-cost is
high; `cautious` is the leak-prone mid-tier.

See `python/nova_os/simulator/archetype.py` for the full schema.
