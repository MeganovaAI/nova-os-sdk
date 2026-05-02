# Legaltech — contract clause extraction

End-to-end worked example: a legal-tech partner ingests an MSA (Master Services Agreement) text, has Nova OS extract clauses by type with risk flags, and lets the agent call back to the partner's clause-precedent database via a Mode B webhook.

## What this demonstrates

- **Structured output (`output_type`)** — the agent's reply is validated against a JSON Schema before it leaves Nova OS, so the partner gets a typed `{clauses: [...]}` object instead of free-text it has to re-parse.
- **Mode B custom-tool webhook** — when the agent decides it needs to look up precedent for a clause, Nova OS POSTs a signed JSON payload to the partner's webhook. The partner runs the lookup against its own clause DB and returns the result. This is the integration pattern most legal-tech partners use because the precedent corpus is partner IP and never leaves their network.
- **Per-employee model cascade** — answer model on `claude-opus-4-7` for nuanced legal reasoning; skill model on `gemini-2.5-flash` for the cheaper extraction sub-tasks.

## Files

| File | Role |
|---|---|
| `contract_clause_extraction.py` | Main partner-side script: creates the agent, sends the MSA, prints the structured output |
| `webhook_server.py` | FastAPI server hosting the `lookup_clause_precedent` tool callback (Mode B) |
| `sample_msa.txt` | Synthetic MSA text used as input |

## Run

In one terminal, start the partner's webhook server:

```bash
pip install nova-os-sdk fastapi uvicorn
export NOVA_CB_SECRET=$(openssl rand -hex 32)
uvicorn webhook_server:app --port 8080
```

In another terminal, run the extraction with the matching secret + your Nova OS credentials:

```bash
export NOVA_OS_URL=https://nova.your-company.example
export NOVA_OS_API_KEY=msk_live_...
export NOVA_CB_URL=https://partner.example/nova/cb   # public URL of the webhook server above
export NOVA_CB_SECRET=<same value as above>
python contract_clause_extraction.py
```

You'll see the agent extract clauses, call back to the precedent-lookup tool one or more times, and finally print a JSON object listing every clause with its type, risk flag, and precedent score.

## Adapting to your data

Replace `sample_msa.txt` with your contract corpus. The agent's output schema is declared inline in `contract_clause_extraction.py` — extend it with whatever clause types and risk dimensions your reviewers care about. For partner-side precedent lookup, swap the in-memory dict in `webhook_server.py` for a real query against your clause DB.
