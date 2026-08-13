from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PromoteKnowledgeSignalBody")


@_attrs_define
class PromoteKnowledgeSignalBody:
    """
    Attributes:
        collection (str | Unset):  Default: 'default'.
        audience (str | Unset):  Default: 'organization'.
    """

    collection: str | Unset = "default"
    audience: str | Unset = "organization"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection = self.collection

        audience = self.audience

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collection is not UNSET:
            field_dict["collection"] = collection
        if audience is not UNSET:
            field_dict["audience"] = audience

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collection = d.pop("collection", UNSET)

        audience = d.pop("audience", UNSET)

        promote_knowledge_signal_body = cls(
            collection=collection,
            audience=audience,
        )

        promote_knowledge_signal_body.additional_properties = d
        return promote_knowledge_signal_body

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
