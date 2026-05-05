"""Users + Settings — partner-admin onboarding.

Demonstrates the admin surface partners use during tenant
provisioning:

1. Create three users (one admin, two employees) for a fresh tenant.
2. Configure the platform's answer model so every agent on this
   tenant uses Opus by default.
3. Read settings + list users to verify.

These endpoints require partner-admin scope on the API key — JWT
middleware enforces that upstream.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...   # must be a partner-admin token

Run::

    python 15_users_settings_admin.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


NEW_USERS = [
    {"email": "alice@acme.example",   "name": "Alice (Admin)",     "role": "admin"},
    {"email": "bob@acme.example",     "name": "Bob (Employee)",    "role": "employee"},
    {"email": "carol@acme.example",   "name": "Carol (Employee)",  "role": "employee"},
]


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create users. Each gets a default password and is flagged
        #    `must_change_password=true`. Trigger a password reset on
        #    first sign-in or hand the user an out-of-band reset link.
        created_ids = []
        for u in NEW_USERS:
            user = await c.users.create(email=u["email"], name=u["name"], role=u["role"])
            created_ids.append(user["id"])
            print(f"Created: {user['email']:<30s} role={user['role']:<10s} id={user['id']}")

        # 2. Configure the answer model. The Meganova gateway requires
        #    the <provider>/<model> shape — bare names 404. ``put`` is
        #    upsert (idempotent on repeat).
        await c.settings.put("answer_model", "anthropic/claude-opus-4-7")
        await c.settings.put("skill_model", "gemini/gemini-2.5-flash")
        print("\nUpdated platform settings.")

        # 3. Read back to verify. ``settings.get`` returns the value
        #    directly (not a {key, value} envelope).
        answer = await c.settings.get("answer_model")
        skill = await c.settings.get("skill_model")
        print(f"  answer_model = {answer!r}")
        print(f"  skill_model  = {skill!r}")

        # 4. List the tenant's users to confirm the three landed.
        users = await c.users.list()
        print(f"\nAll users on this tenant ({len(users)}):")
        for u in users:
            print(f"  {u.get('email', ''):<30s} role={u.get('role', '?')}")

        # 5. Cleanup — typical demo pattern. Production code would NOT
        #    delete users at the end of an onboarding run.
        for user_id in created_ids:
            await c.users.delete(user_id)
        print(f"\nCleaned up {len(created_ids)} demo users")


if __name__ == "__main__":
    asyncio.run(main())
