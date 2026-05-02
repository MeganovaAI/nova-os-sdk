"""Mode A custom tool — inline (SSE stream) pattern.

In Mode A, Nova OS pauses the agent mid-run and sends a
``custom_tool_use`` SSE event to the partner's streaming connection.
The partner executes the tool locally and submits the result back via
``c.messages.submit_tool_result(...)``.

This example shows the streaming loop pattern. The Mode A streaming
context manager (``c.messages.stream(...)``) will be available in the
next SDK release; a note is included where you would swap in that API.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.partner.com
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 04_custom_tool_inline.py
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

from nova_os import Client


# ---------------------------------------------------------------------------
# Partner tool implementation — replace with your real business logic.
# ---------------------------------------------------------------------------

async def fetch_invoice(input_data: dict[str, Any]) -> str:
    """Look up an invoice by ID and return its details as a string."""
    invoice_id = input_data.get("invoice_id", "UNKNOWN")
    # In production: query your DB / ERP here.
    return f"Invoice {invoice_id}: status=paid, amount=$1,250.00, due=2026-03-31"


TOOL_HANDLERS: dict[str, Any] = {
    "fetch_invoice": fetch_invoice,
}


async def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.partner.com")
    api_key = os.environ["NOVA_OS_API_KEY"]
    agent_id = os.environ.get("NOVA_OS_AGENT_ID", "invoice-bot")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # Start the message — stream=True activates Mode A SSE delivery.
        # Note: the high-level c.messages.stream(...) context manager
        # is available in the next SDK release. This lower-level pattern
        # uses the underlying HTTP client directly to show the wire protocol.
        resp = await c.messages.create(
            agent_id=agent_id,
            messages=[{"role": "user", "content": "Show me invoice INV-2026-042"}],
            metadata={"stream": True},
        )

        # In a full Mode A implementation the response is an SSE stream.
        # Events to handle:
        #   text_delta      → accumulate into the reply text
        #   custom_tool_use → call partner tool, submit result
        #   done            → stream finished
        #
        # Example event loop (pseudocode matching the wire protocol):
        #
        #   async for event in resp.iter_events():
        #       if event["type"] == "text_delta":
        #           print(event["content"], end="", flush=True)
        #       elif event["type"] == "custom_tool_use":
        #           tool_name = event["name"]
        #           handler = TOOL_HANDLERS.get(tool_name)
        #           if handler:
        #               result = await handler(event["input"])
        #               await c.messages.submit_tool_result(
        #                   agent_id=agent_id,
        #                   message_id=event["message_id"],
        #                   tool_use_id=event["id"],
        #                   result=result,
        #               )
        #       elif event["type"] == "done":
        #           break

        # For now (non-streaming path), print the synchronous response.
        print("Response:", resp)


if __name__ == "__main__":
    asyncio.run(main())
