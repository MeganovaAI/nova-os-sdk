from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.app_migration_status import AppMigrationStatus

T = TypeVar("T", bound="AppMigration")


@_attrs_define
class AppMigration:
    """One schema-migration audit row for an app.

    Attributes:
        filename (str):
        checksum (str):
        status (AppMigrationStatus):
        applied_at (datetime.datetime):
        error_message (None | str): Null when status is applied.
    """

    filename: str
    checksum: str
    status: AppMigrationStatus
    applied_at: datetime.datetime
    error_message: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        checksum = self.checksum

        status = self.status.value

        applied_at = self.applied_at.isoformat()

        error_message: None | str
        error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filename": filename,
                "checksum": checksum,
                "status": status,
                "applied_at": applied_at,
                "error_message": error_message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        checksum = d.pop("checksum")

        status = AppMigrationStatus(d.pop("status"))

        applied_at = isoparse(d.pop("applied_at"))

        def _parse_error_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_message = _parse_error_message(d.pop("error_message"))

        app_migration = cls(
            filename=filename,
            checksum=checksum,
            status=status,
            applied_at=applied_at,
            error_message=error_message,
        )

        app_migration.additional_properties = d
        return app_migration

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
