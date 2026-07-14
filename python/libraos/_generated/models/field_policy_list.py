from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.field_policy_list_policies import FieldPolicyListPolicies


T = TypeVar("T", bound="FieldPolicyList")


@_attrs_define
class FieldPolicyList:
    """The tenant's policies keyed by record type.

    Attributes:
        policies (FieldPolicyListPolicies):
    """

    policies: FieldPolicyListPolicies
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        policies = self.policies.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "policies": policies,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_policy_list_policies import FieldPolicyListPolicies

        d = dict(src_dict)
        policies = FieldPolicyListPolicies.from_dict(d.pop("policies"))

        field_policy_list = cls(
            policies=policies,
        )

        field_policy_list.additional_properties = d
        return field_policy_list

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
