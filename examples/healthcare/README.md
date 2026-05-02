# Healthcare — clinical-note triage

End-to-end worked example: a healthcare partner sends a clinical-note text to a triage agent and gets back a structured triage decision (urgency level, suggested action, red flags).

## What this demonstrates

- **`output_type` JSON-schema validation** — the agent's reply is validated server-side against a contract before it leaves Nova OS. Partners' downstream code (EHR write-back, alerting, dashboards) gets a typed object every time, with no probabilistic free-text parsing.
- **Per-end-user identity passthrough (`X-End-User`)** — every call carries the partner's internal patient identifier on the request. Nova OS scopes the agent's observational memory to that identity so a triage decision for patient A never bleeds into patient B's session — a hard requirement for HIPAA-style minimum-necessary access.
- **Three violation modes for output validation** — `error` (reject + 422), `log` (return as-is + telemetry), `repair` (one bounded retry with the schema in the system prompt). The example uses `repair` because in clinical settings you'd rather a slightly slower second pass than a 422 the partner has to re-prompt.

## Files

| File | Role |
|---|---|
| `clinical_note_triage.py` | Main partner-side script: registers the agent, sends a synthetic note, prints the validated triage decision |
| `sample_note.txt` | Synthetic deidentified clinical note used as input |

## Run

```bash
pip install nova-os-sdk
export NOVA_OS_URL=https://nova.your-company.example
export NOVA_OS_API_KEY=msk_live_...
python clinical_note_triage.py
```

You'll see Nova OS produce a structured JSON object like:

```json
{
  "patient_id": "PT-2026-0942",
  "urgency": "high",
  "suggested_action": "send_to_emergency",
  "red_flags": ["chest_pain_radiating", "diaphoresis", "history_of_cad"],
  "rationale": "..."
}
```

## Adapting to your data

Replace `sample_note.txt` with a real (or representative) clinical-note format from your EHR. Extend the schema in `clinical_note_triage.py` to add fields your downstream systems require (ICD-10 codes, suggested specialty, minutes-to-action SLA, etc.). The `X-End-User` value should be your stable internal patient identifier — never the patient's name or any other PHI element. Map it externally to the chart so the agent's memory is reproducible per patient without leaking PHI into Nova OS's logs.

## A note on data handling

This example sends synthetic clinical text through Nova OS. In a real deployment, the partner is responsible for ensuring the LLM provider Nova OS routes to (declared in `model_config`) is HIPAA-compliant for them — Anthropic, OpenAI, Google all offer BAA terms but require explicit enrollment. Verify with your compliance team before processing real PHI.
