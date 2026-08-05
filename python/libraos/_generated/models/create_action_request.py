from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_action_request_risk import CreateActionRequestRisk
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.action_callback import ActionCallback
    from ..models.create_action_request_input import CreateActionRequestInput
    from ..models.create_action_request_preview import CreateActionRequestPreview


T = TypeVar("T", bound="CreateActionRequest")


@_attrs_define
class CreateActionRequest:
    """Body for a connector parking an action for approval.

    Attributes:
        tool_name (str):
        input_ (CreateActionRequestInput): The tool arguments.
        source (str):
        callback (ActionCallback): Webhook fired when the action is approved. It is snapshotted onto the row and never
            surfaced back to clients.
        agent_id (str | Unset):
        user_id (str | Unset):
        tenant_id (str | Unset):
        session_id (str | Unset):
        group_id (str | Unset): Route the action to a departmental group queue.
        preview (CreateActionRequestPreview | Unset): Optional dry-run preview of the effect.
        risk (CreateActionRequestRisk | Unset): Effective risk tier; absent/unknown fails safe to `high`.
        external_ref (str | Unset):
    """

    tool_name: str
    input_: CreateActionRequestInput
    source: str
    callback: ActionCallback
    agent_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    group_id: str | Unset = UNSET
    preview: CreateActionRequestPreview | Unset = UNSET
    risk: CreateActionRequestRisk | Unset = UNSET
    external_ref: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool_name = self.tool_name

        input_ = self.input_.to_dict()

        source = self.source

        callback = self.callback.to_dict()

        agent_id = self.agent_id

        user_id = self.user_id

        tenant_id = self.tenant_id

        session_id = self.session_id

        group_id = self.group_id

        preview: dict[str, Any] | Unset = UNSET
        if not isinstance(self.preview, Unset):
            preview = self.preview.to_dict()

        risk: str | Unset = UNSET
        if not isinstance(self.risk, Unset):
            risk = self.risk.value

        external_ref = self.external_ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool_name": tool_name,
                "input": input_,
                "source": source,
                "callback": callback,
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
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if preview is not UNSET:
            field_dict["preview"] = preview
        if risk is not UNSET:
            field_dict["risk"] = risk
        if external_ref is not UNSET:
            field_dict["external_ref"] = external_ref

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_callback import ActionCallback
        from ..models.create_action_request_input import CreateActionRequestInput
        from ..models.create_action_request_preview import CreateActionRequestPreview

        d = dict(src_dict)
        tool_name = d.pop("tool_name")

        input_ = CreateActionRequestInput.from_dict(d.pop("input"))

        source = d.pop("source")

        callback = ActionCallback.from_dict(d.pop("callback"))

        agent_id = d.pop("agent_id", UNSET)

        user_id = d.pop("user_id", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        group_id = d.pop("group_id", UNSET)

        _preview = d.pop("preview", UNSET)
        preview: CreateActionRequestPreview | Unset
        if isinstance(_preview, Unset):
            preview = UNSET
        else:
            preview = CreateActionRequestPreview.from_dict(_preview)

        _risk = d.pop("risk", UNSET)
        risk: CreateActionRequestRisk | Unset
        if isinstance(_risk, Unset):
            risk = UNSET
        else:
            risk = CreateActionRequestRisk(_risk)

        external_ref = d.pop("external_ref", UNSET)

        create_action_request = cls(
            tool_name=tool_name,
            input_=input_,
            source=source,
            callback=callback,
            agent_id=agent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            group_id=group_id,
            preview=preview,
            risk=risk,
            external_ref=external_ref,
        )

        create_action_request.additional_properties = d
        return create_action_request

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
