from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StartEvalRunBody")


@_attrs_define
class StartEvalRunBody:
    """
    Attributes:
        suite_name (str):
        agent_id (str):
        blueprint_digest (str):
        knowledge_digest (str):
        suite_revision (int | Unset): Zero or omitted selects the latest revision.
    """

    suite_name: str
    agent_id: str
    blueprint_digest: str
    knowledge_digest: str
    suite_revision: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        suite_name = self.suite_name

        agent_id = self.agent_id

        blueprint_digest = self.blueprint_digest

        knowledge_digest = self.knowledge_digest

        suite_revision = self.suite_revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "suite_name": suite_name,
                "agent_id": agent_id,
                "blueprint_digest": blueprint_digest,
                "knowledge_digest": knowledge_digest,
            }
        )
        if suite_revision is not UNSET:
            field_dict["suite_revision"] = suite_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        suite_name = d.pop("suite_name")

        agent_id = d.pop("agent_id")

        blueprint_digest = d.pop("blueprint_digest")

        knowledge_digest = d.pop("knowledge_digest")

        suite_revision = d.pop("suite_revision", UNSET)

        start_eval_run_body = cls(
            suite_name=suite_name,
            agent_id=agent_id,
            blueprint_digest=blueprint_digest,
            knowledge_digest=knowledge_digest,
            suite_revision=suite_revision,
        )

        start_eval_run_body.additional_properties = d
        return start_eval_run_body

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
