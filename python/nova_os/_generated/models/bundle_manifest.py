from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.bundle_manifest_schema_version import BundleManifestSchemaVersion
from ..types import UNSET, Unset

T = TypeVar("T", bound="BundleManifest")


@_attrs_define
class BundleManifest:
    """
    Attributes:
        schema_version (BundleManifestSchemaVersion):
        employee_id (str):
        nova_os_min_version (str):
        created_at (datetime.datetime):
        agents (list[str] | Unset):
        knowledge_files (int | Unset):
    """

    schema_version: BundleManifestSchemaVersion
    employee_id: str
    nova_os_min_version: str
    created_at: datetime.datetime
    agents: list[str] | Unset = UNSET
    knowledge_files: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schema_version = self.schema_version.value

        employee_id = self.employee_id

        nova_os_min_version = self.nova_os_min_version

        created_at = self.created_at.isoformat()

        agents: list[str] | Unset = UNSET
        if not isinstance(self.agents, Unset):
            agents = self.agents

        knowledge_files = self.knowledge_files

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schema_version": schema_version,
                "employee_id": employee_id,
                "nova_os_min_version": nova_os_min_version,
                "created_at": created_at,
            }
        )
        if agents is not UNSET:
            field_dict["agents"] = agents
        if knowledge_files is not UNSET:
            field_dict["knowledge_files"] = knowledge_files

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        schema_version = BundleManifestSchemaVersion(d.pop("schema_version"))

        employee_id = d.pop("employee_id")

        nova_os_min_version = d.pop("nova_os_min_version")

        created_at = isoparse(d.pop("created_at"))

        agents = cast(list[str], d.pop("agents", UNSET))

        knowledge_files = d.pop("knowledge_files", UNSET)

        bundle_manifest = cls(
            schema_version=schema_version,
            employee_id=employee_id,
            nova_os_min_version=nova_os_min_version,
            created_at=created_at,
            agents=agents,
            knowledge_files=knowledge_files,
        )

        bundle_manifest.additional_properties = d
        return bundle_manifest

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
