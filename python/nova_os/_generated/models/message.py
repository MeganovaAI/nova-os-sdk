from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.role import Role

if TYPE_CHECKING:
    from ..models.text_block import TextBlock
    from ..models.tool_result_block import ToolResultBlock
    from ..models.tool_use_block import ToolUseBlock


T = TypeVar("T", bound="Message")


@_attrs_define
class Message:
    """
    Attributes:
        role (Role):
        content (list[TextBlock | ToolResultBlock | ToolUseBlock] | str):
    """

    role: Role
    content: list[TextBlock | ToolResultBlock | ToolUseBlock] | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.text_block import TextBlock
        from ..models.tool_use_block import ToolUseBlock

        role = self.role.value

        content: list[dict[str, Any]] | str
        if isinstance(self.content, list):
            content = []
            for content_type_1_item_data in self.content:
                content_type_1_item: dict[str, Any]
                if isinstance(content_type_1_item_data, TextBlock):
                    content_type_1_item = content_type_1_item_data.to_dict()
                elif isinstance(content_type_1_item_data, ToolUseBlock):
                    content_type_1_item = content_type_1_item_data.to_dict()
                else:
                    content_type_1_item = content_type_1_item_data.to_dict()

                content.append(content_type_1_item)

        else:
            content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.text_block import TextBlock
        from ..models.tool_result_block import ToolResultBlock
        from ..models.tool_use_block import ToolUseBlock

        d = dict(src_dict)
        role = Role(d.pop("role"))

        def _parse_content(data: object) -> list[TextBlock | ToolResultBlock | ToolUseBlock] | str:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                content_type_1 = []
                _content_type_1 = data
                for content_type_1_item_data in _content_type_1:

                    def _parse_content_type_1_item(data: object) -> TextBlock | ToolResultBlock | ToolUseBlock:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            componentsschemas_content_block_type_0 = TextBlock.from_dict(data)

                            return componentsschemas_content_block_type_0
                        except (TypeError, ValueError, AttributeError, KeyError):
                            pass
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            componentsschemas_content_block_type_1 = ToolUseBlock.from_dict(data)

                            return componentsschemas_content_block_type_1
                        except (TypeError, ValueError, AttributeError, KeyError):
                            pass
                        if not isinstance(data, dict):
                            raise TypeError()
                        componentsschemas_content_block_type_2 = ToolResultBlock.from_dict(data)

                        return componentsschemas_content_block_type_2

                    content_type_1_item = _parse_content_type_1_item(content_type_1_item_data)

                    content_type_1.append(content_type_1_item)

                return content_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[TextBlock | ToolResultBlock | ToolUseBlock] | str, data)

        content = _parse_content(d.pop("content"))

        message = cls(
            role=role,
            content=content,
        )

        message.additional_properties = d
        return message

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
