from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.infra_error_cluster import InfraErrorCluster
    from ..models.infra_grounding_counts import InfraGroundingCounts
    from ..models.infra_latency_stat import InfraLatencyStat
    from ..models.infra_tool_error import InfraToolError


T = TypeVar("T", bound="InfraHealth")


@_attrs_define
class InfraHealth:
    """Aggregated infrastructure-health signals over the requested window.

    Attributes:
        window_since (datetime.datetime):
        error_clusters (list[InfraErrorCluster]):
        tool_errors (list[InfraToolError]):
        latency (list[InfraLatencyStat]):
        identity_errors (list[InfraErrorCluster]):
        grounding_outcomes (InfraGroundingCounts):
    """

    window_since: datetime.datetime
    error_clusters: list[InfraErrorCluster]
    tool_errors: list[InfraToolError]
    latency: list[InfraLatencyStat]
    identity_errors: list[InfraErrorCluster]
    grounding_outcomes: InfraGroundingCounts
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        window_since = self.window_since.isoformat()

        error_clusters = []
        for error_clusters_item_data in self.error_clusters:
            error_clusters_item = error_clusters_item_data.to_dict()
            error_clusters.append(error_clusters_item)

        tool_errors = []
        for tool_errors_item_data in self.tool_errors:
            tool_errors_item = tool_errors_item_data.to_dict()
            tool_errors.append(tool_errors_item)

        latency = []
        for latency_item_data in self.latency:
            latency_item = latency_item_data.to_dict()
            latency.append(latency_item)

        identity_errors = []
        for identity_errors_item_data in self.identity_errors:
            identity_errors_item = identity_errors_item_data.to_dict()
            identity_errors.append(identity_errors_item)

        grounding_outcomes = self.grounding_outcomes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "window_since": window_since,
                "error_clusters": error_clusters,
                "tool_errors": tool_errors,
                "latency": latency,
                "identity_errors": identity_errors,
                "grounding_outcomes": grounding_outcomes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.infra_error_cluster import InfraErrorCluster
        from ..models.infra_grounding_counts import InfraGroundingCounts
        from ..models.infra_latency_stat import InfraLatencyStat
        from ..models.infra_tool_error import InfraToolError

        d = dict(src_dict)
        window_since = isoparse(d.pop("window_since"))

        error_clusters = []
        _error_clusters = d.pop("error_clusters")
        for error_clusters_item_data in _error_clusters:
            error_clusters_item = InfraErrorCluster.from_dict(error_clusters_item_data)

            error_clusters.append(error_clusters_item)

        tool_errors = []
        _tool_errors = d.pop("tool_errors")
        for tool_errors_item_data in _tool_errors:
            tool_errors_item = InfraToolError.from_dict(tool_errors_item_data)

            tool_errors.append(tool_errors_item)

        latency = []
        _latency = d.pop("latency")
        for latency_item_data in _latency:
            latency_item = InfraLatencyStat.from_dict(latency_item_data)

            latency.append(latency_item)

        identity_errors = []
        _identity_errors = d.pop("identity_errors")
        for identity_errors_item_data in _identity_errors:
            identity_errors_item = InfraErrorCluster.from_dict(identity_errors_item_data)

            identity_errors.append(identity_errors_item)

        grounding_outcomes = InfraGroundingCounts.from_dict(d.pop("grounding_outcomes"))

        infra_health = cls(
            window_since=window_since,
            error_clusters=error_clusters,
            tool_errors=tool_errors,
            latency=latency,
            identity_errors=identity_errors,
            grounding_outcomes=grounding_outcomes,
        )

        infra_health.additional_properties = d
        return infra_health

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
