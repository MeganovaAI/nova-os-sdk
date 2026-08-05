from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AppInstallResult")


@_attrs_define
class AppInstallResult:
    """Result of an install, reload, or uninstall operation.

    Attributes:
        name (str):
        version (str):
        registered (bool):
        agents_registered (int):
        agents_unregistered (int):
        migrations_applied (int):
        status (str | Unset):
        errors (list[str] | Unset): Present only when the operation failed.
    """

    name: str
    version: str
    registered: bool
    agents_registered: int
    agents_unregistered: int
    migrations_applied: int
    status: str | Unset = UNSET
    errors: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        version = self.version

        registered = self.registered

        agents_registered = self.agents_registered

        agents_unregistered = self.agents_unregistered

        migrations_applied = self.migrations_applied

        status = self.status

        errors: list[str] | Unset = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "version": version,
                "registered": registered,
                "agents_registered": agents_registered,
                "agents_unregistered": agents_unregistered,
                "migrations_applied": migrations_applied,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        registered = d.pop("registered")

        agents_registered = d.pop("agents_registered")

        agents_unregistered = d.pop("agents_unregistered")

        migrations_applied = d.pop("migrations_applied")

        status = d.pop("status", UNSET)

        errors = cast(list[str], d.pop("errors", UNSET))

        app_install_result = cls(
            name=name,
            version=version,
            registered=registered,
            agents_registered=agents_registered,
            agents_unregistered=agents_unregistered,
            migrations_applied=migrations_applied,
            status=status,
            errors=errors,
        )

        app_install_result.additional_properties = d
        return app_install_result

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
