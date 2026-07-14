from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_evaluate_request_mode import FieldEvaluateRequestMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_caller import FieldCaller
    from ..models.field_evaluate_request_record import FieldEvaluateRequestRecord


T = TypeVar("T", bound="FieldEvaluateRequest")


@_attrs_define
class FieldEvaluateRequest:
    """
    Attributes:
        caller (FieldCaller): The identity evaluated against a policy.
        record (FieldEvaluateRequestRecord):
        mode (FieldEvaluateRequestMode | Unset): Empty for a read evaluation, `write` for a write evaluation.
    """

    caller: FieldCaller
    record: FieldEvaluateRequestRecord
    mode: FieldEvaluateRequestMode | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        caller = self.caller.to_dict()

        record = self.record.to_dict()

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caller": caller,
                "record": record,
            }
        )
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_caller import FieldCaller
        from ..models.field_evaluate_request_record import FieldEvaluateRequestRecord

        d = dict(src_dict)
        caller = FieldCaller.from_dict(d.pop("caller"))

        record = FieldEvaluateRequestRecord.from_dict(d.pop("record"))

        _mode = d.pop("mode", UNSET)
        mode: FieldEvaluateRequestMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = FieldEvaluateRequestMode(_mode)

        field_evaluate_request = cls(
            caller=caller,
            record=record,
            mode=mode,
        )

        field_evaluate_request.additional_properties = d
        return field_evaluate_request

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
