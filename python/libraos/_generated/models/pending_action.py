from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.pending_action_risk import PendingActionRisk
from ..models.pending_action_status import PendingActionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pending_action_input import PendingActionInput
    from ..models.pending_action_preview import PendingActionPreview


T = TypeVar("T", bound="PendingAction")


@_attrs_define
class PendingAction:
    """A side-effecting action parked for human approval.

    Attributes:
        id (str):
        tool_name (str):
        risk (PendingActionRisk): Effective risk tier; an unknown/absent value fails safe to `high`.
        status (PendingActionStatus):
        created_at (datetime.datetime):
        agent_id (str | Unset):
        user_id (str | Unset):
        tenant_id (str | Unset):
        session_id (str | Unset):
        result (str | Unset): Terminal outcome detail (e.g. execution error); omitted when empty.
        decided_at (datetime.datetime | Unset):
        input_ (PendingActionInput | Unset): The tool arguments, forwarded as structured JSON.
        preview (PendingActionPreview | Unset): Dry-run preview of the action's effect, if computed.
        source (str | Unset): Connector queue label (connector-sourced actions).
        external_ref (str | Unset): Connector correlation key.
        group_id (str | Unset): Owning group; empty means admin-only.
        claimed_by (str | Unset): User id that soft-claimed the action.
        decided_by (str | Unset): User id that approved or rejected the action.
        reason (str | Unset): Why the action was approved or rejected.
    """

    id: str
    tool_name: str
    risk: PendingActionRisk
    status: PendingActionStatus
    created_at: datetime.datetime
    agent_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    result: str | Unset = UNSET
    decided_at: datetime.datetime | Unset = UNSET
    input_: PendingActionInput | Unset = UNSET
    preview: PendingActionPreview | Unset = UNSET
    source: str | Unset = UNSET
    external_ref: str | Unset = UNSET
    group_id: str | Unset = UNSET
    claimed_by: str | Unset = UNSET
    decided_by: str | Unset = UNSET
    reason: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tool_name = self.tool_name

        risk = self.risk.value

        status = self.status.value

        created_at = self.created_at.isoformat()

        agent_id = self.agent_id

        user_id = self.user_id

        tenant_id = self.tenant_id

        session_id = self.session_id

        result = self.result

        decided_at: str | Unset = UNSET
        if not isinstance(self.decided_at, Unset):
            decided_at = self.decided_at.isoformat()

        input_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.input_, Unset):
            input_ = self.input_.to_dict()

        preview: dict[str, Any] | Unset = UNSET
        if not isinstance(self.preview, Unset):
            preview = self.preview.to_dict()

        source = self.source

        external_ref = self.external_ref

        group_id = self.group_id

        claimed_by = self.claimed_by

        decided_by = self.decided_by

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tool_name": tool_name,
                "risk": risk,
                "status": status,
                "created_at": created_at,
            }
        )
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if result is not UNSET:
            field_dict["result"] = result
        if decided_at is not UNSET:
            field_dict["decided_at"] = decided_at
        if input_ is not UNSET:
            field_dict["input"] = input_
        if preview is not UNSET:
            field_dict["preview"] = preview
        if source is not UNSET:
            field_dict["source"] = source
        if external_ref is not UNSET:
            field_dict["external_ref"] = external_ref
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if claimed_by is not UNSET:
            field_dict["claimed_by"] = claimed_by
        if decided_by is not UNSET:
            field_dict["decided_by"] = decided_by
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pending_action_input import PendingActionInput
        from ..models.pending_action_preview import PendingActionPreview

        d = dict(src_dict)
        id = d.pop("id")

        tool_name = d.pop("tool_name")

        risk = PendingActionRisk(d.pop("risk"))

        status = PendingActionStatus(d.pop("status"))

        created_at = isoparse(d.pop("created_at"))

        agent_id = d.pop("agent_id", UNSET)

        user_id = d.pop("user_id", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        result = d.pop("result", UNSET)

        _decided_at = d.pop("decided_at", UNSET)
        decided_at: datetime.datetime | Unset
        if isinstance(_decided_at, Unset):
            decided_at = UNSET
        else:
            decided_at = isoparse(_decided_at)

        _input_ = d.pop("input", UNSET)
        input_: PendingActionInput | Unset
        if isinstance(_input_, Unset):
            input_ = UNSET
        else:
            input_ = PendingActionInput.from_dict(_input_)

        _preview = d.pop("preview", UNSET)
        preview: PendingActionPreview | Unset
        if isinstance(_preview, Unset):
            preview = UNSET
        else:
            preview = PendingActionPreview.from_dict(_preview)

        source = d.pop("source", UNSET)

        external_ref = d.pop("external_ref", UNSET)

        group_id = d.pop("group_id", UNSET)

        claimed_by = d.pop("claimed_by", UNSET)

        decided_by = d.pop("decided_by", UNSET)

        reason = d.pop("reason", UNSET)

        pending_action = cls(
            id=id,
            tool_name=tool_name,
            risk=risk,
            status=status,
            created_at=created_at,
            agent_id=agent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            result=result,
            decided_at=decided_at,
            input_=input_,
            preview=preview,
            source=source,
            external_ref=external_ref,
            group_id=group_id,
            claimed_by=claimed_by,
            decided_by=decided_by,
            reason=reason,
        )

        pending_action.additional_properties = d
        return pending_action

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
