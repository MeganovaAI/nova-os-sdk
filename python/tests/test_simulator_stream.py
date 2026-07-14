"""Tests for ``client.simulate(stream=True)`` — Track 1.5 streaming variant.

Covers:

- Happy-path event order: each turn yields ``simulator_turn`` then
  ``target_turn``; stream ends with exactly one ``outcome`` event.
- Outcome always last — success / failure / timeout / error.
- ``turn_index`` matches the position of the just-emitted turn in the
  underlying transcript (0, 1, 2, 3, ... — each event gets its own).
- Cancellation cleanup — when the caller closes the iterator mid-loop,
  any transient simulator agent that was created is still DELETEd.
- Async iterator works under anyio.
- Sync iterator (anyio bridge) works.
- ``Client.simulate(stream=True)`` returns an iterator.
- ``Client.simulate(stream=False)`` still returns a ``SimulationResult``
  (backward-compat with Track 1.3 / 1.4).
- Error paths emit ``outcome`` events with ``outcome="error"`` instead of
  raising through the iterator (per spec §F).
"""

from __future__ import annotations

import json
from typing import Any, Callable

import anyio
import httpx
import pytest

from libraos import Archetype, Client
from libraos.simulator import (
    SimulationResult,
    TurnEvent,
    async_simulate_stream,
    simulate_stream,
)
from libraos.simulator._wiring import (
    HARNESS_AGENT_ID,
    _reset_cache_for_tests,
)


# --------------------------------------------------------------- harness


def _mock_transport(handler: Callable[[httpx.Request], httpx.Response]):
    return httpx.MockTransport(handler)


def _content_block(text: str) -> dict[str, Any]:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def _archetype_basic(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "name": "stream-test-customer",
        "description": "Stream test archetype.",
        "hidden_facts": ["secret"],
        "disclosure_willingness": "cautious",
        "success_signal": "lawyer matched",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def _reset_caches():
    _reset_cache_for_tests()
    yield
    _reset_cache_for_tests()


def _make_handler(
    *,
    harness_present: bool = True,
    simulator_replies: list[str] | None = None,
    target_replies: list[str | int] | None = None,
    captured: dict[str, Any] | None = None,
    on_target_call: Callable[[int], None] | None = None,
) -> Callable[[httpx.Request], httpx.Response]:
    sim_iter = iter(simulator_replies or [])
    tgt_iter = iter(target_replies or [])
    target_call_count = {"n": 0}
    if captured is not None:
        captured.setdefault("requests", [])
        captured.setdefault("agent_get_calls", 0)
        captured.setdefault("agent_create_calls", 0)
        captured.setdefault("agent_delete_calls", 0)

    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        body: Any = None
        if req.content:
            try:
                body = json.loads(req.content)
            except ValueError:
                body = req.content
        if captured is not None:
            captured["requests"].append(
                {"method": req.method, "path": path, "body": body}
            )

        if path == f"/v1/agents/{HARNESS_AGENT_ID}":
            if captured is not None:
                captured["agent_get_calls"] += 1
            if harness_present:
                return httpx.Response(
                    200,
                    json={
                        "id": HARNESS_AGENT_ID,
                        "name": HARNESS_AGENT_ID,
                        "agent_type": "skill",
                    },
                )
            return httpx.Response(
                404,
                json={
                    "type": "not_found_error",
                    "message": "agent not found",
                },
            )

        # Target-model discovery GET (added in simulate.py _fetch_target_model).
        # Returns a generic agent with a baked model.
        if path.startswith("/v1/agents/") and req.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": path.rsplit("/", 1)[-1],
                    "name": path.rsplit("/", 1)[-1],
                    "agent_type": "skill",
                    "model": "anthropic/claude-haiku-4-5",
                },
            )

        if path == "/v1/agents" and req.method == "POST":
            if captured is not None:
                captured["agent_create_calls"] += 1
            assert isinstance(body, dict)
            agent_id = body.get("name") or "transient-agent"
            return httpx.Response(
                201,
                json={
                    "id": agent_id,
                    "name": agent_id,
                    "agent_type": body.get("agent_type", "skill"),
                },
            )

        if path.startswith("/v1/agents/") and req.method == "DELETE":
            if captured is not None:
                captured["agent_delete_calls"] += 1
            return httpx.Response(204)

        if path == "/v1/messages":
            assert isinstance(body, dict)
            metadata = body.get("metadata") or {}
            role = metadata.get("simulator_role")
            if role == "simulator":
                try:
                    text = next(sim_iter)
                except StopIteration:
                    text = ""
                return httpx.Response(
                    200,
                    json={
                        "id": "msg_sim",
                        **_content_block(text),
                        "usage": {
                            "input_tokens": 10,
                            "output_tokens": 5,
                        },
                    },
                )
            # target
            target_call_count["n"] += 1
            if on_target_call is not None:
                on_target_call(target_call_count["n"])
            try:
                reply = next(tgt_iter)
            except StopIteration:
                reply = ""
            if isinstance(reply, int):
                status = reply
                return httpx.Response(
                    status,
                    json={
                        "type": "upstream_error"
                        if status >= 500
                        else "invalid_request_error",
                        "message": f"forced {status}",
                    },
                )
            return httpx.Response(
                200,
                json={
                    "id": "msg_tgt",
                    **_content_block(reply),
                    "usage": {
                        "input_tokens": 20,
                        "output_tokens": 8,
                    },
                },
            )

        return httpx.Response(
            500,
            json={
                "type": "internal_error",
                "message": f"unexpected {req.method} {path}",
            },
        )

    return handler


def _collect_async_events(client, target_id, archetype, **kwargs):
    """Helper: run async_simulate_stream(...) on anyio.run and return the
    list of TurnEvents in order."""

    async def _drive():
        events: list[TurnEvent] = []
        async for ev in async_simulate_stream(
            client, target_id, archetype, **kwargs
        ):
            events.append(ev)
        return events

    return anyio.run(_drive)


# --------------------------------------------------------------- tests


def test_happy_path_event_order_three_turns_then_outcome() -> None:
    """Success-signal match on turn 3 → 3 simulator + 3 target events,
    then one outcome event last."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=[
            "I'm a PGWP applicant",
            "Yes, common-law partner",
            "Great, please help",
        ],
        target_replies=[
            "Tell me about your case",
            "Any common-law representation?",
            "lawyer matched for QC immigration",
        ],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(
        c, "legal-assistant", _archetype_basic()
    )

    # 3 sim + 3 tgt + 1 outcome = 7 events
    assert len(events) == 7
    expected_kinds = [
        "simulator_turn",
        "target_turn",
        "simulator_turn",
        "target_turn",
        "simulator_turn",
        "target_turn",
        "outcome",
    ]
    assert [ev.kind for ev in events] == expected_kinds

    # Each *_turn event carries role + content; outcome carries the
    # SimulationResult and no per-turn fields.
    for ev in events[:-1]:
        assert ev.role in ("simulator", "target")
        assert ev.content is not None
        assert ev.outcome is None
        assert ev.turn_index is not None
        assert ev.timestamp is not None

    outcome_ev = events[-1]
    assert outcome_ev.kind == "outcome"
    assert outcome_ev.role is None
    assert outcome_ev.content is None
    assert isinstance(outcome_ev.outcome, SimulationResult)
    assert outcome_ev.outcome.outcome == "success"
    assert outcome_ev.outcome.outcome_reason == "success_signal_matched"
    assert "lawyer matched" in outcome_ev.outcome.transcript[-1].content


def test_turn_index_increments_per_event() -> None:
    """Each TurnEvent gets its own turn_index matching transcript position."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["a", "b"],
        target_replies=["x", "lawyer matched done"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(c, "agent", _archetype_basic())

    turn_indices = [ev.turn_index for ev in events if ev.kind != "outcome"]
    assert turn_indices == [0, 1, 2, 3]  # 2 sim + 2 tgt = 4 events


def test_outcome_event_last_on_timeout() -> None:
    """No signal match → timeout outcome event last."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["sim" + str(i) for i in range(10)],
        target_replies=["tgt" + str(i) for i in range(10)],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(
        c, "agent", _archetype_basic(), max_turns=3
    )
    assert events[-1].kind == "outcome"
    assert events[-1].outcome.outcome == "timeout"
    assert events[-1].outcome.outcome_reason == "max_turns_reached: 3"
    # 3 simulator + 3 target turn events + 1 outcome
    assert len(events) == 7


def test_outcome_event_last_on_failure_signal() -> None:
    """Failure-signal match → failure outcome event last."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["I need help"],
        target_replies=["I give up, this is too complex"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(
        c, "agent", _archetype_basic(failure_signals=["I give up"])
    )
    assert events[-1].kind == "outcome"
    assert events[-1].outcome.outcome == "failure"
    assert "I give up" in (events[-1].outcome.outcome_reason or "")


def test_error_path_emits_outcome_does_not_raise() -> None:
    """Target 5xx → outcome event with outcome='error' (NOT raised)."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=[500],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(c, "agent", _archetype_basic())

    # Iteration completes successfully with the error surfaced as data.
    kinds = [ev.kind for ev in events]
    assert kinds[-1] == "outcome"
    outcome = events[-1].outcome
    assert outcome.outcome == "error"
    assert (outcome.outcome_reason or "").startswith("target_agent_error")
    assert outcome.error is not None
    # Should have emitted simulator_turn(0) + target_turn(1) (the empty
    # error placeholder) + outcome.
    assert kinds[0] == "simulator_turn"
    # The target_turn event for the failed turn carries empty content.
    target_events = [ev for ev in events if ev.kind == "target_turn"]
    assert target_events and target_events[-1].content == ""


def test_cancellation_cleans_up_transient_agent() -> None:
    """Caller closes the async iterator mid-loop → transient agent is
    still DELETEd before the iterator finishes."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=False,  # forces transient-agent fallback
        simulator_replies=["s0", "s1", "s2", "s3", "s4"],
        target_replies=["t0", "t1", "t2", "t3", "t4"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    async def _drive_and_break():
        events: list[TurnEvent] = []
        agen = async_simulate_stream(c, "agent", _archetype_basic())
        try:
            async for ev in agen:
                events.append(ev)
                # Stop after the first target_turn — well before
                # max_turns or any signal match.
                if ev.kind == "target_turn":
                    break
        finally:
            await agen.aclose()
        return events

    events = anyio.run(_drive_and_break)
    # Should have seen at least one simulator + one target event, but
    # NO outcome event (we broke out before completion).
    kinds = [ev.kind for ev in events]
    assert "simulator_turn" in kinds
    assert "target_turn" in kinds
    assert "outcome" not in kinds

    # Cleanup contract — the transient agent that was created during
    # wiring must have been DELETEd via the try/finally.
    assert captured["agent_create_calls"] == 1
    assert captured["agent_delete_calls"] == 1


def test_async_iterator_works_under_anyio() -> None:
    """The async iterator integrates with `async for` cleanly."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched ok"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    async def _consume():
        out: list[str] = []
        async for ev in async_simulate_stream(c, "agent", _archetype_basic()):
            out.append(ev.kind)
        return out

    kinds = anyio.run(_consume)
    assert kinds == ["simulator_turn", "target_turn", "outcome"]


def test_sync_iterator_via_anyio_bridge() -> None:
    """`simulate_stream(...)` consumed from sync code yields the same
    sequence as the async variant."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched ok"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    events = list(simulate_stream(c, "agent", _archetype_basic()))
    kinds = [ev.kind for ev in events]
    assert kinds == ["simulator_turn", "target_turn", "outcome"]
    assert isinstance(events[-1].outcome, SimulationResult)
    assert events[-1].outcome.outcome == "success"


def test_client_simulate_stream_true_returns_iterator() -> None:
    """`c.simulate(target, archetype, stream=True)` returns a sync iterator."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched done"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    it = c.simulate("agent", _archetype_basic(), stream=True)
    # not a SimulationResult — it's an iterator
    assert not isinstance(it, SimulationResult)
    assert hasattr(it, "__iter__")
    assert hasattr(it, "__next__") or hasattr(it.__iter__(), "__next__")

    events = list(it)
    assert [ev.kind for ev in events] == [
        "simulator_turn",
        "target_turn",
        "outcome",
    ]


def test_client_simulate_stream_false_still_returns_result() -> None:
    """Backward-compat: stream=False (default) returns SimulationResult."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched done"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    result = c.simulate("agent", _archetype_basic())
    assert isinstance(result, SimulationResult)
    assert result.outcome == "success"


def test_client_async_simulate_stream_true_returns_async_iterator() -> None:
    """`c.async_simulate(target, archetype, stream=True)` returns an
    async iterator (NOT a coroutine)."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched done"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    it = c.async_simulate("agent", _archetype_basic(), stream=True)
    # Must be an async iterator, not a coroutine.
    assert hasattr(it, "__aiter__")

    async def _drain():
        return [ev async for ev in it]

    events = anyio.run(_drain)
    assert [ev.kind for ev in events] == [
        "simulator_turn",
        "target_turn",
        "outcome",
    ]


def test_outcome_carries_full_simulation_result() -> None:
    """The outcome event's SimulationResult has the expected fields."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(c, "my-target", _archetype_basic())
    outcome = events[-1].outcome
    assert outcome.archetype_name == "stream-test-customer"
    assert outcome.target_agent_id == "my-target"
    assert outcome.outcome == "success"
    assert outcome.evaluation_signals["success_signal_match"] is True
    assert outcome.evaluation_signals["turn_count"] == 1
    # Transcript has 2 turns (1 simulator + 1 target).
    assert len(outcome.transcript) == 2


def test_simulator_silent_emits_outcome_event() -> None:
    """Empty simulator reply on turn 1 with no prior match → timeout
    outcome event."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=[""],
        target_replies=["never used"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(c, "agent", _archetype_basic())
    # simulator_turn (empty) + outcome — no target_turn because the
    # loop bails before calling target.
    kinds = [ev.kind for ev in events]
    assert kinds == ["simulator_turn", "outcome"]
    assert events[-1].outcome.outcome == "timeout"
    assert events[-1].outcome.outcome_reason == "simulator_silent"


def test_sync_stream_early_break_cleans_up() -> None:
    """Sync iterator: break out of `for ev in simulate_stream(...)` →
    transient agent is DELETEd via the producer thread's finally."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=False,
        simulator_replies=["s0", "s1", "s2"],
        target_replies=["t0", "t1", "t2"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))

    it = simulate_stream(c, "agent", _archetype_basic())
    consumed: list[TurnEvent] = []
    for ev in it:
        consumed.append(ev)
        if ev.kind == "target_turn":
            break
    # GC the generator — closes it and triggers producer cleanup.
    del it

    # Give the producer thread a brief window to drain its finally.
    # The simulate_stream finally already joins with a 5s timeout, but
    # the consumer break path relies on the next gen consumption to
    # propagate close. In practice the join happens at gc time —
    # poll for the DELETE.
    import time as _time
    deadline = _time.time() + 5.0
    while _time.time() < deadline and captured["agent_delete_calls"] == 0:
        _time.sleep(0.05)

    assert captured["agent_create_calls"] == 1
    assert captured["agent_delete_calls"] == 1


def test_stream_session_id_stable_across_events() -> None:
    """All *_turn events in a single stream share one simulator_session_id
    (carried through Turn.metadata in the final outcome's transcript)."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    events = _collect_async_events(c, "agent", _archetype_basic())
    outcome = events[-1].outcome
    session_ids = {
        t.metadata.get("simulator_session_id") for t in outcome.transcript
    }
    assert len(session_ids) == 1
    assert next(iter(session_ids))  # non-empty
