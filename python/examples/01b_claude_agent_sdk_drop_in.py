"""Drop-in compat with Anthropic's Claude Agent SDK.

Pairs with 01_basic_chat.py (which targets ``anthropic.Anthropic(base_url=...)``).
This example targets a different Anthropic-published SDK — the
[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python),
which spawns the bundled ``claude`` CLI as a subprocess and drives a
local agent loop (Read / Write / Bash / Edit + custom MCP tools).

The key compat trick: the Claude Agent SDK's transport inherits the
parent process environment when it spawns the CLI. So setting
``ANTHROPIC_BASE_URL`` + ``ANTHROPIC_API_KEY`` — either globally or
through ``ClaudeAgentOptions.env={...}`` — points every call at Nova OS
without any other code change. Existing Claude Agent SDK code runs
unchanged against your Nova OS instance.

Compared with 01_basic_chat.py (anthropic.Anthropic SDK):

    01_basic_chat.py             01b_claude_agent_sdk_drop_in.py (this)
    ────────────────────         ──────────────────────────────────────
    HTTP client → /v1/messages   Subprocess → claude CLI → /v1/messages
    Stateless single-shot        Local agent loop (multi-turn, tools)
    ``base_url=...`` ctor arg    ``ANTHROPIC_BASE_URL`` env var

Choose 01_basic_chat when you want a stateless message round-trip from
your own backend. Choose this script's pattern when you want the local
CLI's tool ergonomics (Read/Bash/Edit working on local files) backed
by Nova OS's multi-tenant runtime instead of api.anthropic.com.

Prerequisites::

    pip install claude-agent-sdk
    export NOVA_OS_URL=https://nova.your-company.example
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 01b_claude_agent_sdk_drop_in.py
"""

from __future__ import annotations

import os

import anyio

# Imported exactly as Anthropic's Quickstart shows. The only difference
# vs that quickstart: ClaudeAgentOptions(env=...) routes the bundled
# claude CLI's traffic to Nova OS instead of api.anthropic.com.
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)


async def main() -> None:
    nova_os_url = os.environ.get("NOVA_OS_URL", "https://nova.your-company.example")
    nova_os_api_key = os.environ["NOVA_OS_API_KEY"]

    # ClaudeAgentOptions.env overrides the spawned CLI's env without
    # mutating the parent process — preferred over os.environ[...] = ...
    # in library code because it's local to this query.
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant. Answer concisely.",
        max_turns=1,
        env={
            "ANTHROPIC_BASE_URL": nova_os_url,
            "ANTHROPIC_API_KEY": nova_os_api_key,
        },
    )

    async for message in query(prompt="What is 2 + 2?", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Nova OS via Claude Agent SDK: {block.text}")


if __name__ == "__main__":
    anyio.run(main)
