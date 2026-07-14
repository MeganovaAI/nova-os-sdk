from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.count_tokens_message import CountTokensMessage
    from ..models.count_tokens_request_metadata import CountTokensRequestMetadata
    from ..models.count_tokens_request_system_type_1_item import CountTokensRequestSystemType1Item


T = TypeVar("T", bound="CountTokensRequest")


@_attrs_define
class CountTokensRequest:
    """Anthropic-compatible Messages request used for token counting.

    Attributes:
        messages (list[CountTokensMessage]):
        model (str | Unset):
        system (list[CountTokensRequestSystemType1Item] | str | Unset): System prompt — a string or an array of text
            blocks.
        metadata (CountTokensRequestMetadata | Unset): Optional metadata; `agent_id` selects the agent for validation.
    """

    messages: list[CountTokensMessage]
    model: str | Unset = UNSET
    system: list[CountTokensRequestSystemType1Item] | str | Unset = UNSET
    metadata: CountTokensRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        model = self.model

        system: list[dict[str, Any]] | str | Unset
        if isinstance(self.system, Unset):
            system = UNSET
        elif isinstance(self.system, list):
            system = []
            for system_type_1_item_data in self.system:
                system_type_1_item = system_type_1_item_data.to_dict()
                system.append(system_type_1_item)

        else:
            system = self.system

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if model is not UNSET:
            field_dict["model"] = model
        if system is not UNSET:
            field_dict["system"] = system
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.count_tokens_message import CountTokensMessage
        from ..models.count_tokens_request_metadata import CountTokensRequestMetadata
        from ..models.count_tokens_request_system_type_1_item import CountTokensRequestSystemType1Item

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = CountTokensMessage.from_dict(messages_item_data)

            messages.append(messages_item)

        model = d.pop("model", UNSET)

        def _parse_system(data: object) -> list[CountTokensRequestSystemType1Item] | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                system_type_1 = []
                _system_type_1 = data
                for system_type_1_item_data in _system_type_1:
                    system_type_1_item = CountTokensRequestSystemType1Item.from_dict(system_type_1_item_data)

                    system_type_1.append(system_type_1_item)

                return system_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[CountTokensRequestSystemType1Item] | str | Unset, data)

        system = _parse_system(d.pop("system", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: CountTokensRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CountTokensRequestMetadata.from_dict(_metadata)

        count_tokens_request = cls(
            messages=messages,
            model=model,
            system=system,
            metadata=metadata,
        )

        count_tokens_request.additional_properties = d
        return count_tokens_request

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
