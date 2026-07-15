"""Agent authoring.

``define_agent`` returns a serializable definition that ``LibraAdk.deploy``
writes to the LibraOS control plane (``/v1/agents``) and ``LibraAdk.run``
executes on the managed runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .tool import Tool


@dataclass
class Agent:
    name: str
    model: Optional[str] = None
    system: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)  # collection ids for RAG
    memory: Optional[str] = None  # "per-user" | "corporate" | "none"
    guardrails: Optional[dict[str, Any]] = None
    capabilities: list[str] = field(default_factory=list)
    output_type: Optional[dict[str, Any]] = None  # JSON Schema for structured output
    tools: list[Tool] = field(default_factory=list)
    max_turns: Optional[int] = None
    visibility: Optional[str] = None  # "public" | "private"

    def tool(self, name: str) -> Optional[Tool]:
        """Look up a tool by name (used by the runtime callback in v2)."""
        for t in self.tools:
            if t.name == name:
                return t
        return None

    def to_managed_agent_body(self) -> dict[str, Any]:
        """Serialize to the LibraOS ``POST/PUT /v1/agents`` request body.

        Tools are serialized as custom-tool declarations (name + input schema);
        their execution model — webhook (v1) vs. in-process (v2) — is resolved
        at run time, not here.
        """
        body: dict[str, Any] = {"name": self.name}
        if self.model:
            body["model"] = self.model
        if self.system:
            body["system"] = self.system
        if self.skills:
            body["skills"] = self.skills
        if self.capabilities:
            body["capabilities"] = self.capabilities
        if self.knowledge:
            body["knowledge_bindings"] = self.knowledge
        if self.max_turns is not None:
            body["max_turns"] = self.max_turns
        if self.visibility:
            body["visibility"] = self.visibility
        if self.output_type:
            body["output_type"] = self.output_type
        if self.guardrails is not None:
            body["guardrails"] = {"pii_redactor": bool(self.guardrails.get("pii_redactor", False))}
        if self.tools:
            body["custom_tools"] = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.input_schema,
                    **({"callback": t.webhook_url} if t.webhook_url else {}),
                }
                for t in self.tools
            ]
        return body


def define_agent(
    name: str,
    *,
    model: Optional[str] = None,
    system: Optional[str] = None,
    skills: Optional[list[str]] = None,
    knowledge: Optional[list[str]] = None,
    memory: Optional[str] = None,
    guardrails: Optional[dict[str, Any]] = None,
    capabilities: Optional[list[str]] = None,
    output_type: Optional[dict[str, Any]] = None,
    tools: Optional[list[Tool]] = None,
    max_turns: Optional[int] = None,
    visibility: Optional[str] = None,
) -> Agent:
    """Author a LibraOS agent. Deploy + run it with :class:`LibraAdk`."""
    if not name or not name.strip():
        raise ValueError("define_agent: `name` is required")
    tools = tools or []
    names = [t.name for t in tools]
    if len(set(names)) != len(names):
        raise ValueError("define_agent: duplicate tool names")
    return Agent(
        name=name,
        model=model,
        system=system,
        skills=skills or [],
        knowledge=knowledge or [],
        memory=memory,
        guardrails=guardrails,
        capabilities=capabilities or [],
        output_type=output_type,
        tools=tools,
        max_turns=max_turns,
        visibility=visibility,
    )
