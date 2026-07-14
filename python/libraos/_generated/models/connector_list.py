from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connector import Connector


T = TypeVar("T", bound="ConnectorList")


@_attrs_define
class ConnectorList:
    """
    Attributes:
        connectors (list[Connector]):
    """

    connectors: list[Connector]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connectors = []
        for connectors_item_data in self.connectors:
            connectors_item = connectors_item_data.to_dict()
            connectors.append(connectors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectors": connectors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector import Connector

        d = dict(src_dict)
        connectors = []
        _connectors = d.pop("connectors")
        for connectors_item_data in _connectors:
            connectors_item = Connector.from_dict(connectors_item_data)

            connectors.append(connectors_item)

        connector_list = cls(
            connectors=connectors,
        )

        connector_list.additional_properties = d
        return connector_list

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
