from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.authorization_intent import AuthorizationIntent


T = TypeVar("T", bound="ListAuthorizationIntentsResponse200")


@_attrs_define
class ListAuthorizationIntentsResponse200:
    """
    Attributes:
        intents (list[AuthorizationIntent]):
    """

    intents: list[AuthorizationIntent]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        intents = []
        for intents_item_data in self.intents:
            intents_item = intents_item_data.to_dict()
            intents.append(intents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "intents": intents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_intent import AuthorizationIntent

        d = dict(src_dict)
        intents = []
        _intents = d.pop("intents")
        for intents_item_data in _intents:
            intents_item = AuthorizationIntent.from_dict(intents_item_data)

            intents.append(intents_item)

        list_authorization_intents_response_200 = cls(
            intents=intents,
        )

        list_authorization_intents_response_200.additional_properties = d
        return list_authorization_intents_response_200

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
