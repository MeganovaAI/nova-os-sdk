from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BundleImportResult")


@_attrs_define
class BundleImportResult:
    """
    Attributes:
        employee_id (str):
        agents_imported (int):
        knowledge_files_indexed (int | Unset):
        warnings (list[str] | Unset):
    """

    employee_id: str
    agents_imported: int
    knowledge_files_indexed: int | Unset = UNSET
    warnings: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        employee_id = self.employee_id

        agents_imported = self.agents_imported

        knowledge_files_indexed = self.knowledge_files_indexed

        warnings: list[str] | Unset = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = self.warnings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "employee_id": employee_id,
                "agents_imported": agents_imported,
            }
        )
        if knowledge_files_indexed is not UNSET:
            field_dict["knowledge_files_indexed"] = knowledge_files_indexed
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        employee_id = d.pop("employee_id")

        agents_imported = d.pop("agents_imported")

        knowledge_files_indexed = d.pop("knowledge_files_indexed", UNSET)

        warnings = cast(list[str], d.pop("warnings", UNSET))

        bundle_import_result = cls(
            employee_id=employee_id,
            agents_imported=agents_imported,
            knowledge_files_indexed=knowledge_files_indexed,
            warnings=warnings,
        )

        bundle_import_result.additional_properties = d
        return bundle_import_result

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
