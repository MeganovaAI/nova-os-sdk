from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.execution_capability_issue_request_callback_auth import ExecutionCapabilityIssueRequestCallbackAuth


T = TypeVar("T", bound="ExecutionCapabilityIssueRequestCallback")


@_attrs_define
class ExecutionCapabilityIssueRequestCallback:
    """
    Attributes:
        url (str):
        auth (ExecutionCapabilityIssueRequestCallbackAuth):
    """

    url: str
    auth: ExecutionCapabilityIssueRequestCallbackAuth
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        auth = self.auth.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "auth": auth,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execution_capability_issue_request_callback_auth import (
            ExecutionCapabilityIssueRequestCallbackAuth,
        )

        d = dict(src_dict)
        url = d.pop("url")

        auth = ExecutionCapabilityIssueRequestCallbackAuth.from_dict(d.pop("auth"))

        execution_capability_issue_request_callback = cls(
            url=url,
            auth=auth,
        )

        execution_capability_issue_request_callback.additional_properties = d
        return execution_capability_issue_request_callback

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
