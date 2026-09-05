from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_knowledge_collection_body_access_level import CreateKnowledgeCollectionBodyAccessLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateKnowledgeCollectionBody")


@_attrs_define
class CreateKnowledgeCollectionBody:
    """
    Attributes:
        name (str):
        access_level (CreateKnowledgeCollectionBodyAccessLevel | Unset):
        description (str | Unset):
    """

    name: str
    access_level: CreateKnowledgeCollectionBodyAccessLevel | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        access_level: str | Unset = UNSET
        if not isinstance(self.access_level, Unset):
            access_level = self.access_level.value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if access_level is not UNSET:
            field_dict["access_level"] = access_level
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        _access_level = d.pop("access_level", UNSET)
        access_level: CreateKnowledgeCollectionBodyAccessLevel | Unset
        if isinstance(_access_level, Unset):
            access_level = UNSET
        else:
            access_level = CreateKnowledgeCollectionBodyAccessLevel(_access_level)

        description = d.pop("description", UNSET)

        create_knowledge_collection_body = cls(
            name=name,
            access_level=access_level,
            description=description,
        )

        create_knowledge_collection_body.additional_properties = d
        return create_knowledge_collection_body

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
