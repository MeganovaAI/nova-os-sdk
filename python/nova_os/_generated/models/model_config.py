from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_slot import ModelSlot


T = TypeVar("T", bound="ModelConfig")


@_attrs_define
class ModelConfig:
    """Three-slot model configuration. Any slot may be omitted; resolution
    falls through per the spec (per-call → per-skill → per-agent →
    per-employee → server default).

        Attributes:
            answer (ModelSlot | Unset):
            planner (ModelSlot | Unset):
            skill (ModelSlot | Unset):
    """

    answer: ModelSlot | Unset = UNSET
    planner: ModelSlot | Unset = UNSET
    skill: ModelSlot | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        answer: dict[str, Any] | Unset = UNSET
        if not isinstance(self.answer, Unset):
            answer = self.answer.to_dict()

        planner: dict[str, Any] | Unset = UNSET
        if not isinstance(self.planner, Unset):
            planner = self.planner.to_dict()

        skill: dict[str, Any] | Unset = UNSET
        if not isinstance(self.skill, Unset):
            skill = self.skill.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if answer is not UNSET:
            field_dict["answer"] = answer
        if planner is not UNSET:
            field_dict["planner"] = planner
        if skill is not UNSET:
            field_dict["skill"] = skill

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_slot import ModelSlot

        d = dict(src_dict)
        _answer = d.pop("answer", UNSET)
        answer: ModelSlot | Unset
        if isinstance(_answer, Unset):
            answer = UNSET
        else:
            answer = ModelSlot.from_dict(_answer)

        _planner = d.pop("planner", UNSET)
        planner: ModelSlot | Unset
        if isinstance(_planner, Unset):
            planner = UNSET
        else:
            planner = ModelSlot.from_dict(_planner)

        _skill = d.pop("skill", UNSET)
        skill: ModelSlot | Unset
        if isinstance(_skill, Unset):
            skill = UNSET
        else:
            skill = ModelSlot.from_dict(_skill)

        model_config = cls(
            answer=answer,
            planner=planner,
            skill=skill,
        )

        model_config.additional_properties = d
        return model_config

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
