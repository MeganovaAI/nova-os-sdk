from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InfraToolError")


@_attrs_define
class InfraToolError:
    """
    Attributes:
        tool (str):
        invocations (int):
        errored_turns (int):
        errored_turn_rate (float):
        sample_errors (list[str] | Unset):
    """

    tool: str
    invocations: int
    errored_turns: int
    errored_turn_rate: float
    sample_errors: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool = self.tool

        invocations = self.invocations

        errored_turns = self.errored_turns

        errored_turn_rate = self.errored_turn_rate

        sample_errors: list[str] | Unset = UNSET
        if not isinstance(self.sample_errors, Unset):
            sample_errors = self.sample_errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool": tool,
                "invocations": invocations,
                "errored_turns": errored_turns,
                "errored_turn_rate": errored_turn_rate,
            }
        )
        if sample_errors is not UNSET:
            field_dict["sample_errors"] = sample_errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tool = d.pop("tool")

        invocations = d.pop("invocations")

        errored_turns = d.pop("errored_turns")

        errored_turn_rate = d.pop("errored_turn_rate")

        sample_errors = cast(list[str], d.pop("sample_errors", UNSET))

        infra_tool_error = cls(
            tool=tool,
            invocations=invocations,
            errored_turns=errored_turns,
            errored_turn_rate=errored_turn_rate,
            sample_errors=sample_errors,
        )

        infra_tool_error.additional_properties = d
        return infra_tool_error

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
