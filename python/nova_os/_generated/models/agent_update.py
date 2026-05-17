from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_type import AgentType
from ..models.agent_update_visibility import AgentUpdateVisibility
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_update_filesystem import AgentUpdateFilesystem
    from ..models.agent_update_guardrails import AgentUpdateGuardrails
    from ..models.output_type_contract import OutputTypeContract


T = TypeVar("T", bound="AgentUpdate")


@_attrs_define
class AgentUpdate:
    """Partial update; only the fields supplied are changed.

    Attributes:
        name (str | Unset):
        model (str | Unset):
        system (str | Unset):
        tools (list[str] | Unset):
        owner (str | Unset):
        visibility (AgentUpdateVisibility | Unset):
        filesystem (AgentUpdateFilesystem | Unset):
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
        guardrails (AgentUpdateGuardrails | Unset):
    """

    name: str | Unset = UNSET
    model: str | Unset = UNSET
    system: str | Unset = UNSET
    tools: list[str] | Unset = UNSET
    owner: str | Unset = UNSET
    visibility: AgentUpdateVisibility | Unset = UNSET
    filesystem: AgentUpdateFilesystem | Unset = UNSET
    agent_type: AgentType | Unset = UNSET
    brain: bool | Unset = UNSET
    capabilities: list[str] | Unset = UNSET
    max_turns: int | Unset = UNSET
    output_type: OutputTypeContract | Unset = UNSET
    knowledge_bindings: list[str] | Unset = UNSET
    guardrails: AgentUpdateGuardrails | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        model = self.model

        system = self.system

        tools: list[str] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = self.tools

        owner = self.owner

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        filesystem: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filesystem, Unset):
            filesystem = self.filesystem.to_dict()

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
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
        if filesystem is not UNSET:
            field_dict["filesystem"] = filesystem
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_update_filesystem import AgentUpdateFilesystem
        from ..models.agent_update_guardrails import AgentUpdateGuardrails
        from ..models.output_type_contract import OutputTypeContract

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        model = d.pop("model", UNSET)

        system = d.pop("system", UNSET)

        tools = cast(list[str], d.pop("tools", UNSET))

        owner = d.pop("owner", UNSET)

        _visibility = d.pop("visibility", UNSET)
        visibility: AgentUpdateVisibility | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = AgentUpdateVisibility(_visibility)

        _filesystem = d.pop("filesystem", UNSET)
        filesystem: AgentUpdateFilesystem | Unset
        if isinstance(_filesystem, Unset):
            filesystem = UNSET
        else:
            filesystem = AgentUpdateFilesystem.from_dict(_filesystem)

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
        guardrails: AgentUpdateGuardrails | Unset
        if isinstance(_guardrails, Unset):
            guardrails = UNSET
        else:
            guardrails = AgentUpdateGuardrails.from_dict(_guardrails)

        agent_update = cls(
            name=name,
            model=model,
            system=system,
            tools=tools,
            owner=owner,
            visibility=visibility,
            filesystem=filesystem,
            agent_type=agent_type,
            brain=brain,
            capabilities=capabilities,
            max_turns=max_turns,
            output_type=output_type,
            knowledge_bindings=knowledge_bindings,
            guardrails=guardrails,
        )

        agent_update.additional_properties = d
        return agent_update

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
