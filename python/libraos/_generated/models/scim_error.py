from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScimError")


@_attrs_define
class ScimError:
    """SCIM error response (RFC 7644 §3.12). `status` is a string.

    Attributes:
        schemas (list[str] | Unset):  Example: ['urn:ietf:params:scim:api:messages:2.0:Error'].
        status (str | Unset):  Example: 404.
        scim_type (str | Unset): e.g. `invalidFilter`, `invalidValue`, `invalidSyntax`, `uniqueness`.
        detail (str | Unset):
    """

    schemas: list[str] | Unset = UNSET
    status: str | Unset = UNSET
    scim_type: str | Unset = UNSET
    detail: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schemas: list[str] | Unset = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        status = self.status

        scim_type = self.scim_type

        detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if schemas is not UNSET:
            field_dict["schemas"] = schemas
        if status is not UNSET:
            field_dict["status"] = status
        if scim_type is not UNSET:
            field_dict["scimType"] = scim_type
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        schemas = cast(list[str], d.pop("schemas", UNSET))

        status = d.pop("status", UNSET)

        scim_type = d.pop("scimType", UNSET)

        detail = d.pop("detail", UNSET)

        scim_error = cls(
            schemas=schemas,
            status=status,
            scim_type=scim_type,
            detail=detail,
        )

        scim_error.additional_properties = d
        return scim_error

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
