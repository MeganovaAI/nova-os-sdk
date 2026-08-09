from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.autonomy_grant_lifecycle_state import AutonomyGrantLifecycleState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope
    from ..models.authorization_evidence_profile import AuthorizationEvidenceProfile
    from ..models.autonomy_grant_constraints import AutonomyGrantConstraints


T = TypeVar("T", bound="AutonomyGrant")


@_attrs_define
class AutonomyGrant:
    """Immutable grant definition plus current lifecycle-event projection.

    Attributes:
        id (str):
        revision (int):
        tenant_id (str):
        agent_id (str):
        action_class (str):
        tool_bindings (list[str]):
        risk_tier (str):
        data_scope (AuthorizationDataScope): Canonical comparable policy envelope.
        policy_version (str):
        runtime_profile (Any):
        profile_hash (str):
        evidence_window (AuthorizationEvidenceProfile):
        constraints (AutonomyGrantConstraints):
        issued_by (str):
        issued_at (datetime.datetime):
        expires_at (datetime.datetime):
        lifecycle_state (AutonomyGrantLifecycleState):
        lifecycle_reason (str):
        lifecycle_changed_at (datetime.datetime):
        previous_grant_id (str | Unset):
        superseded_by (str | Unset):
    """

    id: str
    revision: int
    tenant_id: str
    agent_id: str
    action_class: str
    tool_bindings: list[str]
    risk_tier: str
    data_scope: AuthorizationDataScope
    policy_version: str
    runtime_profile: Any
    profile_hash: str
    evidence_window: AuthorizationEvidenceProfile
    constraints: AutonomyGrantConstraints
    issued_by: str
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    lifecycle_state: AutonomyGrantLifecycleState
    lifecycle_reason: str
    lifecycle_changed_at: datetime.datetime
    previous_grant_id: str | Unset = UNSET
    superseded_by: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        revision = self.revision

        tenant_id = self.tenant_id

        agent_id = self.agent_id

        action_class = self.action_class

        tool_bindings = self.tool_bindings

        risk_tier = self.risk_tier

        data_scope = self.data_scope.to_dict()

        policy_version = self.policy_version

        runtime_profile = self.runtime_profile

        profile_hash = self.profile_hash

        evidence_window = self.evidence_window.to_dict()

        constraints = self.constraints.to_dict()

        issued_by = self.issued_by

        issued_at = self.issued_at.isoformat()

        expires_at = self.expires_at.isoformat()

        lifecycle_state = self.lifecycle_state.value

        lifecycle_reason = self.lifecycle_reason

        lifecycle_changed_at = self.lifecycle_changed_at.isoformat()

        previous_grant_id = self.previous_grant_id

        superseded_by = self.superseded_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "revision": revision,
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "action_class": action_class,
                "tool_bindings": tool_bindings,
                "risk_tier": risk_tier,
                "data_scope": data_scope,
                "policy_version": policy_version,
                "runtime_profile": runtime_profile,
                "profile_hash": profile_hash,
                "evidence_window": evidence_window,
                "constraints": constraints,
                "issued_by": issued_by,
                "issued_at": issued_at,
                "expires_at": expires_at,
                "lifecycle_state": lifecycle_state,
                "lifecycle_reason": lifecycle_reason,
                "lifecycle_changed_at": lifecycle_changed_at,
            }
        )
        if previous_grant_id is not UNSET:
            field_dict["previous_grant_id"] = previous_grant_id
        if superseded_by is not UNSET:
            field_dict["superseded_by"] = superseded_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope
        from ..models.authorization_evidence_profile import AuthorizationEvidenceProfile
        from ..models.autonomy_grant_constraints import AutonomyGrantConstraints

        d = dict(src_dict)
        id = d.pop("id")

        revision = d.pop("revision")

        tenant_id = d.pop("tenant_id")

        agent_id = d.pop("agent_id")

        action_class = d.pop("action_class")

        tool_bindings = cast(list[str], d.pop("tool_bindings"))

        risk_tier = d.pop("risk_tier")

        data_scope = AuthorizationDataScope.from_dict(d.pop("data_scope"))

        policy_version = d.pop("policy_version")

        runtime_profile = d.pop("runtime_profile")

        profile_hash = d.pop("profile_hash")

        evidence_window = AuthorizationEvidenceProfile.from_dict(d.pop("evidence_window"))

        constraints = AutonomyGrantConstraints.from_dict(d.pop("constraints"))

        issued_by = d.pop("issued_by")

        issued_at = isoparse(d.pop("issued_at"))

        expires_at = isoparse(d.pop("expires_at"))

        lifecycle_state = AutonomyGrantLifecycleState(d.pop("lifecycle_state"))

        lifecycle_reason = d.pop("lifecycle_reason")

        lifecycle_changed_at = isoparse(d.pop("lifecycle_changed_at"))

        previous_grant_id = d.pop("previous_grant_id", UNSET)

        superseded_by = d.pop("superseded_by", UNSET)

        autonomy_grant = cls(
            id=id,
            revision=revision,
            tenant_id=tenant_id,
            agent_id=agent_id,
            action_class=action_class,
            tool_bindings=tool_bindings,
            risk_tier=risk_tier,
            data_scope=data_scope,
            policy_version=policy_version,
            runtime_profile=runtime_profile,
            profile_hash=profile_hash,
            evidence_window=evidence_window,
            constraints=constraints,
            issued_by=issued_by,
            issued_at=issued_at,
            expires_at=expires_at,
            lifecycle_state=lifecycle_state,
            lifecycle_reason=lifecycle_reason,
            lifecycle_changed_at=lifecycle_changed_at,
            previous_grant_id=previous_grant_id,
            superseded_by=superseded_by,
        )

        autonomy_grant.additional_properties = d
        return autonomy_grant

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
