"""Filesystem — seed an agent's workspace before its first turn.

Common partner pattern: the agent's workspace exists (was provisioned
when the agent was assigned to this tenant/session pair) but it's
empty. Partners want to drop in policy docs, prompt files, or other
context the agent should read on its first read of the FS.

This script writes three seeded files, lists them back, reads one to
confirm round-trip, then cleans up.

Workspaces are scoped to ``(tenant_id, session_id)`` pairs. Use your
partner-side stable identifiers for both — no opaque random IDs
required (memorability helps debugging).

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 14_filesystem_seed.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


SEED_FILES = {
    "workspace/PLAN.md": b"# Plan\n\n- [ ] Read intake.md\n- [ ] Draft response\n",
    "workspace/intake.md": b"Customer reported: 'invoice INV-2026-042 missing'.\n",
    "workspace/style-guide.md": b"Always cite the invoice ID. Always.\n",
}


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]
    tenant = os.environ.get("NOVA_OS_TENANT_ID", "demo-tenant")
    session = os.environ.get("NOVA_OS_SESSION_ID", "demo-session")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Seed three files. Each is independent — partners can
        #    parallelise these with asyncio.gather() at scale.
        for path, content in SEED_FILES.items():
            meta = await c.filesystem.write(
                tenant_id=tenant,
                session_id=session,
                path=path,
                content=content,
                content_type="text/markdown",
            )
            print(f"Wrote {meta['path']:<40s} sha256={meta.get('sha256', '?')[:12]}…")

        # 2. List to confirm. The mount default is /workspace so we
        #    don't need to pass `mount=` explicitly.
        files = await c.filesystem.list(tenant_id=tenant, session_id=session)
        print(f"\nWorkspace contents ({len(files)} files):")
        for f in files:
            print(f"  {f['path']:<40s} size={f['size']}b")

        # 3. Read one back to prove the round-trip works.
        content = await c.filesystem.read(
            tenant_id=tenant, session_id=session, path="workspace/PLAN.md"
        )
        print(f"\nPLAN.md contents:\n{content.decode()}")

        # 4. Cleanup. Delete is idempotent.
        for path in SEED_FILES:
            await c.filesystem.delete(tenant_id=tenant, session_id=session, path=path)
        print("Cleaned up all seeded files")


if __name__ == "__main__":
    asyncio.run(main())
