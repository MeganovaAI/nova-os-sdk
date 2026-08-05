from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_role import GroupRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="MyGroupMembership")


@_attrs_define
class MyGroupMembership:
    """One of the caller's own group memberships.

    Attributes:
        id (str):
        name (str):
        role (GroupRole): A member's role in a group.
        description (str | Unset):
    """

    id: str
    name: str
    role: GroupRole
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        role = self.role.value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "role": role,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        role = GroupRole(d.pop("role"))

        description = d.pop("description", UNSET)

        my_group_membership = cls(
            id=id,
            name=name,
            role=role,
            description=description,
        )

        my_group_membership.additional_properties = d
        return my_group_membership

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
