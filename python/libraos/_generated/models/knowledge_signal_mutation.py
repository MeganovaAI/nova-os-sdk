from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_signal import KnowledgeSignal
    from ..models.knowledge_signal_promotion_receipt import KnowledgeSignalPromotionReceipt


T = TypeVar("T", bound="KnowledgeSignalMutation")


@_attrs_define
class KnowledgeSignalMutation:
    """
    Attributes:
        signal (KnowledgeSignal):
        receipt (KnowledgeSignalPromotionReceipt | Unset):
    """

    signal: KnowledgeSignal
    receipt: KnowledgeSignalPromotionReceipt | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signal = self.signal.to_dict()

        receipt: dict[str, Any] | Unset = UNSET
        if not isinstance(self.receipt, Unset):
            receipt = self.receipt.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "signal": signal,
            }
        )
        if receipt is not UNSET:
            field_dict["receipt"] = receipt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_signal import KnowledgeSignal
        from ..models.knowledge_signal_promotion_receipt import KnowledgeSignalPromotionReceipt

        d = dict(src_dict)
        signal = KnowledgeSignal.from_dict(d.pop("signal"))

        _receipt = d.pop("receipt", UNSET)
        receipt: KnowledgeSignalPromotionReceipt | Unset
        if isinstance(_receipt, Unset):
            receipt = UNSET
        else:
            receipt = KnowledgeSignalPromotionReceipt.from_dict(_receipt)

        knowledge_signal_mutation = cls(
            signal=signal,
            receipt=receipt,
        )

        knowledge_signal_mutation.additional_properties = d
        return knowledge_signal_mutation

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
