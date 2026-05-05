"""Knowledge — ingest a document then search it back.

Demonstrates the full ingest → search round-trip on a Nova OS
knowledge collection. Useful as a smoke test that retrieval is wired
correctly end-to-end before pointing real agents at the corpus.

Knowledge collections are scoped via the partner's API-key auth —
``c.knowledge.search(...)`` defaults to the caller's own collection
when ``collection`` is unset. Pass ``collection="shared"`` (or
whatever name your tenant has provisioned) to scope explicitly.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 03_upload_knowledge.py
"""

from __future__ import annotations

import asyncio
import os

from nova_os import Client


SAMPLE_DOC = """
Acme MSA — clause 7.3 (Termination for Cause).

Either party may terminate this Agreement for material breach upon
ninety (90) days' written notice if the breach remains uncured.
Customer's termination for convenience requires payment of all
remaining contract value through the end of the initial term.
""".strip()


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. List collections — sanity check that the API is reachable
        #    and the partner has at least one collection provisioned.
        collections = await c.knowledge.collections()
        print(f"Available collections: {collections}")

        # 2. Ingest a document into the default collection. Title and
        #    metadata are optional but partners usually want both for
        #    filterable retrieval downstream.
        result = await c.knowledge.ingest(
            content=SAMPLE_DOC,
            title="Acme MSA — clause 7.3",
            collection="default",
            metadata={"source": "msa-2026", "clause": "termination"},
        )
        print(f"Ingest: {result}")

        # 3. Search the same collection. The chunk you just ingested
        #    should be the top hit if retrieval indexed it cleanly.
        chunks = await c.knowledge.search(
            query="termination for material breach notice period",
            collection="default",
            top_k=3,
        )
        print(f"\nTop {len(chunks)} hits:")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] score={chunk.get('score', 0):.3f} content={chunk.get('content', '')[:80]!r}")


if __name__ == "__main__":
    asyncio.run(main())
