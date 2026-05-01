from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelSlot")


@_attrs_define
class ModelSlot:
    """
    Attributes:
        primary (str): Model identifier in `<vendor>/<model>` shape (e.g., `anthropic/claude-opus-4-7`).
        fallback (list[str] | Unset): Ordered fallback chain. Activates on rate-limit / 5xx / vendor outage /
            Vertex 400 schema-error before falling through to the next resolution level.
    """

    primary: str
    fallback: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        primary = self.primary

        fallback: list[str] | Unset = UNSET
        if not isinstance(self.fallback, Unset):
            fallback = self.fallback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "primary": primary,
            }
        )
        if fallback is not UNSET:
            field_dict["fallback"] = fallback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        primary = d.pop("primary")

        fallback = cast(list[str], d.pop("fallback", UNSET))

        model_slot = cls(
            primary=primary,
            fallback=fallback,
        )

        model_slot.additional_properties = d
        return model_slot

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
