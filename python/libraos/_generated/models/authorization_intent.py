from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_data_scope import AuthorizationDataScope


T = TypeVar("T", bound="AuthorizationIntent")


@_attrs_define
class AuthorizationIntent:
    """Append-only declaration of a proposed side effect.

    Attributes:
        id (str):
        tenant_id (str):
        agent_id (str):
        session_id (str):
        tool_name (str):
        action_class (str):
        params (Any):
        reversible (bool | None):
        max_authorization_seconds (int | None):
        risk_tier (str):
        purpose (str):
        source (str):
        external_ref (str):
        group_id (str):
        proposed_by (str):
        proposed_by_kind (str):
        proposed_at (datetime.datetime):
        data_scope (AuthorizationDataScope | Unset): Canonical comparable policy envelope.
        side_effects (Any | Unset):
        legacy_action_id (str | Unset):
        policy_version (str | Unset):
        agent_config_hash (str | Unset):
        runtime_profile (Any | Unset):
        tool_schema_hash (str | Unset):
    """

    id: str
    tenant_id: str
    agent_id: str
    session_id: str
    tool_name: str
    action_class: str
    params: Any
    reversible: bool | None
    max_authorization_seconds: int | None
    risk_tier: str
    purpose: str
    source: str
    external_ref: str
    group_id: str
    proposed_by: str
    proposed_by_kind: str
    proposed_at: datetime.datetime
    data_scope: AuthorizationDataScope | Unset = UNSET
    side_effects: Any | Unset = UNSET
    legacy_action_id: str | Unset = UNSET
    policy_version: str | Unset = UNSET
    agent_config_hash: str | Unset = UNSET
    runtime_profile: Any | Unset = UNSET
    tool_schema_hash: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        agent_id = self.agent_id

        session_id = self.session_id

        tool_name = self.tool_name

        action_class = self.action_class

        params = self.params

        reversible: bool | None
        reversible = self.reversible

        max_authorization_seconds: int | None
        max_authorization_seconds = self.max_authorization_seconds

        risk_tier = self.risk_tier

        purpose = self.purpose

        source = self.source

        external_ref = self.external_ref

        group_id = self.group_id

        proposed_by = self.proposed_by

        proposed_by_kind = self.proposed_by_kind

        proposed_at = self.proposed_at.isoformat()

        data_scope: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data_scope, Unset):
            data_scope = self.data_scope.to_dict()

        side_effects = self.side_effects

        legacy_action_id = self.legacy_action_id

        policy_version = self.policy_version

        agent_config_hash = self.agent_config_hash

        runtime_profile = self.runtime_profile

        tool_schema_hash = self.tool_schema_hash

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "tool_name": tool_name,
                "action_class": action_class,
                "params": params,
                "reversible": reversible,
                "max_authorization_seconds": max_authorization_seconds,
                "risk_tier": risk_tier,
                "purpose": purpose,
                "source": source,
                "external_ref": external_ref,
                "group_id": group_id,
                "proposed_by": proposed_by,
                "proposed_by_kind": proposed_by_kind,
                "proposed_at": proposed_at,
            }
        )
        if data_scope is not UNSET:
            field_dict["data_scope"] = data_scope
        if side_effects is not UNSET:
            field_dict["side_effects"] = side_effects
        if legacy_action_id is not UNSET:
            field_dict["legacy_action_id"] = legacy_action_id
        if policy_version is not UNSET:
            field_dict["policy_version"] = policy_version
        if agent_config_hash is not UNSET:
            field_dict["agent_config_hash"] = agent_config_hash
        if runtime_profile is not UNSET:
            field_dict["runtime_profile"] = runtime_profile
        if tool_schema_hash is not UNSET:
            field_dict["tool_schema_hash"] = tool_schema_hash

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_data_scope import AuthorizationDataScope

        d = dict(src_dict)
        id = d.pop("id")

        tenant_id = d.pop("tenant_id")

        agent_id = d.pop("agent_id")

        session_id = d.pop("session_id")

        tool_name = d.pop("tool_name")

        action_class = d.pop("action_class")

        params = d.pop("params")

        def _parse_reversible(data: object) -> bool | None:
            if data is None:
                return data
            return cast(bool | None, data)

        reversible = _parse_reversible(d.pop("reversible"))

        def _parse_max_authorization_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        max_authorization_seconds = _parse_max_authorization_seconds(d.pop("max_authorization_seconds"))

        risk_tier = d.pop("risk_tier")

        purpose = d.pop("purpose")

        source = d.pop("source")

        external_ref = d.pop("external_ref")

        group_id = d.pop("group_id")

        proposed_by = d.pop("proposed_by")

        proposed_by_kind = d.pop("proposed_by_kind")

        proposed_at = isoparse(d.pop("proposed_at"))

        _data_scope = d.pop("data_scope", UNSET)
        data_scope: AuthorizationDataScope | Unset
        if isinstance(_data_scope, Unset):
            data_scope = UNSET
        else:
            data_scope = AuthorizationDataScope.from_dict(_data_scope)

        side_effects = d.pop("side_effects", UNSET)

        legacy_action_id = d.pop("legacy_action_id", UNSET)

        policy_version = d.pop("policy_version", UNSET)

        agent_config_hash = d.pop("agent_config_hash", UNSET)

        runtime_profile = d.pop("runtime_profile", UNSET)

        tool_schema_hash = d.pop("tool_schema_hash", UNSET)

        authorization_intent = cls(
            id=id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            session_id=session_id,
            tool_name=tool_name,
            action_class=action_class,
            params=params,
            reversible=reversible,
            max_authorization_seconds=max_authorization_seconds,
            risk_tier=risk_tier,
            purpose=purpose,
            source=source,
            external_ref=external_ref,
            group_id=group_id,
            proposed_by=proposed_by,
            proposed_by_kind=proposed_by_kind,
            proposed_at=proposed_at,
            data_scope=data_scope,
            side_effects=side_effects,
            legacy_action_id=legacy_action_id,
            policy_version=policy_version,
            agent_config_hash=agent_config_hash,
            runtime_profile=runtime_profile,
            tool_schema_hash=tool_schema_hash,
        )

        authorization_intent.additional_properties = d
        return authorization_intent

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
