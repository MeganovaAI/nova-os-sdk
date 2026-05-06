from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Session")


@_attrs_define
class Session:
    """
    Attributes:
        id (str): Format: sess_<uuid>.
        agent_id (str):
        environment_id (str | Unset):
        model (str | Unset): Session-default LLM override; per-event model on the messages endpoint takes precedence.
        created_at (datetime.datetime | Unset):
    """

    id: str
    agent_id: str
    environment_id: str | Unset = UNSET
    model: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        agent_id = self.agent_id

        environment_id = self.environment_id

        model = self.model

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "agent_id": agent_id,
            }
        )
        if environment_id is not UNSET:
            field_dict["environment_id"] = environment_id
        if model is not UNSET:
            field_dict["model"] = model
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        agent_id = d.pop("agent_id")

        environment_id = d.pop("environment_id", UNSET)

        model = d.pop("model", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        session = cls(
            id=id,
            agent_id=agent_id,
            environment_id=environment_id,
            model=model,
            created_at=created_at,
        )

        session.additional_properties = d
        return session

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
