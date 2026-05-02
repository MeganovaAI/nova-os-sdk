"""SSE event parser — handles event/data/comment lines per the
HTML5 EventSource spec."""

from __future__ import annotations

from typing import Any, AsyncIterator

import pytest

from nova_os._sse import parse_lines


async def _lines(*items: str) -> AsyncIterator[str]:
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_parse_basic_event() -> None:
    src = _lines(
        "event: text",
        'data: {"type":"text","content":"hi"}',
        "",
    )
    events = [e async for e in parse_lines(src)]
    assert events == [{"event": "text", "data": {"type": "text", "content": "hi"}}]


@pytest.mark.asyncio
async def test_skips_heartbeat_comments() -> None:
    src = _lines(
        ":nova-heartbeat elapsed_ms=10000",
        ":nova-heartbeat elapsed_ms=20000",
        "event: text",
        'data: {"type":"text","content":"hi"}',
        "",
    )
    events = [e async for e in parse_lines(src)]
    assert len(events) == 1
    assert events[0]["event"] == "text"


@pytest.mark.asyncio
async def test_multiple_events() -> None:
    src = _lines(
        "event: tool_use",
        'data: {"type":"tool_use","id":"t1","name":"x","input":{}}',
        "",
        "event: text",
        'data: {"type":"text","content":"a"}',
        "",
        "event: done",
        'data: {"type":"done","status":"completed"}',
        "",
    )
    events = [e async for e in parse_lines(src)]
    assert [e["event"] for e in events] == ["tool_use", "text", "done"]


@pytest.mark.asyncio
async def test_data_only_no_event_name() -> None:
    """Per EventSource spec, missing `event:` defaults to 'message'."""
    src = _lines('data: {"x":1}', "")
    events = [e async for e in parse_lines(src)]
    assert events == [{"event": "message", "data": {"x": 1}}]


@pytest.mark.asyncio
async def test_invalid_json_data_yields_raw_string() -> None:
    """If data isn't JSON, surface it as a string under 'raw'."""
    src = _lines("event: text", "data: not json at all", "")
    events = [e async for e in parse_lines(src)]
    assert events == [{"event": "text", "data": None, "raw": "not json at all"}]
