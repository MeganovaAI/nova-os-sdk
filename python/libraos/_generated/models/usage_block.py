from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_stage import UsageStage


T = TypeVar("T", bound="UsageBlock")


@_attrs_define
class UsageBlock:
    """Aggregated token usage across all of the turn's model sub-calls, with a per-stage breakdown. Omitted on non-
    model/zero-usage turns. Excludes embedding calls.

        Attributes:
            prompt_tokens (int | Unset):
            completion_tokens (int | Unset):
            total_tokens (int | Unset):
            by_stage (list[UsageStage] | Unset):
    """

    prompt_tokens: int | Unset = UNSET
    completion_tokens: int | Unset = UNSET
    total_tokens: int | Unset = UNSET
    by_stage: list[UsageStage] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        prompt_tokens = self.prompt_tokens

        completion_tokens = self.completion_tokens

        total_tokens = self.total_tokens

        by_stage: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.by_stage, Unset):
            by_stage = []
            for by_stage_item_data in self.by_stage:
                by_stage_item = by_stage_item_data.to_dict()
                by_stage.append(by_stage_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if prompt_tokens is not UNSET:
            field_dict["prompt_tokens"] = prompt_tokens
        if completion_tokens is not UNSET:
            field_dict["completion_tokens"] = completion_tokens
        if total_tokens is not UNSET:
            field_dict["total_tokens"] = total_tokens
        if by_stage is not UNSET:
            field_dict["by_stage"] = by_stage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_stage import UsageStage

        d = dict(src_dict)
        prompt_tokens = d.pop("prompt_tokens", UNSET)

        completion_tokens = d.pop("completion_tokens", UNSET)

        total_tokens = d.pop("total_tokens", UNSET)

        _by_stage = d.pop("by_stage", UNSET)
        by_stage: list[UsageStage] | Unset = UNSET
        if _by_stage is not UNSET:
            by_stage = []
            for by_stage_item_data in _by_stage:
                by_stage_item = UsageStage.from_dict(by_stage_item_data)

                by_stage.append(by_stage_item)

        usage_block = cls(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            by_stage=by_stage,
        )

        usage_block.additional_properties = d
        return usage_block

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
