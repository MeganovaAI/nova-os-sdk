from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OidcClient")


@_attrs_define
class OidcClient:
    """
    Attributes:
        client_id (str | Unset):
        redirect_uri (str | Unset):
        app_id (str | Unset):
    """

    client_id: str | Unset = UNSET
    redirect_uri: str | Unset = UNSET
    app_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        redirect_uri = self.redirect_uri

        app_id = self.app_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri
        if app_id is not UNSET:
            field_dict["app_id"] = app_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("client_id", UNSET)

        redirect_uri = d.pop("redirect_uri", UNSET)

        app_id = d.pop("app_id", UNSET)

        oidc_client = cls(
            client_id=client_id,
            redirect_uri=redirect_uri,
            app_id=app_id,
        )

        oidc_client.additional_properties = d
        return oidc_client

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
