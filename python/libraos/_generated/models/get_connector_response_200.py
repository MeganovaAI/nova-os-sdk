from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connector import Connector


T = TypeVar("T", bound="GetConnectorResponse200")


@_attrs_define
class GetConnectorResponse200:
    """
    Attributes:
        connector (Connector): A connector configuration with secret values masked; secret_keys lists which secrets are
            set.
    """

    connector: Connector
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector = self.connector.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connector": connector,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector import Connector

        d = dict(src_dict)
        connector = Connector.from_dict(d.pop("connector"))

        get_connector_response_200 = cls(
            connector=connector,
        )

        get_connector_response_200.additional_properties = d
        return get_connector_response_200

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
