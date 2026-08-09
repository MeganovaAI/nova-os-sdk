from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.execute_capability_response_200_status import ExecuteCapabilityResponse200Status

if TYPE_CHECKING:
    from ..models.authorization_graph import AuthorizationGraph


T = TypeVar("T", bound="ExecuteCapabilityResponse200")


@_attrs_define
class ExecuteCapabilityResponse200:
    """
    Attributes:
        status (ExecuteCapabilityResponse200Status):
        intent (AuthorizationGraph):
    """

    status: ExecuteCapabilityResponse200Status
    intent: AuthorizationGraph
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        intent = self.intent.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "intent": intent,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_graph import AuthorizationGraph

        d = dict(src_dict)
        status = ExecuteCapabilityResponse200Status(d.pop("status"))

        intent = AuthorizationGraph.from_dict(d.pop("intent"))

        execute_capability_response_200 = cls(
            status=status,
            intent=intent,
        )

        execute_capability_response_200.additional_properties = d
        return execute_capability_response_200

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
