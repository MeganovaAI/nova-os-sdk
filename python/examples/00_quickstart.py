"""Quickstart — fastest path from zero to a digital agent answering you.

Maps onto Anthropic's Managed Agents Quickstart
(https://platform.claude.com/docs/en/managed-agents/overview):

    Anthropic Managed Agents          Nova OS SDK (this script)
    ─────────────────────────         ─────────────────────────────
    1. agents.create(model, ...)      1. employees.create(...)        # owns one or more agents
    2. environments.create(...)       2. agents.create(id, type, ...) # the digital agent itself
    3. sessions.create(agent_id)      (no separate session — observational memory is keyed on
                                       the (api_key, end_user, agent) triple automatically)
    4. sessions.events.send(...)      3. messages.create(agent_id, messages=[...])
    5. (interrupt / steer)            (send another messages.create() at any time)

Why no separate session/environment in Nova OS:
- Sessions are implicit. Nova OS scopes per-user memory automatically — pass
  ``X-End-User`` on the request and you get isolation equivalent to a session.
- Environment is the Nova OS server itself. Need a per-tenant filesystem? Add
  ``filesystem.enabled: true`` to the agent's frontmatter — six FS tools auto-
  register. No container plumbing on the partner side.

Total surface to go from nothing to a working digital agent: 3 SDK calls.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 00_quickstart.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create the employee — the owner of one or more agents.
        #    Equivalent to declaring the agent's identity + model config in
        #    Anthropic's agents.create() call.
        await c.employees.create(
            id="my-first-employee",
            display_name="My First Employee",
            model_config={
                "answer": {
                    "primary": "anthropic/claude-opus-4-7",
                    "fallback": ["gemini/gemini-2.5-flash"],
                }
            },
        )

        # 2. Create the agent — the runnable behavior bound to that employee.
        #    Equivalent to picking an environment template + tool set in
        #    Anthropic. Nova OS's "type" tells the registry what loop to run
        #    (skill = single-call, persona = multi-turn, etc.).
        await c.agents.create(
            id="my-first-agent",
            type="skill",
            owner_employee="my-first-employee",
            instructions="You are a helpful assistant. Answer concisely.",
        )

        # 3. Send the first message. Anthropic-equivalent: sessions.events.send.
        #    No session ID needed — observational memory is keyed on the
        #    (API key, end_user, agent) triple automatically. Pass the
        #    ``X-End-User`` header to scope memory per end-user; omit it for
        #    a single shared scope (fine for evaluation).
        resp = await c.messages.create(
            agent_id="my-first-agent",
            messages=[{"role": "user", "content": "What are you good at?"}],
            metadata={"agent_id": "my-first-agent"},
        )
        print(resp)

        # Cleanup (optional). Production code keeps these objects around.
        await c.agents.delete("my-first-agent")
        await c.employees.delete("my-first-employee")


if __name__ == "__main__":
    asyncio.run(main())
