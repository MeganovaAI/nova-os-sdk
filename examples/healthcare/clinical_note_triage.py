"""Healthcare — clinical-note triage with structured output + per-patient isolation.

End-to-end partner-side script:
    1. Creates a `clinical-triage` agent whose reply is validated against a
       JSON-schema contract — partners receive a typed `{urgency, action, red_flags}`
       object every time, no free-text parsing.
    2. Sends a synthetic clinical note. The `X-End-User` header carries the
       partner's stable internal patient identifier so the agent's
       observational memory is scoped per-patient (HIPAA-style minimum-necessary
       isolation — patient A's conversation history never bleeds into B's).
    3. Prints the validated triage decision.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python clinical_note_triage.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from nova_os import Client


TRIAGE_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["patient_id", "urgency", "suggested_action", "red_flags", "rationale"],
    "properties": {
        "patient_id": {"type": "string"},
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"],
        },
        "suggested_action": {
            "type": "string",
            "enum": [
                "self_care_education",
                "schedule_pcp_followup",
                "schedule_urgent_followup",
                "send_to_urgent_care",
                "send_to_emergency",
                "telephone_advice_line",
            ],
        },
        "red_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Standardised flag tokens (e.g. chest_pain_radiating, diaphoresis)",
        },
        "rationale": {
            "type": "string",
            "description": "One-paragraph clinical rationale tying flags to action",
        },
        "icd10_suggested": {
            "type": "array",
            "items": {"type": "string", "pattern": "^[A-Z][0-9]{2}(\\.[0-9A-Z]{1,4})?$"},
            "description": "ICD-10 codes consistent with the note (advisory only)",
        },
    },
    "additionalProperties": False,
}


SAMPLE_NOTE_PATH = Path(__file__).with_name("sample_note.txt")


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    note_text = SAMPLE_NOTE_PATH.read_text(encoding="utf-8")

    # Stable per-patient identifier. NEVER use patient name or other PHI here —
    # map your internal chart ID externally and pass only the opaque token.
    patient_id = "PT-2026-0942"

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create the digital employee. Answer model on Opus for clinical
        #    reasoning; skill model on Flash for the schema-validation retry.
        await c.employees.create(
            id="triage-clinician",
            display_name="Triage Clinician",
            model_config={
                "answer": {
                    "primary": "anthropic/claude-opus-4-7",
                    "fallback": ["gemini/gemini-2.5-pro"],
                },
                "skill": {
                    "primary": "gemini/gemini-2.5-flash",
                    "fallback": ["anthropic/claude-haiku-4-5"],
                },
            },
        )

        # 2. Attach the triage agent. `output_type.violation_mode=repair` means
        #    if the model's first reply doesn't match TRIAGE_SCHEMA, Nova OS
        #    re-prompts once with the schema in the system prompt before
        #    returning the result. Better than a 422 in a clinical workflow.
        await c.agents.create(
            id="clinical-triage",
            type="skill",
            owner_employee="triage-clinician",
            description=(
                "Triages clinical notes into a structured urgency + suggested-action "
                "decision. Outputs are validated against a hard JSON Schema contract."
            ),
            output_type={"schema": TRIAGE_SCHEMA, "violation_mode": "repair"},
            instructions=(
                "You are a clinical triage decision-support tool. Read the note, "
                "identify red flags using standard clinical-decision keywords, and "
                "produce a triage decision. Be conservative — when in doubt, escalate. "
                "Never fabricate findings not in the note. The patient_id field MUST "
                "match the X-End-User header value passed by the partner."
            ),
        )

        # 3. Send the note. The patient identifier flows on the request as
        #    X-End-User so the agent's observational memory is scoped per
        #    patient — A's prior visits never bleed into B's reasoning.
        resp = await c.messages.create(
            agent_id="clinical-triage",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Patient ID: {patient_id}\n\n"
                        f"Clinical note (deidentified):\n\n{note_text}\n\n"
                        f"Produce a triage decision."
                    ),
                }
            ],
            metadata={"agent_id": "clinical-triage"},
            extra_headers={"X-End-User": patient_id},
        )

        # 4. Validated structured output — partners can json.loads directly.
        decision = resp.structured_output if hasattr(resp, "structured_output") else resp
        print("Triage decision:")
        print(json.dumps(decision, indent=2))

        # 5. Optional cleanup for dev loops.
        await c.agents.delete("clinical-triage")
        await c.employees.delete("triage-clinician")


if __name__ == "__main__":
    asyncio.run(main())
