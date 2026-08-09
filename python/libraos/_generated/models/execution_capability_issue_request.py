from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.execution_capability_issue_request_governance_mode import ExecutionCapabilityIssueRequestGovernanceMode
from ..models.execution_capability_issue_request_policy import ExecutionCapabilityIssueRequestPolicy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope
    from ..models.execution_capability_issue_request_callback import ExecutionCapabilityIssueRequestCallback
    from ..models.execution_capability_issue_request_managed_connector import (
        ExecutionCapabilityIssueRequestManagedConnector,
    )


T = TypeVar("T", bound="ExecutionCapabilityIssueRequest")


@_attrs_define
class ExecutionCapabilityIssueRequest:
    """Supply `callback` for brokered mode or `managed_connector` for desk-managed mode. The server rejects zero or two
    execution targets.

        Attributes:
            agent_id (str):
            tool_name (str):
            action_class (str):
            risk_tier (str):
            data_scope (AuthorizationDataScope): Canonical comparable policy envelope.
            policy (ExecutionCapabilityIssueRequestPolicy):
            policy_version (str):
            grant_id (str | Unset):
            governance_mode (ExecutionCapabilityIssueRequestGovernanceMode | Unset):  Default:
                ExecutionCapabilityIssueRequestGovernanceMode.BROKERED.
            callback (ExecutionCapabilityIssueRequestCallback | Unset):
            managed_connector (ExecutionCapabilityIssueRequestManagedConnector | Unset):
            ttl_seconds (int | Unset):
    """

    agent_id: str
    tool_name: str
    action_class: str
    risk_tier: str
    data_scope: AuthorizationDataScope
    policy: ExecutionCapabilityIssueRequestPolicy
    policy_version: str
    grant_id: str | Unset = UNSET
    governance_mode: ExecutionCapabilityIssueRequestGovernanceMode | Unset = (
        ExecutionCapabilityIssueRequestGovernanceMode.BROKERED
    )
    callback: ExecutionCapabilityIssueRequestCallback | Unset = UNSET
    managed_connector: ExecutionCapabilityIssueRequestManagedConnector | Unset = UNSET
    ttl_seconds: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        tool_name = self.tool_name

        action_class = self.action_class

        risk_tier = self.risk_tier

        data_scope = self.data_scope.to_dict()

        policy = self.policy.value

        policy_version = self.policy_version

        grant_id = self.grant_id

        governance_mode: str | Unset = UNSET
        if not isinstance(self.governance_mode, Unset):
            governance_mode = self.governance_mode.value

        callback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.callback, Unset):
            callback = self.callback.to_dict()

        managed_connector: dict[str, Any] | Unset = UNSET
        if not isinstance(self.managed_connector, Unset):
            managed_connector = self.managed_connector.to_dict()

        ttl_seconds = self.ttl_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "tool_name": tool_name,
                "action_class": action_class,
                "risk_tier": risk_tier,
                "data_scope": data_scope,
                "policy": policy,
                "policy_version": policy_version,
            }
        )
        if grant_id is not UNSET:
            field_dict["grant_id"] = grant_id
        if governance_mode is not UNSET:
            field_dict["governance_mode"] = governance_mode
        if callback is not UNSET:
            field_dict["callback"] = callback
        if managed_connector is not UNSET:
            field_dict["managed_connector"] = managed_connector
        if ttl_seconds is not UNSET:
            field_dict["ttl_seconds"] = ttl_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope
        from ..models.execution_capability_issue_request_callback import ExecutionCapabilityIssueRequestCallback
        from ..models.execution_capability_issue_request_managed_connector import (
            ExecutionCapabilityIssueRequestManagedConnector,
        )

        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        tool_name = d.pop("tool_name")

        action_class = d.pop("action_class")

        risk_tier = d.pop("risk_tier")

        data_scope = AuthorizationDataScope.from_dict(d.pop("data_scope"))

        policy = ExecutionCapabilityIssueRequestPolicy(d.pop("policy"))

        policy_version = d.pop("policy_version")

        grant_id = d.pop("grant_id", UNSET)

        _governance_mode = d.pop("governance_mode", UNSET)
        governance_mode: ExecutionCapabilityIssueRequestGovernanceMode | Unset
        if isinstance(_governance_mode, Unset):
            governance_mode = UNSET
        else:
            governance_mode = ExecutionCapabilityIssueRequestGovernanceMode(_governance_mode)

        _callback = d.pop("callback", UNSET)
        callback: ExecutionCapabilityIssueRequestCallback | Unset
        if isinstance(_callback, Unset):
            callback = UNSET
        else:
            callback = ExecutionCapabilityIssueRequestCallback.from_dict(_callback)

        _managed_connector = d.pop("managed_connector", UNSET)
        managed_connector: ExecutionCapabilityIssueRequestManagedConnector | Unset
        if isinstance(_managed_connector, Unset):
            managed_connector = UNSET
        else:
            managed_connector = ExecutionCapabilityIssueRequestManagedConnector.from_dict(_managed_connector)

        ttl_seconds = d.pop("ttl_seconds", UNSET)

        execution_capability_issue_request = cls(
            agent_id=agent_id,
            tool_name=tool_name,
            action_class=action_class,
            risk_tier=risk_tier,
            data_scope=data_scope,
            policy=policy,
            policy_version=policy_version,
            grant_id=grant_id,
            governance_mode=governance_mode,
            callback=callback,
            managed_connector=managed_connector,
            ttl_seconds=ttl_seconds,
        )

        execution_capability_issue_request.additional_properties = d
        return execution_capability_issue_request

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
