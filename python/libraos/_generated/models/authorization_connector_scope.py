from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_connector_scope_details import AuthorizationConnectorScopeDetails


T = TypeVar("T", bound="AuthorizationConnectorScope")


@_attrs_define
class AuthorizationConnectorScope:
    """
    Attributes:
        kind (str):
        connection_id (str | Unset):
        details (AuthorizationConnectorScopeDetails | Unset): Connector-specific vocabulary, namespaced away from
            comparable outer fields.
    """

    kind: str
    connection_id: str | Unset = UNSET
    details: AuthorizationConnectorScopeDetails | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        connection_id = self.connection_id

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
            }
        )
        if connection_id is not UNSET:
            field_dict["connection_id"] = connection_id
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_connector_scope_details import AuthorizationConnectorScopeDetails

        d = dict(src_dict)
        kind = d.pop("kind")

        connection_id = d.pop("connection_id", UNSET)

        _details = d.pop("details", UNSET)
        details: AuthorizationConnectorScopeDetails | Unset
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = AuthorizationConnectorScopeDetails.from_dict(_details)

        authorization_connector_scope = cls(
            kind=kind,
            connection_id=connection_id,
            details=details,
        )

        authorization_connector_scope.additional_properties = d
        return authorization_connector_scope

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
