"""Multi-model fallback — per-employee model_config cascade.

Nova OS supports a primary model + ordered fallback chain per-employee.
When the primary model is unavailable (rate limit, quota, downstream error),
Nova OS automatically promotes the first healthy fallback. The response
includes ``model_used`` and ``fallback_triggered`` fields so partners can
observe which tier served the request.

This example creates an employee with a three-tier model cascade, sends a
message, and inspects the routing result.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.partner.com
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 06_multi_model_fallback.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.partner.com")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create an employee with a three-tier model cascade.
        #    - Primary   : claude-opus-4-7 (best quality, higher cost)
        #    - Fallback 1: gemini-2.5-flash (fast + cheap)
        #    - Fallback 2: gemini-2.5-pro (high quality backup)
        #
        #    Nova OS promotes the next fallback automatically on:
        #      - HTTP 429 rate limit
        #      - HTTP 503 / upstream timeout
        #      - provider billing exhaustion
        await c.employees.create(
            id="multi-model-demo",
            display_name="Multi-Model Demo Employee",
            model_config={
                "answer": {
                    "primary": "anthropic/claude-opus-4-7",
                    "fallback": [
                        "gemini/gemini-2.5-flash",
                        "gemini/gemini-2.5-pro",
                    ],
                }
            },
        )

        # 2. Create a skill agent owned by this employee.
        await c.agents.create(
            id="multi-model-agent",
            type="skill",
            owner_employee="multi-model-demo",
            description="Demo agent for multi-model fallback",
        )

        # 3. Send a message and inspect the routing result.
        resp = await c.messages.create(
            agent_id="multi-model-agent",
            messages=[{"role": "user", "content": "Summarise the benefits of multi-model routing."}],
        )

        # The response dict includes Nova OS-specific fields alongside the
        # standard message response shape:
        if isinstance(resp, dict):
            model_used = resp.get("model_used", "unknown")
            fallback_triggered = resp.get("fallback_triggered", False)
            print(f"Model used       : {model_used}")
            print(f"Fallback triggered: {fallback_triggered}")
            if fallback_triggered:
                print("  ↳ Primary was unavailable — fallback served the request.")
            content = resp.get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    print(f"\nResponse:\n{block['text']}")
        else:
            print("Response:", resp)

        # 4. Clean up.
        await c.agents.delete("multi-model-agent")
        await c.employees.delete("multi-model-demo")
        print("\nCleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
