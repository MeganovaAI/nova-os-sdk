from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.hook_event import HookEvent
from ..types import UNSET, Unset

T = TypeVar("T", bound="HookSubscription")


@_attrs_define
class HookSubscription:
    """
    Attributes:
        id (str):
        event (HookEvent): The 9 canonical lifecycle events. Validated server-side at
            registration time; unknown values return 400.
        target_url (str):
        enabled (bool):  Default: True.
        created_at (datetime.datetime):
        secret_env (str | Unset): Env var name holding the HMAC shared secret on the partner side.
        description (str | Unset):
    """

    id: str
    event: HookEvent
    target_url: str
    created_at: datetime.datetime
    enabled: bool = True
    secret_env: str | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        event = self.event.value

        target_url = self.target_url

        enabled = self.enabled

        created_at = self.created_at.isoformat()

        secret_env = self.secret_env

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "event": event,
                "target_url": target_url,
                "enabled": enabled,
                "created_at": created_at,
            }
        )
        if secret_env is not UNSET:
            field_dict["secret_env"] = secret_env
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        event = HookEvent(d.pop("event"))

        target_url = d.pop("target_url")

        enabled = d.pop("enabled")

        created_at = isoparse(d.pop("created_at"))

        secret_env = d.pop("secret_env", UNSET)

        description = d.pop("description", UNSET)

        hook_subscription = cls(
            id=id,
            event=event,
            target_url=target_url,
            enabled=enabled,
            created_at=created_at,
            secret_env=secret_env,
            description=description,
        )

        hook_subscription.additional_properties = d
        return hook_subscription

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
