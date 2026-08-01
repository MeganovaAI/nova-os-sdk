"""Work-product evaluation runner — ``client.evaluate()`` (#30).

Flow, per case:

1. **Produce.** Send ``case.instruction`` + matter context to the target agent,
   capture its work product.
2. **Grade.** Ask a judge agent, in a single call, to return a PASS/FAIL verdict
   for every rubric criterion against that work product.
3. **Aggregate.** Build a :class:`RubricResult` — per-criterion verdicts,
   ``pass_rate``, and ``task_passed`` under the Harvey 100%-of-required rule.

The judge verdict format is one line per criterion — ``<n>: PASS`` or
``<n>: FAIL - <reason>`` — which is robust to parse and easy to mock in tests.
Any criterion the judge doesn't clearly mark PASS is scored as failed
(conservative: ambiguity should not inflate a 100%-threshold pass).
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any

from libraos.simulator.rubric import RubricCase
from libraos.simulator.rubric_types import CriterionResult, RubricResult

if TYPE_CHECKING:
    from libraos.client import Client

_VERDICT_RE = re.compile(r"^\s*(\d+)\s*[:.)\-]\s*(PASS|FAIL)\b(.*)$", re.IGNORECASE)


def _text_of(resp: Any) -> str:
    """Extract assistant text from a /v1/messages reply.

    Handles the canonical block-list shape and the simplified string shape,
    and the typed ``Message`` (which exposes ``.text``). Never raises.
    """
    if resp is None:
        return ""
    text = getattr(resp, "text", None)
    if isinstance(text, str) and text:
        return text
    content = resp.get("content") if isinstance(resp, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _tokens_of(resp: Any) -> tuple[int, int]:
    usage = resp.get("usage") if isinstance(resp, dict) else getattr(resp, "usage", None)
    if isinstance(usage, dict):
        return int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0)
    return 0, 0


def _producer_message(case: RubricCase) -> str:
    parts = [case.instruction.strip()]
    if case.matter.context.strip():
        parts.append("\n\n--- Matter context ---\n" + case.matter.context.strip())
    if case.matter.documents:
        refs = ", ".join(str(d.get("path", d)) for d in case.matter.documents)
        parts.append(f"\n\n--- Referenced documents ---\n{refs}")
    return "".join(parts)


def _judge_prompt(case: RubricCase, work_product: str) -> str:
    lines = [
        "You are a strict senior reviewer grading a work product against a rubric.",
        "For EACH numbered criterion, decide whether the work product satisfies it.",
        "Respond with exactly one line per criterion, in order, formatted as:",
        "  <number>: PASS",
        "  <number>: FAIL - <short reason>",
        "Do not add any other text.\n",
        f"TASK: {case.instruction.strip()}\n",
        "RUBRIC:",
    ]
    for i, c in enumerate(case.rubric, 1):
        lines.append(f"  {i}. {c.criterion}")
    lines.append("\nWORK PRODUCT:\n" + work_product.strip())
    return "\n".join(lines)


def _parse_verdicts(judge_text: str, n: int) -> dict[int, tuple[bool, str]]:
    out: dict[int, tuple[bool, str]] = {}
    for line in judge_text.splitlines():
        m = _VERDICT_RE.match(line)
        if not m:
            continue
        idx = int(m.group(1))
        passed = m.group(2).upper() == "PASS"
        reason = m.group(3).strip(" -\t")
        if 1 <= idx <= n:
            out[idx] = (passed, reason)
    return out


def _build_result(
    case: RubricCase, work_product: str, judge_text: str, in_tok: int, out_tok: int, dur: float
) -> RubricResult:
    verdicts = _parse_verdicts(judge_text, len(case.rubric))
    criteria: list[CriterionResult] = []
    for i, c in enumerate(case.rubric, 1):
        passed, reason = verdicts.get(i, (False, "no verdict from grader"))
        criteria.append(
            CriterionResult(criterion=c.criterion, required=c.required, passed=passed, reason=reason)
        )
    pass_rate = (sum(c.passed for c in criteria) / len(criteria)) if criteria else 0.0
    task_passed = all(c.passed for c in criteria if c.required)
    return RubricResult(
        case_id=case.case_id,
        criteria=criteria,
        task_passed=task_passed,
        pass_rate=pass_rate,
        work_product=work_product,
        input_tokens=in_tok,
        output_tokens=out_tok,
        duration_s=dur,
        metadata={"case_id": case.case_id, "practice_area": case.practice_area},
    )


async def async_evaluate(
    client: "Client",
    target_agent_id: str,
    case: RubricCase,
    *,
    judge_agent_id: str | None = None,
    judge_model: str | None = None,
) -> RubricResult:
    """Async runner behind :meth:`Client.async_evaluate`."""
    started = time.time()
    produce = await client.messages.create(
        target_agent_id,
        messages=[{"role": "user", "content": _producer_message(case)}],
        metadata={"eval": "rubric", "case_id": case.case_id, "role": "producer"},
    )
    work_product = _text_of(produce)
    p_in, p_out = _tokens_of(produce)

    judge = await client.messages.create(
        judge_agent_id or target_agent_id,
        messages=[{"role": "user", "content": _judge_prompt(case, work_product)}],
        model=judge_model,
        metadata={"eval": "rubric", "case_id": case.case_id, "role": "grader"},
    )
    j_in, j_out = _tokens_of(judge)
    return _build_result(
        case, work_product, _text_of(judge), p_in + j_in, p_out + j_out, time.time() - started
    )


def evaluate(
    client: "Client",
    target_agent_id: str,
    case: RubricCase,
    *,
    judge_agent_id: str | None = None,
    judge_model: str | None = None,
) -> RubricResult:
    """Sync runner behind :meth:`Client.evaluate` — see it for the contract."""
    import anyio

    return anyio.run(
        lambda: async_evaluate(
            client, target_agent_id, case, judge_agent_id=judge_agent_id, judge_model=judge_model
        )
    )
