from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tool_definition_type import ToolDefinitionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.json_schema_object import JSONSchemaObject


T = TypeVar("T", bound="ToolDefinition")


@_attrs_define
class ToolDefinition:
    """
    Attributes:
        name (str):
        input_schema (JSONSchemaObject): A subset of JSON Schema Draft 2020-12 used for tool input schemas.
            Vertex AI rejects `type:array` without `items` — the SDK validator
            enforces `items` is present everywhere on write.
        description (str | Unset):
        type_ (ToolDefinitionType | Unset):  Default: ToolDefinitionType.CUSTOM.
    """

    name: str
    input_schema: JSONSchemaObject
    description: str | Unset = UNSET
    type_: ToolDefinitionType | Unset = ToolDefinitionType.CUSTOM
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        input_schema = self.input_schema.to_dict()

        description = self.description

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

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
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.json_schema_object import JSONSchemaObject

        d = dict(src_dict)
        name = d.pop("name")

        input_schema = JSONSchemaObject.from_dict(d.pop("input_schema"))

        description = d.pop("description", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: ToolDefinitionType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ToolDefinitionType(_type_)

        tool_definition = cls(
            name=name,
            input_schema=input_schema,
            description=description,
            type_=type_,
        )

        tool_definition.additional_properties = d
        return tool_definition

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
