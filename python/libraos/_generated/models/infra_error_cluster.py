from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="InfraErrorCluster")


@_attrs_define
class InfraErrorCluster:
    """
    Attributes:
        pattern (str):
        count (int):
        sample (str):
        first_seen (datetime.datetime):
        last_seen (datetime.datetime):
        top_agents (list[str] | Unset):
        top_models (list[str] | Unset):
        top_providers (list[str] | Unset):
    """

    pattern: str
    count: int
    sample: str
    first_seen: datetime.datetime
    last_seen: datetime.datetime
    top_agents: list[str] | Unset = UNSET
    top_models: list[str] | Unset = UNSET
    top_providers: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pattern = self.pattern

        count = self.count

        sample = self.sample

        first_seen = self.first_seen.isoformat()

        last_seen = self.last_seen.isoformat()

        top_agents: list[str] | Unset = UNSET
        if not isinstance(self.top_agents, Unset):
            top_agents = self.top_agents

        top_models: list[str] | Unset = UNSET
        if not isinstance(self.top_models, Unset):
            top_models = self.top_models

        top_providers: list[str] | Unset = UNSET
        if not isinstance(self.top_providers, Unset):
            top_providers = self.top_providers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pattern": pattern,
                "count": count,
                "sample": sample,
                "first_seen": first_seen,
                "last_seen": last_seen,
            }
        )
        if top_agents is not UNSET:
            field_dict["top_agents"] = top_agents
        if top_models is not UNSET:
            field_dict["top_models"] = top_models
        if top_providers is not UNSET:
            field_dict["top_providers"] = top_providers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pattern = d.pop("pattern")

        count = d.pop("count")

        sample = d.pop("sample")

        first_seen = isoparse(d.pop("first_seen"))

        last_seen = isoparse(d.pop("last_seen"))

        top_agents = cast(list[str], d.pop("top_agents", UNSET))

        top_models = cast(list[str], d.pop("top_models", UNSET))

        top_providers = cast(list[str], d.pop("top_providers", UNSET))

        infra_error_cluster = cls(
            pattern=pattern,
            count=count,
            sample=sample,
            first_seen=first_seen,
            last_seen=last_seen,
            top_agents=top_agents,
            top_models=top_models,
            top_providers=top_providers,
        )

        infra_error_cluster.additional_properties = d
        return infra_error_cluster

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
