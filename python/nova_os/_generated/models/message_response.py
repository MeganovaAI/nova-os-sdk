from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.message_response_stop_reason import MessageResponseStopReason
from ..models.message_response_type import MessageResponseType
from ..models.role import Role
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_response_usage import MessageResponseUsage
    from ..models.output_violation import OutputViolation
    from ..models.route_hint_ask_clarification import RouteHintAskClarification
    from ..models.route_hint_navigate_to import RouteHintNavigateTo
    from ..models.route_hint_render_inline import RouteHintRenderInline
    from ..models.text_block import TextBlock
    from ..models.tool_result_block import ToolResultBlock
    from ..models.tool_use_block import ToolUseBlock


T = TypeVar("T", bound="MessageResponse")


@_attrs_define
class MessageResponse:
    """
    Attributes:
        id (str):
        role (Role):
        content (list[TextBlock | ToolResultBlock | ToolUseBlock]):
        model (str): Resolved model that handled the request.
        stop_reason (MessageResponseStopReason):
        type_ (MessageResponseType | Unset):
        usage (MessageResponseUsage | Unset):
        model_used (str | Unset): Nova OS extension — same as `model`, surfaced for clarity.
        fallback_triggered (bool | Unset): Nova OS extension — true if a fallback model handled the request.
        output_violations (list[OutputViolation] | Unset): Nova OS extension — populated only when the agent declared an
            `output_type` contract AND the reply failed validation AND the
            agent's `violation_mode` is `log` or `repair` (with `error`,
            the response is a 422 instead). Empty array means no violations.
        route_hint (RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline | Unset): Brain's dispatch
            hint, present on every terminal reply (v0.1.5+).
            Three kinds — partners switch on `kind` to decide UI behaviour.
    """

    id: str
    role: Role
    content: list[TextBlock | ToolResultBlock | ToolUseBlock]
    model: str
    stop_reason: MessageResponseStopReason
    type_: MessageResponseType | Unset = UNSET
    usage: MessageResponseUsage | Unset = UNSET
    model_used: str | Unset = UNSET
    fallback_triggered: bool | Unset = UNSET
    output_violations: list[OutputViolation] | Unset = UNSET
    route_hint: RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.route_hint_navigate_to import RouteHintNavigateTo
        from ..models.route_hint_render_inline import RouteHintRenderInline
        from ..models.text_block import TextBlock
        from ..models.tool_use_block import ToolUseBlock

        id = self.id

        role = self.role.value

        content = []
        for content_item_data in self.content:
            content_item: dict[str, Any]
            if isinstance(content_item_data, TextBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, ToolUseBlock):
                content_item = content_item_data.to_dict()
            else:
                content_item = content_item_data.to_dict()

            content.append(content_item)

        model = self.model

        stop_reason = self.stop_reason.value

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()

        model_used = self.model_used

        fallback_triggered = self.fallback_triggered

        output_violations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.output_violations, Unset):
            output_violations = []
            for output_violations_item_data in self.output_violations:
                output_violations_item = output_violations_item_data.to_dict()
                output_violations.append(output_violations_item)

        route_hint: dict[str, Any] | Unset
        if isinstance(self.route_hint, Unset):
            route_hint = UNSET
        elif isinstance(self.route_hint, RouteHintRenderInline):
            route_hint = self.route_hint.to_dict()
        elif isinstance(self.route_hint, RouteHintNavigateTo):
            route_hint = self.route_hint.to_dict()
        else:
            route_hint = self.route_hint.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "role": role,
                "content": content,
                "model": model,
                "stop_reason": stop_reason,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if usage is not UNSET:
            field_dict["usage"] = usage
        if model_used is not UNSET:
            field_dict["model_used"] = model_used
        if fallback_triggered is not UNSET:
            field_dict["fallback_triggered"] = fallback_triggered
        if output_violations is not UNSET:
            field_dict["output_violations"] = output_violations
        if route_hint is not UNSET:
            field_dict["route_hint"] = route_hint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_response_usage import MessageResponseUsage
        from ..models.output_violation import OutputViolation
        from ..models.route_hint_ask_clarification import RouteHintAskClarification
        from ..models.route_hint_navigate_to import RouteHintNavigateTo
        from ..models.route_hint_render_inline import RouteHintRenderInline
        from ..models.text_block import TextBlock
        from ..models.tool_result_block import ToolResultBlock
        from ..models.tool_use_block import ToolUseBlock

        d = dict(src_dict)
        id = d.pop("id")

        role = Role(d.pop("role"))

        content = []
        _content = d.pop("content")
        for content_item_data in _content:

            def _parse_content_item(data: object) -> TextBlock | ToolResultBlock | ToolUseBlock:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_content_block_type_0 = TextBlock.from_dict(data)

                    return componentsschemas_content_block_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_content_block_type_1 = ToolUseBlock.from_dict(data)

                    return componentsschemas_content_block_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_content_block_type_2 = ToolResultBlock.from_dict(data)

                return componentsschemas_content_block_type_2

            content_item = _parse_content_item(content_item_data)

            content.append(content_item)

        model = d.pop("model")

        stop_reason = MessageResponseStopReason(d.pop("stop_reason"))

        _type_ = d.pop("type", UNSET)
        type_: MessageResponseType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = MessageResponseType(_type_)

        _usage = d.pop("usage", UNSET)
        usage: MessageResponseUsage | Unset
        if isinstance(_usage, Unset):
            usage = UNSET
        else:
            usage = MessageResponseUsage.from_dict(_usage)

        model_used = d.pop("model_used", UNSET)

        fallback_triggered = d.pop("fallback_triggered", UNSET)

        _output_violations = d.pop("output_violations", UNSET)
        output_violations: list[OutputViolation] | Unset = UNSET
        if _output_violations is not UNSET:
            output_violations = []
            for output_violations_item_data in _output_violations:
                output_violations_item = OutputViolation.from_dict(output_violations_item_data)

                output_violations.append(output_violations_item)

        def _parse_route_hint(
            data: object,
        ) -> RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_route_hint_type_0 = RouteHintRenderInline.from_dict(data)

                return componentsschemas_route_hint_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_route_hint_type_1 = RouteHintNavigateTo.from_dict(data)

                return componentsschemas_route_hint_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_route_hint_type_2 = RouteHintAskClarification.from_dict(data)

            return componentsschemas_route_hint_type_2

        route_hint = _parse_route_hint(d.pop("route_hint", UNSET))

        message_response = cls(
            id=id,
            role=role,
            content=content,
            model=model,
            stop_reason=stop_reason,
            type_=type_,
            usage=usage,
            model_used=model_used,
            fallback_triggered=fallback_triggered,
            output_violations=output_violations,
            route_hint=route_hint,
        )

        message_response.additional_properties = d
        return message_response

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
