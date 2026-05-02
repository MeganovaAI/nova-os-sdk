"""AnthropicCompatClient — factory wrapping anthropic.Anthropic.

The factory's job is intentionally minimal: pass base_url through unchanged
(stripping a single trailing slash for hygiene), forward api_key + kwargs.
The Anthropic SDK appends ``/v1/messages`` itself; pre-appending any path
segment (the v0.1.0-alpha bug) breaks SDK path resolution.
"""

from __future__ import annotations

import pytest

from nova_os.anthropic_compat import AnthropicCompatClient


def test_returns_anthropic_client_instance() -> None:
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",
        api_key="msk_live_test",
    )
    assert isinstance(c, anthropic.Anthropic)


def test_passes_through_extra_kwargs() -> None:
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",
        api_key="msk_live_test",
        timeout=120.0,
    )
    # Just confirm we got back an Anthropic client without error; the SDK
    # internalizes timeout differently across versions, so don't probe it.
    assert isinstance(c, anthropic.Anthropic)


def test_does_not_pre_suffix_base_url() -> None:
    """The factory MUST NOT append /v1/managed (the v0.1.0-alpha bug).

    SDK versions store the base differently; check the URL string directly
    via the recorded-fixture round-trip test instead of probing private
    attrs. This test exists for fast feedback when the implementation
    drifts; the round-trip test in test_anthropic_sdk_roundtrip.py is
    the load-bearing path-resolution gate.
    """
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",
        api_key="msk_live_test",
    )
    assert isinstance(c, anthropic.Anthropic)
    base = getattr(c, "base_url", None) or getattr(c, "_base_url", None)
    if base is not None:
        # If the factory regressed to appending /v1/managed, the base_url
        # would contain it. We assert the negation.
        assert "/v1/managed" not in str(base), (
            f"AnthropicCompatClient regressed to pre-suffixing base_url: {base!r}"
        )


def test_strips_trailing_slash() -> None:
    """Trailing slash on base_url should be stripped (hygiene; not load-bearing)."""
    anthropic = pytest.importorskip("anthropic")
    # Should not raise; trailing slash handled cleanly.
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com/",
        api_key="k",
    )
    assert isinstance(c, anthropic.Anthropic)
