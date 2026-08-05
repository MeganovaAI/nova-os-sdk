from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.token_request_grant_type import TokenRequestGrantType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenRequest")


@_attrs_define
class TokenRequest:
    """Token request. Required fields depend on `grant_type`: `authorization_code` uses code/redirect_uri/(code_verifier);
    `refresh_token` uses refresh_token/(scope); `client_credentials` uses client_id/client_secret.

        Attributes:
            grant_type (TokenRequestGrantType):
            client_id (str | Unset):
            client_secret (str | Unset):
            code (str | Unset):
            redirect_uri (str | Unset):
            code_verifier (str | Unset): PKCE verifier.
            refresh_token (str | Unset):
            scope (str | Unset): Space-delimited.
    """

    grant_type: TokenRequestGrantType
    client_id: str | Unset = UNSET
    client_secret: str | Unset = UNSET
    code: str | Unset = UNSET
    redirect_uri: str | Unset = UNSET
    code_verifier: str | Unset = UNSET
    refresh_token: str | Unset = UNSET
    scope: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type.value

        client_id = self.client_id

        client_secret = self.client_secret

        code = self.code

        redirect_uri = self.redirect_uri

        code_verifier = self.code_verifier

        refresh_token = self.refresh_token

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
            }
        )
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret
        if code is not UNSET:
            field_dict["code"] = code
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri
        if code_verifier is not UNSET:
            field_dict["code_verifier"] = code_verifier
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grant_type = TokenRequestGrantType(d.pop("grant_type"))

        client_id = d.pop("client_id", UNSET)

        client_secret = d.pop("client_secret", UNSET)

        code = d.pop("code", UNSET)

        redirect_uri = d.pop("redirect_uri", UNSET)

        code_verifier = d.pop("code_verifier", UNSET)

        refresh_token = d.pop("refresh_token", UNSET)

        scope = d.pop("scope", UNSET)

        token_request = cls(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            refresh_token=refresh_token,
            scope=scope,
        )

        token_request.additional_properties = d
        return token_request

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
