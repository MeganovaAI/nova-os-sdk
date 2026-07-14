from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.agent_type import AgentType
from ..models.agent_visibility import AgentVisibility
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_filesystem import AgentFilesystem
    from ..models.agent_guardrails import AgentGuardrails
    from ..models.output_type_contract import OutputTypeContract


T = TypeVar("T", bound="Agent")


@_attrs_define
class Agent:
    """
    Attributes:
        id (str): Slug generated from the agent name.
        name (str):
        version (int | Unset):
        model (str | Unset): Optional model override; empty means inherit the server tier default.
        system (str | Unset):
        tools (list[str] | Unset):
        owner (str | Unset): Owner email; defaults to the caller when omitted.
        visibility (AgentVisibility | Unset):
        agent_type (AgentType | Unset): Whether this agent dispatches to other skill agents (persona) or
            executes one skill directly (skill). Maps to nova-os internals;
            partners only see the discriminator.
        brain (bool | Unset):
        capabilities (list[str] | Unset):
        max_turns (int | Unset):
        output_type (OutputTypeContract | Unset): Structured-output contract for agent replies. When set, Nova OS
            validates every assistant reply against `schema` before return.
            Server-side since v0.1.4.
        knowledge_bindings (list[str] | Unset):
        guardrails (AgentGuardrails | Unset):
        filesystem (AgentFilesystem | Unset):
        created_at (datetime.datetime | Unset):
        type_ (AgentType | Unset): Whether this agent dispatches to other skill agents (persona) or
            executes one skill directly (skill). Maps to nova-os internals;
            partners only see the discriminator.
        owner_employee (str | Unset):
        system_prompt (str | Unset):
    """

    id: str
    name: str
    version: int | Unset = UNSET
    model: str | Unset = UNSET
    system: str | Unset = UNSET
    tools: list[str] | Unset = UNSET
    owner: str | Unset = UNSET
    visibility: AgentVisibility | Unset = UNSET
    agent_type: AgentType | Unset = UNSET
    brain: bool | Unset = UNSET
    capabilities: list[str] | Unset = UNSET
    max_turns: int | Unset = UNSET
    output_type: OutputTypeContract | Unset = UNSET
    knowledge_bindings: list[str] | Unset = UNSET
    guardrails: AgentGuardrails | Unset = UNSET
    filesystem: AgentFilesystem | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    type_: AgentType | Unset = UNSET
    owner_employee: str | Unset = UNSET
    system_prompt: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        version = self.version

        model = self.model

        system = self.system

        tools: list[str] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = self.tools

        owner = self.owner

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        agent_type: str | Unset = UNSET
        if not isinstance(self.agent_type, Unset):
            agent_type = self.agent_type.value

        brain = self.brain

        capabilities: list[str] | Unset = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = self.capabilities

        max_turns = self.max_turns

        output_type: dict[str, Any] | Unset = UNSET
        if not isinstance(self.output_type, Unset):
            output_type = self.output_type.to_dict()

        knowledge_bindings: list[str] | Unset = UNSET
        if not isinstance(self.knowledge_bindings, Unset):
            knowledge_bindings = self.knowledge_bindings

        guardrails: dict[str, Any] | Unset = UNSET
        if not isinstance(self.guardrails, Unset):
            guardrails = self.guardrails.to_dict()

        filesystem: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filesystem, Unset):
            filesystem = self.filesystem.to_dict()

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        owner_employee = self.owner_employee

        system_prompt = self.system_prompt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if model is not UNSET:
            field_dict["model"] = model
        if system is not UNSET:
            field_dict["system"] = system
        if tools is not UNSET:
            field_dict["tools"] = tools
        if owner is not UNSET:
            field_dict["owner"] = owner
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if agent_type is not UNSET:
            field_dict["agent_type"] = agent_type
        if brain is not UNSET:
            field_dict["brain"] = brain
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if max_turns is not UNSET:
            field_dict["max_turns"] = max_turns
        if output_type is not UNSET:
            field_dict["output_type"] = output_type
        if knowledge_bindings is not UNSET:
            field_dict["knowledge_bindings"] = knowledge_bindings
        if guardrails is not UNSET:
            field_dict["guardrails"] = guardrails
        if filesystem is not UNSET:
            field_dict["filesystem"] = filesystem
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if type_ is not UNSET:
            field_dict["type"] = type_
        if owner_employee is not UNSET:
            field_dict["owner_employee"] = owner_employee
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_filesystem import AgentFilesystem
        from ..models.agent_guardrails import AgentGuardrails
        from ..models.output_type_contract import OutputTypeContract

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        version = d.pop("version", UNSET)

        model = d.pop("model", UNSET)

        system = d.pop("system", UNSET)

        tools = cast(list[str], d.pop("tools", UNSET))

        owner = d.pop("owner", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: AgentVisibility | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = AgentVisibility(_visibility)

        _agent_type = d.pop("agent_type", UNSET)
        agent_type: AgentType | Unset
        if isinstance(_agent_type, Unset):
            agent_type = UNSET
        else:
            agent_type = AgentType(_agent_type)

        brain = d.pop("brain", UNSET)

        capabilities = cast(list[str], d.pop("capabilities", UNSET))

        max_turns = d.pop("max_turns", UNSET)

        _output_type = d.pop("output_type", UNSET)
        output_type: OutputTypeContract | Unset
        if isinstance(_output_type, Unset):
            output_type = UNSET
        else:
            output_type = OutputTypeContract.from_dict(_output_type)

        knowledge_bindings = cast(list[str], d.pop("knowledge_bindings", UNSET))

        _guardrails = d.pop("guardrails", UNSET)
        guardrails: AgentGuardrails | Unset
        if isinstance(_guardrails, Unset):
            guardrails = UNSET
        else:
            guardrails = AgentGuardrails.from_dict(_guardrails)

        _filesystem = d.pop("filesystem", UNSET)
        filesystem: AgentFilesystem | Unset
        if isinstance(_filesystem, Unset):
            filesystem = UNSET
        else:
            filesystem = AgentFilesystem.from_dict(_filesystem)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _type_ = d.pop("type", UNSET)
        type_: AgentType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = AgentType(_type_)

        owner_employee = d.pop("owner_employee", UNSET)

        system_prompt = d.pop("system_prompt", UNSET)

        agent = cls(
            id=id,
            name=name,
            version=version,
            model=model,
            system=system,
            tools=tools,
            owner=owner,
            visibility=visibility,
            agent_type=agent_type,
            brain=brain,
            capabilities=capabilities,
            max_turns=max_turns,
            output_type=output_type,
            knowledge_bindings=knowledge_bindings,
            guardrails=guardrails,
            filesystem=filesystem,
            created_at=created_at,
            type_=type_,
            owner_employee=owner_employee,
            system_prompt=system_prompt,
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
