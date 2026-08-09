from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.execute_capability_response_202_status import ExecuteCapabilityResponse202Status

T = TypeVar("T", bound="ExecuteCapabilityResponse202")


@_attrs_define
class ExecuteCapabilityResponse202:
    """
    Attributes:
        status (ExecuteCapabilityResponse202Status):
        sampled (bool):
        action_id (str):
        intent_id (str):
    """

    status: ExecuteCapabilityResponse202Status
    sampled: bool
    action_id: str
    intent_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        sampled = self.sampled

        action_id = self.action_id

        intent_id = self.intent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "sampled": sampled,
                "action_id": action_id,
                "intent_id": intent_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = ExecuteCapabilityResponse202Status(d.pop("status"))

        sampled = d.pop("sampled")

        action_id = d.pop("action_id")

        intent_id = d.pop("intent_id")

        execute_capability_response_202 = cls(
            status=status,
            sampled=sampled,
            action_id=action_id,
            intent_id=intent_id,
        )

        execute_capability_response_202.additional_properties = d
        return execute_capability_response_202

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
