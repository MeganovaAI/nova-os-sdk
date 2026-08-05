from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileObject")


@_attrs_define
class FileObject:
    """An uploaded file, OpenAI Files API compatible.

    Attributes:
        id (str): File identifier, prefixed with `file-`.
        object_ (Literal['file']):
        bytes_ (int): Size of the file in bytes.
        created_at (int): Unix timestamp (seconds) of creation.
        filename (str):
        purpose (str | Unset): Intended use of the file.
        status (str | Unset): Processing status, e.g. `processed`.
        status_details (None | str | Unset):
    """

    id: str
    object_: Literal["file"]
    bytes_: int
    created_at: int
    filename: str
    purpose: str | Unset = UNSET
    status: str | Unset = UNSET
    status_details: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        object_ = self.object_

        bytes_ = self.bytes_

        created_at = self.created_at

        filename = self.filename

        purpose = self.purpose

        status = self.status

        status_details: None | str | Unset
        if isinstance(self.status_details, Unset):
            status_details = UNSET
        else:
            status_details = self.status_details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "object": object_,
                "bytes": bytes_,
                "created_at": created_at,
                "filename": filename,
            }
        )
        if purpose is not UNSET:
            field_dict["purpose"] = purpose
        if status is not UNSET:
            field_dict["status"] = status
        if status_details is not UNSET:
            field_dict["status_details"] = status_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        object_ = cast(Literal["file"], d.pop("object"))
        if object_ != "file":
            raise ValueError(f"object must match const 'file', got '{object_}'")

        bytes_ = d.pop("bytes")

        created_at = d.pop("created_at")

        filename = d.pop("filename")

        purpose = d.pop("purpose", UNSET)

        status = d.pop("status", UNSET)

        def _parse_status_details(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status_details = _parse_status_details(d.pop("status_details", UNSET))

        file_object = cls(
            id=id,
            object_=object_,
            bytes_=bytes_,
            created_at=created_at,
            filename=filename,
            purpose=purpose,
            status=status,
            status_details=status_details,
        )

        file_object.additional_properties = d
        return file_object

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
