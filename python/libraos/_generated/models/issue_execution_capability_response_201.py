from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_mode import GovernanceMode

if TYPE_CHECKING:
    from ..models.execution_capability import ExecutionCapability


T = TypeVar("T", bound="IssueExecutionCapabilityResponse201")


@_attrs_define
class IssueExecutionCapabilityResponse201:
    """
    Attributes:
        capability (ExecutionCapability): Short-lived brokered authorization credential; token appears only at issue
            time.
        governance_mode (GovernanceMode): Where pre-execution policy is enforced. `desk_managed` is native, `brokered`
            uses a short-lived scoped capability, and `external` is audited but the outside service receives credentials.
        governance_enforcement (str):
        warning (str):
    """

    capability: ExecutionCapability
    governance_mode: GovernanceMode
    governance_enforcement: str
    warning: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capability = self.capability.to_dict()

        governance_mode = self.governance_mode.value

        governance_enforcement = self.governance_enforcement

        warning = self.warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capability": capability,
                "governance_mode": governance_mode,
                "governance_enforcement": governance_enforcement,
                "warning": warning,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execution_capability import ExecutionCapability

        d = dict(src_dict)
        capability = ExecutionCapability.from_dict(d.pop("capability"))

        governance_mode = GovernanceMode(d.pop("governance_mode"))

        governance_enforcement = d.pop("governance_enforcement")

        warning = d.pop("warning")

        issue_execution_capability_response_201 = cls(
            capability=capability,
            governance_mode=governance_mode,
            governance_enforcement=governance_enforcement,
            warning=warning,
        )

        issue_execution_capability_response_201.additional_properties = d
        return issue_execution_capability_response_201

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
