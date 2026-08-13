from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.eval_run_status import EvalRunStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.eval_case_result import EvalCaseResult
    from ..models.eval_run_metrics import EvalRunMetrics


T = TypeVar("T", bound="EvalRun")


@_attrs_define
class EvalRun:
    """
    Attributes:
        run_id (str):
        suite_name (str):
        suite_revision (int):
        suite_digest (str):
        blueprint_digest (str):
        knowledge_digest (str):
        agent_id (str):
        status (EvalRunStatus):
        total_cases (int):
        passed_cases (int | Unset):
        score (float | Unset):
        metrics (EvalRunMetrics | Unset):
        release_blocked (bool | Unset):
        receipt_id (str | Unset):
        results (list[EvalCaseResult] | Unset):
        created_at (datetime.datetime | Unset):
        completed_at (datetime.datetime | Unset):
    """

    run_id: str
    suite_name: str
    suite_revision: int
    suite_digest: str
    blueprint_digest: str
    knowledge_digest: str
    agent_id: str
    status: EvalRunStatus
    total_cases: int
    passed_cases: int | Unset = UNSET
    score: float | Unset = UNSET
    metrics: EvalRunMetrics | Unset = UNSET
    release_blocked: bool | Unset = UNSET
    receipt_id: str | Unset = UNSET
    results: list[EvalCaseResult] | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    completed_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run_id = self.run_id

        suite_name = self.suite_name

        suite_revision = self.suite_revision

        suite_digest = self.suite_digest

        blueprint_digest = self.blueprint_digest

        knowledge_digest = self.knowledge_digest

        agent_id = self.agent_id

        status = self.status.value

        total_cases = self.total_cases

        passed_cases = self.passed_cases

        score = self.score

        metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        release_blocked = self.release_blocked

        receipt_id = self.receipt_id

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        completed_at: str | Unset = UNSET
        if not isinstance(self.completed_at, Unset):
            completed_at = self.completed_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id": run_id,
                "suite_name": suite_name,
                "suite_revision": suite_revision,
                "suite_digest": suite_digest,
                "blueprint_digest": blueprint_digest,
                "knowledge_digest": knowledge_digest,
                "agent_id": agent_id,
                "status": status,
                "total_cases": total_cases,
            }
        )
        if passed_cases is not UNSET:
            field_dict["passed_cases"] = passed_cases
        if score is not UNSET:
            field_dict["score"] = score
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if release_blocked is not UNSET:
            field_dict["release_blocked"] = release_blocked
        if receipt_id is not UNSET:
            field_dict["receipt_id"] = receipt_id
        if results is not UNSET:
            field_dict["results"] = results
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.eval_case_result import EvalCaseResult
        from ..models.eval_run_metrics import EvalRunMetrics

        d = dict(src_dict)
        run_id = d.pop("run_id")

        suite_name = d.pop("suite_name")

        suite_revision = d.pop("suite_revision")

        suite_digest = d.pop("suite_digest")

        blueprint_digest = d.pop("blueprint_digest")

        knowledge_digest = d.pop("knowledge_digest")

        agent_id = d.pop("agent_id")

        status = EvalRunStatus(d.pop("status"))

        total_cases = d.pop("total_cases")

        passed_cases = d.pop("passed_cases", UNSET)

        score = d.pop("score", UNSET)

        _metrics = d.pop("metrics", UNSET)
        metrics: EvalRunMetrics | Unset
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = EvalRunMetrics.from_dict(_metrics)

        release_blocked = d.pop("release_blocked", UNSET)

        receipt_id = d.pop("receipt_id", UNSET)

        _results = d.pop("results", UNSET)
        results: list[EvalCaseResult] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = EvalCaseResult.from_dict(results_item_data)

                results.append(results_item)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _completed_at = d.pop("completed_at", UNSET)
        completed_at: datetime.datetime | Unset
        if isinstance(_completed_at, Unset):
            completed_at = UNSET
        else:
            completed_at = isoparse(_completed_at)

        eval_run = cls(
            run_id=run_id,
            suite_name=suite_name,
            suite_revision=suite_revision,
            suite_digest=suite_digest,
            blueprint_digest=blueprint_digest,
            knowledge_digest=knowledge_digest,
            agent_id=agent_id,
            status=status,
            total_cases=total_cases,
            passed_cases=passed_cases,
            score=score,
            metrics=metrics,
            release_blocked=release_blocked,
            receipt_id=receipt_id,
            results=results,
            created_at=created_at,
            completed_at=completed_at,
        )

        eval_run.additional_properties = d
        return eval_run

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
