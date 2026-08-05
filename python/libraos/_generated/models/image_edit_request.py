from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..models.image_edit_request_response_format import ImageEditRequestResponseFormat
from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="ImageEditRequest")


@_attrs_define
class ImageEditRequest:
    """Multipart body forwarded verbatim to the image model; additional provider-specific fields are accepted.

    Attributes:
        model (str): Image model, provider-prefixed. Example: Alibaba/z-image-turbo.
        image (File): Source image to edit.
        prompt (str): Text description of the desired edit.
        mask (File | Unset): Optional mask; transparent areas indicate where the image should be edited.
        n (int | Unset):  Default: 1.
        size (str | Unset):  Example: 1024x1024.
        response_format (ImageEditRequestResponseFormat | Unset):
    """

    model: str
    image: File
    prompt: str
    mask: File | Unset = UNSET
    n: int | Unset = 1
    size: str | Unset = UNSET
    response_format: ImageEditRequestResponseFormat | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model = self.model

        image = self.image.to_tuple()

        prompt = self.prompt

        mask: FileTypes | Unset = UNSET
        if not isinstance(self.mask, Unset):
            mask = self.mask.to_tuple()

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
                "image": image,
                "prompt": prompt,
            }
        )
        if mask is not UNSET:
            field_dict["mask"] = mask
        if n is not UNSET:
            field_dict["n"] = n
        if size is not UNSET:
            field_dict["size"] = size
        if response_format is not UNSET:
            field_dict["response_format"] = response_format

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("model", (None, str(self.model).encode(), "text/plain")))

        files.append(("image", self.image.to_tuple()))

        files.append(("prompt", (None, str(self.prompt).encode(), "text/plain")))

        if not isinstance(self.mask, Unset):
            files.append(("mask", self.mask.to_tuple()))

        if not isinstance(self.n, Unset):
            files.append(("n", (None, str(self.n).encode(), "text/plain")))

        if not isinstance(self.size, Unset):
            files.append(("size", (None, str(self.size).encode(), "text/plain")))

        if not isinstance(self.response_format, Unset):
            files.append(("response_format", (None, str(self.response_format.value).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model = d.pop("model")

        image = File(payload=BytesIO(d.pop("image")))

        prompt = d.pop("prompt")

        _mask = d.pop("mask", UNSET)
        mask: File | Unset
        if isinstance(_mask, Unset):
            mask = UNSET
        else:
            mask = File(payload=BytesIO(_mask))

        n = d.pop("n", UNSET)

        size = d.pop("size", UNSET)

        _response_format = d.pop("response_format", UNSET)
        response_format: ImageEditRequestResponseFormat | Unset
        if isinstance(_response_format, Unset):
            response_format = UNSET
        else:
            response_format = ImageEditRequestResponseFormat(_response_format)

        image_edit_request = cls(
            model=model,
            image=image,
            prompt=prompt,
            mask=mask,
            n=n,
            size=size,
            response_format=response_format,
        )

        image_edit_request.additional_properties = d
        return image_edit_request

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
