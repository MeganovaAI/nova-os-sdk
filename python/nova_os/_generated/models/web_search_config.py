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
    """
    Attributes:
        backend (WebSearchBackend | Unset): Web search backend selection. `auto` uses Nova OS DefaultSearcher()
            priority (Ceramic → Tavily → Brave → Exa → SearXNG, with reformulator
            + Tavily fallback wrappers when configured).
        fallback (list[WebSearchBackend] | Unset): Ordered fallback chain. Used on empty/error/off-topic results.
        reformulator (bool | Unset): Wrap the search call with the LLM reformulator. Lifts Ceramic
            42→70% on broad queries; only applied to keyword backends
            (ceramic / searxng / exa), not bundled-extraction backends.
             Default: True.
        recency_terms (list[str] | Unset): Custom recency markers for the recency-intent escalator.
    """

    backend: WebSearchBackend | Unset = UNSET
    fallback: list[WebSearchBackend] | Unset = UNSET
    reformulator: bool | Unset = True
    recency_terms: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        backend: str | Unset = UNSET
        if not isinstance(self.backend, Unset):
            backend = self.backend.value

        fallback: list[str] | Unset = UNSET
        if not isinstance(self.fallback, Unset):
            fallback = []
            for fallback_item_data in self.fallback:
                fallback_item = fallback_item_data.value
                fallback.append(fallback_item)

        reformulator = self.reformulator

        recency_terms: list[str] | Unset = UNSET
        if not isinstance(self.recency_terms, Unset):
            recency_terms = self.recency_terms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if backend is not UNSET:
            field_dict["backend"] = backend
        if fallback is not UNSET:
            field_dict["fallback"] = fallback
        if reformulator is not UNSET:
            field_dict["reformulator"] = reformulator
        if recency_terms is not UNSET:
            field_dict["recency_terms"] = recency_terms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _backend = d.pop("backend", UNSET)
        backend: WebSearchBackend | Unset
        if isinstance(_backend, Unset):
            backend = UNSET
        else:
            backend = WebSearchBackend(_backend)

        _fallback = d.pop("fallback", UNSET)
        fallback: list[WebSearchBackend] | Unset = UNSET
        if _fallback is not UNSET:
            fallback = []
            for fallback_item_data in _fallback:
                fallback_item = WebSearchBackend(fallback_item_data)

                fallback.append(fallback_item)

        reformulator = d.pop("reformulator", UNSET)

        recency_terms = cast(list[str], d.pop("recency_terms", UNSET))

        web_search_config = cls(
            backend=backend,
            fallback=fallback,
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
