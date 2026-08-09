from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.execution_receipt_outcome import ExecutionReceiptOutcome
from ..models.execution_receipt_verification_status import ExecutionReceiptVerificationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecutionReceipt")


@_attrs_define
class ExecutionReceipt:
    """Immutable result for exactly one execution attempt; retries append receipts.

    Attributes:
        id (str):
        intent_id (str):
        attempt_no (int):
        started_at (datetime.datetime):
        finished_at (datetime.datetime):
        outcome (ExecutionReceiptOutcome):
        verification_status (ExecutionReceiptVerificationStatus):
        effect_summary (str):
        idempotency_key (str):
        rollback_available (bool):
        provider_reference (str | Unset):
        effect (Any | Unset):
        error (str | Unset):
        rollback (Any | Unset):
    """

    id: str
    intent_id: str
    attempt_no: int
    started_at: datetime.datetime
    finished_at: datetime.datetime
    outcome: ExecutionReceiptOutcome
    verification_status: ExecutionReceiptVerificationStatus
    effect_summary: str
    idempotency_key: str
    rollback_available: bool
    provider_reference: str | Unset = UNSET
    effect: Any | Unset = UNSET
    error: str | Unset = UNSET
    rollback: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        intent_id = self.intent_id

        attempt_no = self.attempt_no

        started_at = self.started_at.isoformat()

        finished_at = self.finished_at.isoformat()

        outcome = self.outcome.value

        verification_status = self.verification_status.value

        effect_summary = self.effect_summary

        idempotency_key = self.idempotency_key

        rollback_available = self.rollback_available

        provider_reference = self.provider_reference

        effect = self.effect

        error = self.error

        rollback = self.rollback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "intent_id": intent_id,
                "attempt_no": attempt_no,
                "started_at": started_at,
                "finished_at": finished_at,
                "outcome": outcome,
                "verification_status": verification_status,
                "effect_summary": effect_summary,
                "idempotency_key": idempotency_key,
                "rollback_available": rollback_available,
            }
        )
        if provider_reference is not UNSET:
            field_dict["provider_reference"] = provider_reference
        if effect is not UNSET:
            field_dict["effect"] = effect
        if error is not UNSET:
            field_dict["error"] = error
        if rollback is not UNSET:
            field_dict["rollback"] = rollback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        intent_id = d.pop("intent_id")

        attempt_no = d.pop("attempt_no")

        started_at = isoparse(d.pop("started_at"))

        finished_at = isoparse(d.pop("finished_at"))

        outcome = ExecutionReceiptOutcome(d.pop("outcome"))

        verification_status = ExecutionReceiptVerificationStatus(d.pop("verification_status"))

        effect_summary = d.pop("effect_summary")

        idempotency_key = d.pop("idempotency_key")

        rollback_available = d.pop("rollback_available")

        provider_reference = d.pop("provider_reference", UNSET)

        effect = d.pop("effect", UNSET)

        error = d.pop("error", UNSET)

        rollback = d.pop("rollback", UNSET)

        execution_receipt = cls(
            id=id,
            intent_id=intent_id,
            attempt_no=attempt_no,
            started_at=started_at,
            finished_at=finished_at,
            outcome=outcome,
            verification_status=verification_status,
            effect_summary=effect_summary,
            idempotency_key=idempotency_key,
            rollback_available=rollback_available,
            provider_reference=provider_reference,
            effect=effect,
            error=error,
            rollback=rollback,
        )

        execution_receipt.additional_properties = d
        return execution_receipt

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
