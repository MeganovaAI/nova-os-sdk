from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_decision import AuthorizationDecision
    from ..models.authorization_intent import AuthorizationIntent
    from ..models.autonomy_grant import AutonomyGrant
    from ..models.execution_receipt import ExecutionReceipt


T = TypeVar("T", bound="AuthorizationGraph")


@_attrs_define
class AuthorizationGraph:
    """
    Attributes:
        intent (AuthorizationIntent): Append-only declaration of a proposed side effect.
        decisions (list[AuthorizationDecision]):
        receipts (list[ExecutionReceipt]):
        state (str):
        grant (AutonomyGrant | Unset): Immutable grant definition plus current lifecycle-event projection.
    """

    intent: AuthorizationIntent
    decisions: list[AuthorizationDecision]
    receipts: list[ExecutionReceipt]
    state: str
    grant: AutonomyGrant | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        intent = self.intent.to_dict()

        decisions = []
        for decisions_item_data in self.decisions:
            decisions_item = decisions_item_data.to_dict()
            decisions.append(decisions_item)

        receipts = []
        for receipts_item_data in self.receipts:
            receipts_item = receipts_item_data.to_dict()
            receipts.append(receipts_item)

        state = self.state

        grant: dict[str, Any] | Unset = UNSET
        if not isinstance(self.grant, Unset):
            grant = self.grant.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "intent": intent,
                "decisions": decisions,
                "receipts": receipts,
                "state": state,
            }
        )
        if grant is not UNSET:
            field_dict["grant"] = grant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_decision import AuthorizationDecision
        from ..models.authorization_intent import AuthorizationIntent
        from ..models.autonomy_grant import AutonomyGrant
        from ..models.execution_receipt import ExecutionReceipt

        d = dict(src_dict)
        intent = AuthorizationIntent.from_dict(d.pop("intent"))

        decisions = []
        _decisions = d.pop("decisions")
        for decisions_item_data in _decisions:
            decisions_item = AuthorizationDecision.from_dict(decisions_item_data)

            decisions.append(decisions_item)

        receipts = []
        _receipts = d.pop("receipts")
        for receipts_item_data in _receipts:
            receipts_item = ExecutionReceipt.from_dict(receipts_item_data)

            receipts.append(receipts_item)

        state = d.pop("state")

        _grant = d.pop("grant", UNSET)
        grant: AutonomyGrant | Unset
        if isinstance(_grant, Unset):
            grant = UNSET
        else:
            grant = AutonomyGrant.from_dict(_grant)

        authorization_graph = cls(
            intent=intent,
            decisions=decisions,
            receipts=receipts,
            state=state,
            grant=grant,
        )

        authorization_graph.additional_properties = d
        return authorization_graph

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
