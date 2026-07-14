from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (str):
        email (str):
        role (UserRole):
        name (str | Unset):
        must_change_password (bool | Unset):
        created_at (datetime.datetime | Unset):
    """

    id: str
    email: str
    role: UserRole
    name: str | Unset = UNSET
    must_change_password: bool | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        role = self.role.value

        name = self.name

        must_change_password = self.must_change_password

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "role": role,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if must_change_password is not UNSET:
            field_dict["must_change_password"] = must_change_password
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        role = UserRole(d.pop("role"))

        name = d.pop("name", UNSET)

        must_change_password = d.pop("must_change_password", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        user = cls(
            id=id,
            email=email,
            role=role,
            name=name,
            must_change_password=must_change_password,
            created_at=created_at,
        )

        user.additional_properties = d
        return user

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
