"""Personas — boot-time discovery with ETag caching.

Demonstrates the partner-side persona-manifest pattern:

1. Fetch the full manifest once at startup; cache the
   ``manifest_version`` (ETag) in process memory.
2. On subsequent boots / periodic refresh, send
   ``if_none_match=cached_version`` — server replies 304 (returns
   ``None``) if unchanged; partner skips re-parsing.
3. Use the manifest to drive partner-side dispatch decisions:
   which personas exist, what triage mode each has, which
   ``route_hint`` kinds they emit, what ``route_templates`` they
   reference.

This is the boot-time companion to the per-response ``route_hint``
API on chat completions — together they form the persona contract
surface partners need to stop mirroring nova-os YAML in their own
code.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 17_personas_discovery.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. First fetch — no cached version, expect a full manifest.
        manifest = await c.personas.list()
        if manifest is None:
            print("Unexpected None on first fetch (no If-None-Match passed)")
            return
        version = manifest["manifest_version"]
        print(f"Manifest version: {version}")
        print(f"Personas registered: {len(manifest['personas'])}\n")

        for p in manifest["personas"]:
            print(f"  {p['id']:<35s}  triage={p['triage']:<14s}  emits={p['emits_route_hint_kinds']}")

        # 2. Round-trip with If-None-Match — should be 304 (None).
        print("\nRe-fetching with If-None-Match (cache validation)…")
        cached = await c.personas.list(if_none_match=version)
        if cached is None:
            print(f"  → 304: cached version {version[:20]}… is current")
        else:
            print(f"  → 200: manifest changed; new version {cached['manifest_version']}")

        # 3. Look up a single persona by id (e.g. for a deep-link
        #    refresh after a UI route change).
        if manifest["personas"]:
            target_id = manifest["personas"][0]["id"]
            single = await c.personas.get(target_id)
            print(f"\nPersona detail for {target_id!r}:")
            print(f"  display_name = {single.get('display_name')!r}")
            print(f"  capabilities = {single.get('capabilities')}")
            print(f"  route_template_names = {single.get('route_template_names')}")


if __name__ == "__main__":
    asyncio.run(main())
