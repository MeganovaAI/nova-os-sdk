from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stream_event_route_hint_type import StreamEventRouteHintType

if TYPE_CHECKING:
    from ..models.route_hint_ask_clarification import RouteHintAskClarification
    from ..models.route_hint_navigate_to import RouteHintNavigateTo
    from ..models.route_hint_render_inline import RouteHintRenderInline


T = TypeVar("T", bound="StreamEventRouteHint")


@_attrs_define
class StreamEventRouteHint:
    """Nova OS extension (v0.1.5+) — emitted exactly once per terminal
    message right before `done`. Carries Brain's dispatch decision so
    partner UIs can react before the full reply is rendered.

        Attributes:
            type_ (StreamEventRouteHintType):
            route_hint (RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline): Brain's dispatch hint,
                present on every terminal reply (v0.1.5+).
                Three kinds — partners switch on `kind` to decide UI behaviour.
    """

    type_: StreamEventRouteHintType
    route_hint: RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.route_hint_navigate_to import RouteHintNavigateTo
        from ..models.route_hint_render_inline import RouteHintRenderInline

        type_ = self.type_.value

        route_hint: dict[str, Any]
        if isinstance(self.route_hint, RouteHintRenderInline):
            route_hint = self.route_hint.to_dict()
        elif isinstance(self.route_hint, RouteHintNavigateTo):
            route_hint = self.route_hint.to_dict()
        else:
            route_hint = self.route_hint.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "route_hint": route_hint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.route_hint_ask_clarification import RouteHintAskClarification
        from ..models.route_hint_navigate_to import RouteHintNavigateTo
        from ..models.route_hint_render_inline import RouteHintRenderInline

        d = dict(src_dict)
        type_ = StreamEventRouteHintType(d.pop("type"))

        def _parse_route_hint(data: object) -> RouteHintAskClarification | RouteHintNavigateTo | RouteHintRenderInline:
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

        route_hint = _parse_route_hint(d.pop("route_hint"))

        stream_event_route_hint = cls(
            type_=type_,
            route_hint=route_hint,
        )

        stream_event_route_hint.additional_properties = d
        return stream_event_route_hint

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
