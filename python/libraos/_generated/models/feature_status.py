from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.feature_status_resolved_from import FeatureStatusResolvedFrom
from ..models.feature_status_state import FeatureStatusState
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureStatus")


@_attrs_define
class FeatureStatus:
    """Resolved state of one gated feature.

    Attributes:
        name (str):
        state (FeatureStatusState):
        resolved_from (FeatureStatusResolvedFrom):
        flag (str | Unset):
        reason (str | Unset):
        runtime_mutable (bool | Unset):
    """

    name: str
    state: FeatureStatusState
    resolved_from: FeatureStatusResolvedFrom
    flag: str | Unset = UNSET
    reason: str | Unset = UNSET
    runtime_mutable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        state = self.state.value

        resolved_from = self.resolved_from.value

        flag = self.flag

        reason = self.reason

        runtime_mutable = self.runtime_mutable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "state": state,
                "resolved_from": resolved_from,
            }
        )
        if flag is not UNSET:
            field_dict["flag"] = flag
        if reason is not UNSET:
            field_dict["reason"] = reason
        if runtime_mutable is not UNSET:
            field_dict["runtime_mutable"] = runtime_mutable

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        state = FeatureStatusState(d.pop("state"))

        resolved_from = FeatureStatusResolvedFrom(d.pop("resolved_from"))

        flag = d.pop("flag", UNSET)

        reason = d.pop("reason", UNSET)

        runtime_mutable = d.pop("runtime_mutable", UNSET)

        feature_status = cls(
            name=name,
            state=state,
            resolved_from=resolved_from,
            flag=flag,
            reason=reason,
            runtime_mutable=runtime_mutable,
        )

        feature_status.additional_properties = d
        return feature_status

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
