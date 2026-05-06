from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_type import AgentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_create_route_templates import AgentCreateRouteTemplates
    from ..models.custom_tool import CustomTool
    from ..models.custom_tool_callback import CustomToolCallback
    from ..models.model_config import ModelConfig
    from ..models.output_type_contract import OutputTypeContract
    from ..models.skill import Skill
    from ..models.web_search_config import WebSearchConfig


T = TypeVar("T", bound="AgentCreate")


@_attrs_define
class AgentCreate:
    """
    Attributes:
        id (str):
        type_ (AgentType): Whether this agent dispatches to other skill agents (persona) or
            executes one skill directly (skill). Maps to nova-os internals;
            partners only see the discriminator.
        owner_employee (str | Unset):
        system_prompt (str | Unset):
        capabilities (list[str] | Unset):
        skills (list[Skill] | Unset):
        model_config (ModelConfig | Unset): Three-slot model configuration. Any slot may be omitted; resolution
            falls through per the spec (per-call → per-skill → per-agent →
            per-employee → server default).
        web_search_config (WebSearchConfig | Unset): Persona-level web-search configuration. Resolved per-invocation on
            ``skill_deep_research`` via ``searchctx.WebSearchConfigFromContext``.
            Field names changed in nova-os PR #212 (closes #200) — old
            ``backend`` / ``fallback`` are no longer accepted.
        custom_tools (list[CustomTool] | Unset):
        callback (CustomToolCallback | Unset):
        max_turns (int | Unset):  Default: 10.
        output_type (OutputTypeContract | Unset): Structured-output contract for agent replies. When set, Nova OS
            validates every assistant reply against `schema` before return.
            Server-side since v0.1.4.
        route_templates (AgentCreateRouteTemplates | Unset): URL templates Brain may fill into `navigate_to:` route
            hints.
            Server-side validation rejects non-string values; see Agent
            schema for the typed shape.
    """

    id: str
    type_: AgentType
    owner_employee: str | Unset = UNSET
    system_prompt: str | Unset = UNSET
    capabilities: list[str] | Unset = UNSET
    skills: list[Skill] | Unset = UNSET
    model_config: ModelConfig | Unset = UNSET
    web_search_config: WebSearchConfig | Unset = UNSET
    custom_tools: list[CustomTool] | Unset = UNSET
    callback: CustomToolCallback | Unset = UNSET
    max_turns: int | Unset = 10
    output_type: OutputTypeContract | Unset = UNSET
    route_templates: AgentCreateRouteTemplates | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_.value

        owner_employee = self.owner_employee

        system_prompt = self.system_prompt

        capabilities: list[str] | Unset = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = self.capabilities

        skills: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.skills, Unset):
            skills = []
            for skills_item_data in self.skills:
                skills_item = skills_item_data.to_dict()
                skills.append(skills_item)

        model_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.model_config, Unset):
            model_config = self.model_config.to_dict()

        web_search_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.web_search_config, Unset):
            web_search_config = self.web_search_config.to_dict()

        custom_tools: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.custom_tools, Unset):
            custom_tools = []
            for custom_tools_item_data in self.custom_tools:
                custom_tools_item = custom_tools_item_data.to_dict()
                custom_tools.append(custom_tools_item)

        callback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.callback, Unset):
            callback = self.callback.to_dict()

        max_turns = self.max_turns

        output_type: dict[str, Any] | Unset = UNSET
        if not isinstance(self.output_type, Unset):
            output_type = self.output_type.to_dict()

        route_templates: dict[str, Any] | Unset = UNSET
        if not isinstance(self.route_templates, Unset):
            route_templates = self.route_templates.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
            }
        )
        if owner_employee is not UNSET:
            field_dict["owner_employee"] = owner_employee
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if skills is not UNSET:
            field_dict["skills"] = skills
        if model_config is not UNSET:
            field_dict["model_config"] = model_config
        if web_search_config is not UNSET:
            field_dict["web_search_config"] = web_search_config
        if custom_tools is not UNSET:
            field_dict["custom_tools"] = custom_tools
        if callback is not UNSET:
            field_dict["callback"] = callback
        if max_turns is not UNSET:
            field_dict["max_turns"] = max_turns
        if output_type is not UNSET:
            field_dict["output_type"] = output_type
        if route_templates is not UNSET:
            field_dict["route_templates"] = route_templates

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_create_route_templates import AgentCreateRouteTemplates
        from ..models.custom_tool import CustomTool
        from ..models.custom_tool_callback import CustomToolCallback
        from ..models.model_config import ModelConfig
        from ..models.output_type_contract import OutputTypeContract
        from ..models.skill import Skill
        from ..models.web_search_config import WebSearchConfig

        d = dict(src_dict)
        id = d.pop("id")

        type_ = AgentType(d.pop("type"))

        owner_employee = d.pop("owner_employee", UNSET)

        system_prompt = d.pop("system_prompt", UNSET)

        capabilities = cast(list[str], d.pop("capabilities", UNSET))

        _skills = d.pop("skills", UNSET)
        skills: list[Skill] | Unset = UNSET
        if _skills is not UNSET:
            skills = []
            for skills_item_data in _skills:
                skills_item = Skill.from_dict(skills_item_data)

                skills.append(skills_item)

        _model_config = d.pop("model_config", UNSET)
        model_config: ModelConfig | Unset
        if isinstance(_model_config, Unset):
            model_config = UNSET
        else:
            model_config = ModelConfig.from_dict(_model_config)

        _web_search_config = d.pop("web_search_config", UNSET)
        web_search_config: WebSearchConfig | Unset
        if isinstance(_web_search_config, Unset):
            web_search_config = UNSET
        else:
            web_search_config = WebSearchConfig.from_dict(_web_search_config)

        _custom_tools = d.pop("custom_tools", UNSET)
        custom_tools: list[CustomTool] | Unset = UNSET
        if _custom_tools is not UNSET:
            custom_tools = []
            for custom_tools_item_data in _custom_tools:
                custom_tools_item = CustomTool.from_dict(custom_tools_item_data)

                custom_tools.append(custom_tools_item)

        _callback = d.pop("callback", UNSET)
        callback: CustomToolCallback | Unset
        if isinstance(_callback, Unset):
            callback = UNSET
        else:
            callback = CustomToolCallback.from_dict(_callback)

        max_turns = d.pop("max_turns", UNSET)

        _output_type = d.pop("output_type", UNSET)
        output_type: OutputTypeContract | Unset
        if isinstance(_output_type, Unset):
            output_type = UNSET
        else:
            output_type = OutputTypeContract.from_dict(_output_type)

        _route_templates = d.pop("route_templates", UNSET)
        route_templates: AgentCreateRouteTemplates | Unset
        if isinstance(_route_templates, Unset):
            route_templates = UNSET
        else:
            route_templates = AgentCreateRouteTemplates.from_dict(_route_templates)

        agent_create = cls(
            id=id,
            type_=type_,
            owner_employee=owner_employee,
            system_prompt=system_prompt,
            capabilities=capabilities,
            skills=skills,
            model_config=model_config,
            web_search_config=web_search_config,
            custom_tools=custom_tools,
            callback=callback,
            max_turns=max_turns,
            output_type=output_type,
            route_templates=route_templates,
        )

        agent_create.additional_properties = d
        return agent_create

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
