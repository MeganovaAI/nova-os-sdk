from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_config import ConnectorConfig


T = TypeVar("T", bound="Connector")


@_attrs_define
class Connector:
    """A connector configuration with secret values masked; secret_keys lists which secrets are set.

    Attributes:
        kind (str): Connector kind identifier.
        enabled (bool):
        config (ConnectorConfig): Connector-specific non-secret settings.
        secret_keys (list[str]): Names of the secrets that are set; values are never returned here.
        updated_at (datetime.datetime):
        tenant_id (str | Unset): Owning tenant; omitted when unscoped.
        group_id (str | Unset): Optional group scoping the connector.
    """

    kind: str
    enabled: bool
    config: ConnectorConfig
    secret_keys: list[str]
    updated_at: datetime.datetime
    tenant_id: str | Unset = UNSET
    group_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        enabled = self.enabled

        config = self.config.to_dict()

        secret_keys = self.secret_keys

        updated_at = self.updated_at.isoformat()

        tenant_id = self.tenant_id

        group_id = self.group_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "enabled": enabled,
                "config": config,
                "secret_keys": secret_keys,
                "updated_at": updated_at,
            }
        )
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if group_id is not UNSET:
            field_dict["group_id"] = group_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector_config import ConnectorConfig

        d = dict(src_dict)
        kind = d.pop("kind")

        enabled = d.pop("enabled")

        config = ConnectorConfig.from_dict(d.pop("config"))

        secret_keys = cast(list[str], d.pop("secret_keys"))

        updated_at = isoparse(d.pop("updated_at"))

        tenant_id = d.pop("tenant_id", UNSET)

        group_id = d.pop("group_id", UNSET)

        connector = cls(
            kind=kind,
            enabled=enabled,
            config=config,
            secret_keys=secret_keys,
            updated_at=updated_at,
            tenant_id=tenant_id,
            group_id=group_id,
        )

        connector.additional_properties = d
        return connector

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
