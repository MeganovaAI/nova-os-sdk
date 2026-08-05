from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="InfraGroundingCounts")


@_attrs_define
class InfraGroundingCounts:
    """
    Attributes:
        grounded (int):
        ungrounded_refusal (int):
        ungrounded_no_chunks (int):
        degraded (int):
        unknown (int):
    """

    grounded: int
    ungrounded_refusal: int
    ungrounded_no_chunks: int
    degraded: int
    unknown: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grounded = self.grounded

        ungrounded_refusal = self.ungrounded_refusal

        ungrounded_no_chunks = self.ungrounded_no_chunks

        degraded = self.degraded

        unknown = self.unknown

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grounded": grounded,
                "ungrounded_refusal": ungrounded_refusal,
                "ungrounded_no_chunks": ungrounded_no_chunks,
                "degraded": degraded,
                "unknown": unknown,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grounded = d.pop("grounded")

        ungrounded_refusal = d.pop("ungrounded_refusal")

        ungrounded_no_chunks = d.pop("ungrounded_no_chunks")

        degraded = d.pop("degraded")

        unknown = d.pop("unknown")

        infra_grounding_counts = cls(
            grounded=grounded,
            ungrounded_refusal=ungrounded_refusal,
            ungrounded_no_chunks=ungrounded_no_chunks,
            degraded=degraded,
            unknown=unknown,
        )

        infra_grounding_counts.additional_properties = d
        return infra_grounding_counts

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
