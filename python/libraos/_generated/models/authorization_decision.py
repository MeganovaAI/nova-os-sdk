from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthorizationDecision")


@_attrs_define
class AuthorizationDecision:
    """Append-only authorization decision with its complete authorization-basis snapshot.

    Attributes:
        id (str):
        intent_id (str):
        outcome (str):
        risk_tier (str):
        evaluated_at (datetime.datetime):
        decided_by (str):
        decided_by_kind (str):
        decided_at (datetime.datetime):
        reason (str):
        edited (bool):
        evidence_weight (float):
        corrected (bool):
        grant_id (str | Unset):
        grant_revision (int | Unset):
        policy_version (str | Unset):
        runtime_profile (Any | Unset):
        original_params (Any | Unset):
        review_duration_ms (int | Unset):
        batch_id (str | Unset):
        correction_reason (str | Unset):
    """

    id: str
    intent_id: str
    outcome: str
    risk_tier: str
    evaluated_at: datetime.datetime
    decided_by: str
    decided_by_kind: str
    decided_at: datetime.datetime
    reason: str
    edited: bool
    evidence_weight: float
    corrected: bool
    grant_id: str | Unset = UNSET
    grant_revision: int | Unset = UNSET
    policy_version: str | Unset = UNSET
    runtime_profile: Any | Unset = UNSET
    original_params: Any | Unset = UNSET
    review_duration_ms: int | Unset = UNSET
    batch_id: str | Unset = UNSET
    correction_reason: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        intent_id = self.intent_id

        outcome = self.outcome

        risk_tier = self.risk_tier

        evaluated_at = self.evaluated_at.isoformat()

        decided_by = self.decided_by

        decided_by_kind = self.decided_by_kind

        decided_at = self.decided_at.isoformat()

        reason = self.reason

        edited = self.edited

        evidence_weight = self.evidence_weight

        corrected = self.corrected

        grant_id = self.grant_id

        grant_revision = self.grant_revision

        policy_version = self.policy_version

        runtime_profile = self.runtime_profile

        original_params = self.original_params

        review_duration_ms = self.review_duration_ms

        batch_id = self.batch_id

        correction_reason = self.correction_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "intent_id": intent_id,
                "outcome": outcome,
                "risk_tier": risk_tier,
                "evaluated_at": evaluated_at,
                "decided_by": decided_by,
                "decided_by_kind": decided_by_kind,
                "decided_at": decided_at,
                "reason": reason,
                "edited": edited,
                "evidence_weight": evidence_weight,
                "corrected": corrected,
            }
        )
        if grant_id is not UNSET:
            field_dict["grant_id"] = grant_id
        if grant_revision is not UNSET:
            field_dict["grant_revision"] = grant_revision
        if policy_version is not UNSET:
            field_dict["policy_version"] = policy_version
        if runtime_profile is not UNSET:
            field_dict["runtime_profile"] = runtime_profile
        if original_params is not UNSET:
            field_dict["original_params"] = original_params
        if review_duration_ms is not UNSET:
            field_dict["review_duration_ms"] = review_duration_ms
        if batch_id is not UNSET:
            field_dict["batch_id"] = batch_id
        if correction_reason is not UNSET:
            field_dict["correction_reason"] = correction_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        intent_id = d.pop("intent_id")

        outcome = d.pop("outcome")

        risk_tier = d.pop("risk_tier")

        evaluated_at = isoparse(d.pop("evaluated_at"))

        decided_by = d.pop("decided_by")

        decided_by_kind = d.pop("decided_by_kind")

        decided_at = isoparse(d.pop("decided_at"))

        reason = d.pop("reason")

        edited = d.pop("edited")

        evidence_weight = d.pop("evidence_weight")

        corrected = d.pop("corrected")

        grant_id = d.pop("grant_id", UNSET)

        grant_revision = d.pop("grant_revision", UNSET)

        policy_version = d.pop("policy_version", UNSET)

        runtime_profile = d.pop("runtime_profile", UNSET)

        original_params = d.pop("original_params", UNSET)

        review_duration_ms = d.pop("review_duration_ms", UNSET)

        batch_id = d.pop("batch_id", UNSET)

        correction_reason = d.pop("correction_reason", UNSET)

        authorization_decision = cls(
            id=id,
            intent_id=intent_id,
            outcome=outcome,
            risk_tier=risk_tier,
            evaluated_at=evaluated_at,
            decided_by=decided_by,
            decided_by_kind=decided_by_kind,
            decided_at=decided_at,
            reason=reason,
            edited=edited,
            evidence_weight=evidence_weight,
            corrected=corrected,
            grant_id=grant_id,
            grant_revision=grant_revision,
            policy_version=policy_version,
            runtime_profile=runtime_profile,
            original_params=original_params,
            review_duration_ms=review_duration_ms,
            batch_id=batch_id,
            correction_reason=correction_reason,
        )

        authorization_decision.additional_properties = d
        return authorization_decision

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
