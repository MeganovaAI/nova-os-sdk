from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.route_hint_render_inline_kind import RouteHintRenderInlineKind

T = TypeVar("T", bound="RouteHintRenderInline")


@_attrs_define
class RouteHintRenderInline:
    """Brain decided the reply is the answer — render it inline in the
    partner's chat UI. No navigation needed.

        Attributes:
            kind (RouteHintRenderInlineKind):
    """

    kind: RouteHintRenderInlineKind
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = RouteHintRenderInlineKind(d.pop("kind"))

        route_hint_render_inline = cls(
            kind=kind,
        )

        route_hint_render_inline.additional_properties = d
        return route_hint_render_inline

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
