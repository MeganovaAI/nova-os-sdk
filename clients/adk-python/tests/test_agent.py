from libraos_adk import define_agent, tool


def test_serializes_to_managed_body():
    agent = define_agent(
        "refund-copilot",
        model="libraos/brain",
        system="hi",
        skills=["docx"],
        knowledge=["collection:refunds"],
        guardrails={"pii_redactor": True},
        max_turns=8,
        tools=[
            tool(
                "lookup_order",
                {"type": "object", "properties": {"orderId": {"type": "string"}}, "required": ["orderId"]},
                lambda a: a["orderId"],
            )
        ],
    )
    body = agent.to_managed_agent_body()
    assert body["name"] == "refund-copilot"
    assert body["model"] == "libraos/brain"
    assert body["knowledge_bindings"] == ["collection:refunds"]
    assert body["guardrails"] == {"pii_redactor": True}
    assert body["max_turns"] == 8
    assert body["custom_tools"][0]["name"] == "lookup_order"
    assert body["custom_tools"][0]["input_schema"]["required"] == ["orderId"]
    assert agent.tool("lookup_order") is not None


def test_webhook_tool_serializes_callback():
    agent = define_agent(
        "wh",
        tools=[tool("t", {"type": "object"}, webhook_url="https://x/tool")],
    )
    assert agent.to_managed_agent_body()["custom_tools"][0]["callback"] == "https://x/tool"


def test_rejects_duplicate_tool_names():
    import pytest

    with pytest.raises(ValueError):
        define_agent("a", tools=[tool("x", {}), tool("x", {})])
