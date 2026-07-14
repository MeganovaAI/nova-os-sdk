from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_tool_callback import CustomToolCallback
    from ..models.json_schema_object import JSONSchemaObject


T = TypeVar("T", bound="CustomTool")


@_attrs_define
class CustomTool:
    """
    Attributes:
        name (str): Lowercase snake_case identifier; unique within the agent.
        input_schema (JSONSchemaObject): A subset of JSON Schema Draft 2020-12 used for tool input schemas.
            Vertex AI rejects `type:array` without `items` — the SDK validator
            enforces `items` is present everywhere on write.
        description (str | Unset): Free-text description shown to the LLM via the tool definition.
        callback (CustomToolCallback | Unset):
    """

    name: str
    input_schema: JSONSchemaObject
    description: str | Unset = UNSET
    callback: CustomToolCallback | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        input_schema = self.input_schema.to_dict()

        description = self.description

        callback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.callback, Unset):
            callback = self.callback.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "input_schema": input_schema,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if callback is not UNSET:
            field_dict["callback"] = callback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_tool_callback import CustomToolCallback
        from ..models.json_schema_object import JSONSchemaObject

        d = dict(src_dict)
        name = d.pop("name")

        input_schema = JSONSchemaObject.from_dict(d.pop("input_schema"))

        description = d.pop("description", UNSET)

        _callback = d.pop("callback", UNSET)
        callback: CustomToolCallback | Unset
        if isinstance(_callback, Unset):
            callback = UNSET
        else:
            callback = CustomToolCallback.from_dict(_callback)

        custom_tool = cls(
            name=name,
            input_schema=input_schema,
            description=description,
            callback=callback,
        )

        custom_tool.additional_properties = d
        return custom_tool

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
