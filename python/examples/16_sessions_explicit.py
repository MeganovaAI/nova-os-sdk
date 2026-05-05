"""Sessions — explicit session lifecycle.

Demonstrates the Nova OS native ``c.sessions`` resource — partner-side
explicit sessions for cases where the implicit ``(API key, end_user,
agent)`` triple isn't enough:

- One session per support ticket / pipeline run / batch job.
- Session-default model overrides (``model="anthropic/claude-opus-4-7"``).
- Coexists with the Anthropic-compat ``/v1/sessions`` surface — a
  session created here is readable via either mount.

For lighter-weight per-end-user isolation that doesn't need explicit
session management, just pass the ``X-End-User`` header on
``c.messages.create()`` calls. See the healthcare vertical example
(``examples/healthcare/clinical_note_triage.py``) for that pattern.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 16_sessions_explicit.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]
    agent_id = os.environ.get("NOVA_OS_AGENT_ID", "default-assistant")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Create a session with a per-session model override. Every
        #    message in this session will route to Opus by default;
        #    individual messages.create() calls can still override
        #    further if needed.
        session = await c.sessions.create(
            agent_id=agent_id,
            model="anthropic/claude-opus-4-7",
        )
        sid = session["id"]
        print(f"Created session: {sid} (agent={session['agent_id']}, model={session.get('model', 'default')!r})")

        # 2. Get it back — sanity check the session exists + state.
        got = await c.sessions.get(sid)
        print(f"Read back: id={got['id']} created_at={got.get('created_at', '?')}")

        # 3. The session is now usable as the addressing root for
        #    subsequent message calls. Per-message integration is on
        #    the partner's side — pass the session_id in metadata
        #    or via the existing /v1/sessions/{id}/events surface
        #    (Anthropic-compat) for full conversation tracking.


if __name__ == "__main__":
    asyncio.run(main())
