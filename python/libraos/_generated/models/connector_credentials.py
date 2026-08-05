from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connector import Connector
    from ..models.connector_credentials_secrets import ConnectorCredentialsSecrets


T = TypeVar("T", bound="ConnectorCredentials")


@_attrs_define
class ConnectorCredentials:
    """A connector config together with its decrypted secret values.

    Attributes:
        connector (Connector): A connector configuration with secret values masked; secret_keys lists which secrets are
            set.
        secrets (ConnectorCredentialsSecrets): Decrypted secret values keyed by secret name.
    """

    connector: Connector
    secrets: ConnectorCredentialsSecrets
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector = self.connector.to_dict()

        secrets = self.secrets.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connector": connector,
                "secrets": secrets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector import Connector
        from ..models.connector_credentials_secrets import ConnectorCredentialsSecrets

        d = dict(src_dict)
        connector = Connector.from_dict(d.pop("connector"))

        secrets = ConnectorCredentialsSecrets.from_dict(d.pop("secrets"))

        connector_credentials = cls(
            connector=connector,
            secrets=secrets,
        )

        connector_credentials.additional_properties = d
        return connector_credentials

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
