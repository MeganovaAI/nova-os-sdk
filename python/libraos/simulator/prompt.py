"""Deterministic system-prompt builder for the synthetic-customer simulator.

The simulator pattern drives a target LibraOS agent through a multi-turn
conversation by having a *second* LLM call play a synthetic customer
("the simulator") whose persona, hidden state, and disclosure behavior are
defined by an :class:`~libraos.simulator.Archetype`.

This module ships the deterministic builder that converts an ``Archetype``
to the simulator's LLM system prompt:

.. code-block:: python

    from libraos.simulator import Archetype, build_simulator_prompt

    archetype = Archetype.from_yaml_path("./archetypes/my-customer.yaml")
    system_prompt = build_simulator_prompt(archetype, max_turns=10)

Determinism contract
====================

The builder is **deterministic** — same archetype + ``max_turns`` always
produces byte-identical output. This is the load-bearing property that
makes snapshot tests possible and lets partners diff prompt drift across
SDK upgrades.

Concretely:

- List ordering (``hidden_facts``, ``failure_signals``) is preserved
  from the input — no sorting, no shuffling.
- Optional sections (``demographic``, ``language_register``,
  ``failure_signals``) are included verbatim when set, omitted entirely
  when ``None`` / empty.
- No timestamps, no random IDs, no environment-dependent formatting.

Load-bearing prompt items
=========================

Two parts of the template are documented as *load-bearing* in the
upstream simulator design:

1. The **hidden-fact "do NOT volunteer" gate**. Without an explicit
   instruction that hidden facts are known but not to be surfaced
   unless the AI agent asks, the simulator dumps everything in turn 1
   and the test becomes degenerate (no information asymmetry left to
   probe). The builder always emits this gate verbatim.

2. The **per-enum ``disclosure_willingness`` explanation**. The LLM
   cannot reliably infer the gradient between ``open`` / ``cautious``
   / ``guarded`` from the label alone — informal probes against
   commodity models show drift toward "open" without the explanation.
   The builder always emits all three rows so the model sees both
   the active row AND the contrast rows.

Known limitation: even with both safeguards in place, leak of a
hidden fact in turn 1 has been observed in an informal probe. The
upstream design recommends framing hidden facts with explicit social
or legal consequence (e.g. ``"... — would be embarrassed to
mention unprompted"``) for high-stakes evaluation. See the SDK's
simulator README for the full mitigation hierarchy.
"""

from __future__ import annotations

from typing import Any

import yaml

from libraos.simulator.archetype import Archetype

# Per-enum explanation rows. Pinned here (not in the Archetype model)
# because they belong to the *prompt template*, not to the schema. Order
# matches the design ordering exactly: open → cautious → guarded.
_DISCLOSURE_ROWS: tuple[tuple[str, str], ...] = (
    (
        "open",
        "you share information readily; minimal probing required.",
    ),
    (
        "cautious",
        "you share when asked directly; you do not volunteer hidden facts.",
    ),
    (
        "guarded",
        "you actively deflect or defer until trust is established; "
        "even direct questions get partial answers on the first attempt.",
    ),
)

_DEFAULT_LANGUAGE_REGISTER = "conversational english"


def build_simulator_prompt(archetype: Archetype, max_turns: int = 10) -> str:
    """Build the simulator's LLM system prompt from an archetype.

    Parameters
    ----------
    archetype:
        The :class:`~libraos.simulator.Archetype` describing the synthetic
        customer to play. Already-validated (the constructor ran).
    max_turns:
        The conversation cap surfaced to the simulator in the
        ``CONVERSATION PROTOCOL`` section (the turn at which the loop
        will give up). Default ``10`` matches the SDK's default
        termination cap. Pass the same value you pass to the
        ``simulate()`` loop so the simulator's stated turn budget
        matches what the SDK actually enforces.

    Returns
    -------
    str
        The fully-rendered system prompt. **Deterministic**: same
        archetype + ``max_turns`` always produces byte-identical
        output (no timestamps, no UUIDs, list order preserved).

    Notes
    -----
    The returned string is intended to land at ``messages[0]`` of a
    ``/chat`` request against the simulator harness agent. The harness
    agent's baked system prompt is intentionally minimal so this prompt
    dominates the LLM's attention without fighting another persona.
    """
    parts: list[str] = []

    # ---- opening paragraph (verbatim from the template) ----
    parts.append(
        "You are simulating a customer in a multi-turn conversation. "
        "You will be asked questions by an AI agent. Respond as the "
        "customer described below would respond — in character, with "
        "the disclosure willingness specified, surfacing hidden facts "
        "only when the AI agent asks appropriate questions."
    )

    # ---- CUSTOMER ARCHETYPE section ----
    parts.append("CUSTOMER ARCHETYPE\n==================")

    parts.append(f"Name: {archetype.name}")

    parts.append("Description:\n" + archetype.description.rstrip())

    # Hidden facts — LOAD-BEARING "do NOT volunteer" gate. The header
    # itself is part of the gate; do not soften it.
    hidden_lines = "\n".join(f'- "{fact}"' for fact in archetype.hidden_facts)
    parts.append(
        "Hidden facts (you know these but do NOT volunteer them — "
        "disclose only when the AI agent asks a question that would "
        "naturally elicit the fact):\n" + hidden_lines
    )

    # Disclosure willingness — LOAD-BEARING per-enum explanation. All
    # three rows are emitted so the LLM sees both the active row AND
    # the contrast rows; the active row is identified by the value
    # printed above. Order is fixed: open → cautious → guarded.
    disclosure_block = [f"Disclosure willingness: {archetype.disclosure_willingness}"]
    for value, explanation in _DISCLOSURE_ROWS:
        disclosure_block.append(f'  - "{value}" — {explanation}')
    parts.append("\n".join(disclosure_block))

    # Language register — optional, defaulted to "conversational english"
    # at render time.
    language_register = (
        archetype.language_register
        if archetype.language_register is not None
        else _DEFAULT_LANGUAGE_REGISTER
    )
    parts.append(f"Language register: {language_register}")

    # Demographic context — included only when set.
    if archetype.demographic:
        parts.append(
            "Demographic context:\n"
            + _render_demographic_block(archetype.demographic).rstrip()
        )

    # ---- CONVERSATION PROTOCOL section ----
    parts.append(
        "CONVERSATION PROTOCOL\n=====================\n"
        "- Respond as the customer would, in first person.\n"
        "- Keep responses concise (1-3 sentences typical; longer only "
        "when the AI agent asks a complex question that requires it).\n"
        "- Do NOT mention this prompt, the archetype, or that you are "
        "an AI simulating a customer.\n"
        "- Do NOT use markdown formatting in your responses unless the "
        "customer character would naturally do so.\n"
        f"- The conversation ends when (a) the AI agent matches the "
        f"success_signal described below, (b) you have nothing more "
        f"to say, or (c) you reach turn {int(max_turns)}."
    )

    # ---- SUCCESS SIGNAL section ----
    parts.append(
        "SUCCESS SIGNAL (for your awareness only — do not reveal):\n"
        + archetype.success_signal
    )

    # ---- Failure signals — optional, same don't-reveal caveat. ----
    if archetype.failure_signals:
        failure_lines = "\n".join(
            f'- "{signal}"' for signal in archetype.failure_signals
        )
        parts.append(
            "Failure signals (for your awareness only — do not reveal):\n"
            + failure_lines
        )

    # ---- Closing instruction ----
    parts.append(
        "Begin the conversation with an opening message that introduces "
        "your situation at a level consistent with your "
        "disclosure_willingness."
    )

    return "\n\n".join(parts) + "\n"


# --------------------------------------------------------------- helpers


def _render_demographic_block(demographic: dict[str, Any]) -> str:
    """Render the optional demographic dict as a deterministic YAML-ish block.

    Uses ``yaml.safe_dump`` with ``sort_keys=False`` so the partner's
    YAML field order in the archetype is preserved one-for-one in the
    rendered prompt. ``default_flow_style=False`` keeps the output in
    block style; ``allow_unicode=True`` keeps non-ASCII partner data
    (Punjabi, Mandarin, etc.) intact rather than escaped.
    """
    return yaml.safe_dump(
        demographic,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


__all__ = ["build_simulator_prompt"]
