import { defineAgent, tool } from "@libraos/adk";

// A refund copilot: grounded in a knowledge collection, with a developer-supplied
// tool to look up orders. Deploy with `adk deploy`, run with `adk run`.
export default defineAgent({
  name: "refund-copilot",
  model: "libraos/brain",
  system: "You handle refund requests. Be concise; cite the policy when relevant.",
  skills: ["docx"],
  knowledge: ["collection:refunds"],
  memory: "per-user",
  guardrails: { piiRedactor: true },
  tools: [
    tool(
      "lookup_order",
      {
        type: "object",
        properties: { orderId: { type: "string", description: "The order id" } },
        required: ["orderId"],
      },
      // In-process handler — runs in the developer's process (needs the v2
      // custom-tool round-trip, libraos/libraos#842). For v1, pass
      // `{ webhookUrl: "https://…" }` as the 4th arg instead.
      async ({ orderId }) => ({ orderId, status: "shipped", refundable: true }),
    ),
  ],
});
