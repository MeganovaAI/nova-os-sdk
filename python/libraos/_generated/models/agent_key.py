from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentKey")


@_attrs_define
class AgentKey:
    """One-time mint response for a per-agent key carrying the full secret.

    Attributes:
        id (str | Unset):
        key_prefix (str | Unset):  Example: nk_Ng9IdeX4S.
        secret (str | Unset): The full `nk_` key. Returned only once.
        name (str | Unset):
        created_at (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    key_prefix: str | Unset = UNSET
    secret: str | Unset = UNSET
    name: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        key_prefix = self.key_prefix

        secret = self.secret

        name = self.name

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if key_prefix is not UNSET:
            field_dict["key_prefix"] = key_prefix
        if secret is not UNSET:
            field_dict["secret"] = secret
        if name is not UNSET:
            field_dict["name"] = name
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        key_prefix = d.pop("key_prefix", UNSET)

        secret = d.pop("secret", UNSET)

        name = d.pop("name", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        agent_key = cls(
            id=id,
            key_prefix=key_prefix,
            secret=secret,
            name=name,
            created_at=created_at,
        )

        agent_key.additional_properties = d
        return agent_key

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
