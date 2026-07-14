from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeploymentAuth")


@_attrs_define
class DeploymentAuth:
    """The interactive-login contract clients should use. OIDC details
    live in the hand-authored `docs/oidc-client-flow.md`; this block
    only advertises the issuer + whether OIDC is enabled so a client
    can construct the Auth-Code+PKCE flow.

        Attributes:
            oidc_enabled (bool | Unset): True when the embedded OIDC provider is available for interactive login.
            issuer (str | Unset): OIDC issuer / public base URL (discovery root). Empty when OIDC disabled.
    """

    oidc_enabled: bool | Unset = UNSET
    issuer: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        oidc_enabled = self.oidc_enabled

        issuer = self.issuer

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if oidc_enabled is not UNSET:
            field_dict["oidc_enabled"] = oidc_enabled
        if issuer is not UNSET:
            field_dict["issuer"] = issuer

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        oidc_enabled = d.pop("oidc_enabled", UNSET)

        issuer = d.pop("issuer", UNSET)

        deployment_auth = cls(
            oidc_enabled=oidc_enabled,
            issuer=issuer,
        )

        return deployment_auth
