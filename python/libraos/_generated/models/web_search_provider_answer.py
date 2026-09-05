from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_search_provider_answer_derivation import WebSearchProviderAnswerDerivation
from ..models.web_search_provider_answer_representation import WebSearchProviderAnswerRepresentation
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchProviderAnswer")


@_attrs_define
class WebSearchProviderAnswer:
    """A model's answer to the query, supplied by a provider that offers one. Carried outside `results` so it can never be
    read as a hit, and never cited as a source.

        Attributes:
            text (str | Unset):
            representation (WebSearchProviderAnswerRepresentation | Unset):
            derivation (WebSearchProviderAnswerDerivation | Unset):
    """

    text: str | Unset = UNSET
    representation: WebSearchProviderAnswerRepresentation | Unset = UNSET
    derivation: WebSearchProviderAnswerDerivation | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        representation: str | Unset = UNSET
        if not isinstance(self.representation, Unset):
            representation = self.representation.value

        derivation: str | Unset = UNSET
        if not isinstance(self.derivation, Unset):
            derivation = self.derivation.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if representation is not UNSET:
            field_dict["representation"] = representation
        if derivation is not UNSET:
            field_dict["derivation"] = derivation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        text = d.pop("text", UNSET)

        _representation = d.pop("representation", UNSET)
        representation: WebSearchProviderAnswerRepresentation | Unset
        if isinstance(_representation, Unset):
            representation = UNSET
        else:
            representation = WebSearchProviderAnswerRepresentation(_representation)

        _derivation = d.pop("derivation", UNSET)
        derivation: WebSearchProviderAnswerDerivation | Unset
        if isinstance(_derivation, Unset):
            derivation = UNSET
        else:
            derivation = WebSearchProviderAnswerDerivation(_derivation)

        web_search_provider_answer = cls(
            text=text,
            representation=representation,
            derivation=derivation,
        )

        web_search_provider_answer.additional_properties = d
        return web_search_provider_answer

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
