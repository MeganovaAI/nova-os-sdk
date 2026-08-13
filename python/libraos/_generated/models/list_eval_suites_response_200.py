from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.eval_suite_revision import EvalSuiteRevision


T = TypeVar("T", bound="ListEvalSuitesResponse200")


@_attrs_define
class ListEvalSuitesResponse200:
    """
    Attributes:
        suites (list[EvalSuiteRevision] | Unset):
    """

    suites: list[EvalSuiteRevision] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        suites: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.suites, Unset):
            suites = []
            for suites_item_data in self.suites:
                suites_item = suites_item_data.to_dict()
                suites.append(suites_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if suites is not UNSET:
            field_dict["suites"] = suites

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.eval_suite_revision import EvalSuiteRevision

        d = dict(src_dict)
        _suites = d.pop("suites", UNSET)
        suites: list[EvalSuiteRevision] | Unset = UNSET
        if _suites is not UNSET:
            suites = []
            for suites_item_data in _suites:
                suites_item = EvalSuiteRevision.from_dict(suites_item_data)

                suites.append(suites_item)

        list_eval_suites_response_200 = cls(
            suites=suites,
        )

        list_eval_suites_response_200.additional_properties = d
        return list_eval_suites_response_200

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
