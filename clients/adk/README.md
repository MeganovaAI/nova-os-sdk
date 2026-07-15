# @libraos/adk

**LibraOS Agent Development Kit** — author agents in code, run them on the
**LibraOS managed stack** (hosted, governed execution). ADK-style ergonomics;
LibraOS-hosted execution. Companion to [`@libraos/client`](../typescript).

> **Status: v1 scaffold (alpha).** The authoring API + CLI are stable in shape.
> `run` targets the durable **jobs** surface that works today; the exact wire
> shapes and the in-process custom-tool round-trip are being finalized — see
> the design docs in `libraos/libraos` (`docs/design/agent-sdk-rfc.md`,
> `agent-sdk-runtime-audit.md`) and issues #840–#842.

## Install

```bash
npm install @libraos/adk
```

## Author an agent

```ts
// agent.ts
import { defineAgent, tool } from "@libraos/adk";

export default defineAgent({
  name: "refund-copilot",
  model: "libraos/brain",                 // or "anthropic/claude-opus-4-8", "openai/…", "gemini/…"
  system: "You handle refund requests…",
  skills: ["docx", "xlsx"],               // LibraOS server-side skills (run on the stack)
  knowledge: ["collection:refunds"],      // declarative RAG binding
  memory: "per-user",                     // governed cross-session memory
  guardrails: { piiRedactor: true },
  tools: [
    tool(
      "lookup_order",
      { type: "object", properties: { orderId: { type: "string" } }, required: ["orderId"] },
      async ({ orderId }) => myDb.orders.get(orderId as string), // in-process (v2)
    ),
  ],
});
```

## Deploy + run

```bash
export LIBRAOS_BASE_URL=https://your-libraos.example.com
export LIBRAOS_API_KEY=…

adk deploy                                  # upserts the agent on /v1/agents (idempotent)
adk run refund-copilot "refund order 8842"  # runs on the stack, streaming events
```

TypeScript agent files load under a loader: `npx tsx node_modules/.bin/adk deploy agent.ts`
(or compile `agent.ts` to JS first).

## Programmatic API

```ts
import { LibraAdk } from "@libraos/adk";
import agent from "./agent.js";

const adk = new LibraAdk(); // reads LIBRAOS_BASE_URL / LIBRAOS_API_KEY
await adk.deploy(agent);
await adk.run("refund-copilot", "refund order 8842", {
  onEvent: (e) => console.log(e.type, e),
});
```

## What runs where

- **You author + deploy** the agent definition and (optionally) supply your own tools.
- **LibraOS runs everything else** — the agent loop, server-side skills, RAG, memory —
  and enforces governance you can't get from a dev-hosted framework: signed tenant/app
  identity, a capability membrane, a live kill-switch + firewall, a human-approval queue
  for side-effecting tools, and append-only audit trails.

## Custom tools: two models

- **Webhook (works today):** `tool(name, schema, undefined, { webhookUrl })` — LibraOS
  HMAC-POSTs the tool call to your endpoint.
- **In-process (v2):** `tool(name, schema, handler)` — the agent pauses, your `handler`
  answers over the stream, the run resumes. Needs the server round-trip (libraos/libraos#842).

## Roadmap

- **v1 (now):** authoring + deploy + run over the jobs surface; webhook tools; full governance.
- **v2:** session-based runs + live streaming + in-process tools (Anthropic-Managed-Agents wire-compatible).
- **v3:** agent versioning/pinning, MCP client, scheduled deployments.
