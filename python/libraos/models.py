"""Typed response models for the Messages API.

These subclass ``dict`` on purpose. ``messages.create()`` historically
returned a raw ``dict``, and both user code (``resp["content"][0]["text"]``)
and the SDK's own internals (``isinstance(response, dict)`` guards in the
simulator, ``json.dumps`` in logs, ``**resp`` splats) rely on that. By making
the typed models *actual dicts*, every one of those keeps working unchanged —
``isinstance(msg, dict)`` is ``True`` — while callers additionally get typed
attribute access (``resp.content[0].text``) and a ``.text`` convenience.

This is a strict superset of the previous behaviour: anything that worked on
the raw dict still works, so there is no migration for existing code.
"""

from __future__ import annotations

from typing import Any


class ContentBlock(dict):
    """One assistant content block. Text blocks carry ``.text``."""

    @property
    def type(self) -> str:
        return self.get("type", "text")

    @property
    def text(self) -> str | None:
        return self.get("text")


class Usage(dict):
    @property
    def input_tokens(self) -> int | None:
        return self.get("input_tokens")

    @property
    def output_tokens(self) -> int | None:
        return self.get("output_tokens")


class Message(dict):
    """Non-streaming ``/v1/messages`` response.

    A ``dict`` subclass, so ``resp["content"][0]["text"]`` and every existing
    dict operation work unchanged; ``resp.content[0].text`` and ``resp.text``
    are the typed conveniences.
    """

    @property
    def id(self) -> str | None:
        return self.get("id")

    @property
    def role(self) -> str:
        return self.get("role", "assistant")

    @property
    def model(self) -> str | None:
        return self.get("model")

    @property
    def stop_reason(self) -> str | None:
        return self.get("stop_reason")

    @property
    def content(self) -> list[ContentBlock]:
        raw = self.get("content")
        if isinstance(raw, list):
            return [b if isinstance(b, ContentBlock) else ContentBlock(b)
                    for b in raw if isinstance(b, dict)]
        return []

    @property
    def usage(self) -> Usage | None:
        raw = self.get("usage")
        return Usage(raw) if isinstance(raw, dict) else None

    @property
    def text(self) -> str:
        """Concatenate the text of every ``text`` content block.

        Also handles the simplified shape where ``content`` is a plain
        string (older/simplified server builds), returning it as-is.
        """
        raw = self.get("content")
        if isinstance(raw, str):
            return raw
        return "".join(b.text or "" for b in self.content if b.type == "text")


def parse_message(payload: Any) -> Any:
    """Wrap a ``/v1/messages`` payload in a dict-compatible :class:`Message`.

    Returns the payload unchanged if it isn't a dict — never makes a response
    harder to read than the raw value it replaced.
    """
    if isinstance(payload, dict):
        return Message(payload)
    return payload
