"""``adk`` CLI — deploy and run LibraOS agents authored with ``libraos_adk``.

  adk deploy [file]         Deploy agent(s) from a module (default agent.py)
  adk run <agent> <input>   Run an agent on the LibraOS stack, streaming events

Env: LIBRAOS_BASE_URL, LIBRAOS_API_KEY.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Optional, Sequence

from .agent import Agent
from .client import LibraAdk


def _load_agents(file: str) -> list[Agent]:
    path = Path(file).resolve()
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {file}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    seen: set[str] = set()
    agents: list[Agent] = []
    for v in vars(mod).values():
        if isinstance(v, Agent) and v.name not in seen:
            seen.add(v.name)
            agents.append(v)
    if not agents:
        raise RuntimeError(f"no Agent found in {file} — assign one: agent = define_agent(...)")
    return agents


def _usage() -> None:
    sys.stderr.write(
        "libraos adk\n\n"
        "  adk deploy [file]         Deploy agent(s) from a module (default agent.py)\n"
        "  adk run <agent> <input>   Run an agent on the LibraOS stack, streaming events\n\n"
        "Env: LIBRAOS_BASE_URL, LIBRAOS_API_KEY\n"
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _usage()
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "deploy":
        file = rest[0] if rest else "agent.py"
        adk = LibraAdk()
        for agent in _load_agents(file):
            res = adk.deploy(agent)
            print(f"deployed {agent.name} -> {res['id']}")
        return 0
    if cmd == "run":
        if len(rest) < 2:
            _usage()
            return 2
        name, message = rest[0], " ".join(rest[1:])
        LibraAdk().run(
            name,
            message,
            on_event=lambda e: print(f"{e.get('type')}" + (f": {e['text']}" if "text" in e else "")),
        )
        return 0
    _usage()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
