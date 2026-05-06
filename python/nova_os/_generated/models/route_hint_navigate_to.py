from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.route_hint_navigate_to_kind import RouteHintNavigateToKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.route_hint_navigate_to_params import RouteHintNavigateToParams


T = TypeVar("T", bound="RouteHintNavigateTo")


@_attrs_define
class RouteHintNavigateTo:
    """Brain decided the partner UI should navigate to a route. The
    template name MUST match a key in the agent's `route_templates`;
    the server interpolates `params` into the URL template.

        Attributes:
            kind (RouteHintNavigateToKind):
            template (str): Key into the agent's `route_templates` map.
            params (RouteHintNavigateToParams | Unset): Values to interpolate into the template's `{placeholder}` segments.
    """

    kind: RouteHintNavigateToKind
    template: str
    params: RouteHintNavigateToParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        template = self.template

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "template": template,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.route_hint_navigate_to_params import RouteHintNavigateToParams

        d = dict(src_dict)
        kind = RouteHintNavigateToKind(d.pop("kind"))

        template = d.pop("template")

        _params = d.pop("params", UNSET)
        params: RouteHintNavigateToParams | Unset
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = RouteHintNavigateToParams.from_dict(_params)

        route_hint_navigate_to = cls(
            kind=kind,
            template=template,
            params=params,
        )

        route_hint_navigate_to.additional_properties = d
        return route_hint_navigate_to

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
