"""Loop runner for the synthetic-customer simulator.

The loop alternates simulator-side and target-side ``/v1/messages``
calls until one of three termination conditions fires (in order):

1. ``success_signal`` matches in the target's most recent response.
2. ``failure_signals`` match in the target's most recent response
   (combine rule per archetype's ``failure_signal_match`` — ``any`` /
   ``all``; default ``any``).
3. The effective turn cap is reached.

A fourth outcome — ``"error"`` — fires when transport calls fail
unrecoverably (target 5xx; simulator double-failure). See the
``run_loop`` docstring for the full failure table.

The runner is async because the underlying ``Client`` is async; the
public ``simulate()`` helper wraps this in ``anyio.run`` for sync
partners. See ``simulate.py``.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, AsyncIterator

from nova_os.errors import NovaOSError
from nova_os.simulator._signals import (
    all_signals_match,
    any_signal_matches,
    signal_matches,
)
from nova_os.simulator.archetype import Archetype
from nova_os.simulator.types import SimulationResult, Turn, TurnEvent

if TYPE_CHECKING:
    from nova_os.client import Client


_TARGET_4XX_RETRIES = 3
_SIMULATOR_RETRIES = 1  # one extra attempt after the initial call


async def run_loop(
    client: "Client",
    *,
    target_agent_id: str,
    archetype: Archetype,
    simulator_agent_id: str,
    simulator_system_prompt: str,
    effective_max_turns: int,
    simulator_model: str,
    session_id: str,
    metadata: dict[str, Any] | None,
    target_api_key: str | None,  # reserved — surfaced for symmetry with the public signature, currently piggybacks on the client default
) -> SimulationResult:
    """Drive the simulator ↔ target loop and return a SimulationResult.

    Thin aggregator over :func:`stream_loop` — the streaming variant
    is the canonical implementation. ``run_loop`` consumes the async
    iterator and returns the final ``outcome`` event's
    :class:`SimulationResult`. See ``stream_loop`` for the loop body
    and failure-handling table.
    """
    result: SimulationResult | None = None
    async for ev in stream_loop(
        client,
        target_agent_id=target_agent_id,
        archetype=archetype,
        simulator_agent_id=simulator_agent_id,
        simulator_system_prompt=simulator_system_prompt,
        effective_max_turns=effective_max_turns,
        simulator_model=simulator_model,
        session_id=session_id,
        metadata=metadata,
        target_api_key=target_api_key,
    ):
        if ev.kind == "outcome":
            result = ev.outcome
    # stream_loop guarantees exactly one outcome event; the assertion
    # is defensive — if it ever fires the streaming layer has a bug.
    assert result is not None, "stream_loop did not emit an outcome event"
    return result


async def stream_loop(
    client: "Client",
    *,
    target_agent_id: str,
    archetype: Archetype,
    simulator_agent_id: str,
    simulator_system_prompt: str,
    effective_max_turns: int,
    simulator_model: str,
    session_id: str,
    metadata: dict[str, Any] | None,
    target_api_key: str | None,  # reserved — surfaced for symmetry with the public signature, currently piggybacks on the client default
) -> AsyncIterator[TurnEvent]:
    """Async-iterator variant of :func:`run_loop`. Yields per-turn events.

    Event sequence per turn (in order): ``simulator_turn`` →
    ``target_turn``. After the loop terminates (success / failure /
    timeout / error / simulator-silent), exactly one ``outcome`` event
    is emitted as the LAST event, carrying the full materialised
    :class:`SimulationResult`. Errors are NEVER raised through the
    iterator — they are surfaced via ``outcome``'s ``outcome=="error"``
    state (per spec §F: partners handle failed simulations as data).

    Cancellation: if the consumer stops iterating early (``break`` out
    of ``async for`` or ``await it.aclose()``), the underlying
    asynchronous-generator protocol fires ``GeneratorExit`` inside the
    body and the helper raises out cleanly. Caller-owned cleanup (eg.
    transient-agent DELETE) runs in the outer ``try/finally`` in
    :func:`async_simulate_stream` — not inside this iterator — so it
    fires deterministically whether the iterator is exhausted, broken
    out of, or aclose'd.

    Failure handling (per the v1 spec table):

    +-----------------------------+----------------------------------+---------------------------+
    | Failure                     | Action                           | Resulting outcome         |
    +=============================+==================================+===========================+
    | target_agent 5xx            | record error turn, return        | ``"error"``               |
    | target_agent 4xx            | exp-backoff up to 3 retries      | ``"error"`` if all fail   |
    | simulator LLM 5xx/timeout   | retry once                       | ``"error"`` if both fail  |
    | simulator returns empty     | treat as silent                  | ``"success"`` if         |
    |                             |                                  | matched previously else  |
    |                             |                                  | ``"timeout"``             |
    | max_turns reached           | clean exit                       | ``"timeout"``             |
    | success_signal match        | clean exit                       | ``"success"``             |
    | failure_signal match        | clean exit                       | ``"failure"``             |
    +-----------------------------+----------------------------------+---------------------------+

    The order in step 5.f of the spec is enforced strictly: success
    is checked first, then failure, then timeout.
    """
    started_ns = time.perf_counter_ns()

    transcript: list[Turn] = []
    simulator_messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": (
                "You are about to start a conversation. Send your opening "
                "message."
            ),
        }
    ]

    success_matched = False
    matched_failure_signals: list[str] = []
    success_signal_was_matched_earlier = False

    tokens_used = {
        "simulator_input": 0,
        "simulator_output": 0,
        "target_input": 0,
        "target_output": 0,
    }

    base_metadata = dict(metadata or {})

    outcome: str | None = None
    outcome_reason: str | None = None
    error_msg: str | None = None

    turn_count = 0

    try:
        for turn_index in range(effective_max_turns):
            turn_count = turn_index + 1

            # ----- (a) simulator turn -----
            sim_metadata = {
                **base_metadata,
                "simulator_session_id": session_id,
                "simulator_role": "simulator",
                "simulator_turn_index": turn_index,
            }
            sim_response, sim_err = await _call_with_retries(
                _call_simulator,
                client=client,
                agent_id=simulator_agent_id,
                system=simulator_system_prompt,
                messages=simulator_messages,
                model=simulator_model,
                metadata=sim_metadata,
                retries=_SIMULATOR_RETRIES,
            )

            if sim_err is not None:
                outcome = "error"
                outcome_reason = f"simulator_error: {sim_err}"
                error_msg = str(sim_err)
                err_ts = time.time()
                transcript.append(
                    Turn(
                        role="simulator",
                        content="",
                        timestamp=err_ts,
                        metadata={**sim_metadata, "error": True},
                    )
                )
                yield TurnEvent(
                    kind="simulator_turn",
                    role="simulator",
                    content="",
                    turn_index=len(transcript) - 1,
                    timestamp=err_ts,
                )
                break

            sim_text, sim_in, sim_out = _extract_text_and_tokens(sim_response)
            tokens_used["simulator_input"] += sim_in
            tokens_used["simulator_output"] += sim_out

            sim_ts = time.time()
            transcript.append(
                Turn(
                    role="simulator",
                    content=sim_text,
                    timestamp=sim_ts,
                    metadata=sim_metadata,
                )
            )
            yield TurnEvent(
                kind="simulator_turn",
                role="simulator",
                content=sim_text,
                turn_index=len(transcript) - 1,
                timestamp=sim_ts,
            )

            # Empty simulator response → terminate per failure-mode rule
            # "simulator_silent". Per spec F: outcome = success if signal
            # was matched in a PRIOR turn; else timeout.
            if not sim_text.strip():
                if success_signal_was_matched_earlier:
                    outcome = "success"
                    outcome_reason = "simulator_silent"
                else:
                    outcome = "timeout"
                    outcome_reason = "simulator_silent"
                break

            # Append to simulator history so subsequent simulator calls
            # see what it just produced as the assistant turn.
            simulator_messages.append(
                {"role": "assistant", "content": sim_text}
            )

            # ----- (b) target turn -----
            tgt_metadata = {
                **base_metadata,
                "simulator_session_id": session_id,
                "simulator_role": "target",
                "simulator_turn_index": turn_index,
            }

            target_messages = _transcript_as_target_sees_it(transcript)

            tgt_response, tgt_err = await _call_target_with_retries(
                client=client,
                agent_id=target_agent_id,
                messages=target_messages,
                metadata=tgt_metadata,
            )

            if tgt_err is not None:
                outcome = "error"
                outcome_reason = tgt_err  # already prefixed
                error_msg = tgt_err
                err_ts = time.time()
                transcript.append(
                    Turn(
                        role="target",
                        content="",
                        timestamp=err_ts,
                        metadata={**tgt_metadata, "error": True},
                    )
                )
                yield TurnEvent(
                    kind="target_turn",
                    role="target",
                    content="",
                    turn_index=len(transcript) - 1,
                    timestamp=err_ts,
                )
                break

            tgt_text, tgt_in, tgt_out = _extract_text_and_tokens(tgt_response)
            tokens_used["target_input"] += tgt_in
            tokens_used["target_output"] += tgt_out

            tgt_ts = time.time()
            transcript.append(
                Turn(
                    role="target",
                    content=tgt_text,
                    timestamp=tgt_ts,
                    metadata=tgt_metadata,
                )
            )
            yield TurnEvent(
                kind="target_turn",
                role="target",
                content=tgt_text,
                turn_index=len(transcript) - 1,
                timestamp=tgt_ts,
            )

            # Feed target's reply back to the simulator as user.
            simulator_messages.append(
                {"role": "user", "content": tgt_text}
            )

            # ----- (f) termination checks, in spec order -----
            # 1. success_signal in target response
            if signal_matches(archetype.success_signal, tgt_text):
                success_matched = True
                success_signal_was_matched_earlier = True
                outcome = "success"
                outcome_reason = "success_signal_matched"
                break

            # 2. failure_signals in target response (any/all)
            if archetype.failure_signals:
                combine = (
                    archetype.termination_conditions.failure_signal_match
                    if archetype.termination_conditions
                    and archetype.termination_conditions.failure_signal_match
                    is not None
                    else "any"
                )
                if combine == "all":
                    matched_all, matched = all_signals_match(
                        archetype.failure_signals, tgt_text
                    )
                    if matched_all:
                        matched_failure_signals = matched
                        outcome = "failure"
                        outcome_reason = (
                            "failure_signal_matched: "
                            + ", ".join(matched)
                        )
                        break
                else:
                    matched_any, first = any_signal_matches(
                        archetype.failure_signals, tgt_text
                    )
                    if matched_any:
                        matched_failure_signals = [first] if first else []
                        outcome = "failure"
                        outcome_reason = (
                            f"failure_signal_matched: {first}"
                        )
                        break

            # 3. turn cap — checked implicitly by the for-loop bounds;
            # set the outcome on natural loop exit below.

        if outcome is None:
            outcome = "timeout"
            outcome_reason = f"max_turns_reached: {effective_max_turns}"

    except Exception as exc:  # noqa: BLE001 — defensive: never raise during the loop
        outcome = "error"
        outcome_reason = f"simulator_error: {exc}"
        error_msg = str(exc)

    duration_ms = (time.perf_counter_ns() - started_ns) // 1_000_000

    evaluation_signals: dict[str, Any] = {
        "success_signal_match": success_matched,
        "failure_signal_matches": matched_failure_signals,
        "turn_count": turn_count,
    }

    result = SimulationResult(
        archetype_name=archetype.name,
        target_agent_id=target_agent_id,
        transcript=transcript,
        outcome=outcome,  # type: ignore[arg-type]
        outcome_reason=outcome_reason,
        evaluation_signals=evaluation_signals,
        duration_ms=int(duration_ms),
        tokens_used=tokens_used,
        error=error_msg,
    )
    yield TurnEvent(kind="outcome", outcome=result)


# --------------------------------------------------------------- chat calls


async def _call_simulator(
    *,
    client: "Client",
    agent_id: str,
    system: str,
    messages: list[dict[str, Any]],
    model: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """One /v1/messages call against the simulator harness/transient."""
    return await client.messages.create(
        agent_id,
        messages=messages,
        model=model,
        system=system,
        metadata=metadata,
    )


async def _call_target(
    *,
    client: "Client",
    agent_id: str,
    messages: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """One /v1/messages call against the target agent (no extra system)."""
    return await client.messages.create(
        agent_id,
        messages=messages,
        metadata=metadata,
    )


async def _call_with_retries(
    fn,
    *,
    retries: int,
    **kwargs: Any,
) -> tuple[dict[str, Any] | None, str | None]:
    """Run ``fn(**kwargs)`` up to ``retries+1`` total attempts.

    Returns ``(response, None)`` on eventual success or
    ``(None, last_error)`` after exhausting retries. Retries on any
    exception — the simulator side treats both 5xx and timeouts as
    retryable (per spec F).
    """
    last_err: BaseException | None = None
    for attempt in range(retries + 1):
        try:
            resp = await fn(**kwargs)
            return resp, None
        except BaseException as exc:  # noqa: BLE001
            last_err = exc
            # Small sleep between retries — keeps the simulator from
            # hammering an upstream that's mid-recovery without
            # ballooning total wall-clock.
            if attempt < retries:
                await asyncio.sleep(0.1 * (attempt + 1))
    return None, _format_exc(last_err)


async def _call_target_with_retries(
    *,
    client: "Client",
    agent_id: str,
    messages: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """Target-side retry logic per spec F.

    5xx → no retry; return ``"target_agent_error: <status>"``.
    4xx → retry up to 3 times w/ exponential backoff; if all fail,
    return ``"target_agent_4xx_unrecoverable: <body excerpt>"``.
    Other transport errors → retry once silently per the "network
    jitter" row.
    """
    backoff = 0.2
    for attempt in range(_TARGET_4XX_RETRIES + 1):
        try:
            resp = await _call_target(
                client=client,
                agent_id=agent_id,
                messages=messages,
                metadata=metadata,
            )
            return resp, None
        except NovaOSError as exc:
            status = getattr(exc, "status", None)
            if status is not None and 500 <= int(status) < 600:
                # 5xx — return immediately per spec.
                return None, f"target_agent_error: {status}"
            if status is not None and 400 <= int(status) < 500:
                # 4xx — retry path.
                if attempt < _TARGET_4XX_RETRIES:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return (
                    None,
                    f"target_agent_4xx_unrecoverable: {str(exc)[:200]}",
                )
            # Other typed error — treat as a generic transient.
            if attempt < _TARGET_4XX_RETRIES:
                await asyncio.sleep(backoff)
                backoff *= 2
                continue
            return None, f"target_agent_error: {exc}"
        except BaseException as exc:  # noqa: BLE001
            # Transport-level (timeout / connect error). Retry once
            # silently per spec "network jitter"; second failure
            # surfaces as an error.
            if attempt < 1:
                await asyncio.sleep(backoff)
                backoff *= 2
                continue
            return None, f"target_agent_error: {_format_exc(exc)}"
    # Defensive — should never reach here.
    return None, "target_agent_error: retry loop exhausted"


def _format_exc(exc: BaseException | None) -> str:
    if exc is None:
        return "unknown"
    return f"{type(exc).__name__}: {exc}"


# ------------------------------------------------------------- helpers


def _extract_text_and_tokens(
    response: dict[str, Any]
) -> tuple[str, int, int]:
    """Pull the assistant text + token counts from a /v1/messages reply.

    Defensively handles both shapes the SDK sees in the wild:

    - Anthropic-canonical: ``content`` is a list of content blocks
      with ``{"type": "text", "text": "..."}``.
    - Simplified: ``content`` is a plain string (used in tests + by
      some early server builds).

    Token fields under ``usage.input_tokens`` / ``output_tokens``;
    missing → 0.
    """
    text = ""
    content = response.get("content") if isinstance(response, dict) else None
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        chunks: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text")
                if isinstance(t, str):
                    chunks.append(t)
        text = "".join(chunks)
    elif isinstance(response, dict) and isinstance(
        response.get("text"), str
    ):
        text = response["text"]

    usage = (
        response.get("usage") if isinstance(response, dict) else None
    ) or {}
    in_tokens = int(usage.get("input_tokens") or 0) if isinstance(
        usage, dict
    ) else 0
    out_tokens = int(usage.get("output_tokens") or 0) if isinstance(
        usage, dict
    ) else 0

    return text, in_tokens, out_tokens


def _transcript_as_target_sees_it(
    transcript: list[Turn],
) -> list[dict[str, Any]]:
    """Map transcript to messages-from-the-target's-POV.

    Simulator turns → ``role: "user"``. Target's prior turns →
    ``role: "assistant"``. The current incoming simulator turn is
    always the trailing message; the just-appended simulator Turn is
    therefore last in the input ``transcript`` slice when this is
    called.
    """
    out: list[dict[str, Any]] = []
    for turn in transcript:
        if turn.role == "simulator":
            out.append({"role": "user", "content": turn.content})
        else:
            out.append({"role": "assistant", "content": turn.content})
    return out


__all__ = ["run_loop", "stream_loop"]
