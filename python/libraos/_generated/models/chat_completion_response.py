from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chat_completion_response_nova_grounding import ChatCompletionResponseNovaGrounding
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_completion_choice import ChatCompletionChoice
    from ..models.chat_completion_response_persisted_state import ChatCompletionResponsePersistedState
    from ..models.chat_completion_usage import ChatCompletionUsage


T = TypeVar("T", bound="ChatCompletionResponse")


@_attrs_define
class ChatCompletionResponse:
    """OpenAI-compatible chat completion response.

    Attributes:
        id (str | Unset):
        object_ (str | Unset): Always `chat.completion`.
        created (int | Unset): Unix timestamp (seconds).
        model (str | Unset):
        choices (list[ChatCompletionChoice] | Unset):
        usage (ChatCompletionUsage | Unset): Per-response token usage.
        nova_grounding (ChatCompletionResponseNovaGrounding | Unset): Nova OS extension — per-turn grounded-vs-refusal
            outcome. Omitted on non-retrieval turns.
        persisted_state (ChatCompletionResponsePersistedState | Unset): Merged persisted field state, present only for
            agents that declare a persist-fields schema.
    """

    id: str | Unset = UNSET
    object_: str | Unset = UNSET
    created: int | Unset = UNSET
    model: str | Unset = UNSET
    choices: list[ChatCompletionChoice] | Unset = UNSET
    usage: ChatCompletionUsage | Unset = UNSET
    nova_grounding: ChatCompletionResponseNovaGrounding | Unset = UNSET
    persisted_state: ChatCompletionResponsePersistedState | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        object_ = self.object_

        created = self.created

        model = self.model

        choices: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.choices, Unset):
            choices = []
            for choices_item_data in self.choices:
                choices_item = choices_item_data.to_dict()
                choices.append(choices_item)

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()

        nova_grounding: str | Unset = UNSET
        if not isinstance(self.nova_grounding, Unset):
            nova_grounding = self.nova_grounding.value

        persisted_state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.persisted_state, Unset):
            persisted_state = self.persisted_state.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if object_ is not UNSET:
            field_dict["object"] = object_
        if created is not UNSET:
            field_dict["created"] = created
        if model is not UNSET:
            field_dict["model"] = model
        if choices is not UNSET:
            field_dict["choices"] = choices
        if usage is not UNSET:
            field_dict["usage"] = usage
        if nova_grounding is not UNSET:
            field_dict["nova_grounding"] = nova_grounding
        if persisted_state is not UNSET:
            field_dict["persisted_state"] = persisted_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_completion_choice import ChatCompletionChoice
        from ..models.chat_completion_response_persisted_state import ChatCompletionResponsePersistedState
        from ..models.chat_completion_usage import ChatCompletionUsage

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        object_ = d.pop("object", UNSET)

        created = d.pop("created", UNSET)

        model = d.pop("model", UNSET)

        _choices = d.pop("choices", UNSET)
        choices: list[ChatCompletionChoice] | Unset = UNSET
        if _choices is not UNSET:
            choices = []
            for choices_item_data in _choices:
                choices_item = ChatCompletionChoice.from_dict(choices_item_data)

                choices.append(choices_item)

        _usage = d.pop("usage", UNSET)
        usage: ChatCompletionUsage | Unset
        if isinstance(_usage, Unset):
            usage = UNSET
        else:
            usage = ChatCompletionUsage.from_dict(_usage)

        _nova_grounding = d.pop("nova_grounding", UNSET)
        nova_grounding: ChatCompletionResponseNovaGrounding | Unset
        if isinstance(_nova_grounding, Unset):
            nova_grounding = UNSET
        else:
            nova_grounding = ChatCompletionResponseNovaGrounding(_nova_grounding)

        _persisted_state = d.pop("persisted_state", UNSET)
        persisted_state: ChatCompletionResponsePersistedState | Unset
        if isinstance(_persisted_state, Unset):
            persisted_state = UNSET
        else:
            persisted_state = ChatCompletionResponsePersistedState.from_dict(_persisted_state)

        chat_completion_response = cls(
            id=id,
            object_=object_,
            created=created,
            model=model,
            choices=choices,
            usage=usage,
            nova_grounding=nova_grounding,
            persisted_state=persisted_state,
        )

        chat_completion_response.additional_properties = d
        return chat_completion_response

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
