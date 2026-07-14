#!/usr/bin/env python3
"""examples/simulator/run_eval.py — canonical CI example for the synthetic-customer simulator.

Loads each archetype under ``examples/simulator/``, runs
``client.simulate(stream=True)`` against a target agent on a SEPARATE
evaluation ``nova-os`` instance, streams turn events to stdout, and
writes the full transcript + outcome to ``output/<archetype-name>.json``.

Two-instance pattern
--------------------
Production traffic and evaluation traffic must not share a database.
The recommended deployment is a sibling ``docker-compose`` service that
brings up a second ``nova-os`` on port 8901 with its own PostgreSQL
database, gateway key, and empty knowledge collections. See the
public template in the
`nova-os-stack repo <https://github.com/MeganovaAI/nova-os-stack>`__
(``docker-compose.eval.yaml``).

This script connects to the EVAL instance only — it never touches
production. Apps that need both surfaces typically keep two ``Client``
instances side-by-side::

    prod_client = Client(base_url=os.environ["PROD_NOVA_BASE_URL"], api_key=...)
    eval_client = Client(base_url=os.environ["EVAL_NOVA_BASE_URL"], api_key=...)
    # … but only eval_client gets passed to simulate().
    result = eval_client.simulate(target_agent_id=..., archetype=...)

We deliberately don't construct a prod_client in this example: any
``simulate()`` call against production accumulates eval traffic in the
prod ``call_log`` table, which is what the separation is meant to
avoid.

Environment
-----------
Required:

* ``EVAL_NOVA_BASE_URL`` — base URL of the eval nova-os, e.g.
  ``http://localhost:8901``.
* ``EVAL_NOVA_API_KEY``  — eval-instance JWT bearer or agent api-key.

Optional:

* ``EVAL_TARGET_AGENT_ID`` — target agent under test (default
  ``"default"``).
* ``EVAL_MAX_TURNS`` — per-archetype max-turn cap (default ``10``).
* ``EVAL_SIMULATOR_MODEL`` — simulator-side LLM
  (default ``"anthropic/claude-haiku-4-5"``).
* ``EVAL_OUTPUT_DIR`` — where to write transcripts (default ``./output``).

Exit code
---------
``0`` if every archetype terminates with an outcome other than
``"error"``. ``1`` if any archetype errors out (transport failure,
unreachable eval instance, etc.) — those are surfaced via the
``outcome`` event per the streaming contract, not via raised
exceptions.

Run
---
::

    pip install libraos-sdk
    export EVAL_NOVA_BASE_URL=http://localhost:8901
    export EVAL_NOVA_API_KEY=<your eval JWT or agent key>
    export EVAL_TARGET_AGENT_ID=default
    python examples/simulator/run_eval.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from libraos import Archetype, Client
from libraos.simulator import SimulationResult, TurnEvent


def main() -> int:
    # 1. Read configuration. We construct ONLY the eval client — see the
    #    module docstring for the two-client rationale.
    base_url = os.environ.get("EVAL_NOVA_BASE_URL", "http://localhost:8901")
    api_key = os.environ.get("EVAL_NOVA_API_KEY")
    if not api_key:
        print("error: EVAL_NOVA_API_KEY is required", file=sys.stderr)
        return 2

    target = os.environ.get("EVAL_TARGET_AGENT_ID", "default")
    max_turns = int(os.environ.get("EVAL_MAX_TURNS", "10"))
    simulator_model = os.environ.get(
        "EVAL_SIMULATOR_MODEL", "anthropic/claude-haiku-4-5"
    )
    output_dir = Path(os.environ.get("EVAL_OUTPUT_DIR", "./output"))
    output_dir.mkdir(exist_ok=True, parents=True)

    eval_client = Client(base_url=base_url, api_key=api_key)

    # 2. Discover archetypes. We pick up every *.yaml sibling so partners
    #    can drop new archetypes into examples/simulator/ without editing
    #    this script.
    archetype_dir = Path(__file__).resolve().parent
    archetype_files = sorted(archetype_dir.glob("*.yaml"))
    if not archetype_files:
        print(f"error: no archetypes found in {archetype_dir}", file=sys.stderr)
        return 1

    print(f"Eval target:     {target}")
    print(f"Eval base URL:   {base_url}")
    print(f"Simulator model: {simulator_model}")
    print(f"Max turns:       {max_turns}")
    print(f"Archetypes:      {len(archetype_files)}")

    # 3. Run each archetype. Streaming mode lets partners watch a live
    #    CI run; the loop also records each outcome row for the summary
    #    table at the end.
    summary: list[dict[str, Any]] = []
    any_error = False

    for path in archetype_files:
        print(f"\n{'=' * 72}")
        print(f"Archetype: {path.name}")
        print("=" * 72)

        archetype = Archetype.from_yaml_path(str(path))

        turn_count = 0
        final_outcome: SimulationResult | None = None
        started = datetime.now(timezone.utc)

        # Streaming variant — per spec §F, the iterator never raises
        # on in-loop failures; transport / target errors arrive as
        # outcome events with outcome="error".
        for event in eval_client.simulate(
            target_agent_id=target,
            archetype=archetype,
            stream=True,
            max_turns=max_turns,
            simulator_model=simulator_model,
        ):
            # mypy / pyright hint — narrows event for the branches below.
            assert isinstance(event, TurnEvent)

            if event.kind == "simulator_turn":
                turn_count += 1
                preview = (event.content or "").replace("\n", " ")[:160]
                print(f"  [{turn_count:2d}] SIMULATOR: {preview}")
            elif event.kind == "target_turn":
                turn_count += 1
                preview = (event.content or "").replace("\n", " ")[:160]
                print(f"  [{turn_count:2d}] TARGET:    {preview}")
            elif event.kind == "outcome":
                final_outcome = event.outcome

        # The streaming contract guarantees exactly one outcome event
        # as the final event — even on cancellation / error.
        assert final_outcome is not None, (
            "simulate(stream=True) must always yield a final outcome event"
        )

        print(f"  outcome:  {final_outcome.outcome}")
        print(f"  reason:   {final_outcome.outcome_reason or '-'}")
        print(f"  turns:    {len(final_outcome.transcript)}")
        print(f"  duration: {final_outcome.duration_ms}ms")
        if final_outcome.error:
            print(f"  error:    {final_outcome.error}")

        if final_outcome.outcome == "error":
            any_error = True

        # Persist the transcript. JSON is the canonical CI artefact —
        # partners can diff it across model releases or feed it into a
        # downstream judge / regression suite.
        out_path = output_dir / f"{archetype.name}.json"
        out_path.write_text(
            json.dumps(
                {
                    "archetype": archetype.name,
                    "target_agent_id": final_outcome.target_agent_id,
                    "outcome": final_outcome.outcome,
                    "outcome_reason": final_outcome.outcome_reason,
                    "evaluation_signals": final_outcome.evaluation_signals,
                    "duration_ms": final_outcome.duration_ms,
                    "tokens_used": final_outcome.tokens_used,
                    "error": final_outcome.error,
                    "started": started.isoformat(),
                    "transcript": [
                        {
                            "role": turn.role,
                            "content": turn.content,
                            "timestamp": turn.timestamp,
                            "metadata": turn.metadata,
                        }
                        for turn in final_outcome.transcript
                    ],
                },
                indent=2,
            )
            + "\n"
        )
        print(f"  wrote:    {out_path}")

        summary.append(
            {
                "archetype": archetype.name,
                "outcome": final_outcome.outcome,
                "turns": len(final_outcome.transcript),
                "duration_ms": final_outcome.duration_ms,
                "success_signal_matched": bool(
                    final_outcome.evaluation_signals.get("success_signal_match")
                ),
            }
        )

    # 4. Summary table — easy to grep in CI logs.
    print(f"\n{'=' * 72}")
    print("SUMMARY")
    print("=" * 72)
    header = f"{'archetype':45s} {'outcome':10s} {'turns':>6s} {'duration':>10s} {'success':>8s}"
    print(header)
    print("-" * len(header))
    for row in summary:
        print(
            f"{row['archetype']:45s} "
            f"{row['outcome']:10s} "
            f"{row['turns']:>6d} "
            f"{row['duration_ms']:>8d}ms "
            f"{str(row['success_signal_matched']):>8s}"
        )

    counts: dict[str, int] = {}
    for row in summary:
        counts[row["outcome"]] = counts.get(row["outcome"], 0) + 1
    print(f"\nCounts: {counts}")

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
