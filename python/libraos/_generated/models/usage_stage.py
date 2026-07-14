from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageStage")


@_attrs_define
class UsageStage:
    """Token usage for one stage/sub-call of a turn.

    Attributes:
        stage (str | Unset): The stage/agent that made the sub-call.
        model (str | Unset): The model used for the sub-call.
        prompt_tokens (int | Unset):
        completion_tokens (int | Unset):
    """

    stage: str | Unset = UNSET
    model: str | Unset = UNSET
    prompt_tokens: int | Unset = UNSET
    completion_tokens: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stage = self.stage

        model = self.model

        prompt_tokens = self.prompt_tokens

        completion_tokens = self.completion_tokens

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if stage is not UNSET:
            field_dict["stage"] = stage
        if model is not UNSET:
            field_dict["model"] = model
        if prompt_tokens is not UNSET:
            field_dict["prompt_tokens"] = prompt_tokens
        if completion_tokens is not UNSET:
            field_dict["completion_tokens"] = completion_tokens

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stage = d.pop("stage", UNSET)

        model = d.pop("model", UNSET)

        prompt_tokens = d.pop("prompt_tokens", UNSET)

        completion_tokens = d.pop("completion_tokens", UNSET)

        usage_stage = cls(
            stage=stage,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        usage_stage.additional_properties = d
        return usage_stage

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
