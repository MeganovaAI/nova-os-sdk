from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SessionCreate")


@_attrs_define
class SessionCreate:
    """
    Attributes:
        agent_id (str):
        environment_id (str | Unset):
        model (str | Unset):
    """

    agent_id: str
    environment_id: str | Unset = UNSET
    model: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        environment_id = self.environment_id

        model = self.model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
            }
        )
        if environment_id is not UNSET:
            field_dict["environment_id"] = environment_id
        if model is not UNSET:
            field_dict["model"] = model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        environment_id = d.pop("environment_id", UNSET)

        model = d.pop("model", UNSET)

        session_create = cls(
            agent_id=agent_id,
            environment_id=environment_id,
            model=model,
        )

        session_create.additional_properties = d
        return session_create

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
