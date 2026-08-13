from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.eval_case import EvalCase


T = TypeVar("T", bound="EvalSuiteRevision")


@_attrs_define
class EvalSuiteRevision:
    """
    Attributes:
        name (str):
        revision (int):
        case_count (int):
        content_hash (str):
        description (str | Unset):
        approved_by (str | Unset): Admin/domain-owner identity that froze this immutable revision.
        approved_at (datetime.datetime | Unset):
        cases (list[EvalCase] | Unset):
        created_at (datetime.datetime | Unset):
    """

    name: str
    revision: int
    case_count: int
    content_hash: str
    description: str | Unset = UNSET
    approved_by: str | Unset = UNSET
    approved_at: datetime.datetime | Unset = UNSET
    cases: list[EvalCase] | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        revision = self.revision

        case_count = self.case_count

        content_hash = self.content_hash

        description = self.description

        approved_by = self.approved_by

        approved_at: str | Unset = UNSET
        if not isinstance(self.approved_at, Unset):
            approved_at = self.approved_at.isoformat()

        cases: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.cases, Unset):
            cases = []
            for cases_item_data in self.cases:
                cases_item = cases_item_data.to_dict()
                cases.append(cases_item)

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "revision": revision,
                "case_count": case_count,
                "content_hash": content_hash,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if approved_by is not UNSET:
            field_dict["approved_by"] = approved_by
        if approved_at is not UNSET:
            field_dict["approved_at"] = approved_at
        if cases is not UNSET:
            field_dict["cases"] = cases
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.eval_case import EvalCase

        d = dict(src_dict)
        name = d.pop("name")

        revision = d.pop("revision")

        case_count = d.pop("case_count")

        content_hash = d.pop("content_hash")

        description = d.pop("description", UNSET)

        approved_by = d.pop("approved_by", UNSET)

        _approved_at = d.pop("approved_at", UNSET)
        approved_at: datetime.datetime | Unset
        if isinstance(_approved_at, Unset):
            approved_at = UNSET
        else:
            approved_at = isoparse(_approved_at)

        _cases = d.pop("cases", UNSET)
        cases: list[EvalCase] | Unset = UNSET
        if _cases is not UNSET:
            cases = []
            for cases_item_data in _cases:
                cases_item = EvalCase.from_dict(cases_item_data)

                cases.append(cases_item)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        eval_suite_revision = cls(
            name=name,
            revision=revision,
            case_count=case_count,
            content_hash=content_hash,
            description=description,
            approved_by=approved_by,
            approved_at=approved_at,
            cases=cases,
            created_at=created_at,
        )

        eval_suite_revision.additional_properties = d
        return eval_suite_revision

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
