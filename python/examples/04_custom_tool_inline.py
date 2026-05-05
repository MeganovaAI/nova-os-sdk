"""Mode A custom tool — inline (SSE stream) pattern.

In Mode A, Nova OS pauses the agent mid-run and emits a ``custom_tool_use``
SSE event on the partner's open streaming connection. The partner runs the
tool locally and submits the result back via
``MessageStream.submit_tool_result(...)`` — same socket, no separate HTTP
round-trip.

Use Mode A when you don't want to expose a public webhook endpoint and your
process can hold a streaming connection while the agent runs (typical for
backend services; awkward for serverless). Use Mode B (webhook) — see
``05_custom_tool_webhook.py`` — when the agent run is long enough that
holding the connection is impractical, or when the partner is naturally
HTTP-server-shaped.

Prerequisites::

    pip install nova-os-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...
    export NOVA_OS_AGENT_ID=invoice-bot

Run::

    python 04_custom_tool_inline.py
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from nova_os import Client


# ---------------------------------------------------------------------------
# Partner tool implementations — replace with your real business logic.
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
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    api_key = os.environ["NOVA_OS_API_KEY"]
    agent_id = os.environ.get("NOVA_OS_AGENT_ID", "invoice-bot")

    async with Client(base_url=base_url, api_key=api_key) as c:
        # ``c.messages.stream(...)`` opens an SSE connection and yields
        # parsed events. Inside the context manager we can dispatch tool
        # calls back over the same socket via ``s.submit_tool_result(...)``.
        async with c.messages.stream(
            agent_id=agent_id,
            messages=[{"role": "user", "content": "Show me invoice INV-2026-042"}],
        ) as s:
            async for event in s:
                kind = event.get("type")

                if kind == "text_delta":
                    # Accumulate the reply text as it streams.
                    print(event.get("content", ""), end="", flush=True)

                elif kind == "custom_tool_use":
                    # Agent paused mid-run requesting a partner tool.
                    handler = TOOL_HANDLERS.get(event["name"])
                    if handler is None:
                        # Tell the agent we don't know this tool — it can
                        # recover (often by trying a different approach).
                        await s.submit_tool_result(
                            tool_use_id=event["id"],
                            result=f"unknown tool: {event['name']}",
                            is_error=True,
                        )
                        continue

                    result = await handler(event.get("input", {}))
                    await s.submit_tool_result(
                        tool_use_id=event["id"],
                        result=result,
                    )

                elif kind == "done":
                    print()  # newline after the streamed text
                    break


if __name__ == "__main__":
    asyncio.run(main())
