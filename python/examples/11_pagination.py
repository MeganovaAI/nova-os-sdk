"""Pagination — auto-iterate every agent without hand-rolling cursors.

Every ``list()`` method on the SDK is an async iterator. The server returns
pages with ``next_cursor`` + ``has_more``; the SDK fetches the next page
transparently as you iterate. Partner code never has to manage cursors
unless they want explicit page boundaries (rare).

Demonstrates two patterns:

1. **The 95% case** — ``async for x in c.agents.list()`` walks every agent,
   page boundaries invisible.

2. **The 5% case** — passing ``limit=`` to constrain page size when the
   default (server picks) is wrong for your workload.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 11_pagination.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # Pattern 1: just iterate. SDK pages transparently.
        print("All agents:")
        count = 0
        async for agent in c.agents.list():
            count += 1
            print(f"  {agent.get('id'):<40s} type={agent.get('type')}")
        print(f"  ({count} agents total)\n")

        # Pattern 2: constrain page size. Useful when the agent count is large
        # and you want predictable per-page latency, or when you're feeding
        # the result into a UI that paginates at the same boundary.
        print("First 5 employees:")
        seen = 0
        async for employee in c.employees.list(limit=5):
            seen += 1
            print(f"  {employee.get('id'):<40s} display_name={employee.get('display_name')!r}")
            if seen >= 5:
                break  # take only the first page; SDK won't fetch further

        # Pattern 3 (advanced): explicit cursor management. Rarely needed —
        # for parallel page fetching or resumable scans. Most partners will
        # not touch this.
        #
        #   first_page = await c.agents._page(limit=20)
        #   next_cursor = first_page.get("next_cursor")
        #   if next_cursor:
        #       second_page = await c.agents._page(limit=20, cursor=next_cursor)


if __name__ == "__main__":
    asyncio.run(main())
