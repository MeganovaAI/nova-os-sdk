from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_connector_scope import AuthorizationConnectorScope
    from ..models.authorization_data_scope_constraints import AuthorizationDataScopeConstraints
    from ..models.authorization_data_scope_selectors import AuthorizationDataScopeSelectors


T = TypeVar("T", bound="AuthorizationDataScope")


@_attrs_define
class AuthorizationDataScope:
    """Canonical comparable policy envelope.

    Attributes:
        resource (str):
        operation (str):
        connector (AuthorizationConnectorScope):
        selectors (AuthorizationDataScopeSelectors | Unset):
        constraints (AuthorizationDataScopeConstraints | Unset):
    """

    resource: str
    operation: str
    connector: AuthorizationConnectorScope
    selectors: AuthorizationDataScopeSelectors | Unset = UNSET
    constraints: AuthorizationDataScopeConstraints | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource = self.resource

        operation = self.operation

        connector = self.connector.to_dict()

        selectors: dict[str, Any] | Unset = UNSET
        if not isinstance(self.selectors, Unset):
            selectors = self.selectors.to_dict()

        constraints: dict[str, Any] | Unset = UNSET
        if not isinstance(self.constraints, Unset):
            constraints = self.constraints.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource": resource,
                "operation": operation,
                "connector": connector,
            }
        )
        if selectors is not UNSET:
            field_dict["selectors"] = selectors
        if constraints is not UNSET:
            field_dict["constraints"] = constraints

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_connector_scope import AuthorizationConnectorScope
        from ..models.authorization_data_scope_constraints import AuthorizationDataScopeConstraints
        from ..models.authorization_data_scope_selectors import AuthorizationDataScopeSelectors

        d = dict(src_dict)
        resource = d.pop("resource")

        operation = d.pop("operation")

        connector = AuthorizationConnectorScope.from_dict(d.pop("connector"))

        _selectors = d.pop("selectors", UNSET)
        selectors: AuthorizationDataScopeSelectors | Unset
        if isinstance(_selectors, Unset):
            selectors = UNSET
        else:
            selectors = AuthorizationDataScopeSelectors.from_dict(_selectors)

        _constraints = d.pop("constraints", UNSET)
        constraints: AuthorizationDataScopeConstraints | Unset
        if isinstance(_constraints, Unset):
            constraints = UNSET
        else:
            constraints = AuthorizationDataScopeConstraints.from_dict(_constraints)

        authorization_data_scope = cls(
            resource=resource,
            operation=operation,
            connector=connector,
            selectors=selectors,
            constraints=constraints,
        )

        authorization_data_scope.additional_properties = d
        return authorization_data_scope

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
