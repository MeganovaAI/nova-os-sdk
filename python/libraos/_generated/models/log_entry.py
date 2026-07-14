from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_entry_fields import LogEntryFields


T = TypeVar("T", bound="LogEntry")


@_attrs_define
class LogEntry:
    """One log row. Stable across both sources.

    Attributes:
        ts (datetime.datetime):
        level (str):
        msg (str):
        fields (LogEntryFields | Unset):
        request_id (str | Unset): Set only on source=requests rows.
    """

    ts: datetime.datetime
    level: str
    msg: str
    fields: LogEntryFields | Unset = UNSET
    request_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ts = self.ts.isoformat()

        level = self.level

        msg = self.msg

        fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.fields, Unset):
            fields = self.fields.to_dict()

        request_id = self.request_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ts": ts,
                "level": level,
                "msg": msg,
            }
        )
        if fields is not UNSET:
            field_dict["fields"] = fields
        if request_id is not UNSET:
            field_dict["request_id"] = request_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.log_entry_fields import LogEntryFields

        d = dict(src_dict)
        ts = isoparse(d.pop("ts"))

        level = d.pop("level")

        msg = d.pop("msg")

        _fields = d.pop("fields", UNSET)
        fields: LogEntryFields | Unset
        if isinstance(_fields, Unset):
            fields = UNSET
        else:
            fields = LogEntryFields.from_dict(_fields)

        request_id = d.pop("request_id", UNSET)

        log_entry = cls(
            ts=ts,
            level=level,
            msg=msg,
            fields=fields,
            request_id=request_id,
        )

        log_entry.additional_properties = d
        return log_entry

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
