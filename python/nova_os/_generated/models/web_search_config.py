from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_search_backend import WebSearchBackend
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchConfig")


@_attrs_define
class WebSearchConfig:
    """Persona-level web-search configuration. Resolved per-invocation on
    ``skill_deep_research`` via ``searchctx.WebSearchConfigFromContext``.
    Field names changed in nova-os PR #212 (closes #200) — old
    ``backend`` / ``fallback`` are no longer accepted.

        Attributes:
            primary_backend (WebSearchBackend | Unset): Web search backend selection. `auto` uses the server's default
                priority order (operator-configured).
            fallback_chain (list[WebSearchBackend] | Unset): Ordered fallback chain. Used on empty/error/off-topic results.
                Wraps the primary in a ``FallbackSearcher`` whose ``Name()``
                renders as ``primary→fallback1→fallback2``.
            reformulator (bool | Unset): Wrap the search call with the LLM reformulator. Improves
                retrieval quality on broad queries. Applied only to keyword
                backends; bundled-extraction backends handle reformulation
                internally.
                 Default: True.
            recency_terms (list[str] | Unset): Custom recency markers for the recency-intent escalator.
    """

    primary_backend: WebSearchBackend | Unset = UNSET
    fallback_chain: list[WebSearchBackend] | Unset = UNSET
    reformulator: bool | Unset = True
    recency_terms: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        primary_backend: str | Unset = UNSET
        if not isinstance(self.primary_backend, Unset):
            primary_backend = self.primary_backend.value

        fallback_chain: list[str] | Unset = UNSET
        if not isinstance(self.fallback_chain, Unset):
            fallback_chain = []
            for fallback_chain_item_data in self.fallback_chain:
                fallback_chain_item = fallback_chain_item_data.value
                fallback_chain.append(fallback_chain_item)

        reformulator = self.reformulator

        recency_terms: list[str] | Unset = UNSET
        if not isinstance(self.recency_terms, Unset):
            recency_terms = self.recency_terms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if primary_backend is not UNSET:
            field_dict["primary_backend"] = primary_backend
        if fallback_chain is not UNSET:
            field_dict["fallback_chain"] = fallback_chain
        if reformulator is not UNSET:
            field_dict["reformulator"] = reformulator
        if recency_terms is not UNSET:
            field_dict["recency_terms"] = recency_terms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _primary_backend = d.pop("primary_backend", UNSET)
        primary_backend: WebSearchBackend | Unset
        if isinstance(_primary_backend, Unset):
            primary_backend = UNSET
        else:
            primary_backend = WebSearchBackend(_primary_backend)

        _fallback_chain = d.pop("fallback_chain", UNSET)
        fallback_chain: list[WebSearchBackend] | Unset = UNSET
        if _fallback_chain is not UNSET:
            fallback_chain = []
            for fallback_chain_item_data in _fallback_chain:
                fallback_chain_item = WebSearchBackend(fallback_chain_item_data)

                fallback_chain.append(fallback_chain_item)

        reformulator = d.pop("reformulator", UNSET)

        recency_terms = cast(list[str], d.pop("recency_terms", UNSET))

        web_search_config = cls(
            primary_backend=primary_backend,
            fallback_chain=fallback_chain,
            reformulator=reformulator,
            recency_terms=recency_terms,
        )

        web_search_config.additional_properties = d
        return web_search_config

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
