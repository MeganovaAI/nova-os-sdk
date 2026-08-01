"""Rubric-grading harness — client.evaluate() (#30).

The producer and grader are both `messages.create` calls; the mock transport
routes on `metadata.role` to return a fixed work product and a fixed judge
verdict block, so the harness's aggregation is tested deterministically.
"""

from __future__ import annotations

import json

import httpx
import pytest

from libraos import Client, RubricCase, RubricResult, load_rubric_pack
from libraos.simulator import RubricValidationError

CASE = RubricCase.from_dict(
    {
        "case_id": "msa-review",
        "practice_area": "commercial",
        "instruction": "Review the MSA and list every issue.",
        "matter": {"context": "The vendor MSA has an uncapped liability clause."},
        "expected_work_product_shape": "legal-memo",
        "rubric": [
            {"criterion": "flags the uncapped liability clause", "required": True},
            {"criterion": "references the indemnity section", "required": True},
            {"criterion": "notes the auto-renewal", "required": False},
        ],
    }
)


def _transport(work_product: str, judge_block: str) -> httpx.MockTransport:
    def handler(req: httpx.Request) -> httpx.Response:
        body = json.loads(req.content)
        role = body.get("metadata", {}).get("role")
        text = work_product if role == "producer" else judge_block
        return httpx.Response(
            200,
            json={"id": "m", "role": "assistant", "model": "j",
                  "content": [{"type": "text", "text": text}],
                  "usage": {"input_tokens": 5, "output_tokens": 7}},
        )
    return httpx.MockTransport(handler)


def _run(work_product: str, judge_block: str) -> RubricResult:
    c = Client("https://eval.local", "k", transport=_transport(work_product, judge_block))
    return c.evaluate("legal-assistant", CASE)


def test_all_pass_task_passes() -> None:
    r = _run("memo text", "1: PASS\n2: PASS\n3: PASS")
    assert isinstance(r, RubricResult)
    assert [c.passed for c in r.criteria] == [True, True, True]
    assert r.pass_rate == 1.0
    assert r.task_passed is True


def test_optional_fail_still_task_passes() -> None:
    # optional criterion 3 fails, but both REQUIRED pass -> Harvey threshold met
    r = _run("memo", "1: PASS\n2: PASS\n3: FAIL - not mentioned")
    assert r.task_passed is True
    assert r.required_pass_rate == 1.0
    assert r.pass_rate == pytest.approx(2 / 3)
    assert r.criteria[2].passed is False and "not mentioned" in r.criteria[2].reason


def test_required_fail_fails_task() -> None:
    r = _run("memo", "1: PASS\n2: FAIL - missing\n3: PASS")
    assert r.task_passed is False
    assert r.pass_rate == pytest.approx(2 / 3)


def test_all_fail() -> None:
    r = _run("memo", "1: FAIL\n2: FAIL\n3: FAIL")
    assert r.task_passed is False
    assert r.pass_rate == 0.0


def test_missing_verdict_scores_conservative_fail() -> None:
    # grader only returned two lines; criterion 3 has no verdict -> failed
    r = _run("memo", "1: PASS\n2: PASS")
    assert r.criteria[2].passed is False
    assert "no verdict" in r.criteria[2].reason


def test_producer_and_grader_wire_metadata() -> None:
    seen: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        role = json.loads(req.content).get("metadata", {}).get("role")
        seen.append(role)
        text = "work" if role == "producer" else "1: PASS\n2: PASS\n3: PASS"
        return httpx.Response(200, json={"content": [{"type": "text", "text": text}]})

    c = Client("https://eval.local", "k", transport=httpx.MockTransport(handler))
    r = c.evaluate("legal-assistant", CASE)
    assert seen == ["producer", "grader"]  # producer first, then judge
    assert r.work_product == "work"


def test_case_validation_requires_a_required_criterion() -> None:
    with pytest.raises(RubricValidationError):
        RubricCase.from_dict(
            {"case_id": "x", "instruction": "do", "rubric": [{"criterion": "y", "required": False}]}
        )


def test_load_rubric_pack(tmp_path) -> None:
    import yaml
    for cid in ("b-case", "a-case"):
        (tmp_path / f"{cid}.yaml").write_text(
            yaml.safe_dump({"case_id": cid, "instruction": "do", "rubric": [{"criterion": "c"}]})
        )
    pack = load_rubric_pack(tmp_path)
    assert [c.case_id for c in pack] == ["a-case", "b-case"]  # sorted, deterministic
