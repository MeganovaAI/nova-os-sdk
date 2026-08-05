from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.image_generation_request_response_format import ImageGenerationRequestResponseFormat
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageGenerationRequest")


@_attrs_define
class ImageGenerationRequest:
    """Forwarded verbatim to the image model; additional provider-specific fields are accepted and passed through.

    Attributes:
        model (str): Image model, provider-prefixed. Example: Alibaba/z-image-turbo.
        prompt (str): Text description of the desired image(s).
        n (int | Unset): Number of images to generate. Default: 1.
        size (str | Unset): Requested image dimensions. Example: 1024x1024.
        response_format (ImageGenerationRequestResponseFormat | Unset): How images are returned.
    """

    model: str
    prompt: str
    n: int | Unset = 1
    size: str | Unset = UNSET
    response_format: ImageGenerationRequestResponseFormat | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model = self.model

        prompt = self.prompt

        n = self.n

        size = self.size

        response_format: str | Unset = UNSET
        if not isinstance(self.response_format, Unset):
            response_format = self.response_format.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model": model,
                "prompt": prompt,
            }
        )
        if n is not UNSET:
            field_dict["n"] = n
        if size is not UNSET:
            field_dict["size"] = size
        if response_format is not UNSET:
            field_dict["response_format"] = response_format

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model = d.pop("model")

        prompt = d.pop("prompt")

        n = d.pop("n", UNSET)

        size = d.pop("size", UNSET)

        _response_format = d.pop("response_format", UNSET)
        response_format: ImageGenerationRequestResponseFormat | Unset
        if isinstance(_response_format, Unset):
            response_format = UNSET
        else:
            response_format = ImageGenerationRequestResponseFormat(_response_format)

        image_generation_request = cls(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
            response_format=response_format,
        )

        image_generation_request.additional_properties = d
        return image_generation_request

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
