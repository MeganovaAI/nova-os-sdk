"""Termination-signal matcher used by the simulate loop.

Each signal string is one of:

- **Plain substring** (default) — case-insensitive substring match.
- **``re:``-prefixed regex** — the suffix is compiled with
  ``re.IGNORECASE`` and used with ``re.search``.

The regex shape is the same one ``Archetype`` validates at load time,
so a malformed regex is rejected before the loop starts — this module
treats both branches as well-formed.

Both forms are documented in the SDK README so archetype authors
can pick the cheaper substring form for keyword targets and the
regex form when the signal is a templated phrase ("lawyer matched
... (common-law|spousal) ...").
"""

from __future__ import annotations

import re


_RE_PREFIX = "re:"


def signal_matches(signal: str, text: str) -> bool:
    """Return True if ``signal`` matches anywhere in ``text``.

    Substring is case-insensitive. Regex (``re:`` prefix) uses
    :func:`re.search` with :data:`re.IGNORECASE`.

    The regex branch never raises on a malformed pattern — at that
    point in the SDK we always have a pre-validated archetype, so
    ``re.compile`` should succeed; defensively, a compile failure
    here falls back to substring on the raw suffix to avoid
    terminating a long-running loop on a programming-error path.
    """
    if signal.startswith(_RE_PREFIX):
        pattern = signal[len(_RE_PREFIX):]
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            # Archetype.from_dict validates this at load time; the
            # only way to land here is a hand-built archetype that
            # bypassed validation. Fall back to substring on the
            # raw suffix so the loop continues.
            return pattern.lower() in text.lower()
    return signal.lower() in text.lower()


def any_signal_matches(
    signals: list[str], text: str
) -> tuple[bool, str | None]:
    """Return ``(matched, first_matching_signal)``.

    Used for ``failure_signal_match == "any"`` (default) and for
    success-signal evaluation (single-signal, so equivalent).
    """
    for s in signals:
        if signal_matches(s, text):
            return True, s
    return False, None


def all_signals_match(
    signals: list[str], text: str
) -> tuple[bool, list[str]]:
    """Return ``(all_matched, matched_signal_list)``.

    Used for ``failure_signal_match == "all"``. The matched list is
    always all of ``signals`` when ``all_matched`` is True (or a
    proper subset when not), so partners can render the same field
    structure in both ``any`` / ``all`` cases.
    """
    matched: list[str] = []
    for s in signals:
        if signal_matches(s, text):
            matched.append(s)
    return len(matched) == len(signals), matched


__all__ = ["signal_matches", "any_signal_matches", "all_signals_match"]
