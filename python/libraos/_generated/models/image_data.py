from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageData")


@_attrs_define
class ImageData:
    """A single generated image, per the requested `response_format`.

    Attributes:
        url (str | Unset): Image URL (when `response_format=url`).
        b64_json (str | Unset): Base64-encoded image (when `response_format=b64_json`).
        revised_prompt (str | Unset): Prompt as revised by the model, when provided.
    """

    url: str | Unset = UNSET
    b64_json: str | Unset = UNSET
    revised_prompt: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        b64_json = self.b64_json

        revised_prompt = self.revised_prompt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if b64_json is not UNSET:
            field_dict["b64_json"] = b64_json
        if revised_prompt is not UNSET:
            field_dict["revised_prompt"] = revised_prompt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        b64_json = d.pop("b64_json", UNSET)

        revised_prompt = d.pop("revised_prompt", UNSET)

        image_data = cls(
            url=url,
            b64_json=b64_json,
            revised_prompt=revised_prompt,
        )

        image_data.additional_properties = d
        return image_data

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
