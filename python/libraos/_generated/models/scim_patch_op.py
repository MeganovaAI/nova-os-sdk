from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.scim_patch_op_operations_item import ScimPatchOpOperationsItem


T = TypeVar("T", bound="ScimPatchOp")


@_attrs_define
class ScimPatchOp:
    """SCIM PatchOp request (RFC 7644 §3.5.2).

    Attributes:
        operations (list[ScimPatchOpOperationsItem]):
        schemas (list[str] | Unset):  Example: ['urn:ietf:params:scim:api:messages:2.0:PatchOp'].
    """

    operations: list[ScimPatchOpOperationsItem]
    schemas: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operations = []
        for operations_item_data in self.operations:
            operations_item = operations_item_data.to_dict()
            operations.append(operations_item)

        schemas: list[str] | Unset = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Operations": operations,
            }
        )
        if schemas is not UNSET:
            field_dict["schemas"] = schemas

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scim_patch_op_operations_item import ScimPatchOpOperationsItem

        d = dict(src_dict)
        operations = []
        _operations = d.pop("Operations")
        for operations_item_data in _operations:
            operations_item = ScimPatchOpOperationsItem.from_dict(operations_item_data)

            operations.append(operations_item)

        schemas = cast(list[str], d.pop("schemas", UNSET))

        scim_patch_op = cls(
            operations=operations,
            schemas=schemas,
        )

        scim_patch_op.additional_properties = d
        return scim_patch_op

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
