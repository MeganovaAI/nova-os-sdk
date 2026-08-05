from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="App")


@_attrs_define
class App:
    """One installed app.

    Attributes:
        name (str):
        version (str):
        schema_prefix (str):
        manifest_path (str):
        status (str):
        installed_at (datetime.datetime):
        last_seen_at (datetime.datetime):
        agents_count (int):
        archived_at (datetime.datetime | None | Unset):
        archived_by (None | str | Unset):
        last_error (None | str | Unset):
    """

    name: str
    version: str
    schema_prefix: str
    manifest_path: str
    status: str
    installed_at: datetime.datetime
    last_seen_at: datetime.datetime
    agents_count: int
    archived_at: datetime.datetime | None | Unset = UNSET
    archived_by: None | str | Unset = UNSET
    last_error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        version = self.version

        schema_prefix = self.schema_prefix

        manifest_path = self.manifest_path

        status = self.status

        installed_at = self.installed_at.isoformat()

        last_seen_at = self.last_seen_at.isoformat()

        agents_count = self.agents_count

        archived_at: None | str | Unset
        if isinstance(self.archived_at, Unset):
            archived_at = UNSET
        elif isinstance(self.archived_at, datetime.datetime):
            archived_at = self.archived_at.isoformat()
        else:
            archived_at = self.archived_at

        archived_by: None | str | Unset
        if isinstance(self.archived_by, Unset):
            archived_by = UNSET
        else:
            archived_by = self.archived_by

        last_error: None | str | Unset
        if isinstance(self.last_error, Unset):
            last_error = UNSET
        else:
            last_error = self.last_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "version": version,
                "schema_prefix": schema_prefix,
                "manifest_path": manifest_path,
                "status": status,
                "installed_at": installed_at,
                "last_seen_at": last_seen_at,
                "agents_count": agents_count,
            }
        )
        if archived_at is not UNSET:
            field_dict["archived_at"] = archived_at
        if archived_by is not UNSET:
            field_dict["archived_by"] = archived_by
        if last_error is not UNSET:
            field_dict["last_error"] = last_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        schema_prefix = d.pop("schema_prefix")

        manifest_path = d.pop("manifest_path")

        status = d.pop("status")

        installed_at = isoparse(d.pop("installed_at"))

        last_seen_at = isoparse(d.pop("last_seen_at"))

        agents_count = d.pop("agents_count")

        def _parse_archived_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                archived_at_type_0 = isoparse(data)

                return archived_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        archived_at = _parse_archived_at(d.pop("archived_at", UNSET))

        def _parse_archived_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        archived_by = _parse_archived_by(d.pop("archived_by", UNSET))

        def _parse_last_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_error = _parse_last_error(d.pop("last_error", UNSET))

        app = cls(
            name=name,
            version=version,
            schema_prefix=schema_prefix,
            manifest_path=manifest_path,
            status=status,
            installed_at=installed_at,
            last_seen_at=last_seen_at,
            agents_count=agents_count,
            archived_at=archived_at,
            archived_by=archived_by,
            last_error=last_error,
        )

        app.additional_properties = d
        return app

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
