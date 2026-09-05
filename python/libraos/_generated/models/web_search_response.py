from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_block import UsageBlock
    from ..models.web_search_provider_answer import WebSearchProviderAnswer
    from ..models.web_search_result import WebSearchResult


T = TypeVar("T", bound="WebSearchResponse")


@_attrs_define
class WebSearchResponse:
    """
    Attributes:
        results (list[WebSearchResult]):
        bucket_miss (bool): True when no bound bucket produced a hit and the general searcher answered instead.
        provider_answer (WebSearchProviderAnswer | Unset): A model's answer to the query, supplied by a provider that
            offers one. Carried outside `results` so it can never be read as a hit, and never cited as a source.
        refusals (list[str] | Unset): Per-source refusals, each naming the source and the reason (e.g.
            `blocked_by_publisher_policy: ...`). A refusal is not fatal and is never silent: the remaining sources still
            return.
        usage (UsageBlock | Unset): Aggregated token usage across all of the turn's model sub-calls, with a per-stage
            breakdown. Omitted on non-model/zero-usage turns. Excludes embedding calls.
    """

    results: list[WebSearchResult]
    bucket_miss: bool
    provider_answer: WebSearchProviderAnswer | Unset = UNSET
    refusals: list[str] | Unset = UNSET
    usage: UsageBlock | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        bucket_miss = self.bucket_miss

        provider_answer: dict[str, Any] | Unset = UNSET
        if not isinstance(self.provider_answer, Unset):
            provider_answer = self.provider_answer.to_dict()

        refusals: list[str] | Unset = UNSET
        if not isinstance(self.refusals, Unset):
            refusals = self.refusals

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
                "bucket_miss": bucket_miss,
            }
        )
        if provider_answer is not UNSET:
            field_dict["provider_answer"] = provider_answer
        if refusals is not UNSET:
            field_dict["refusals"] = refusals
        if usage is not UNSET:
            field_dict["usage"] = usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_block import UsageBlock
        from ..models.web_search_provider_answer import WebSearchProviderAnswer
        from ..models.web_search_result import WebSearchResult

        d = dict(src_dict)
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = WebSearchResult.from_dict(results_item_data)

            results.append(results_item)

        bucket_miss = d.pop("bucket_miss")

        _provider_answer = d.pop("provider_answer", UNSET)
        provider_answer: WebSearchProviderAnswer | Unset
        if isinstance(_provider_answer, Unset):
            provider_answer = UNSET
        else:
            provider_answer = WebSearchProviderAnswer.from_dict(_provider_answer)

        refusals = cast(list[str], d.pop("refusals", UNSET))

        _usage = d.pop("usage", UNSET)
        usage: UsageBlock | Unset
        if isinstance(_usage, Unset):
            usage = UNSET
        else:
            usage = UsageBlock.from_dict(_usage)

        web_search_response = cls(
            results=results,
            bucket_miss=bucket_miss,
            provider_answer=provider_answer,
            refusals=refusals,
            usage=usage,
        )

        web_search_response.additional_properties = d
        return web_search_response

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
