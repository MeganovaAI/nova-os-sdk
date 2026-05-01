"""Full lifecycle — create an employee, attach an owned agent, send first chat.

Demonstrates the Nova OS extended client surface:
- ``c.employees.create(...)`` — define a digital employee with model config
- ``c.agents.create(...)`` — attach a skill agent owned by that employee
- ``c.messages.create(...)`` — send the first message to the agent

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.partner.com
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 02_create_employee_and_agent.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.partner.com")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create the employee (digital persona that owns agents).
        employee = await c.employees.create(
            id="frontdesk",
            display_name="Front Desk",
            model_config={
                "answer": {
                    "primary": "anthropic/claude-opus-4-7",
                    "fallback": ["gemini/gemini-2.5-flash"],
                }
            },
        )
        print(f"Created employee: {employee.get('id', employee)}")

        # 2. Create a skill agent owned by the employee.
        agent = await c.agents.create(
            id="intake-specialist",
            type="skill",
            owner_employee="frontdesk",
            description="Intake assistant — gathers case details from clients",
        )
        print(f"Created agent   : {agent.get('id', agent)}")

        # 3. Send the first message.
        resp = await c.messages.create(
            agent_id="intake-specialist",
            messages=[{"role": "user", "content": "Hi, I need help with my case"}],
        )
        print(f"Response: {resp}")

        # 4. Clean up (optional in production; shown for idempotent dev loops).
        await c.agents.delete("intake-specialist")
        await c.employees.delete("frontdesk")
        print("Cleaned up agent and employee.")


if __name__ == "__main__":
    asyncio.run(main())
