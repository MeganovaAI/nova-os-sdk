from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OcrResponse")


@_attrs_define
class OcrResponse:
    """
    Attributes:
        markdown (str | Unset): The extracted document text as markdown.
        page_count (int | Unset): Number of pages processed.
        model_used (str | Unset): Vision model that produced the result.
        fallback_chain_triggered (bool | Unset): True if a fallback vision model was used for one or more pages.
        cost_usd (float | Unset): Billed cost of this OCR call in USD.
        cache_hit (bool | Unset): True when the result was served from cache (no new billing).
        elapsed_ms (int | Unset): Server-side processing time in milliseconds.
    """

    markdown: str | Unset = UNSET
    page_count: int | Unset = UNSET
    model_used: str | Unset = UNSET
    fallback_chain_triggered: bool | Unset = UNSET
    cost_usd: float | Unset = UNSET
    cache_hit: bool | Unset = UNSET
    elapsed_ms: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        page_count = self.page_count

        model_used = self.model_used

        fallback_chain_triggered = self.fallback_chain_triggered

        cost_usd = self.cost_usd

        cache_hit = self.cache_hit

        elapsed_ms = self.elapsed_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if markdown is not UNSET:
            field_dict["markdown"] = markdown
        if page_count is not UNSET:
            field_dict["page_count"] = page_count
        if model_used is not UNSET:
            field_dict["model_used"] = model_used
        if fallback_chain_triggered is not UNSET:
            field_dict["fallback_chain_triggered"] = fallback_chain_triggered
        if cost_usd is not UNSET:
            field_dict["cost_usd"] = cost_usd
        if cache_hit is not UNSET:
            field_dict["cache_hit"] = cache_hit
        if elapsed_ms is not UNSET:
            field_dict["elapsed_ms"] = elapsed_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        markdown = d.pop("markdown", UNSET)

        page_count = d.pop("page_count", UNSET)

        model_used = d.pop("model_used", UNSET)

        fallback_chain_triggered = d.pop("fallback_chain_triggered", UNSET)

        cost_usd = d.pop("cost_usd", UNSET)

        cache_hit = d.pop("cache_hit", UNSET)

        elapsed_ms = d.pop("elapsed_ms", UNSET)

        ocr_response = cls(
            markdown=markdown,
            page_count=page_count,
            model_used=model_used,
            fallback_chain_triggered=fallback_chain_triggered,
            cost_usd=cost_usd,
            cache_hit=cache_hit,
            elapsed_ms=elapsed_ms,
        )

        ocr_response.additional_properties = d
        return ocr_response

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
