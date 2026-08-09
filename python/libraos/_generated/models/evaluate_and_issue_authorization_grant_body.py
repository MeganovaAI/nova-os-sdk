from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope


T = TypeVar("T", bound="EvaluateAndIssueAuthorizationGrantBody")


@_attrs_define
class EvaluateAndIssueAuthorizationGrantBody:
    """
    Attributes:
        agent_id (str):
        action_class (str):
        tool_bindings (list[str]):
        risk_tier (str):
        policy_version (str):
        data_scope (AuthorizationDataScope): Canonical comparable policy envelope.
        min_evidence (float | Unset):
        ttl_seconds (int | Unset):
        sample_rate (float | Unset):
    """

    agent_id: str
    action_class: str
    tool_bindings: list[str]
    risk_tier: str
    policy_version: str
    data_scope: AuthorizationDataScope
    min_evidence: float | Unset = UNSET
    ttl_seconds: int | Unset = UNSET
    sample_rate: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        action_class = self.action_class

        tool_bindings = self.tool_bindings

        risk_tier = self.risk_tier

        policy_version = self.policy_version

        data_scope = self.data_scope.to_dict()

        min_evidence = self.min_evidence

        ttl_seconds = self.ttl_seconds

        sample_rate = self.sample_rate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "action_class": action_class,
                "tool_bindings": tool_bindings,
                "risk_tier": risk_tier,
                "policy_version": policy_version,
                "data_scope": data_scope,
            }
        )
        if min_evidence is not UNSET:
            field_dict["min_evidence"] = min_evidence
        if ttl_seconds is not UNSET:
            field_dict["ttl_seconds"] = ttl_seconds
        if sample_rate is not UNSET:
            field_dict["sample_rate"] = sample_rate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope

        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        action_class = d.pop("action_class")

        tool_bindings = cast(list[str], d.pop("tool_bindings"))

        risk_tier = d.pop("risk_tier")

        policy_version = d.pop("policy_version")

        data_scope = AuthorizationDataScope.from_dict(d.pop("data_scope"))

        min_evidence = d.pop("min_evidence", UNSET)

        ttl_seconds = d.pop("ttl_seconds", UNSET)

        sample_rate = d.pop("sample_rate", UNSET)

        evaluate_and_issue_authorization_grant_body = cls(
            agent_id=agent_id,
            action_class=action_class,
            tool_bindings=tool_bindings,
            risk_tier=risk_tier,
            policy_version=policy_version,
            data_scope=data_scope,
            min_evidence=min_evidence,
            ttl_seconds=ttl_seconds,
            sample_rate=sample_rate,
        )

        evaluate_and_issue_authorization_grant_body.additional_properties = d
        return evaluate_and_issue_authorization_grant_body

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
