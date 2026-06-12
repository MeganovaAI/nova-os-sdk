from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentModels")


@_attrs_define
class DeploymentModels:
    """Resolved model tiers (advisory; no secrets). Lets a client show
    "powered by" / pick a tier without hardcoding model ids.

        Attributes:
            answer (str | Unset): Default answer/synthesis model id.
            skill (str | Unset): Cheap-tier skill/section model id.
            brain (str | Unset): Planner/brain model id.
    """

    answer: str | Unset = UNSET
    skill: str | Unset = UNSET
    brain: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        answer = self.answer

        skill = self.skill

        brain = self.brain

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if answer is not UNSET:
            field_dict["answer"] = answer
        if skill is not UNSET:
            field_dict["skill"] = skill
        if brain is not UNSET:
            field_dict["brain"] = brain

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        answer = d.pop("answer", UNSET)

        skill = d.pop("skill", UNSET)

        brain = d.pop("brain", UNSET)

        deployment_models = cls(
            answer=answer,
            skill=skill,
            brain=brain,
        )

        return deployment_models
