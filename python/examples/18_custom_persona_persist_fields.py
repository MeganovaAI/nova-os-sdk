"""Custom persona + persist_fields — multi-turn slot collection (sync + streaming).

Stitches three v0.1.7 server primitives end-to-end:

1. **Custom persona authoring** — drop a YAML file into the writable
   ``data/agents/_runtime/`` layer (new in v0.1.7), gitignored and not
   baked into the release image. Partners use this for site-specific
   personas that shouldn't ship in the catalog.

2. **Manifest refresh** — confirm LibraOS picked up the new persona via
   ``c.personas.list()``.

3. **`output_type.persist_fields` slot collection** — across both sync
   (``c.messages.create()``) and streaming (``c.messages.stream()``)
   calls, LibraOS auto-persists schema-validated slot values keyed by
   ``persist_scope`` (``session`` here) and injects a ``## Known
   fields`` block before the system prompt on subsequent turns so the
   model never re-asks for slots it has already collected. Merged
   state surfaces as ``metadata.persisted_state`` on sync responses and
   on the terminal ``done`` streaming event.

Requires nova-os ≥ v0.1.7 with PRs #328 (sync) + #334 (streaming) on
the ``/v1/messages`` partner-prefix surface. The bundled image at
``ghcr.io/meganovaai/nova-os:v0.1.7`` lags the git tag until
``docker-publish.yml`` rebuilds — pin to the weekly explicitly until
then::

    docker pull ghcr.io/meganovaai/nova-os:v0.1.7-week-2026-05-26

Prerequisites::

    pip install libraos-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...
    # The directory must match what LibraOS scans server-side.
    # Defaults to data/agents/_runtime/ inside the container.
    export NOVA_OS_AGENTS_RUNTIME_DIR=/srv/nova-os/data/agents/_runtime

Run::

    python 18_custom_persona_persist_fields.py
"""

from __future__ import annotations

import asyncio
import os
import uuid
from pathlib import Path

from libraos import Client


# Custom persona — appointment booking. Three slots accumulate across
# turns under output_type.persist_fields.
PERSONA_YAML = """---
name: appointment-booker
agent_type: persona
brain: true
display_name: Appointment Booker
description: Collects appointment date, time, and contact email across turns.
model: gemini/gemini-2.5-flash

system_prompt: |
  You are an appointment-booking assistant. Collect three slots from the
  user, one at a time, in this order: preferred date, preferred time,
  contact email. Acknowledge values the user has already given (LibraOS
  injects a "## Known fields" block before this prompt with current
  slot state) and ask for the next missing slot. Once all three are
  collected, confirm by echoing them back and set next_step=confirm.

output_type:
  schema_id: appointment-booker-v1
  schema_inline:
    type: object
    required: [next_step, reply_to_user]
    properties:
      next_step:
        enum: [ask_date, ask_time, ask_email, confirm, complete]
      reply_to_user: {type: string}
      collected:
        type: object
        properties:
          date:  {type: [string, "null"]}
          time:  {type: [string, "null"]}
          email: {type: [string, "null"]}

  persist_fields:
    - {path: collected.date,  merge: non_null_overwrite}
    - {path: collected.time,  merge: non_null_overwrite}
    - {path: collected.email, merge: non_null_overwrite}

  persist_scope: session
  on_violation: error
---
"""


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]
    runtime_dir = os.environ.get(
        "NOVA_OS_AGENTS_RUNTIME_DIR",
        "/srv/nova-os/data/agents/_runtime",
    )

    # 1. Install the persona into the runtime-agents directory. Single-host
    #    self-host: write directly. Multi-host: this directory is a shared
    #    volume; write from any host with access.
    target = Path(runtime_dir) / "appointment-booker.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PERSONA_YAML)
    print(f"Installed persona at {target}")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 2. Refresh manifest — confirms LibraOS scanned the new YAML.
        manifest = await c.personas.list()
        ids = {p["id"] for p in (manifest or {}).get("personas", [])}
        if "appointment-booker" not in ids:
            print(
                "appointment-booker not registered yet. Verify "
                "NOVA_OS_AGENTS_RUNTIME_DIR matches what the server scans, "
                "then re-run."
            )
            return
        print("Persona registered.\n")

        # All turns share one session_id so persist_fields keys off
        # session:{tenant_id}/{session_id}/{schema_id} per the persona's
        # persist_scope: session declaration.
        session_id = f"appt-demo-{uuid.uuid4().hex[:8]}"
        meta = {"session_id": session_id}

        # 3. Sync turns — read metadata.persisted_state from each response.
        sync_turns = [
            "Hi, I'd like to book an appointment.",
            "Let's go with Tuesday.",
            "3pm works for me.",
        ]

        print("=== sync turns ===")
        for i, user_msg in enumerate(sync_turns, start=1):
            print(f"\n--- Turn {i}: {user_msg!r}")
            resp = await c.messages.create(
                agent_id="appointment-booker",
                messages=[{"role": "user", "content": user_msg}],
                metadata=meta,
            )
            persisted = (resp.get("metadata") or {}).get("persisted_state") or {}
            print(f"  reply     : {_text(resp)!r}")
            print(f"  persisted : {persisted}")

        # 4. Streaming turn (final slot). Same session_id continues
        #    accumulation. Wire-shape: events arrive as
        #    {"event": "<name>", "data": {...}} per libraos._sse.parse_lines.
        #    Terminal "done" event carries persisted_state.
        print("\n=== streaming turn (final slot) ===")
        async with c.messages.stream(
            agent_id="appointment-booker",
            messages=[{"role": "user", "content": "My email is alex@example.com."}],
            metadata=meta,
        ) as stream:
            print("  reply     : ", end="", flush=True)
            async for event in stream:
                kind = event.get("event")
                data = event.get("data") or {}
                if kind == "text_delta":
                    print(data.get("content", ""), end="", flush=True)
                elif kind == "done":
                    print()  # newline after streamed text
                    persisted = data.get("persisted_state") or {}
                    print(f"  persisted : {persisted}")
                    break

        # 5. Final state lives server-side under the session_id key. A
        #    fresh client process posting to the same agent + session_id
        #    would see the same Known fields injected automatically —
        #    persistence survives client lifetime, not just this loop.


def _text(resp: dict) -> str:
    """Pull reply_to_user from a sync response. messages_api returns
    Anthropic-shape content blocks; the validated reply lives in the
    text block."""
    for block in resp.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            return block.get("text", "")
    return ""


if __name__ == "__main__":
    asyncio.run(main())
