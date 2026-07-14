from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.feature_status import FeatureStatus


T = TypeVar("T", bound="FeatureList")


@_attrs_define
class FeatureList:
    """
    Attributes:
        generated_at (datetime.datetime):
        features (list[FeatureStatus]):
    """

    generated_at: datetime.datetime
    features: list[FeatureStatus]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generated_at = self.generated_at.isoformat()

        features = []
        for features_item_data in self.features:
            features_item = features_item_data.to_dict()
            features.append(features_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generated_at": generated_at,
                "features": features,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feature_status import FeatureStatus

        d = dict(src_dict)
        generated_at = isoparse(d.pop("generated_at"))

        features = []
        _features = d.pop("features")
        for features_item_data in _features:
            features_item = FeatureStatus.from_dict(features_item_data)

            features.append(features_item)

        feature_list = cls(
            generated_at=generated_at,
            features=features,
        )

        feature_list.additional_properties = d
        return feature_list

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
