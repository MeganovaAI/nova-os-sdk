from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileMeta")


@_attrs_define
class FileMeta:
    """
    Attributes:
        path (str): Agent-visible path including mount prefix (e.g. "/workspace/PLAN.md").
        size (int): Plaintext byte length.
        mtime (datetime.datetime):
        content_type (str | Unset):
        sha256 (str | Unset): Hex-encoded SHA-256 of the plaintext. Used for If-Match optimistic concurrency.
    """

    path: str
    size: int
    mtime: datetime.datetime
    content_type: str | Unset = UNSET
    sha256: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        size = self.size

        mtime = self.mtime.isoformat()

        content_type = self.content_type

        sha256 = self.sha256

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "size": size,
                "mtime": mtime,
            }
        )
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if sha256 is not UNSET:
            field_dict["sha256"] = sha256

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        size = d.pop("size")

        mtime = isoparse(d.pop("mtime"))

        content_type = d.pop("content_type", UNSET)

        sha256 = d.pop("sha256", UNSET)

        file_meta = cls(
            path=path,
            size=size,
            mtime=mtime,
            content_type=content_type,
            sha256=sha256,
        )

        file_meta.additional_properties = d
        return file_meta

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
