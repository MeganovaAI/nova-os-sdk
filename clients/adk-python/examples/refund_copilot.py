from libraos_adk import define_agent, tool


def _lookup_order(args):
    # In-process handler — runs in the developer's process (needs the v2
    # round-trip, libraos/libraos#842). For v1, pass webhook_url=... instead.
    return {"orderId": args["orderId"], "status": "shipped", "refundable": True}


agent = define_agent(
    "refund-copilot",
    model="libraos/brain",
    system="You handle refund requests. Be concise; cite the policy when relevant.",
    skills=["docx"],
    knowledge=["collection:refunds"],
    memory="per-user",
    guardrails={"pii_redactor": True},
    tools=[
        tool(
            "lookup_order",
            {"type": "object", "properties": {"orderId": {"type": "string"}}, "required": ["orderId"]},
            _lookup_order,
        )
    ],
)
