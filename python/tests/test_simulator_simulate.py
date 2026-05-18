"""Tests for ``client.simulate()`` — Track 1.3 + 1.4 (sync loop core).

Covers:

- happy path with success-signal match
- timeout when no termination fires
- failure-signal match
- regex (``re:``) success-signal
- model precedence (archetype.model_override wins)
- 3-key metadata convention (and absence of the dropped keys)
- effective max_turns = min(caller_cap, archetype cap)
- harness-agent wiring path (PRIMARY)
- transient-agent wiring fallback (FALLBACK) — create + delete cycle
- target-side 5xx → outcome="error"
- simulator empty response → success-if-prior-match else timeout
- cleanup on exception path (transient still DELETEd)
"""

from __future__ import annotations

import json
from typing import Any, Callable

import httpx
import pytest

from nova_os import Archetype, Client
from nova_os.simulator import SimulationResult, simulate
from nova_os.simulator._wiring import (
    HARNESS_AGENT_ID,
    _reset_cache_for_tests,
)


# --------------------------------------------------------------- harness


def _mock_transport(handler: Callable[[httpx.Request], httpx.Response]):
    return httpx.MockTransport(handler)


def _content_block(text: str) -> dict[str, Any]:
    """Anthropic-shaped content block."""
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def _archetype_basic(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "name": "test-customer",
        "description": "A test customer for simulator unit tests.",
        "hidden_facts": ["secret fact one"],
        "disclosure_willingness": "cautious",
        "success_signal": "lawyer matched",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def _reset_caches():
    """The wiring module caches agent-id resolution per process.
    Reset between tests so each test exercises the probe path."""
    _reset_cache_for_tests()
    yield
    _reset_cache_for_tests()


def _make_handler(
    *,
    harness_present: bool = True,
    simulator_replies: list[str] | None = None,
    target_replies: list[str | dict[str, Any] | int] | None = None,
    captured: dict[str, Any] | None = None,
) -> Callable[[httpx.Request], httpx.Response]:
    """Build a mock-transport handler that scripts the SDK round-trips.

    Parameters
    ----------
    harness_present:
        Whether ``GET /v1/agents/nova-os-simulator-harness`` returns
        200 (PRIMARY) or 404 (FALLBACK).
    simulator_replies:
        Sequenced list of simulator response texts.
    target_replies:
        Sequenced list of target responses. Each entry is either a
        str (plain text reply), a dict (full response shape), or an
        int (HTTP status to return — for 5xx-mid-loop tests).
    captured:
        If provided, the handler appends every ``{path, method,
        body}`` triple to this dict's "requests" list for assertion.
    """
    sim_iter = iter(simulator_replies or [])
    tgt_iter = iter(target_replies or [])
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

        # ----- agents resource -----
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
        # All other agent GETs return a generic agent with a baked model so the
        # simulator can pass ``model=`` on its target /v1/messages calls.
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

        # ----- /v1/messages — simulator + target both ride here -----
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
            try:
                reply = next(tgt_iter)
            except StopIteration:
                reply = ""
            if isinstance(reply, int):
                status = reply
                return httpx.Response(
                    status,
                    json={
                        "type": "upstream_error" if status >= 500 else "invalid_request_error",
                        "message": f"forced {status}",
                    },
                )
            if isinstance(reply, dict):
                return httpx.Response(200, json=reply)
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

        # Unknown path — fail loudly.
        return httpx.Response(
            500,
            json={
                "type": "internal_error",
                "message": f"unexpected {req.method} {path}",
            },
        )

    return handler


# ------------------------------------------------------------- tests


def test_happy_path_success_signal_matches() -> None:
    """Target replies with success_signal in turn 3 → outcome=success.
    Transcript should have 6 turns (3 simulator + 3 target)."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=True,
        simulator_replies=[
            "hello, I'm a PGWP applicant",
            "I'm looking for a lawyer who can help me with my visa",
            "yes, my partner is in Brazil",
        ],
        target_replies=[
            "tell me about your case",
            "do you have any common-law representation?",
            "lawyer matched for QC immigration — I have a candidate ready",
        ],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result: SimulationResult = c.simulate(
        target_agent_id="legal-assistant",
        archetype=_archetype_basic(),
    )

    assert isinstance(result, SimulationResult)
    assert result.outcome == "success"
    assert result.outcome_reason == "success_signal_matched"
    assert result.evaluation_signals["success_signal_match"] is True
    assert result.evaluation_signals["turn_count"] == 3
    assert len(result.transcript) == 6
    assert result.transcript[0].role == "simulator"
    assert result.transcript[1].role == "target"
    assert result.transcript[-1].role == "target"
    assert "lawyer matched" in result.transcript[-1].content
    # session id must be present on every turn metadata
    session_ids = {t.metadata.get("simulator_session_id") for t in result.transcript}
    assert len(session_ids) == 1
    assert next(iter(session_ids))  # non-empty


def test_timeout_when_no_termination_fires() -> None:
    """No success / failure ever matches → outcome=timeout at max_turns."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["msg" + str(i) for i in range(15)],
        target_replies=["reply" + str(i) for i in range(15)],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(),
        max_turns=10,
    )
    assert result.outcome == "timeout"
    assert result.outcome_reason == "max_turns_reached: 10"
    assert result.evaluation_signals["turn_count"] == 10
    assert len(result.transcript) == 20  # 10 simulator + 10 target


def test_failure_signal_match() -> None:
    """Target says 'I give up' → outcome=failure."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["I need help"],
        target_replies=["I give up, this is too complex"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(failure_signals=["I give up"]),
    )
    assert result.outcome == "failure"
    assert "I give up" in (result.outcome_reason or "")
    assert result.evaluation_signals["failure_signal_matches"] == ["I give up"]


def test_success_signal_as_regex() -> None:
    """re:-prefixed signals compile and match via re.search, case-insensitive."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["I need help"],
        target_replies=[
            "lawyer matched for QC immigration with spousal representation"
        ],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(
            success_signal=r"re:lawyer matched.*(common-law|spousal)"
        ),
    )
    assert result.outcome == "success"
    assert result.outcome_reason == "success_signal_matched"


def test_model_precedence_archetype_wins() -> None:
    """When archetype.model_override is set, simulate(simulator_model=...) loses.

    The /chat for simulator should use the archetype's model.
    """
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched — done"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(model_override="anthropic/claude-sonnet-4-6"),
        simulator_model="anthropic/claude-haiku-4-5",
    )
    # Find the first /v1/messages POST with simulator_role=simulator.
    sim_bodies = [
        r["body"]
        for r in captured["requests"]
        if r["path"] == "/v1/messages"
        and r["method"] == "POST"
        and r["body"]
        and (r["body"].get("metadata") or {}).get("simulator_role") == "simulator"
    ]
    assert sim_bodies, "no simulator-side /v1/messages call captured"
    assert sim_bodies[0]["model"] == "anthropic/claude-sonnet-4-6"


def test_metadata_three_key_set_only() -> None:
    """Every /chat call carries the 3 simulator metadata keys, and NOT the dropped legacy keys."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    c.simulate(target_agent_id="agent", archetype=_archetype_basic())

    chat_calls = [
        r for r in captured["requests"] if r["path"] == "/v1/messages"
    ]
    assert len(chat_calls) >= 2  # at least simulator + target
    for call in chat_calls:
        meta = (call["body"] or {}).get("metadata") or {}
        # the three required keys
        assert "simulator_session_id" in meta
        assert "simulator_role" in meta
        assert "simulator_turn_index" in meta
        assert meta["simulator_role"] in ("simulator", "target")
        assert isinstance(meta["simulator_turn_index"], int)
        # legacy keys must be absent
        assert "simulator_run" not in meta
        assert "simulator_archetype" not in meta
        assert "simulator_target" not in meta


def test_effective_max_turns_archetype_tighter() -> None:
    """archetype cap of 5 + caller cap of 10 → loop caps at 5."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["s" + str(i) for i in range(10)],
        target_replies=["t" + str(i) for i in range(10)],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(termination_conditions={"max_turns": 5}),
        max_turns=10,
    )
    assert result.outcome == "timeout"
    assert result.outcome_reason == "max_turns_reached: 5"
    assert result.evaluation_signals["turn_count"] == 5


def test_wiring_fallback_creates_and_deletes_transient_agent() -> None:
    """When harness GET returns 404, SDK creates a transient agent and deletes it."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=False,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(target_agent_id="agent", archetype=_archetype_basic())
    assert result.outcome == "success"
    assert captured["agent_get_calls"] == 1
    assert captured["agent_create_calls"] == 1
    assert captured["agent_delete_calls"] == 1


def test_target_5xx_returns_error_outcome() -> None:
    """Target returns HTTP 500 mid-loop → outcome=error, reason starts with target_agent_error."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=[500],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(target_agent_id="agent", archetype=_archetype_basic())
    assert result.outcome == "error"
    assert (result.outcome_reason or "").startswith("target_agent_error")
    assert result.error is not None
    # The transcript should still contain the simulator turn that was
    # made before the target call failed, plus an error placeholder.
    assert any(
        t.role == "target" and t.metadata.get("error") for t in result.transcript
    )


def test_simulator_empty_response_no_prior_match_yields_timeout() -> None:
    """Empty simulator response on turn 1 → outcome=timeout, reason=simulator_silent."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=[""],
        target_replies=["reply"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    result = c.simulate(target_agent_id="agent", archetype=_archetype_basic())
    assert result.outcome == "timeout"
    assert result.outcome_reason == "simulator_silent"


def test_cleanup_on_simulator_error_still_deletes_transient() -> None:
    """When the loop hits an error path, the transient agent is STILL deleted."""
    captured: dict[str, Any] = {}

    # All simulator calls raise → SDK retries once, then surfaces error.
    # We achieve "raise" by returning a 500 for the simulator role.
    sim_calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        body: Any = None
        if req.content:
            try:
                body = json.loads(req.content)
            except ValueError:
                body = req.content
        captured.setdefault("agent_get_calls", 0)
        captured.setdefault("agent_create_calls", 0)
        captured.setdefault("agent_delete_calls", 0)

        if path == f"/v1/agents/{HARNESS_AGENT_ID}":
            captured["agent_get_calls"] += 1
            return httpx.Response(
                404,
                json={"type": "not_found_error", "message": "no harness"},
            )
        if path == "/v1/agents" and req.method == "POST":
            captured["agent_create_calls"] += 1
            return httpx.Response(
                201,
                json={
                    "id": (body or {}).get("name") or "transient",
                    "name": (body or {}).get("name") or "transient",
                },
            )
        if path.startswith("/v1/agents/") and req.method == "DELETE":
            captured["agent_delete_calls"] += 1
            return httpx.Response(204)
        if path == "/v1/messages":
            metadata = (body or {}).get("metadata") or {}
            if metadata.get("simulator_role") == "simulator":
                sim_calls["n"] += 1
                return httpx.Response(
                    500,
                    json={
                        "type": "upstream_error",
                        "message": "simulator down",
                    },
                )
            # target side — never reached but defensively reply
            return httpx.Response(200, json={"content": "ignored"})
        return httpx.Response(500)

    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    # Pass target_model explicitly — this minimal handler doesn't mock the
    # GET /v1/agents/<target> path. The simulator-error path doesn't reach
    # the target side anyway, so the model value is irrelevant here.
    result = c.simulate(
        target_agent_id="agent",
        archetype=_archetype_basic(),
        target_model="anthropic/claude-haiku-4-5",
    )
    # outcome=error because both simulator attempts failed
    assert result.outcome == "error"
    assert (result.outcome_reason or "").startswith("simulator_error")
    # transient agent was created AND deleted despite the error
    assert captured["agent_create_calls"] == 1
    assert captured["agent_delete_calls"] == 1


def test_simulate_accepts_archetype_instance() -> None:
    """Direct Archetype instance flows through without re-validation surprise."""
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    arche = Archetype.from_dict(_archetype_basic())
    result = c.simulate(target_agent_id="agent", archetype=arche)
    assert result.outcome == "success"
    assert result.archetype_name == "test-customer"


def test_invalid_archetype_dict_raises_before_any_chat_call() -> None:
    """A bogus archetype dict raises ArchetypeValidationError before /chat fires."""
    from nova_os import ArchetypeValidationError

    called: dict[str, int] = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        called["n"] += 1
        return httpx.Response(200, json={"content": "should not happen"})

    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    with pytest.raises(ArchetypeValidationError):
        c.simulate(
            target_agent_id="agent",
            archetype={
                # missing required hidden_facts, disclosure_willingness, success_signal
                "name": "broken",
                "description": "x",
            },
        )
    assert called["n"] == 0


def test_target_agent_id_propagates_to_messages_create() -> None:
    """Each target /v1/messages call carries metadata.agent_id = target_agent_id (per Messages resource convention)."""
    captured: dict[str, Any] = {}
    handler = _make_handler(
        harness_present=True,
        simulator_replies=["hi"],
        target_replies=["lawyer matched"],
        captured=captured,
    )
    c = Client("https://eval.local", "key", transport=_mock_transport(handler))
    c.simulate(target_agent_id="my-target", archetype=_archetype_basic())
    target_bodies = [
        r["body"]
        for r in captured["requests"]
        if r["path"] == "/v1/messages"
        and (r["body"] or {}).get("metadata", {}).get("simulator_role") == "target"
    ]
    assert target_bodies
    for body in target_bodies:
        assert body["metadata"]["agent_id"] == "my-target"
