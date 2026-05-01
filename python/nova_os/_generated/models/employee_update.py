from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_tool_callback import CustomToolCallback
    from ..models.model_config import ModelConfig
    from ..models.web_search_config import WebSearchConfig


T = TypeVar("T", bound="EmployeeUpdate")


@_attrs_define
class EmployeeUpdate:
    """
    Attributes:
        display_name (str | Unset):
        description (str | Unset):
        model_config (ModelConfig | Unset): Three-slot model configuration. Any slot may be omitted; resolution
            falls through per the spec (per-call → per-skill → per-agent →
            per-employee → server default).
        web_search_config (WebSearchConfig | Unset):
        callback (CustomToolCallback | Unset):
    """

    display_name: str | Unset = UNSET
    description: str | Unset = UNSET
    model_config: ModelConfig | Unset = UNSET
    web_search_config: WebSearchConfig | Unset = UNSET
    callback: CustomToolCallback | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        description = self.description

        model_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.model_config, Unset):
            model_config = self.model_config.to_dict()

        web_search_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.web_search_config, Unset):
            web_search_config = self.web_search_config.to_dict()

        callback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.callback, Unset):
            callback = self.callback.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if model_config is not UNSET:
            field_dict["model_config"] = model_config
        if web_search_config is not UNSET:
            field_dict["web_search_config"] = web_search_config
        if callback is not UNSET:
            field_dict["callback"] = callback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_tool_callback import CustomToolCallback
        from ..models.model_config import ModelConfig
        from ..models.web_search_config import WebSearchConfig

        d = dict(src_dict)
        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        _model_config = d.pop("model_config", UNSET)
        model_config: ModelConfig | Unset
        if isinstance(_model_config, Unset):
            model_config = UNSET
        else:
            model_config = ModelConfig.from_dict(_model_config)

        _web_search_config = d.pop("web_search_config", UNSET)
        web_search_config: WebSearchConfig | Unset
        if isinstance(_web_search_config, Unset):
            web_search_config = UNSET
        else:
            web_search_config = WebSearchConfig.from_dict(_web_search_config)

        _callback = d.pop("callback", UNSET)
        callback: CustomToolCallback | Unset
        if isinstance(_callback, Unset):
            callback = UNSET
        else:
            callback = CustomToolCallback.from_dict(_callback)

        employee_update = cls(
            display_name=display_name,
            description=description,
            model_config=model_config,
            web_search_config=web_search_config,
            callback=callback,
        )

        employee_update.additional_properties = d
        return employee_update

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
