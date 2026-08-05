from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="SyncStatus")


@_attrs_define
class SyncStatus:
    """SharePoint sync worker status snapshot.

    Attributes:
        configured (bool):
        enabled (bool):
        last_sync_at (datetime.datetime):
        items_synced (int):
        items_deleted (int):
        items_failed (int):
        items_skipped (int):
        cycles_run (int):
        has_delta_link (bool): Whether a delta resume link is persisted.
        resume_pending (bool): True when the last cycle stopped at the item cap and the next cycle resumes the same
            delta round.
        collection_id (str | Unset):
        last_error (str | Unset):
    """

    configured: bool
    enabled: bool
    last_sync_at: datetime.datetime
    items_synced: int
    items_deleted: int
    items_failed: int
    items_skipped: int
    cycles_run: int
    has_delta_link: bool
    resume_pending: bool
    collection_id: str | Unset = UNSET
    last_error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configured = self.configured

        enabled = self.enabled

        last_sync_at = self.last_sync_at.isoformat()

        items_synced = self.items_synced

        items_deleted = self.items_deleted

        items_failed = self.items_failed

        items_skipped = self.items_skipped

        cycles_run = self.cycles_run

        has_delta_link = self.has_delta_link

        resume_pending = self.resume_pending

        collection_id = self.collection_id

        last_error = self.last_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configured": configured,
                "enabled": enabled,
                "last_sync_at": last_sync_at,
                "items_synced": items_synced,
                "items_deleted": items_deleted,
                "items_failed": items_failed,
                "items_skipped": items_skipped,
                "cycles_run": cycles_run,
                "has_delta_link": has_delta_link,
                "resume_pending": resume_pending,
            }
        )
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if last_error is not UNSET:
            field_dict["last_error"] = last_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        configured = d.pop("configured")

        enabled = d.pop("enabled")

        last_sync_at = isoparse(d.pop("last_sync_at"))

        items_synced = d.pop("items_synced")

        items_deleted = d.pop("items_deleted")

        items_failed = d.pop("items_failed")

        items_skipped = d.pop("items_skipped")

        cycles_run = d.pop("cycles_run")

        has_delta_link = d.pop("has_delta_link")

        resume_pending = d.pop("resume_pending")

        collection_id = d.pop("collection_id", UNSET)

        last_error = d.pop("last_error", UNSET)

        sync_status = cls(
            configured=configured,
            enabled=enabled,
            last_sync_at=last_sync_at,
            items_synced=items_synced,
            items_deleted=items_deleted,
            items_failed=items_failed,
            items_skipped=items_skipped,
            cycles_run=cycles_run,
            has_delta_link=has_delta_link,
            resume_pending=resume_pending,
            collection_id=collection_id,
            last_error=last_error,
        )

        sync_status.additional_properties = d
        return sync_status

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
