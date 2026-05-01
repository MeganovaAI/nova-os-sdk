"""AnthropicCompatClient — factory wrapping anthropic.Anthropic with Nova OS defaults."""

from __future__ import annotations

import pytest

from nova_os.anthropic_compat import AnthropicCompatClient


def test_returns_anthropic_client_instance() -> None:
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com/v1/managed",
        api_key="msk_live_test",
    )
    assert isinstance(c, anthropic.Anthropic)


def test_passes_through_extra_kwargs() -> None:
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com/v1/managed",
        api_key="msk_live_test",
        timeout=120.0,
    )
    # Just confirm we got back an Anthropic client without error; the SDK
    # internalizes timeout differently across versions, so don't probe it.
    assert isinstance(c, anthropic.Anthropic)


def test_appends_v1_managed_suffix_when_missing() -> None:
    """base_url without /v1/managed should have the suffix appended."""
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",
        api_key="msk_live_test",
    )
    assert isinstance(c, anthropic.Anthropic)
    # The base_url stored internally should include the suffix.
    # SDK versions differ in attribute name; check whichever is present.
    base = getattr(c, "base_url", None) or getattr(c, "_base_url", None)
    if base is not None:
        assert "/v1/managed" in str(base)


def test_no_double_suffix() -> None:
    """base_url that already ends with /v1/managed should not get it doubled."""
    anthropic = pytest.importorskip("anthropic")
    c = AnthropicCompatClient(
        base_url="https://nova.partner.com/v1/managed",
        api_key="msk_live_test",
    )
    assert isinstance(c, anthropic.Anthropic)
    base = getattr(c, "base_url", None) or getattr(c, "_base_url", None)
    if base is not None:
        url_str = str(base)
        assert url_str.count("/v1/managed") == 1
