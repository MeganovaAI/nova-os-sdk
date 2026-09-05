from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_search_result_derivation import WebSearchResultDerivation
from ..models.web_search_result_representation import WebSearchResultRepresentation
from ..models.web_search_result_status import WebSearchResultStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchResult")


@_attrs_define
class WebSearchResult:
    """
    Attributes:
        title (str | Unset):
        url (str | Unset):
        source (str | Unset): Driver attribution, e.g. `source:soquij` or `general (bucket-miss)`.
        content (str | Unset):
        published_date (str | Unset):
        representation (WebSearchResultRepresentation | Unset): What `content` IS, as declared by whichever component
            produced it. `search_snippet`, `provider_excerpt` and `page_extract` are page-derived; `provider_summary` and
            `model_answer` are generated prose about the page and are not evidence of what it says.
        derivation (WebSearchResultDerivation | Unset): Coarse axis over `representation`.
        status (WebSearchResultStatus | Unset): What happened to the hit. Empty means it was found and nothing more was
            attempted — found and opened are different claims. `blocked_policy` is our refusal to read the source;
            `blocked_soft` is the source refusing us with an anti-bot challenge served at HTTP 200.
    """

    title: str | Unset = UNSET
    url: str | Unset = UNSET
    source: str | Unset = UNSET
    content: str | Unset = UNSET
    published_date: str | Unset = UNSET
    representation: WebSearchResultRepresentation | Unset = UNSET
    derivation: WebSearchResultDerivation | Unset = UNSET
    status: WebSearchResultStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        url = self.url

        source = self.source

        content = self.content

        published_date = self.published_date

        representation: str | Unset = UNSET
        if not isinstance(self.representation, Unset):
            representation = self.representation.value

        derivation: str | Unset = UNSET
        if not isinstance(self.derivation, Unset):
            derivation = self.derivation.value

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url
        if source is not UNSET:
            field_dict["source"] = source
        if content is not UNSET:
            field_dict["content"] = content
        if published_date is not UNSET:
            field_dict["published_date"] = published_date
        if representation is not UNSET:
            field_dict["representation"] = representation
        if derivation is not UNSET:
            field_dict["derivation"] = derivation
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        url = d.pop("url", UNSET)

        source = d.pop("source", UNSET)

        content = d.pop("content", UNSET)

        published_date = d.pop("published_date", UNSET)

        _representation = d.pop("representation", UNSET)
        representation: WebSearchResultRepresentation | Unset
        if isinstance(_representation, Unset):
            representation = UNSET
        else:
            representation = WebSearchResultRepresentation(_representation)

        _derivation = d.pop("derivation", UNSET)
        derivation: WebSearchResultDerivation | Unset
        if isinstance(_derivation, Unset):
            derivation = UNSET
        else:
            derivation = WebSearchResultDerivation(_derivation)

        _status = d.pop("status", UNSET)
        status: WebSearchResultStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = WebSearchResultStatus(_status)

        web_search_result = cls(
            title=title,
            url=url,
            source=source,
            content=content,
            published_date=published_date,
            representation=representation,
            derivation=derivation,
            status=status,
        )

        web_search_result.additional_properties = d
        return web_search_result

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
