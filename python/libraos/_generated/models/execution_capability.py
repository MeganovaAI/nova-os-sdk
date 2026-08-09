from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.execution_capability_governance_mode import ExecutionCapabilityGovernanceMode
from ..models.execution_capability_policy import ExecutionCapabilityPolicy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope


T = TypeVar("T", bound="ExecutionCapability")


@_attrs_define
class ExecutionCapability:
    """Short-lived brokered authorization credential; token appears only at issue time.

    Attributes:
        id (str):
        tenant_id (str):
        agent_id (str):
        tool_name (str):
        action_class (str):
        risk_tier (str):
        data_scope (AuthorizationDataScope): Canonical comparable policy envelope.
        policy (ExecutionCapabilityPolicy):
        policy_version (str):
        governance_mode (ExecutionCapabilityGovernanceMode):
        runtime_profile (Any):
        issued_by (str):
        issued_at (datetime.datetime):
        expires_at (datetime.datetime):
        grant_id (str | Unset):
        grant_revision (int | Unset):
        revoked_at (datetime.datetime | Unset):
        revocation_reason (str | Unset):
        token (str | Unset):
    """

    id: str
    tenant_id: str
    agent_id: str
    tool_name: str
    action_class: str
    risk_tier: str
    data_scope: AuthorizationDataScope
    policy: ExecutionCapabilityPolicy
    policy_version: str
    governance_mode: ExecutionCapabilityGovernanceMode
    runtime_profile: Any
    issued_by: str
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    grant_id: str | Unset = UNSET
    grant_revision: int | Unset = UNSET
    revoked_at: datetime.datetime | Unset = UNSET
    revocation_reason: str | Unset = UNSET
    token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        agent_id = self.agent_id

        tool_name = self.tool_name

        action_class = self.action_class

        risk_tier = self.risk_tier

        data_scope = self.data_scope.to_dict()

        policy = self.policy.value

        policy_version = self.policy_version

        governance_mode = self.governance_mode.value

        runtime_profile = self.runtime_profile

        issued_by = self.issued_by

        issued_at = self.issued_at.isoformat()

        expires_at = self.expires_at.isoformat()

        grant_id = self.grant_id

        grant_revision = self.grant_revision

        revoked_at: str | Unset = UNSET
        if not isinstance(self.revoked_at, Unset):
            revoked_at = self.revoked_at.isoformat()

        revocation_reason = self.revocation_reason

        token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "action_class": action_class,
                "risk_tier": risk_tier,
                "data_scope": data_scope,
                "policy": policy,
                "policy_version": policy_version,
                "governance_mode": governance_mode,
                "runtime_profile": runtime_profile,
                "issued_by": issued_by,
                "issued_at": issued_at,
                "expires_at": expires_at,
            }
        )
        if grant_id is not UNSET:
            field_dict["grant_id"] = grant_id
        if grant_revision is not UNSET:
            field_dict["grant_revision"] = grant_revision
        if revoked_at is not UNSET:
            field_dict["revoked_at"] = revoked_at
        if revocation_reason is not UNSET:
            field_dict["revocation_reason"] = revocation_reason
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope

        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenant_id")

        agent_id = d.pop("agent_id")

        tool_name = d.pop("tool_name")

        action_class = d.pop("action_class")

        risk_tier = d.pop("risk_tier")

        data_scope = AuthorizationDataScope.from_dict(d.pop("data_scope"))

        policy = ExecutionCapabilityPolicy(d.pop("policy"))

        policy_version = d.pop("policy_version")

        governance_mode = ExecutionCapabilityGovernanceMode(d.pop("governance_mode"))

        runtime_profile = d.pop("runtime_profile")

        issued_by = d.pop("issued_by")

        issued_at = isoparse(d.pop("issued_at"))

        expires_at = isoparse(d.pop("expires_at"))

        grant_id = d.pop("grant_id", UNSET)

        grant_revision = d.pop("grant_revision", UNSET)

        _revoked_at = d.pop("revoked_at", UNSET)
        revoked_at: datetime.datetime | Unset
        if isinstance(_revoked_at, Unset):
            revoked_at = UNSET
        else:
            revoked_at = isoparse(_revoked_at)

        revocation_reason = d.pop("revocation_reason", UNSET)

        token = d.pop("token", UNSET)

        execution_capability = cls(
            id=id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            tool_name=tool_name,
            action_class=action_class,
            risk_tier=risk_tier,
            data_scope=data_scope,
            policy=policy,
            policy_version=policy_version,
            governance_mode=governance_mode,
            runtime_profile=runtime_profile,
            issued_by=issued_by,
            issued_at=issued_at,
            expires_at=expires_at,
            grant_id=grant_id,
            grant_revision=grant_revision,
            revoked_at=revoked_at,
            revocation_reason=revocation_reason,
            token=token,
        )

        execution_capability.additional_properties = d
        return execution_capability

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
