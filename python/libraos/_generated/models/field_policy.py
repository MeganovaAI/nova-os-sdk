from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_tier import FieldTier
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_owner_override import FieldOwnerOverride
    from ..models.field_rule import FieldRule


T = TypeVar("T", bound="FieldPolicy")


@_attrs_define
class FieldPolicy:
    """Declarative per-(tenant, record type) field-access policy.

    Attributes:
        sensitive_fields (list[str] | Unset):
        rules (list[FieldRule] | Unset):
        owner_override (FieldOwnerOverride | Unset): Raises (never lowers) the caller's tiers when the caller owns the
            record. An empty tier leaves the corresponding tier unchanged.
        default_read (FieldTier | Unset): A read or write access level over a record's fields.
        default_write (FieldTier | Unset): A read or write access level over a record's fields.
    """

    sensitive_fields: list[str] | Unset = UNSET
    rules: list[FieldRule] | Unset = UNSET
    owner_override: FieldOwnerOverride | Unset = UNSET
    default_read: FieldTier | Unset = UNSET
    default_write: FieldTier | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sensitive_fields: list[str] | Unset = UNSET
        if not isinstance(self.sensitive_fields, Unset):
            sensitive_fields = self.sensitive_fields

        rules: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.rules, Unset):
            rules = []
            for rules_item_data in self.rules:
                rules_item = rules_item_data.to_dict()
                rules.append(rules_item)

        owner_override: dict[str, Any] | Unset = UNSET
        if not isinstance(self.owner_override, Unset):
            owner_override = self.owner_override.to_dict()

        default_read: str | Unset = UNSET
        if not isinstance(self.default_read, Unset):
            default_read = self.default_read.value

        default_write: str | Unset = UNSET
        if not isinstance(self.default_write, Unset):
            default_write = self.default_write.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sensitive_fields is not UNSET:
            field_dict["sensitiveFields"] = sensitive_fields
        if rules is not UNSET:
            field_dict["rules"] = rules
        if owner_override is not UNSET:
            field_dict["ownerOverride"] = owner_override
        if default_read is not UNSET:
            field_dict["defaultRead"] = default_read
        if default_write is not UNSET:
            field_dict["defaultWrite"] = default_write

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_owner_override import FieldOwnerOverride
        from ..models.field_rule import FieldRule

        d = dict(src_dict)
        sensitive_fields = cast(list[str], d.pop("sensitiveFields", UNSET))

        _rules = d.pop("rules", UNSET)
        rules: list[FieldRule] | Unset = UNSET
        if _rules is not UNSET:
            rules = []
            for rules_item_data in _rules:
                rules_item = FieldRule.from_dict(rules_item_data)

                rules.append(rules_item)

        _owner_override = d.pop("ownerOverride", UNSET)
        owner_override: FieldOwnerOverride | Unset
        if isinstance(_owner_override, Unset):
            owner_override = UNSET
        else:
            owner_override = FieldOwnerOverride.from_dict(_owner_override)

        _default_read = d.pop("defaultRead", UNSET)
        default_read: FieldTier | Unset
        if isinstance(_default_read, Unset):
            default_read = UNSET
        else:
            default_read = FieldTier(_default_read)

        _default_write = d.pop("defaultWrite", UNSET)
        default_write: FieldTier | Unset
        if isinstance(_default_write, Unset):
            default_write = UNSET
        else:
            default_write = FieldTier(_default_write)

        field_policy = cls(
            sensitive_fields=sensitive_fields,
            rules=rules,
            owner_override=owner_override,
            default_read=default_read,
            default_write=default_write,
        )

        field_policy.additional_properties = d
        return field_policy

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
