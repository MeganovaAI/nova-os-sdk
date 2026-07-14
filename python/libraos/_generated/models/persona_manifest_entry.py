from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.persona_manifest_entry_emits_route_hint_kinds_item import PersonaManifestEntryEmitsRouteHintKindsItem
from ..models.persona_triage import PersonaTriage

T = TypeVar("T", bound="PersonaManifestEntry")


@_attrs_define
class PersonaManifestEntry:
    """
    Attributes:
        id (str):
        display_name (str):
        capabilities (list[str]): Skill labels the persona dispatches to.
        triage (PersonaTriage): Resolved persona triage default. ``always_brain`` forces the
            planner; ``never_brain`` skips it; ``conditional`` defers to
            the per-turn regex/LLM triage chain. Per-call ``metadata.brain``
            on the messages endpoint still wins as an override. Resolved
            server-side by the canonical ``persona.ResolveTriage`` function
            — partners receive the projected value, not the raw frontmatter.
        emits_route_hint_kinds (list[PersonaManifestEntryEmitsRouteHintKindsItem]): Which RouteHint kinds the persona
            emits at all (drives partner UI prep).
        route_template_names (list[str]): Keys into the agent's route_templates map; partners pre-resolve URL templates.
    """

    id: str
    display_name: str
    capabilities: list[str]
    triage: PersonaTriage
    emits_route_hint_kinds: list[PersonaManifestEntryEmitsRouteHintKindsItem]
    route_template_names: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        capabilities = self.capabilities

        triage = self.triage.value

        emits_route_hint_kinds = []
        for emits_route_hint_kinds_item_data in self.emits_route_hint_kinds:
            emits_route_hint_kinds_item = emits_route_hint_kinds_item_data.value
            emits_route_hint_kinds.append(emits_route_hint_kinds_item)

        route_template_names = self.route_template_names

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "display_name": display_name,
                "capabilities": capabilities,
                "triage": triage,
                "emits_route_hint_kinds": emits_route_hint_kinds,
                "route_template_names": route_template_names,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("display_name")

        capabilities = cast(list[str], d.pop("capabilities"))

        triage = PersonaTriage(d.pop("triage"))

        emits_route_hint_kinds = []
        _emits_route_hint_kinds = d.pop("emits_route_hint_kinds")
        for emits_route_hint_kinds_item_data in _emits_route_hint_kinds:
            emits_route_hint_kinds_item = PersonaManifestEntryEmitsRouteHintKindsItem(emits_route_hint_kinds_item_data)

            emits_route_hint_kinds.append(emits_route_hint_kinds_item)

        route_template_names = cast(list[str], d.pop("route_template_names"))

        persona_manifest_entry = cls(
            id=id,
            display_name=display_name,
            capabilities=capabilities,
            triage=triage,
            emits_route_hint_kinds=emits_route_hint_kinds,
            route_template_names=route_template_names,
        )

        persona_manifest_entry.additional_properties = d
        return persona_manifest_entry

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
