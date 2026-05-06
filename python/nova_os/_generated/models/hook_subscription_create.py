from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.hook_event import HookEvent
from ..types import UNSET, Unset

T = TypeVar("T", bound="HookSubscriptionCreate")


@_attrs_define
class HookSubscriptionCreate:
    """
    Attributes:
        event (HookEvent): The 9 canonical lifecycle events. Validated server-side at
            registration time; unknown values return 400.
        target_url (str):
        secret_env (str | Unset):
        description (str | Unset):
        enabled (bool | Unset):
    """

    event: HookEvent
    target_url: str
    secret_env: str | Unset = UNSET
    description: str | Unset = UNSET
    enabled: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event = self.event.value

        target_url = self.target_url

        secret_env = self.secret_env

        description = self.description

        enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event": event,
                "target_url": target_url,
            }
        )
        if secret_env is not UNSET:
            field_dict["secret_env"] = secret_env
        if description is not UNSET:
            field_dict["description"] = description
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event = HookEvent(d.pop("event"))

        target_url = d.pop("target_url")

        secret_env = d.pop("secret_env", UNSET)

        description = d.pop("description", UNSET)

        enabled = d.pop("enabled", UNSET)

        hook_subscription_create = cls(
            event=event,
            target_url=target_url,
            secret_env=secret_env,
            description=description,
            enabled=enabled,
        )

        hook_subscription_create.additional_properties = d
        return hook_subscription_create

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
