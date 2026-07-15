"""Tool authoring primitive.

A tool is a name + JSON-Schema input + either an in-process handler (the SDK
answers the tool call locally — the v2 round-trip, libraos/libraos#842) or a
webhook URL (LibraOS HMAC-POSTs the call — works today, v1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

JSONSchema = dict[str, Any]
ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass
class Tool:
    name: str
    input_schema: JSONSchema
    description: str = ""
    handler: Optional[ToolHandler] = None
    webhook_url: Optional[str] = None


def tool(
    name: str,
    input_schema: JSONSchema,
    handler: Optional[ToolHandler] = None,
    *,
    description: str = "",
    webhook_url: Optional[str] = None,
) -> Tool:
    """Define a tool the agent can call.

    Provide ``handler`` for the in-process round-trip (the SDK answers the tool
    call locally), or pass ``webhook_url`` for the webhook model that works
    today. ``input_schema`` is a JSON Schema dict.
    """
    if not name or not name.strip():
        raise ValueError("tool: `name` is required")
    return Tool(
        name=name,
        input_schema=input_schema,
        description=description,
        handler=handler,
        webhook_url=webhook_url,
    )
