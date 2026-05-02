"""Finance — 10-K filing year-over-year diff with async-job pattern.

End-to-end partner-side script:
    1. Creates a `filing-analyst` agent with web_search enabled (small budget)
       and a structured output schema covering the analyst-ready material
       changes taxonomy.
    2. Submits an async job containing two 10-K Item 1A excerpts (FY2025 +
       FY2026). Returns immediately with a job_id.
    3. Polls job status every 5 seconds until complete.
    4. Prints the validated structured diff.

Async is the right fit because the analysis takes 60-180 seconds — well past
HTTP timeouts on most reverse proxies. The pattern generalises to any
long-running Nova OS workload (multi-document research, full-corpus risk
review, multi-step plan execution).

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python sec_filing_diff.py
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from nova_os import Client


DIFF_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": [
        "ticker",
        "comparison_period",
        "material_changes",
        "overall_risk_delta",
    ],
    "properties": {
        "ticker": {"type": "string"},
        "comparison_period": {"type": "string"},
        "material_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "summary", "direction"],
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "revenue",
                            "leverage",
                            "liquidity",
                            "segment_mix",
                            "customer_concentration",
                            "regulatory",
                            "litigation",
                            "going_concern",
                            "auditor_change",
                            "other",
                        ],
                    },
                    "summary": {"type": "string"},
                    "direction": {
                        "type": "string",
                        "enum": ["risk_up", "risk_down", "neutral"],
                    },
                    "evidence_excerpt": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "overall_risk_delta": {
            "type": "string",
            "enum": ["materially_lower", "lower", "stable", "elevated", "materially_elevated"],
        },
        "web_citations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["url", "snippet"],
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "snippet": {"type": "string"},
                },
            },
        },
    },
    "additionalProperties": False,
}


SAMPLE_2025 = Path(__file__).with_name("sample_10k_2025.txt")
SAMPLE_2026 = Path(__file__).with_name("sample_10k_2026.txt")


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    fy2025 = SAMPLE_2025.read_text(encoding="utf-8")
    fy2026 = SAMPLE_2026.read_text(encoding="utf-8")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Set up the employee + agent.
        await c.employees.create(
            id="filings-research",
            display_name="Filings Research",
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

        await c.agents.create(
            id="filing-analyst",
            type="skill",
            owner_employee="filings-research",
            description=(
                "Performs year-over-year diff on 10-K Item 1A risk factors, "
                "identifies material changes by analyst-relevant category, "
                "and cites live web sources for context where relevant."
            ),
            output_type={"schema": DIFF_SCHEMA, "violation_mode": "repair"},
            web_search_config={
                "enabled": True,
                "max_calls_per_run": 5,
                "preferred_engine": "tavily",
            },
            instructions=(
                "Compare two 10-K Item 1A excerpts from the same issuer. "
                "Identify every material change. Use web_search sparingly to "
                "look up tickers, recent 8-K filings, or material peer-context "
                "data — every web source must appear in web_citations with a "
                "verbatim snippet. Do not invent figures. If a change is "
                "ambiguous, classify direction as neutral and explain why."
            ),
        )

        # 2. Kick off the async job. The job_input is whatever payload the
        #    agent expects — here, the two excerpts plus the ticker hint.
        job = await c.jobs.create(
            agent_id="filing-analyst",
            job_input={
                "ticker": "ACME",
                "comparison_period": "FY2025 vs FY2026",
                "fy2025_item_1a": fy2025,
                "fy2026_item_1a": fy2026,
            },
            metadata={"agent_id": "filing-analyst"},
            idempotency_key="acme-fy26-diff-v1",
        )
        print(f"Submitted job: {job.id}")

        # 3. Poll until complete. Production code should cap polling at a
        #    sensible budget and surface intermediate progress to the UI.
        for attempt in range(60):  # 60 * 5s = 5 min ceiling
            status = await c.jobs.get(job.id)
            print(f"  [{attempt:>2}] status={status.status} progress={status.progress!r}")
            if status.status in ("complete", "failed", "cancelled"):
                break
            await asyncio.sleep(5)
        else:
            print("Polling budget exhausted — cancelling.")
            await c.jobs.cancel(job.id)
            return

        if status.status != "complete":
            print(f"Job did not complete cleanly: status={status.status} error={status.error!r}")
            return

        # 4. Print the validated diff.
        print()
        print("Material changes:")
        print(json.dumps(status.result, indent=2))

        # 5. Optional cleanup.
        await c.agents.delete("filing-analyst")
        await c.employees.delete("filings-research")


if __name__ == "__main__":
    asyncio.run(main())
