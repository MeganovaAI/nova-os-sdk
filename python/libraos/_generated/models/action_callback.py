from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.action_callback_auth import ActionCallbackAuth


T = TypeVar("T", bound="ActionCallback")


@_attrs_define
class ActionCallback:
    """Webhook fired when the action is approved. It is snapshotted onto the row and never surfaced back to clients.

    Attributes:
        url (str): The webhook endpoint the approved action is dispatched to.
        auth (ActionCallbackAuth):
        timeout_sec (int | Unset):
        retry (int | Unset):
    """

    url: str
    auth: ActionCallbackAuth
    timeout_sec: int | Unset = UNSET
    retry: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        auth = self.auth.to_dict()

        timeout_sec = self.timeout_sec

        retry = self.retry

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "auth": auth,
            }
        )
        if timeout_sec is not UNSET:
            field_dict["timeout_sec"] = timeout_sec
        if retry is not UNSET:
            field_dict["retry"] = retry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_callback_auth import ActionCallbackAuth

        d = dict(src_dict)
        url = d.pop("url")

        auth = ActionCallbackAuth.from_dict(d.pop("auth"))

        timeout_sec = d.pop("timeout_sec", UNSET)

        retry = d.pop("retry", UNSET)

        action_callback = cls(
            url=url,
            auth=auth,
            timeout_sec=timeout_sec,
            retry=retry,
        )

        action_callback.additional_properties = d
        return action_callback

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
