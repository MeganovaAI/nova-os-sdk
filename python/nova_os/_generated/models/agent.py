from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.agent_type import AgentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_tool import CustomTool
    from ..models.custom_tool_callback import CustomToolCallback
    from ..models.model_config import ModelConfig
    from ..models.skill import Skill
    from ..models.web_search_config import WebSearchConfig


T = TypeVar("T", bound="Agent")


@_attrs_define
class Agent:
    """
    Attributes:
        id (str):
        type_ (AgentType): Whether this agent dispatches to other skill agents (persona) or
            executes one skill directly (skill). Maps to nova-os internals;
            partners only see the discriminator.
        owner_employee (str | Unset): Employee that owns this agent (cascades model_config + callback).
        system_prompt (str | Unset):
        capabilities (list[str] | Unset): Skill labels this persona can dispatch to.
        skills (list[Skill] | Unset):
        model_config (ModelConfig | Unset): Three-slot model configuration. Any slot may be omitted; resolution
            falls through per the spec (per-call → per-skill → per-agent →
            per-employee → server default).
        web_search_config (WebSearchConfig | Unset):
        custom_tools (list[CustomTool] | Unset):
        callback (CustomToolCallback | Unset):
        max_turns (int | Unset):  Default: 10.
        created_at (datetime.datetime | Unset):
        updated_at (datetime.datetime | Unset):
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
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
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

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

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
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_tool import CustomTool
        from ..models.custom_tool_callback import CustomToolCallback
        from ..models.model_config import ModelConfig
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

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        agent = cls(
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
            created_at=created_at,
            updated_at=updated_at,
        )

        agent.additional_properties = d
        return agent

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
