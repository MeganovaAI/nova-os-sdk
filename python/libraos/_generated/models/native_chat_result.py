from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.native_chat_result_grounding import NativeChatResultGrounding
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_block import UsageBlock


T = TypeVar("T", bound="NativeChatResult")


@_attrs_define
class NativeChatResult:
    """Synchronous native chat response.

    Attributes:
        response (str | Unset): The assistant's answer text.
        conversation_id (str | Unset):
        agent_id (str | Unset):
        message_id (str | Unset): Assistant turn identifier for per-message correlation.
        images (list[str] | Unset):
        files (list[str] | Unset):
        grounding (NativeChatResultGrounding | Unset): Per-turn grounded-vs-refusal outcome. Omitted on non-retrieval
            turns.
        retrieved_chunks (list[str] | Unset): Source ids of knowledge chunks surfaced by this turn.
        tools_used (list[str] | Unset): Unique tool names dispatched this turn (include_metadata only).
        usage (UsageBlock | Unset): Aggregated token usage across all of the turn's model sub-calls, with a per-stage
            breakdown. Omitted on non-model/zero-usage turns. Excludes embedding calls.
    """

    response: str | Unset = UNSET
    conversation_id: str | Unset = UNSET
    agent_id: str | Unset = UNSET
    message_id: str | Unset = UNSET
    images: list[str] | Unset = UNSET
    files: list[str] | Unset = UNSET
    grounding: NativeChatResultGrounding | Unset = UNSET
    retrieved_chunks: list[str] | Unset = UNSET
    tools_used: list[str] | Unset = UNSET
    usage: UsageBlock | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        response = self.response

        conversation_id = self.conversation_id

        agent_id = self.agent_id

        message_id = self.message_id

        images: list[str] | Unset = UNSET
        if not isinstance(self.images, Unset):
            images = self.images

        files: list[str] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = self.files

        grounding: str | Unset = UNSET
        if not isinstance(self.grounding, Unset):
            grounding = self.grounding.value

        retrieved_chunks: list[str] | Unset = UNSET
        if not isinstance(self.retrieved_chunks, Unset):
            retrieved_chunks = self.retrieved_chunks

        tools_used: list[str] | Unset = UNSET
        if not isinstance(self.tools_used, Unset):
            tools_used = self.tools_used

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if response is not UNSET:
            field_dict["response"] = response
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if message_id is not UNSET:
            field_dict["message_id"] = message_id
        if images is not UNSET:
            field_dict["images"] = images
        if files is not UNSET:
            field_dict["files"] = files
        if grounding is not UNSET:
            field_dict["grounding"] = grounding
        if retrieved_chunks is not UNSET:
            field_dict["retrieved_chunks"] = retrieved_chunks
        if tools_used is not UNSET:
            field_dict["tools_used"] = tools_used
        if usage is not UNSET:
            field_dict["usage"] = usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_block import UsageBlock

        d = dict(src_dict)
        response = d.pop("response", UNSET)

        conversation_id = d.pop("conversation_id", UNSET)

        agent_id = d.pop("agent_id", UNSET)

        message_id = d.pop("message_id", UNSET)

        images = cast(list[str], d.pop("images", UNSET))

        files = cast(list[str], d.pop("files", UNSET))

        _grounding = d.pop("grounding", UNSET)
        grounding: NativeChatResultGrounding | Unset
        if isinstance(_grounding, Unset):
            grounding = UNSET
        else:
            grounding = NativeChatResultGrounding(_grounding)

        retrieved_chunks = cast(list[str], d.pop("retrieved_chunks", UNSET))

        tools_used = cast(list[str], d.pop("tools_used", UNSET))

        _usage = d.pop("usage", UNSET)
        usage: UsageBlock | Unset
        if isinstance(_usage, Unset):
            usage = UNSET
        else:
            usage = UsageBlock.from_dict(_usage)

        native_chat_result = cls(
            response=response,
            conversation_id=conversation_id,
            agent_id=agent_id,
            message_id=message_id,
            images=images,
            files=files,
            grounding=grounding,
            retrieved_chunks=retrieved_chunks,
            tools_used=tools_used,
            usage=usage,
        )

        native_chat_result.additional_properties = d
        return native_chat_result

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
