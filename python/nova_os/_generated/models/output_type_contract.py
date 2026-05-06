from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_type_contract_violation_mode import OutputTypeContractViolationMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.json_schema_object import JSONSchemaObject


T = TypeVar("T", bound="OutputTypeContract")


@_attrs_define
class OutputTypeContract:
    """Structured-output contract for agent replies. When set, Nova OS
    validates every assistant reply against `schema` before return.
    Server-side since v0.1.4.

        Attributes:
            schema (JSONSchemaObject): A subset of JSON Schema Draft 2020-12 used for tool input schemas.
                Vertex AI rejects `type:array` without `items` — the SDK validator
                enforces `items` is present everywhere on write.
            violation_mode (OutputTypeContractViolationMode | Unset): How to handle a reply that fails validation:
                - `error` — return HTTP 422 with the violations.
                - `log` — return the reply as-is plus `output_violations`; partner decides what to do.
                - `repair` — re-prompt the model once with the schema in the system prompt;
                  return whichever attempt validates, plus `output_violations` from the first.
                 Default: OutputTypeContractViolationMode.ERROR.
    """

    schema: JSONSchemaObject
    violation_mode: OutputTypeContractViolationMode | Unset = OutputTypeContractViolationMode.ERROR
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schema = self.schema.to_dict()

        violation_mode: str | Unset = UNSET
        if not isinstance(self.violation_mode, Unset):
            violation_mode = self.violation_mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schema": schema,
            }
        )
        if violation_mode is not UNSET:
            field_dict["violation_mode"] = violation_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.json_schema_object import JSONSchemaObject

        d = dict(src_dict)
        schema = JSONSchemaObject.from_dict(d.pop("schema"))

        _violation_mode = d.pop("violation_mode", UNSET)
        violation_mode: OutputTypeContractViolationMode | Unset
        if isinstance(_violation_mode, Unset):
            violation_mode = UNSET
        else:
            violation_mode = OutputTypeContractViolationMode(_violation_mode)

        output_type_contract = cls(
            schema=schema,
            violation_mode=violation_mode,
        )

        output_type_contract.additional_properties = d
        return output_type_contract

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
