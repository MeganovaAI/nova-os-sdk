from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.log_list_source import LogListSource
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_entry import LogEntry


T = TypeVar("T", bound="LogList")


@_attrs_define
class LogList:
    """
    Attributes:
        logs (list[LogEntry]):
        source (LogListSource):
        total_in_buffer (int):
        next_cursor (str | Unset):
    """

    logs: list[LogEntry]
    source: LogListSource
    total_in_buffer: int
    next_cursor: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logs = []
        for logs_item_data in self.logs:
            logs_item = logs_item_data.to_dict()
            logs.append(logs_item)

        source = self.source.value

        total_in_buffer = self.total_in_buffer

        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "logs": logs,
                "source": source,
                "total_in_buffer": total_in_buffer,
            }
        )
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.log_entry import LogEntry

        d = dict(src_dict)
        logs = []
        _logs = d.pop("logs")
        for logs_item_data in _logs:
            logs_item = LogEntry.from_dict(logs_item_data)

            logs.append(logs_item)

        source = LogListSource(d.pop("source"))

        total_in_buffer = d.pop("total_in_buffer")

        next_cursor = d.pop("next_cursor", UNSET)

        log_list = cls(
            logs=logs,
            source=source,
            total_in_buffer=total_in_buffer,
            next_cursor=next_cursor,
        )

        log_list.additional_properties = d
        return log_list

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
