from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_search_request_fetch import WebSearchRequestFetch
from ..models.web_search_request_kind import WebSearchRequestKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchRequest")


@_attrs_define
class WebSearchRequest:
    """
    Attributes:
        query (str): The search query.
        buckets (list[str] | Unset): Source buckets to search first (e.g. `legal-qc`). Omitted means the calling
            identity's bound buckets, or general search when it has none.
        kind (WebSearchRequestKind | Unset): Drives the publisher-policy gate. `batch` honours robots everywhere,
            including sources where a user-initiated interactive turn is exempt. Default: WebSearchRequestKind.INTERACTIVE.
        top_k (int | Unset): Result ceiling. Values outside the range are clamped, not rejected. Default: 10.
        fetch (WebSearchRequestFetch | Unset): How much of each hit to hydrate. `anchored` is reserved and rejected with
            400 in v1. Default: WebSearchRequestFetch.SNIPPETS.
    """

    query: str
    buckets: list[str] | Unset = UNSET
    kind: WebSearchRequestKind | Unset = WebSearchRequestKind.INTERACTIVE
    top_k: int | Unset = 10
    fetch: WebSearchRequestFetch | Unset = WebSearchRequestFetch.SNIPPETS
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        buckets: list[str] | Unset = UNSET
        if not isinstance(self.buckets, Unset):
            buckets = self.buckets

        kind: str | Unset = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind.value

        top_k = self.top_k

        fetch: str | Unset = UNSET
        if not isinstance(self.fetch, Unset):
            fetch = self.fetch.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if buckets is not UNSET:
            field_dict["buckets"] = buckets
        if kind is not UNSET:
            field_dict["kind"] = kind
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if fetch is not UNSET:
            field_dict["fetch"] = fetch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        buckets = cast(list[str], d.pop("buckets", UNSET))

        _kind = d.pop("kind", UNSET)
        kind: WebSearchRequestKind | Unset
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = WebSearchRequestKind(_kind)

        top_k = d.pop("top_k", UNSET)

        _fetch = d.pop("fetch", UNSET)
        fetch: WebSearchRequestFetch | Unset
        if isinstance(_fetch, Unset):
            fetch = UNSET
        else:
            fetch = WebSearchRequestFetch(_fetch)

        web_search_request = cls(
            query=query,
            buckets=buckets,
            kind=kind,
            top_k=top_k,
            fetch=fetch,
        )

        web_search_request.additional_properties = d
        return web_search_request

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
