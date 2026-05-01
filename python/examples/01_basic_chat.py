"""Anthropic-compat hello world — drop-in usage of the Anthropic SDK.

Demonstrates that code written against ``anthropic.Anthropic(base_url=...)``
works against Nova OS unchanged. Partners who already use the Anthropic SDK
only need to swap the base_url and API key — zero other code changes required.

Prerequisites::

    pip install nova-os-sdk anthropic
    export NOVA_OS_URL=https://nova.partner.com
    export NOVA_OS_API_KEY=msk_live_...

Run::

    python 01_basic_chat.py
"""

from __future__ import annotations

import os

from nova_os import AnthropicCompatClient


def main() -> None:
    base_url = os.environ.get("NOVA_OS_URL", "https://nova.partner.com")
    api_key = os.environ["NOVA_OS_API_KEY"]

    # AnthropicCompatClient returns an anthropic.Anthropic instance pre-configured
    # for Nova OS's /v1/managed compat path. The full Anthropic SDK API is available.
    client = AnthropicCompatClient(base_url=base_url, api_key=api_key)

    msg = client.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=256,
        messages=[{"role": "user", "content": "Hello, Nova OS!"}],
    )

    print(f"Message ID : {msg.id}")
    print(f"Model used : {msg.model}")
    print(f"Stop reason: {msg.stop_reason}")
    print(f"Tokens     : {msg.usage.input_tokens} in / {msg.usage.output_tokens} out")
    print()
    for block in msg.content:
        if hasattr(block, "text"):
            print(block.text)


if __name__ == "__main__":
    main()
