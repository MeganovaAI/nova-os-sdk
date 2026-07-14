from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PromotionCandidates")


@_attrs_define
class PromotionCandidates:
    """
    Attributes:
        fact_keys (list[str] | Unset): Fact keys that have cleared the promotion quorum.
    """

    fact_keys: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fact_keys: list[str] | Unset = UNSET
        if not isinstance(self.fact_keys, Unset):
            fact_keys = self.fact_keys

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fact_keys is not UNSET:
            field_dict["fact_keys"] = fact_keys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fact_keys = cast(list[str], d.pop("fact_keys", UNSET))

        promotion_candidates = cls(
            fact_keys=fact_keys,
        )

        promotion_candidates.additional_properties = d
        return promotion_candidates

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
