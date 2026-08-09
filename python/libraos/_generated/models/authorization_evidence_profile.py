from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope
    from ..models.evidence_decay_bucket import EvidenceDecayBucket
    from ..models.reviewer_evidence import ReviewerEvidence


T = TypeVar("T", bound="AuthorizationEvidenceProfile")


@_attrs_define
class AuthorizationEvidenceProfile:
    """
    Attributes:
        agent_id (str):
        action_class (str):
        risk_tier (str):
        policy_version (str):
        data_scope (AuthorizationDataScope): Canonical comparable policy envelope.
        profile_hash (str):
        weighted_approved (float):
        weighted_rejected (float):
        effective_approval_rate (float):
        current_decisions (int):
        historical_decisions (int):
        incidents (int):
        eligible (bool):
        reason (str):
        decay (list[EvidenceDecayBucket]):
        reviewers (list[ReviewerEvidence]):
    """

    agent_id: str
    action_class: str
    risk_tier: str
    policy_version: str
    data_scope: AuthorizationDataScope
    profile_hash: str
    weighted_approved: float
    weighted_rejected: float
    effective_approval_rate: float
    current_decisions: int
    historical_decisions: int
    incidents: int
    eligible: bool
    reason: str
    decay: list[EvidenceDecayBucket]
    reviewers: list[ReviewerEvidence]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        action_class = self.action_class

        risk_tier = self.risk_tier

        policy_version = self.policy_version

        data_scope = self.data_scope.to_dict()

        profile_hash = self.profile_hash

        weighted_approved = self.weighted_approved

        weighted_rejected = self.weighted_rejected

        effective_approval_rate = self.effective_approval_rate

        current_decisions = self.current_decisions

        historical_decisions = self.historical_decisions

        incidents = self.incidents

        eligible = self.eligible

        reason = self.reason

        decay = []
        for decay_item_data in self.decay:
            decay_item = decay_item_data.to_dict()
            decay.append(decay_item)

        reviewers = []
        for reviewers_item_data in self.reviewers:
            reviewers_item = reviewers_item_data.to_dict()
            reviewers.append(reviewers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "action_class": action_class,
                "risk_tier": risk_tier,
                "policy_version": policy_version,
                "data_scope": data_scope,
                "profile_hash": profile_hash,
                "weighted_approved": weighted_approved,
                "weighted_rejected": weighted_rejected,
                "effective_approval_rate": effective_approval_rate,
                "current_decisions": current_decisions,
                "historical_decisions": historical_decisions,
                "incidents": incidents,
                "eligible": eligible,
                "reason": reason,
                "decay": decay,
                "reviewers": reviewers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope
        from ..models.evidence_decay_bucket import EvidenceDecayBucket
        from ..models.reviewer_evidence import ReviewerEvidence

        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        action_class = d.pop("action_class")

        risk_tier = d.pop("risk_tier")

        policy_version = d.pop("policy_version")

        data_scope = AuthorizationDataScope.from_dict(d.pop("data_scope"))

        profile_hash = d.pop("profile_hash")

        weighted_approved = d.pop("weighted_approved")

        weighted_rejected = d.pop("weighted_rejected")

        effective_approval_rate = d.pop("effective_approval_rate")

        current_decisions = d.pop("current_decisions")

        historical_decisions = d.pop("historical_decisions")

        incidents = d.pop("incidents")

        eligible = d.pop("eligible")

        reason = d.pop("reason")

        decay = []
        _decay = d.pop("decay")
        for decay_item_data in _decay:
            decay_item = EvidenceDecayBucket.from_dict(decay_item_data)

            decay.append(decay_item)

        reviewers = []
        _reviewers = d.pop("reviewers")
        for reviewers_item_data in _reviewers:
            reviewers_item = ReviewerEvidence.from_dict(reviewers_item_data)

            reviewers.append(reviewers_item)

        authorization_evidence_profile = cls(
            agent_id=agent_id,
            action_class=action_class,
            risk_tier=risk_tier,
            policy_version=policy_version,
            data_scope=data_scope,
            profile_hash=profile_hash,
            weighted_approved=weighted_approved,
            weighted_rejected=weighted_rejected,
            effective_approval_rate=effective_approval_rate,
            current_decisions=current_decisions,
            historical_decisions=historical_decisions,
            incidents=incidents,
            eligible=eligible,
            reason=reason,
            decay=decay,
            reviewers=reviewers,
        )

        authorization_evidence_profile.additional_properties = d
        return authorization_evidence_profile

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
