"""Async job — submit, poll status, retrieve final result.

For long-running agent tasks (deep research, multi-section documents,
full-document analyses) that exceed a reasonable HTTP timeout, Nova OS
provides an async job queue. This example demonstrates the submit-poll-result
pattern.

Submit → returns a job_id immediately (202 Accepted)
Poll   → GET /v1/managed/agents/{id}/jobs/{job_id} until status is terminal
Result → the ``result`` field on the completed job contains the agent's output

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.partner.com
    export NOVA_OS_API_KEY=msk_live_...
    export NOVA_OS_AGENT_ID=research-agent  # agent must exist in Nova OS

Run::

    python 08_async_job_long_running.py
"""

from __future__ import annotations

import asyncio
import os
import time

from nova_os import Client

# Terminal states — any of these means the job will not progress further.
TERMINAL_STATES = {"completed", "failed", "cancelled"}

# How often to poll (seconds). Back off on long jobs to avoid rate limits.
POLL_INTERVAL_S = 3.0


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.partner.com")
    api_key = os.environ["NOVA_OS_API_KEY"]
    agent_id = os.environ.get("NOVA_OS_AGENT_ID", "research-agent")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Submit the long-running job.
        job = await c.jobs.create(
            agent_id,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write a comprehensive market analysis for renewable energy storage "
                        "in Southeast Asia, covering technology trends, regulatory environment, "
                        "and investment opportunities. Include citations."
                    ),
                }
            ],
        )
        job_id = job["job_id"]
        print(f"Job submitted: {job_id} (status={job.get('status', '?')})")

        # 2. Poll until the job reaches a terminal state.
        start = time.monotonic()
        while True:
            await asyncio.sleep(POLL_INTERVAL_S)
            job = await c.jobs.get(job_id)
            status = job.get("status", "unknown")
            elapsed = time.monotonic() - start
            print(f"  [{elapsed:5.0f}s] status={status}")

            if status in TERMINAL_STATES:
                break

            # Back off polling on very long jobs (> 2 min).
            if elapsed > 120 and POLL_INTERVAL_S < 10:
                POLL_INTERVAL_S = 10.0  # type: ignore[assignment]

        # 3. Inspect the result.
        print(f"\nJob finished: status={job.get('status')}")
        if job.get("status") == "completed":
            result = job.get("result", {})
            output = result.get("content") or result.get("text") or str(result)
            # Trim long output for readability.
            if len(output) > 500:
                output = output[:500] + "…"
            print(f"\nResult (truncated):\n{output}")
        else:
            error = job.get("error", "no error details")
            print(f"Job did not complete successfully: {error}")

        # 4. Optionally cancel a still-running job (shown for reference).
        # await c.jobs.cancel(job_id)


if __name__ == "__main__":
    asyncio.run(main())
