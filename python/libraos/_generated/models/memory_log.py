from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.memory_log_scope import MemoryLogScope
from ..types import UNSET, Unset

T = TypeVar("T", bound="MemoryLog")


@_attrs_define
class MemoryLog:
    """
    Attributes:
        agent_id (str | Unset): The persona this memory belongs to.
        scope (MemoryLogScope | Unset): The memory scope that was read.
        content (str | Unset): The accumulated memory as text. Empty when nothing has been remembered yet.
        updated_at (datetime.datetime | Unset): When the memory log was last written.
        enabled (bool | Unset): False when observational memory is not active on this deployment.
        last_observed_at (datetime.datetime | Unset): When new activity was last folded into memory. Omitted when never
            observed.
    """

    agent_id: str | Unset = UNSET
    scope: MemoryLogScope | Unset = UNSET
    content: str | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    enabled: bool | Unset = UNSET
    last_observed_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        scope: str | Unset = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.value

        content = self.content

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        enabled = self.enabled

        last_observed_at: str | Unset = UNSET
        if not isinstance(self.last_observed_at, Unset):
            last_observed_at = self.last_observed_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if scope is not UNSET:
            field_dict["scope"] = scope
        if content is not UNSET:
            field_dict["content"] = content
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if last_observed_at is not UNSET:
            field_dict["last_observed_at"] = last_observed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent_id = d.pop("agent_id", UNSET)

        _scope = d.pop("scope", UNSET)
        scope: MemoryLogScope | Unset
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = MemoryLogScope(_scope)

        content = d.pop("content", UNSET)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        enabled = d.pop("enabled", UNSET)

        _last_observed_at = d.pop("last_observed_at", UNSET)
        last_observed_at: datetime.datetime | Unset
        if isinstance(_last_observed_at, Unset):
            last_observed_at = UNSET
        else:
            last_observed_at = isoparse(_last_observed_at)

        memory_log = cls(
            agent_id=agent_id,
            scope=scope,
            content=content,
            updated_at=updated_at,
            enabled=enabled,
            last_observed_at=last_observed_at,
        )

        memory_log.additional_properties = d
        return memory_log

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
