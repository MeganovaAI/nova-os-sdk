from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.group_role import GroupRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="AddGroupMemberResponse200")


@_attrs_define
class AddGroupMemberResponse200:
    """
    Attributes:
        status (str | Unset):  Example: ok.
        group_id (str | Unset):
        user_id (str | Unset):
        role (GroupRole | Unset): A member's role in a group.
    """

    status: str | Unset = UNSET
    group_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    role: GroupRole | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        group_id = self.group_id

        user_id = self.user_id

        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status", UNSET)

        group_id = d.pop("group_id", UNSET)

        user_id = d.pop("user_id", UNSET)

        _role = d.pop("role", UNSET)
        role: GroupRole | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = GroupRole(_role)

        add_group_member_response_200 = cls(
            status=status,
            group_id=group_id,
            user_id=user_id,
            role=role,
        )

        add_group_member_response_200.additional_properties = d
        return add_group_member_response_200

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
