from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldAccessEvent")


@_attrs_define
class FieldAccessEvent:
    """An append-only audit record of sensitive-field access.

    Attributes:
        tenant (str | Unset):
        record_type (str | Unset):
        record_id (str | Unset):
        field (str | Unset):
        action (str | Unset): The audited action (e.g. `read_strip`).
        actor (str | Unset):
        at (datetime.datetime | Unset):
    """

    tenant: str | Unset = UNSET
    record_type: str | Unset = UNSET
    record_id: str | Unset = UNSET
    field: str | Unset = UNSET
    action: str | Unset = UNSET
    actor: str | Unset = UNSET
    at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant = self.tenant

        record_type = self.record_type

        record_id = self.record_id

        field = self.field

        action = self.action

        actor = self.actor

        at: str | Unset = UNSET
        if not isinstance(self.at, Unset):
            at = self.at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if record_type is not UNSET:
            field_dict["record_type"] = record_type
        if record_id is not UNSET:
            field_dict["record_id"] = record_id
        if field is not UNSET:
            field_dict["field"] = field
        if action is not UNSET:
            field_dict["action"] = action
        if actor is not UNSET:
            field_dict["actor"] = actor
        if at is not UNSET:
            field_dict["at"] = at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant = d.pop("tenant", UNSET)

        record_type = d.pop("record_type", UNSET)

        record_id = d.pop("record_id", UNSET)

        field = d.pop("field", UNSET)

        action = d.pop("action", UNSET)

        actor = d.pop("actor", UNSET)

        _at = d.pop("at", UNSET)
        at: datetime.datetime | Unset
        if isinstance(_at, Unset):
            at = UNSET
        else:
            at = isoparse(_at)

        field_access_event = cls(
            tenant=tenant,
            record_type=record_type,
            record_id=record_id,
            field=field,
            action=action,
            actor=actor,
            at=at,
        )

        field_access_event.additional_properties = d
        return field_access_event

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
