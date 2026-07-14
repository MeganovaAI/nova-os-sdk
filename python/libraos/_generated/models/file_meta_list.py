from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_meta import FileMeta


T = TypeVar("T", bound="FileMetaList")


@_attrs_define
class FileMetaList:
    """
    Attributes:
        data (list[FileMeta]):
        has_more (bool | Unset): True when truncated by the limit query param.
    """

    data: list[FileMeta]
    has_more: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if has_more is not UNSET:
            field_dict["has_more"] = has_more

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_meta import FileMeta

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = FileMeta.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more", UNSET)

        file_meta_list = cls(
            data=data,
            has_more=has_more,
        )

        file_meta_list.additional_properties = d
        return file_meta_list

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
