"""SSE wire-format parser.

The HTML5 EventSource spec defines events as `event: <name>\\ndata: <body>\\n\\n`.
Multiple `data:` lines per event are concatenated with newlines. Comment
lines (`:` prefix) are skipped — Nova OS uses them for `:nova-heartbeat`
keep-alive frames.

Returns a stream of dicts: `{"event": <name>, "data": <parsed-json>}`.
On invalid JSON, the dict carries `data: None` and the raw string under
`raw` so callers can choose to ignore or log.
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator


async def parse_lines(lines: AsyncIterator[str]) -> AsyncIterator[dict[str, Any]]:
    event_name: str | None = None
    data_lines: list[str] = []

    async for raw in lines:
        line = raw.rstrip("\r")
        if line == "":
            # Dispatch the buffered event (if any).
            if event_name is None and not data_lines:
                continue
            data_str = "\n".join(data_lines)
            try:
                data: Any = json.loads(data_str) if data_str else None
            except (json.JSONDecodeError, ValueError):
                yield {"event": event_name or "message", "data": None, "raw": data_str}
                event_name = None
                data_lines = []
                continue
            yield {"event": event_name or "message", "data": data}
            event_name = None
            data_lines = []
            continue

        if line.startswith(":"):
            # Comment / heartbeat — ignore.
            continue

        if line.startswith("event:"):
            event_name = line[len("event:"):].strip()
            continue

        if line.startswith("data:"):
            data_lines.append(line[len("data:"):].lstrip())
            continue

        # Other field types (id:, retry:) — silently ignore for v1.


__all__ = ["parse_lines"]
