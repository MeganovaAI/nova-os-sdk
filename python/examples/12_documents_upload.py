"""Documents — upload, list, delete.

Demonstrates the partner-side document lifecycle on Nova OS:

1. Upload a file (multipart). Super Nova auto-indexes it into the
   document engine on receipt — partners don't trigger indexing
   separately.
2. List documents in the target collection to see the new one.
3. Delete the document (cleanup).

Common partner usage: upload at tenant-onboarding time, reference the
returned ``id`` from agent prompts via the document-engine retrieval
tools, delete on tenant offboarding.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 12_documents_upload.py
"""

from __future__ import annotations

import asyncio
import os


from nova_os import Client


SAMPLE_CONTENT = b"""# Acme Onboarding Checklist

- Sign MSA (clause 7.3 covers termination for cause)
- Provision API key
- Bind agent to private collection
""".strip()


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]

    async with Client(base_url=base_url, api_key=api_key) as c:
        # 1. Upload. ``content`` accepts raw bytes or any binary file-like
        #    object — pass ``open(path, 'rb')`` directly when uploading
        #    from disk.
        doc = await c.documents.upload(
            filename="onboarding-checklist.md",
            content=SAMPLE_CONTENT,
            collection_id="onboarding",
            content_type="text/markdown",
        )
        doc_id = doc["id"]
        print(f"Uploaded: id={doc_id} title={doc.get('title')!r}")

        # 2. List the collection. The document we just uploaded should
        #    appear within seconds (auto-indexing is in-process for
        #    text-formatted files).
        print("\nDocuments in collection 'onboarding':")
        async for entry in c.documents.list(collection_id="onboarding", limit=20):
            print(f"  {entry.get('id'):<40s} {entry.get('title', '')[:50]!r}")

        # 3. Cleanup. Delete is idempotent — calling it twice is fine.
        await c.documents.delete(doc_id)
        print(f"\nDeleted {doc_id}")


if __name__ == "__main__":
    asyncio.run(main())
