from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_upsert_config import ConnectorUpsertConfig
    from ..models.connector_upsert_secrets import ConnectorUpsertSecrets


T = TypeVar("T", bound="ConnectorUpsert")


@_attrs_define
class ConnectorUpsert:
    """Upsert payload for a connector's settings and secrets.

    Attributes:
        tenant_id (str | Unset):
        enabled (bool | Unset):
        group_id (str | Unset):
        config (ConnectorUpsertConfig | Unset): Connector-specific non-secret settings (must be a JSON object).
        secrets (ConnectorUpsertSecrets | Unset): Secret values to merge. A non-empty value overwrites, an empty string
            deletes that key, and omitted keys are preserved.
    """

    tenant_id: str | Unset = UNSET
    enabled: bool | Unset = UNSET
    group_id: str | Unset = UNSET
    config: ConnectorUpsertConfig | Unset = UNSET
    secrets: ConnectorUpsertSecrets | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        enabled = self.enabled

        group_id = self.group_id

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        secrets: dict[str, Any] | Unset = UNSET
        if not isinstance(self.secrets, Unset):
            secrets = self.secrets.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if config is not UNSET:
            field_dict["config"] = config
        if secrets is not UNSET:
            field_dict["secrets"] = secrets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector_upsert_config import ConnectorUpsertConfig
        from ..models.connector_upsert_secrets import ConnectorUpsertSecrets

        d = dict(src_dict)
        tenant_id = d.pop("tenant_id", UNSET)

        enabled = d.pop("enabled", UNSET)

        group_id = d.pop("group_id", UNSET)

        _config = d.pop("config", UNSET)
        config: ConnectorUpsertConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = ConnectorUpsertConfig.from_dict(_config)

        _secrets = d.pop("secrets", UNSET)
        secrets: ConnectorUpsertSecrets | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = ConnectorUpsertSecrets.from_dict(_secrets)

        connector_upsert = cls(
            tenant_id=tenant_id,
            enabled=enabled,
            group_id=group_id,
            config=config,
            secrets=secrets,
        )

        connector_upsert.additional_properties = d
        return connector_upsert

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
