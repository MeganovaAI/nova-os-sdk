from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Attachment")


@_attrs_define
class Attachment:
    """A file attached to a conversation.

    Attributes:
        id (str):
        name (str): Original filename.
        mime_type (str):
        size_bytes (int):
        download_url (str): Relative URL for downloading the attachment bytes.
        created_at (datetime.datetime):
        scan_status (str): Malware-scan status, e.g. `not_scanned`.
        deleted_at (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    mime_type: str
    size_bytes: int
    download_url: str
    created_at: datetime.datetime
    scan_status: str
    deleted_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        mime_type = self.mime_type

        size_bytes = self.size_bytes

        download_url = self.download_url

        created_at = self.created_at.isoformat()

        scan_status = self.scan_status

        deleted_at: None | str | Unset
        if isinstance(self.deleted_at, Unset):
            deleted_at = UNSET
        elif isinstance(self.deleted_at, datetime.datetime):
            deleted_at = self.deleted_at.isoformat()
        else:
            deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "mime_type": mime_type,
                "size_bytes": size_bytes,
                "download_url": download_url,
                "created_at": created_at,
                "scan_status": scan_status,
            }
        )
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        mime_type = d.pop("mime_type")

        size_bytes = d.pop("size_bytes")

        download_url = d.pop("download_url")

        created_at = isoparse(d.pop("created_at"))

        scan_status = d.pop("scan_status")

        def _parse_deleted_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_at_type_0 = isoparse(data)

                return deleted_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        deleted_at = _parse_deleted_at(d.pop("deleted_at", UNSET))

        attachment = cls(
            id=id,
            name=name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            download_url=download_url,
            created_at=created_at,
            scan_status=scan_status,
            deleted_at=deleted_at,
        )

        attachment.additional_properties = d
        return attachment

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
