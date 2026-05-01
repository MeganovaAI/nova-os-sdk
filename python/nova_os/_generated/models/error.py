from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.error_type import ErrorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Error")


@_attrs_define
class Error:
    """
    Attributes:
        type_ (ErrorType):
        message (str):
        param (str | Unset): When applicable, the request parameter that failed validation.
        code (str | Unset): Machine-readable subcode (e.g., "credits_exhausted", "USAGE_LIMIT_EXCEEDED").
        retry_after (int | Unset): Seconds — present on rate_limit_error.
        tool_name (str | Unset): Present on vertex_schema_error — the tool whose schema is invalid.
        parameter_path (str | Unset): Present on vertex_schema_error — JSON path to the offending parameter.
        fix_hint (str | Unset): Human-readable hint for actionable errors.
    """

    type_: ErrorType
    message: str
    param: str | Unset = UNSET
    code: str | Unset = UNSET
    retry_after: int | Unset = UNSET
    tool_name: str | Unset = UNSET
    parameter_path: str | Unset = UNSET
    fix_hint: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        message = self.message

        param = self.param

        code = self.code

        retry_after = self.retry_after

        tool_name = self.tool_name

        parameter_path = self.parameter_path

        fix_hint = self.fix_hint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "message": message,
            }
        )
        if param is not UNSET:
            field_dict["param"] = param
        if code is not UNSET:
            field_dict["code"] = code
        if retry_after is not UNSET:
            field_dict["retry_after"] = retry_after
        if tool_name is not UNSET:
            field_dict["tool_name"] = tool_name
        if parameter_path is not UNSET:
            field_dict["parameter_path"] = parameter_path
        if fix_hint is not UNSET:
            field_dict["fix_hint"] = fix_hint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = ErrorType(d.pop("type"))

        message = d.pop("message")

        param = d.pop("param", UNSET)

        code = d.pop("code", UNSET)

        retry_after = d.pop("retry_after", UNSET)

        tool_name = d.pop("tool_name", UNSET)

        parameter_path = d.pop("parameter_path", UNSET)

        fix_hint = d.pop("fix_hint", UNSET)

        error = cls(
            type_=type_,
            message=message,
            param=param,
            code=code,
            retry_after=retry_after,
            tool_name=tool_name,
            parameter_path=parameter_path,
            fix_hint=fix_hint,
        )

        error.additional_properties = d
        return error

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
