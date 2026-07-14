from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.route_hint_ask_clarification_kind import RouteHintAskClarificationKind

T = TypeVar("T", bound="RouteHintAskClarification")


@_attrs_define
class RouteHintAskClarification:
    """Brain decided more input is needed before answering — partner UI
    should present a clarification prompt rather than rendering the
    reply as final.

        Attributes:
            kind (RouteHintAskClarificationKind):
            reason (str): Short human-readable rationale (e.g. `missing_jurisdiction`).
    """

    kind: RouteHintAskClarificationKind
    reason: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = RouteHintAskClarificationKind(d.pop("kind"))

        reason = d.pop("reason")

        route_hint_ask_clarification = cls(
            kind=kind,
            reason=reason,
        )

        route_hint_ask_clarification.additional_properties = d
        return route_hint_ask_clarification

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
