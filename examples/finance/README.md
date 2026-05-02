# Finance — 10-K filing diff with async-job pattern

End-to-end worked example: a financial-services partner submits two consecutive 10-K filing excerpts (this year vs. last year), the agent identifies material changes and risk flags, and returns a structured analyst-ready summary. Because filings are long and the analysis takes minutes, this uses Nova OS's async-job pattern — submit, poll, retrieve.

## What this demonstrates

- **Async jobs (`c.jobs.create` / `c.jobs.get`)** — the partner submits the job, gets a `job_id` back immediately, polls until `status == "complete"`, and reads the structured result. Avoids 30+ second HTTP timeouts on long analyses.
- **`web_search_config` for live enrichment** — the agent is allowed to issue a small budget of web-search calls during analysis (e.g., look up the current ticker price, recent material 8-K filings) and cite each web source inline alongside the user-provided text.
- **Structured output + a "material change" rubric** — the schema constrains the agent to a fixed taxonomy (revenue, leverage, segment-mix, going-concern, etc.) so downstream analyst tooling can pivot the result reliably.

## Files

| File | Role |
|---|---|
| `sec_filing_diff.py` | Main partner-side script: submits the async job, polls, prints the structured diff |
| `sample_10k_2025.txt` | Synthetic FY2025 risk-factors excerpt |
| `sample_10k_2026.txt` | Synthetic FY2026 risk-factors excerpt with 3 material changes |

## Run

```bash
pip install nova-os-sdk
export NOVA_OS_URL=https://nova.your-company.example
export NOVA_OS_API_KEY=msk_live_...
python sec_filing_diff.py
```

You'll see the script submit the job, poll status every 5 seconds for ~1-2 minutes, and finally print:

```json
{
  "ticker": "ACME",
  "comparison_period": "FY2025 vs FY2026",
  "material_changes": [
    {
      "category": "leverage",
      "summary": "Long-term debt increased 38% YoY; new covenant added requiring..."
    },
    ...
  ],
  "overall_risk_delta": "elevated",
  "web_citations": [...]
}
```

## Adapting to your data

Replace the two sample text files with extracted Item 1A (Risk Factors) sections from your filing corpus. For larger jobs (full 10-K, multiple companies), upload the source text via `c.documents.upload` and reference the resulting document IDs in the job input — Nova OS will retrieve from its knowledge index instead of stuffing everything into the prompt.

For sector-specific work, swap the `material_changes.category` enum to match what your analysts actually pivot on (e.g., for banks: NIM, deposit-mix, CRE concentration; for SaaS: ARR, NRR, gross retention).
