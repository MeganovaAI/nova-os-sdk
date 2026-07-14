from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.scim_email import ScimEmail
    from ..models.scim_meta import ScimMeta
    from ..models.scim_name import ScimName


T = TypeVar("T", bound="ScimUser")


@_attrs_define
class ScimUser:
    """SCIM 2.0 core User resource (RFC 7643), restricted to the supported attributes.

    Attributes:
        user_name (str): The user's email; unique.
        schemas (list[str] | Unset):  Example: ['urn:ietf:params:scim:schemas:core:2.0:User'].
        id (str | Unset):
        external_id (str | Unset):
        name (ScimName | Unset):
        display_name (str | Unset):
        active (bool | Unset):
        emails (list[ScimEmail] | Unset):
        meta (ScimMeta | Unset):
    """

    user_name: str
    schemas: list[str] | Unset = UNSET
    id: str | Unset = UNSET
    external_id: str | Unset = UNSET
    name: ScimName | Unset = UNSET
    display_name: str | Unset = UNSET
    active: bool | Unset = UNSET
    emails: list[ScimEmail] | Unset = UNSET
    meta: ScimMeta | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_name = self.user_name

        schemas: list[str] | Unset = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        id = self.id

        external_id = self.external_id

        name: dict[str, Any] | Unset = UNSET
        if not isinstance(self.name, Unset):
            name = self.name.to_dict()

        display_name = self.display_name

        active = self.active

        emails: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.emails, Unset):
            emails = []
            for emails_item_data in self.emails:
                emails_item = emails_item_data.to_dict()
                emails.append(emails_item)

        meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userName": user_name,
            }
        )
        if schemas is not UNSET:
            field_dict["schemas"] = schemas
        if id is not UNSET:
            field_dict["id"] = id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if active is not UNSET:
            field_dict["active"] = active
        if emails is not UNSET:
            field_dict["emails"] = emails
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scim_email import ScimEmail
        from ..models.scim_meta import ScimMeta
        from ..models.scim_name import ScimName

        d = dict(src_dict)
        user_name = d.pop("userName")

        schemas = cast(list[str], d.pop("schemas", UNSET))

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        _name = d.pop("name", UNSET)
        name: ScimName | Unset
        if isinstance(_name, Unset):
            name = UNSET
        else:
            name = ScimName.from_dict(_name)

        display_name = d.pop("displayName", UNSET)

        active = d.pop("active", UNSET)

        _emails = d.pop("emails", UNSET)
        emails: list[ScimEmail] | Unset = UNSET
        if _emails is not UNSET:
            emails = []
            for emails_item_data in _emails:
                emails_item = ScimEmail.from_dict(emails_item_data)

                emails.append(emails_item)

        _meta = d.pop("meta", UNSET)
        meta: ScimMeta | Unset
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = ScimMeta.from_dict(_meta)

        scim_user = cls(
            user_name=user_name,
            schemas=schemas,
            id=id,
            external_id=external_id,
            name=name,
            display_name=display_name,
            active=active,
            emails=emails,
            meta=meta,
        )

        scim_user.additional_properties = d
        return scim_user

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
