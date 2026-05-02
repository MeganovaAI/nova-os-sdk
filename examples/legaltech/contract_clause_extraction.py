"""Legaltech — contract clause extraction with custom-tool callback.

End-to-end partner-side script:
    1. Creates a `legal-clause-extractor` employee with a model cascade
       (Opus answer, Flash skill) and a Mode B custom tool that the agent
       can call to look up precedent in the partner's own clause DB.
    2. Submits an MSA text. Nova OS routes it through the agent, which
       extracts clauses, calls back to the precedent-lookup tool one or
       more times, and returns a structured JSON object.
    3. Pretty-prints the validated structured output.

Pair with `webhook_server.py` (FastAPI) running on `${NOVA_CB_URL}` so the
precedent-lookup tool callback has somewhere to land.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...
    export NOVA_CB_URL=https://partner.example/nova/cb
    export NOVA_CB_SECRET=<your webhook secret>

Run::

    python contract_clause_extraction.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from nova_os import Client


CLAUSE_OUTPUT_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["contract_id", "clauses"],
    "properties": {
        "contract_id": {"type": "string"},
        "clauses": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "text", "risk_flag"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "limitation_of_liability",
                            "indemnification",
                            "termination",
                            "ip_assignment",
                            "confidentiality",
                            "payment_terms",
                            "warranty",
                            "force_majeure",
                            "other",
                        ],
                    },
                    "text": {"type": "string", "description": "Verbatim clause excerpt"},
                    "risk_flag": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                    "rationale": {"type": "string"},
                    "precedent_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "From the partner-side lookup_clause_precedent callback",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


CUSTOM_TOOLS: list[dict] = [
    {
        "name": "lookup_clause_precedent",
        "description": (
            "Query the partner's clause-precedent database for a similarity score "
            "and one example precedent text. Use this when you have extracted a "
            "clause and want to score how unusual its phrasing is."
        ),
        "input_schema": {
            "type": "object",
            "required": ["clause_text", "clause_type"],
            "properties": {
                "clause_text": {"type": "string"},
                "clause_type": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "callback_url": os.environ.get("NOVA_CB_URL", "https://partner.example/nova/cb"),
    },
]


SAMPLE_MSA_PATH = Path(__file__).with_name("sample_msa.txt")


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    msa_text = SAMPLE_MSA_PATH.read_text(encoding="utf-8")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create the digital employee with a multi-tier model cascade.
        await c.employees.create(
            id="contracts-reviewer",
            display_name="Contracts Reviewer",
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

        # 2. Attach the extractor agent. Structured output + custom-tool wiring
        #    are agent-level — every chat hits the same contract.
        await c.agents.create(
            id="legal-clause-extractor",
            type="skill",
            owner_employee="contracts-reviewer",
            description=(
                "Extracts clauses from contract text into a structured JSON "
                "object, flagging risky phrasings against precedent."
            ),
            output_type={"schema": CLAUSE_OUTPUT_SCHEMA, "violation_mode": "repair"},
            custom_tools=CUSTOM_TOOLS,
        )

        # 3. Send the MSA. The agent will call lookup_clause_precedent zero or
        #    more times via the Mode B webhook before producing its final reply.
        resp = await c.messages.create(
            agent_id="legal-clause-extractor",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Contract ID: MSA-2026-042\n\n"
                        f"Extract every operative clause from the agreement below. "
                        f"For each one, call lookup_clause_precedent with the verbatim "
                        f"text + your inferred clause_type, then attach the precedent_score "
                        f"to the result. Flag any clause materially out of line with the "
                        f"precedent corpus as risk_flag=high.\n\n"
                        f"---\n{msa_text}\n---"
                    ),
                }
            ],
            metadata={"agent_id": "legal-clause-extractor"},
        )

        # 4. The reply is validated against CLAUSE_OUTPUT_SCHEMA before return.
        #    Partners can json.loads it directly without re-parsing free text.
        structured = resp.structured_output if hasattr(resp, "structured_output") else resp
        print("Extracted clauses:")
        print(json.dumps(structured, indent=2))

        # 5. (Optional in prod, shown for clean dev loops.)
        await c.agents.delete("legal-clause-extractor")
        await c.employees.delete("contracts-reviewer")


if __name__ == "__main__":
    asyncio.run(main())
