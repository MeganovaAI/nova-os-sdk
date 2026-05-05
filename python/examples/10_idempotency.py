"""Idempotency keys — safely retry create() across network failures.

Every Nova OS ``create()`` call accepts ``idempotency_key=``. The server
remembers the key + the canonical request body for ~24 hours and returns
the same response if the same key + body arrives again. Different body
with the same key returns 409.

The pattern partners need this for: networks fail mid-`create()`. Without
an idempotency key, retrying creates a duplicate resource. With one, the
retry returns the already-created resource — at-least-once becomes
exactly-once.

This example simulates the failure: we create an agent with an idempotency
key, "lose" the response on the wire, then retry with the same key — and
see we get the exact same agent back (same `id`, same created_at) without
a duplicate having been created.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 10_idempotency.py
"""

from __future__ import annotations

import asyncio
import os
import uuid

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    # Fresh idempotency key per logical operation. Persist this client-side
    # before sending the request — that way you can replay it after a crash
    # without producing duplicates.
    key = f"create-demo-agent-{uuid.uuid4()}"

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Set up an owner employee (one-shot; idempotency irrelevant here).
        await c.employees.create(
            id="idem-demo-employee",
            display_name="Idempotency Demo",
            model_config={"answer": {"primary": "anthropic/claude-opus-4-7"}},
        )

        # 2. First "real" attempt — server creates the agent and returns it.
        first = await c.agents.create(
            id="idem-demo-agent",
            type="skill",
            owner_employee="idem-demo-employee",
            instructions="Answer concisely.",
            idempotency_key=key,
        )
        print(f"First call:  id={first.get('id')!r} created_at={first.get('created_at')!r}")

        # 3. Simulated retry after a transient failure — same key, same body.
        #    The server returns the already-created agent, NOT a duplicate.
        retry = await c.agents.create(
            id="idem-demo-agent",
            type="skill",
            owner_employee="idem-demo-employee",
            instructions="Answer concisely.",
            idempotency_key=key,
        )
        print(f"Retry call:  id={retry.get('id')!r} created_at={retry.get('created_at')!r}")

        # 4. Sanity: the two responses are identical — no duplicate created.
        assert first.get("created_at") == retry.get("created_at"), (
            "Expected idempotent retry to return the same created_at — got "
            f"{first.get('created_at')} vs {retry.get('created_at')}"
        )
        print("OK — same created_at on both calls; no duplicate agent.")

        # Cleanup.
        await c.agents.delete("idem-demo-agent")
        await c.employees.delete("idem-demo-employee")


if __name__ == "__main__":
    asyncio.run(main())
