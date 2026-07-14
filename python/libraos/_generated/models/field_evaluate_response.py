from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_access import FieldAccess
    from ..models.field_evaluate_response_filtered import FieldEvaluateResponseFiltered
    from ..models.field_evaluate_response_stripped import FieldEvaluateResponseStripped


T = TypeVar("T", bound="FieldEvaluateResponse")


@_attrs_define
class FieldEvaluateResponse:
    """The access decision plus the enforced record view. Read mode returns `stripped`; write mode returns `filtered`.

    Attributes:
        field_access (FieldAccess): The computed access contract. An omitted field list means "all fields"; a present
            list (including empty) is the explicit permitted set.
        stripped (FieldEvaluateResponseStripped | Unset):
        filtered (FieldEvaluateResponseFiltered | Unset):
    """

    field_access: FieldAccess
    stripped: FieldEvaluateResponseStripped | Unset = UNSET
    filtered: FieldEvaluateResponseFiltered | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_access = self.field_access.to_dict()

        stripped: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stripped, Unset):
            stripped = self.stripped.to_dict()

        filtered: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filtered, Unset):
            filtered = self.filtered.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_access": field_access,
            }
        )
        if stripped is not UNSET:
            field_dict["stripped"] = stripped
        if filtered is not UNSET:
            field_dict["filtered"] = filtered

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_access import FieldAccess
        from ..models.field_evaluate_response_filtered import FieldEvaluateResponseFiltered
        from ..models.field_evaluate_response_stripped import FieldEvaluateResponseStripped

        d = dict(src_dict)
        field_access = FieldAccess.from_dict(d.pop("_access"))

        _stripped = d.pop("stripped", UNSET)
        stripped: FieldEvaluateResponseStripped | Unset
        if isinstance(_stripped, Unset):
            stripped = UNSET
        else:
            stripped = FieldEvaluateResponseStripped.from_dict(_stripped)

        _filtered = d.pop("filtered", UNSET)
        filtered: FieldEvaluateResponseFiltered | Unset
        if isinstance(_filtered, Unset):
            filtered = UNSET
        else:
            filtered = FieldEvaluateResponseFiltered.from_dict(_filtered)

        field_evaluate_response = cls(
            field_access=field_access,
            stripped=stripped,
            filtered=filtered,
        )

        field_evaluate_response.additional_properties = d
        return field_evaluate_response

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
