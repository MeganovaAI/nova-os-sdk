from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.custom_tool_callback_retry_backoff import CustomToolCallbackRetryBackoff
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomToolCallbackRetry")


@_attrs_define
class CustomToolCallbackRetry:
    """
    Attributes:
        max_attempts (int | Unset):  Default: 3.
        backoff (CustomToolCallbackRetryBackoff | Unset):  Default: CustomToolCallbackRetryBackoff.EXPONENTIAL.
    """

    max_attempts: int | Unset = 3
    backoff: CustomToolCallbackRetryBackoff | Unset = (
        CustomToolCallbackRetryBackoff.EXPONENTIAL
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_attempts = self.max_attempts

        backoff: str | Unset = UNSET
        if not isinstance(self.backoff, Unset):
            backoff = self.backoff.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_attempts is not UNSET:
            field_dict["max_attempts"] = max_attempts
        if backoff is not UNSET:
            field_dict["backoff"] = backoff

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_attempts = d.pop("max_attempts", UNSET)

        _backoff = d.pop("backoff", UNSET)
        backoff: CustomToolCallbackRetryBackoff | Unset
        if isinstance(_backoff, Unset):
            backoff = UNSET
        else:
            backoff = CustomToolCallbackRetryBackoff(_backoff)

        custom_tool_callback_retry = cls(
            max_attempts=max_attempts,
            backoff=backoff,
        )

        custom_tool_callback_retry.additional_properties = d
        return custom_tool_callback_retry

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
