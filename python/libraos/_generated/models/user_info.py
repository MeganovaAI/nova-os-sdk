from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserInfo")


@_attrs_define
class UserInfo:
    """
    Attributes:
        sub (str | Unset):
        email (str | Unset):
        name (str | Unset):
        role (str | Unset): Deprecated singular mirror of the highest role in `roles`.
        tenant_id (str | Unset):
        roles (list[str] | Unset):
    """

    sub: str | Unset = UNSET
    email: str | Unset = UNSET
    name: str | Unset = UNSET
    role: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    roles: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sub = self.sub

        email = self.email

        name = self.name

        role = self.role

        tenant_id = self.tenant_id

        roles: list[str] | Unset = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sub is not UNSET:
            field_dict["sub"] = sub
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if role is not UNSET:
            field_dict["role"] = role
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sub = d.pop("sub", UNSET)

        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        role = d.pop("role", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        roles = cast(list[str], d.pop("roles", UNSET))

        user_info = cls(
            sub=sub,
            email=email,
            name=name,
            role=role,
            tenant_id=tenant_id,
            roles=roles,
        )

        user_info.additional_properties = d
        return user_info

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
