from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.eval_case_result_failed_stage import EvalCaseResultFailedStage
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.eval_evidence import EvalEvidence


T = TypeVar("T", bound="EvalCaseResult")


@_attrs_define
class EvalCaseResult:
    """
    Attributes:
        case_id (str):
        output (str):
        sources (list[EvalEvidence]):
        answer_passed (bool):
        retrieval_passed (bool):
        citation_passed (bool):
        access_passed (bool):
        abstention_passed (bool):
        reviewer_note (str | Unset):
        error (str | Unset):
        failed_stage (EvalCaseResultFailedStage | Unset):
        passed (bool | Unset):
        score (float | Unset):
    """

    case_id: str
    output: str
    sources: list[EvalEvidence]
    answer_passed: bool
    retrieval_passed: bool
    citation_passed: bool
    access_passed: bool
    abstention_passed: bool
    reviewer_note: str | Unset = UNSET
    error: str | Unset = UNSET
    failed_stage: EvalCaseResultFailedStage | Unset = UNSET
    passed: bool | Unset = UNSET
    score: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        case_id = self.case_id

        output = self.output

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        answer_passed = self.answer_passed

        retrieval_passed = self.retrieval_passed

        citation_passed = self.citation_passed

        access_passed = self.access_passed

        abstention_passed = self.abstention_passed

        reviewer_note = self.reviewer_note

        error = self.error

        failed_stage: str | Unset = UNSET
        if not isinstance(self.failed_stage, Unset):
            failed_stage = self.failed_stage.value

        passed = self.passed

        score = self.score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "case_id": case_id,
                "output": output,
                "sources": sources,
                "answer_passed": answer_passed,
                "retrieval_passed": retrieval_passed,
                "citation_passed": citation_passed,
                "access_passed": access_passed,
                "abstention_passed": abstention_passed,
            }
        )
        if reviewer_note is not UNSET:
            field_dict["reviewer_note"] = reviewer_note
        if error is not UNSET:
            field_dict["error"] = error
        if failed_stage is not UNSET:
            field_dict["failed_stage"] = failed_stage
        if passed is not UNSET:
            field_dict["passed"] = passed
        if score is not UNSET:
            field_dict["score"] = score

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.eval_evidence import EvalEvidence

        d = dict(src_dict)
        case_id = d.pop("case_id")

        output = d.pop("output")

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = EvalEvidence.from_dict(sources_item_data)

            sources.append(sources_item)

        answer_passed = d.pop("answer_passed")

        retrieval_passed = d.pop("retrieval_passed")

        citation_passed = d.pop("citation_passed")

        access_passed = d.pop("access_passed")

        abstention_passed = d.pop("abstention_passed")

        reviewer_note = d.pop("reviewer_note", UNSET)

        error = d.pop("error", UNSET)

        _failed_stage = d.pop("failed_stage", UNSET)
        failed_stage: EvalCaseResultFailedStage | Unset
        if isinstance(_failed_stage, Unset):
            failed_stage = UNSET
        else:
            failed_stage = EvalCaseResultFailedStage(_failed_stage)

        passed = d.pop("passed", UNSET)

        score = d.pop("score", UNSET)

        eval_case_result = cls(
            case_id=case_id,
            output=output,
            sources=sources,
            answer_passed=answer_passed,
            retrieval_passed=retrieval_passed,
            citation_passed=citation_passed,
            access_passed=access_passed,
            abstention_passed=abstention_passed,
            reviewer_note=reviewer_note,
            error=error,
            failed_stage=failed_stage,
            passed=passed,
            score=score,
        )

        eval_case_result.additional_properties = d
        return eval_case_result

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
