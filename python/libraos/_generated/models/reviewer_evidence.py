from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewerEvidence")


@_attrs_define
class ReviewerEvidence:
    """
    Attributes:
        reviewer (str):
        decisions (int):
        edited (int):
        rejected (int):
        fast (int):
        batched (int):
        edit_rate (float):
        reject_rate (float):
        fast_rate (float):
    """

    reviewer: str
    decisions: int
    edited: int
    rejected: int
    fast: int
    batched: int
    edit_rate: float
    reject_rate: float
    fast_rate: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reviewer = self.reviewer

        decisions = self.decisions

        edited = self.edited

        rejected = self.rejected

        fast = self.fast

        batched = self.batched

        edit_rate = self.edit_rate

        reject_rate = self.reject_rate

        fast_rate = self.fast_rate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reviewer": reviewer,
                "decisions": decisions,
                "edited": edited,
                "rejected": rejected,
                "fast": fast,
                "batched": batched,
                "edit_rate": edit_rate,
                "reject_rate": reject_rate,
                "fast_rate": fast_rate,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reviewer = d.pop("reviewer")

        decisions = d.pop("decisions")

        edited = d.pop("edited")

        rejected = d.pop("rejected")

        fast = d.pop("fast")

        batched = d.pop("batched")

        edit_rate = d.pop("edit_rate")

        reject_rate = d.pop("reject_rate")

        fast_rate = d.pop("fast_rate")

        reviewer_evidence = cls(
            reviewer=reviewer,
            decisions=decisions,
            edited=edited,
            rejected=rejected,
            fast=fast,
            batched=batched,
            edit_rate=edit_rate,
            reject_rate=reject_rate,
            fast_rate=fast_rate,
        )

        reviewer_evidence.additional_properties = d
        return reviewer_evidence

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
