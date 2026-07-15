#!/usr/bin/env node
// `adk` CLI — deploy and run LibraOS agents authored with @libraos/adk.
//
//   adk deploy [file]         Deploy agent(s) exported from a module (default ./agent.js)
//   adk run <agent> <input…>  Run an agent on the LibraOS stack, streaming events
//
// Env: LIBRAOS_BASE_URL, LIBRAOS_API_KEY. To author agents in TypeScript, run
// under a loader: `npx tsx node_modules/.bin/adk deploy agent.ts` (or build to JS).

import type { Agent } from "./agent.js";
import { LibraAdk } from "./client.js";

async function main(argv: string[]): Promise<number> {
  const [cmd, ...rest] = argv;
  switch (cmd) {
    case "deploy": {
      const file = rest[0] ?? "./agent.js";
      const agents = await loadAgents(file);
      const adk = new LibraAdk();
      for (const agent of agents) {
        const { id } = await adk.deploy(agent);
        process.stdout.write(`deployed ${agent.definition.name} → ${id}\n`);
      }
      return 0;
    }
    case "run": {
      const name = rest[0];
      const input = rest.slice(1).join(" ");
      if (!name || !input) {
        usage();
        return 2;
      }
      const adk = new LibraAdk();
      await adk.run(name, input, {
        onEvent: (ev) => {
          const text = typeof ev.text === "string" ? `: ${ev.text}` : "";
          process.stdout.write(`${ev.type}${text}\n`);
        },
      });
      return 0;
    }
    default:
      usage();
      return cmd ? 2 : 0;
  }
}

async function loadAgents(file: string): Promise<Agent[]> {
  const path = file.startsWith("/") ? file : `${process.cwd()}/${file}`;
  const mod = (await import(path)) as Record<string, unknown>;
  const found: Agent[] = [];
  if (isAgent(mod.default)) found.push(mod.default);
  for (const v of Object.values(mod)) if (isAgent(v)) found.push(v);
  const deduped = dedupe(found);
  if (deduped.length === 0) {
    throw new Error(`no agent exported from ${file} — export default defineAgent({...})`);
  }
  return deduped;
}

function isAgent(v: unknown): v is Agent {
  return !!v && typeof v === "object" && "definition" in v && "toManagedAgentBody" in v;
}

function dedupe(agents: Agent[]): Agent[] {
  const seen = new Set<string>();
  return agents.filter((a) => {
    if (seen.has(a.definition.name)) return false;
    seen.add(a.definition.name);
    return true;
  });
}

function usage(): void {
  process.stderr.write(
    "libraos adk\n\n" +
      "  adk deploy [file]         Deploy agent(s) from a module (default ./agent.js)\n" +
      "  adk run <agent> <input>   Run an agent on the LibraOS stack, streaming events\n\n" +
      "Env: LIBRAOS_BASE_URL, LIBRAOS_API_KEY\n",
  );
}

main(process.argv.slice(2)).then(
  (code) => process.exit(code),
  (err: unknown) => {
    process.stderr.write(`adk: ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  },
);
