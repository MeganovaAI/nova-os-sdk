# Worked partner integrations

End-to-end examples for the three verticals Nova OS most commonly ships into. Each is a runnable, partner-side script demonstrating how to wire your application against a Nova OS instance — not server-side internals.

| Vertical | What it shows |
|---|---|
| [`legaltech/`](legaltech/) | Contract clause extraction with structured output + a Mode B custom-tool webhook for partner-side precedent lookup |
| [`healthcare/`](healthcare/) | Clinical-note triage with `output_type` JSON-schema validation + per-end-user identity passthrough for HIPAA-style isolation |
| [`finance/`](finance/) | 10-K filing diff using the async-job pattern for long documents, with `web_search_config` for live market-data enrichment |

For surface-level "how do I call this one API" examples, see the numbered scripts in [`../python/examples/`](../python/examples/).

## Common prerequisites

```bash
pip install nova-os-sdk
export NOVA_OS_URL=https://nova.your-company.example
export NOVA_OS_API_KEY=msk_live_...
```

Each example's README lists any vertical-specific extras (FastAPI for the legaltech webhook, etc.).

## Sample data

All sample inputs are **synthetic**. The legaltech MSA, the healthcare clinical note, and the finance 10-K excerpts in these scripts are constructed for documentation — they don't correspond to real contracts, real patients, or real filings. Replace them with your own data when adapting.
