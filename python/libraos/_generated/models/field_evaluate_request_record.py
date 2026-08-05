from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_evaluate_request_record_fields import FieldEvaluateRequestRecordFields


T = TypeVar("T", bound="FieldEvaluateRequestRecord")


@_attrs_define
class FieldEvaluateRequestRecord:
    """
    Attributes:
        fields (FieldEvaluateRequestRecordFields):
        owner (str | Unset):
        id (str | Unset):
    """

    fields: FieldEvaluateRequestRecordFields
    owner: str | Unset = UNSET
    id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fields = self.fields.to_dict()

        owner = self.owner

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
            }
        )
        if owner is not UNSET:
            field_dict["owner"] = owner
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_evaluate_request_record_fields import FieldEvaluateRequestRecordFields

        d = dict(src_dict)
        fields = FieldEvaluateRequestRecordFields.from_dict(d.pop("fields"))

        owner = d.pop("owner", UNSET)

        id = d.pop("id", UNSET)

        field_evaluate_request_record = cls(
            fields=fields,
            owner=owner,
            id=id,
        )

        field_evaluate_request_record.additional_properties = d
        return field_evaluate_request_record

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
