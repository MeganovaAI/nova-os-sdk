from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.authorization_evidence_profile import AuthorizationEvidenceProfile
    from ..models.autonomy_grant import AutonomyGrant


T = TypeVar("T", bound="EvaluateAndIssueAuthorizationGrantResponse201")


@_attrs_define
class EvaluateAndIssueAuthorizationGrantResponse201:
    """
    Attributes:
        grant (AutonomyGrant): Immutable grant definition plus current lifecycle-event projection.
        evidence (AuthorizationEvidenceProfile):
    """

    grant: AutonomyGrant
    evidence: AuthorizationEvidenceProfile
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant = self.grant.to_dict()

        evidence = self.evidence.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant": grant,
                "evidence": evidence,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_evidence_profile import AuthorizationEvidenceProfile
        from ..models.autonomy_grant import AutonomyGrant

        d = dict(src_dict)
        grant = AutonomyGrant.from_dict(d.pop("grant"))

        evidence = AuthorizationEvidenceProfile.from_dict(d.pop("evidence"))

        evaluate_and_issue_authorization_grant_response_201 = cls(
            grant=grant,
            evidence=evidence,
        )

        evaluate_and_issue_authorization_grant_response_201.additional_properties = d
        return evaluate_and_issue_authorization_grant_response_201

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
