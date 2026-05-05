"""Hooks — subscribe to lifecycle events.

Demonstrates partner registration of webhook subscriptions for the 9
canonical Nova OS lifecycle events.

**Important: as of v0.1.5 the registry is in-memory and the runtime
hook bus does not yet read from it.** Subscriptions are stored and
returned in list/get, but events do not yet fire to the registered
URLs. Persistence + bus bridge are tracked follow-ups. The wire
format on this surface is stable; partner integration code wired
against it today will start receiving deliveries once the bridge
ships — no SDK change required.

The 9 events:

  SessionStart      — opens a new conversation/session
  SessionEnd        — session closed (timeout or explicit close)
  UserPromptSubmit  — partner end-user submits a turn
  PreToolUse        — agent is about to invoke a tool
  PostToolUse       — tool call completed (success or error)
  PreInference      — agent is about to call the LLM
  PostInference     — LLM response received
  Stop              — agent decided to stop the run
  Error             — runtime error during the agent loop

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 13_hooks_subscribe.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Register two subscriptions — one for tool-use telemetry,
        #    one for an audit-log sink on session boundaries.
        tool_hook = await c.hooks.create(
            event="PostToolUse",
            target_url="https://partner.example/hooks/tool-telemetry",
            secret_env="HOOKS_TOOL_SECRET",
            description="Stream every tool-call result into the partner's audit pipeline",
        )
        print(f"Registered: {tool_hook['id']} ({tool_hook['event']})")

        session_hook = await c.hooks.create(
            event="SessionEnd",
            target_url="https://partner.example/hooks/session-end",
            secret_env="HOOKS_SESSION_SECRET",
            description="Close out the conversation in the partner's CRM",
        )
        print(f"Registered: {session_hook['id']} ({session_hook['event']})")

        # 2. List all subscriptions — sanity check.
        subs = await c.hooks.list()
        print(f"\nAll subscriptions ({len(subs)}):")
        for s in subs:
            print(f"  {s['id'][:8]}…  {s['event']:<20s}  {s['target_url']}")

        # 3. Cleanup — delete is idempotent (always returns 204 even if
        #    the subscription doesn't exist).
        await c.hooks.delete(tool_hook["id"])
        await c.hooks.delete(session_hook["id"])
        print(f"\nDeregistered both subscriptions")


if __name__ == "__main__":
    asyncio.run(main())
