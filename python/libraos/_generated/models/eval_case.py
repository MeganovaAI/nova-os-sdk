from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.eval_case_expected_behavior import EvalCaseExpectedBehavior
from ..types import UNSET, Unset

T = TypeVar("T", bound="EvalCase")


@_attrs_define
class EvalCase:
    """
    Attributes:
        case_id (str):
        prompt (str):
        reference (str): Human-authored expected behavior; never model-generated.
        reference_author (str):
        reference_reviewer (str):
        reference_privacy_reviewed (bool):
        expected_behavior (EvalCaseExpectedBehavior):
        source_case_id (str | Unset): Optional privacy-reviewed resolved-work reference.
        criteria (list[str] | Unset):
        tags (list[str] | Unset):
        expected_source_ids (list[str] | Unset):
        forbidden_source_ids (list[str] | Unset):
        required_claims (list[str] | Unset):
        forbidden_claims (list[str] | Unset):
        principal (str | Unset):
        max_source_age_days (int | Unset):
    """

    case_id: str
    prompt: str
    reference: str
    reference_author: str
    reference_reviewer: str
    reference_privacy_reviewed: bool
    expected_behavior: EvalCaseExpectedBehavior
    source_case_id: str | Unset = UNSET
    criteria: list[str] | Unset = UNSET
    tags: list[str] | Unset = UNSET
    expected_source_ids: list[str] | Unset = UNSET
    forbidden_source_ids: list[str] | Unset = UNSET
    required_claims: list[str] | Unset = UNSET
    forbidden_claims: list[str] | Unset = UNSET
    principal: str | Unset = UNSET
    max_source_age_days: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        case_id = self.case_id

        prompt = self.prompt

        reference = self.reference

        reference_author = self.reference_author

        reference_reviewer = self.reference_reviewer

        reference_privacy_reviewed = self.reference_privacy_reviewed

        expected_behavior = self.expected_behavior.value

        source_case_id = self.source_case_id

        criteria: list[str] | Unset = UNSET
        if not isinstance(self.criteria, Unset):
            criteria = self.criteria

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        expected_source_ids: list[str] | Unset = UNSET
        if not isinstance(self.expected_source_ids, Unset):
            expected_source_ids = self.expected_source_ids

        forbidden_source_ids: list[str] | Unset = UNSET
        if not isinstance(self.forbidden_source_ids, Unset):
            forbidden_source_ids = self.forbidden_source_ids

        required_claims: list[str] | Unset = UNSET
        if not isinstance(self.required_claims, Unset):
            required_claims = self.required_claims

        forbidden_claims: list[str] | Unset = UNSET
        if not isinstance(self.forbidden_claims, Unset):
            forbidden_claims = self.forbidden_claims

        principal = self.principal

        max_source_age_days = self.max_source_age_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "case_id": case_id,
                "prompt": prompt,
                "reference": reference,
                "reference_author": reference_author,
                "reference_reviewer": reference_reviewer,
                "reference_privacy_reviewed": reference_privacy_reviewed,
                "expected_behavior": expected_behavior,
            }
        )
        if source_case_id is not UNSET:
            field_dict["source_case_id"] = source_case_id
        if criteria is not UNSET:
            field_dict["criteria"] = criteria
        if tags is not UNSET:
            field_dict["tags"] = tags
        if expected_source_ids is not UNSET:
            field_dict["expected_source_ids"] = expected_source_ids
        if forbidden_source_ids is not UNSET:
            field_dict["forbidden_source_ids"] = forbidden_source_ids
        if required_claims is not UNSET:
            field_dict["required_claims"] = required_claims
        if forbidden_claims is not UNSET:
            field_dict["forbidden_claims"] = forbidden_claims
        if principal is not UNSET:
            field_dict["principal"] = principal
        if max_source_age_days is not UNSET:
            field_dict["max_source_age_days"] = max_source_age_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        case_id = d.pop("case_id")

        prompt = d.pop("prompt")

        reference = d.pop("reference")

        reference_author = d.pop("reference_author")

        reference_reviewer = d.pop("reference_reviewer")

        reference_privacy_reviewed = d.pop("reference_privacy_reviewed")

        expected_behavior = EvalCaseExpectedBehavior(d.pop("expected_behavior"))

        source_case_id = d.pop("source_case_id", UNSET)

        criteria = cast(list[str], d.pop("criteria", UNSET))

        tags = cast(list[str], d.pop("tags", UNSET))

        expected_source_ids = cast(list[str], d.pop("expected_source_ids", UNSET))

        forbidden_source_ids = cast(list[str], d.pop("forbidden_source_ids", UNSET))

        required_claims = cast(list[str], d.pop("required_claims", UNSET))

        forbidden_claims = cast(list[str], d.pop("forbidden_claims", UNSET))

        principal = d.pop("principal", UNSET)

        max_source_age_days = d.pop("max_source_age_days", UNSET)

        eval_case = cls(
            case_id=case_id,
            prompt=prompt,
            reference=reference,
            reference_author=reference_author,
            reference_reviewer=reference_reviewer,
            reference_privacy_reviewed=reference_privacy_reviewed,
            expected_behavior=expected_behavior,
            source_case_id=source_case_id,
            criteria=criteria,
            tags=tags,
            expected_source_ids=expected_source_ids,
            forbidden_source_ids=forbidden_source_ids,
            required_claims=required_claims,
            forbidden_claims=forbidden_claims,
            principal=principal,
            max_source_age_days=max_source_age_days,
        )

        eval_case.additional_properties = d
        return eval_case

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
