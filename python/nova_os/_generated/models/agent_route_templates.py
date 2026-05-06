from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AgentRouteTemplates")


@_attrs_define
class AgentRouteTemplates:
    """URL templates Brain may fill into `navigate_to:` route hints.
    Keys are template names (e.g. `case_detail`); values are URL
    template strings with `{placeholder}` segments (e.g.
    `https://app.example.com/cases/{case_id}`). Validated at server
    boot. v0.1.5+.

    Note: declared as `additionalProperties: true` rather than
    `additionalProperties: { type: string }` because openapi-python-
    client 0.28.3 (#15) chokes on the Schema-object form. Partners
    should still treat values as strings — server-side validation
    rejects non-string values. See nova-os-sdk#15.

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent_route_templates = cls()

        agent_route_templates.additional_properties = d
        return agent_route_templates

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
