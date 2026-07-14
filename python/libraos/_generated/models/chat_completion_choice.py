from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_completion_choice_finish_reason import ChatCompletionChoiceFinishReason
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_message import ChatMessage


T = TypeVar("T", bound="ChatCompletionChoice")


@_attrs_define
class ChatCompletionChoice:
    """
    Attributes:
        index (int | Unset):
        message (ChatMessage | Unset): A single conversation message.
        finish_reason (ChatCompletionChoiceFinishReason | Unset): The provider's real stop reason.
    """

    index: int | Unset = UNSET
    message: ChatMessage | Unset = UNSET
    finish_reason: ChatCompletionChoiceFinishReason | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        index = self.index

        message: dict[str, Any] | Unset = UNSET
        if not isinstance(self.message, Unset):
            message = self.message.to_dict()

        finish_reason: str | Unset = UNSET
        if not isinstance(self.finish_reason, Unset):
            finish_reason = self.finish_reason.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if index is not UNSET:
            field_dict["index"] = index
        if message is not UNSET:
            field_dict["message"] = message
        if finish_reason is not UNSET:
            field_dict["finish_reason"] = finish_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_message import ChatMessage

        d = dict(src_dict)
        index = d.pop("index", UNSET)

        _message = d.pop("message", UNSET)
        message: ChatMessage | Unset
        if isinstance(_message, Unset):
            message = UNSET
        else:
            message = ChatMessage.from_dict(_message)

        _finish_reason = d.pop("finish_reason", UNSET)
        finish_reason: ChatCompletionChoiceFinishReason | Unset
        if isinstance(_finish_reason, Unset):
            finish_reason = UNSET
        else:
            finish_reason = ChatCompletionChoiceFinishReason(_finish_reason)

        chat_completion_choice = cls(
            index=index,
            message=message,
            finish_reason=finish_reason,
        )

        chat_completion_choice.additional_properties = d
        return chat_completion_choice

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
