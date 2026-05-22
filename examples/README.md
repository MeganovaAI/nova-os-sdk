# SDK examples

Runnable scripts that demonstrate how to call the `libraos-sdk` surface. Pick by **SDK feature**, not by use case — for end-to-end vertical workflows (contract extraction, clinical-note triage, 10-K diff, …) see the separate cookbook repo instead.

| Looking for | Go to |
|---|---|
| "How do I call this API?" | This directory + [`../python/examples/`](../python/examples/) |
| "How do I build a contract-extraction app?" | [`libraos/cookbook`](https://github.com/libraos/cookbook) |

## Contents

| Path | What it shows |
|---|---|
| [`simulator/`](simulator/) | Running the offline conversation simulator (`client.simulate(...)`) for evaluation and regression harnesses |

The numbered, per-resource snippets (`messages_create.py`, `agents_list.py`, etc.) live in [`../python/examples/`](../python/examples/).

## Common prerequisites

```bash
pip install libraos-sdk
export NOVA_OS_URL=https://nova.your-company.example
export NOVA_OS_API_KEY=msk_live_...
```

## Why no `legaltech/`, `healthcare/`, `finance/` here?

Those moved to [`libraos/cookbook`](https://github.com/libraos/cookbook) (seed commit imports them verbatim). Reason: they compose the SDK with surrounding partner-side code (webhook receivers, sample documents, structured-output validators), and mixing that with SDK call-pattern reference confused partners trying to learn just the SDK surface. The split matches the [`anthropics/claude-cookbooks`](https://github.com/anthropics/claude-cookbooks) pattern.
