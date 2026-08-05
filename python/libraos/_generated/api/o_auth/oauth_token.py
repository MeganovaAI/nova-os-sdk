from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_error import OauthError
from ...models.token_request import TokenRequest
from ...models.token_response import TokenResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: TokenRequest | TokenRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/token",
    }

    if isinstance(body, TokenRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, TokenRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> OauthError | TokenResponse | None:
    if response.status_code == 200:
        response_200 = TokenResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OauthError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = OauthError.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[OauthError | TokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest | TokenRequest | Unset = UNSET,
) -> Response[OauthError | TokenResponse]:
    """Token endpoint

     Exchanges an authorization code, rotates a refresh token, or (when service clients are configured)
    performs the `client_credentials` grant. Accepts both `application/x-www-form-urlencoded` and
    `application/json` bodies. Issues 1-hour HS256 access/id tokens.

    Args:
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthError | TokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest | TokenRequest | Unset = UNSET,
) -> OauthError | TokenResponse | None:
    """Token endpoint

     Exchanges an authorization code, rotates a refresh token, or (when service clients are configured)
    performs the `client_credentials` grant. Accepts both `application/x-www-form-urlencoded` and
    `application/json` bodies. Issues 1-hour HS256 access/id tokens.

    Args:
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthError | TokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest | TokenRequest | Unset = UNSET,
) -> Response[OauthError | TokenResponse]:
    """Token endpoint

     Exchanges an authorization code, rotates a refresh token, or (when service clients are configured)
    performs the `client_credentials` grant. Accepts both `application/x-www-form-urlencoded` and
    `application/json` bodies. Issues 1-hour HS256 access/id tokens.

    Args:
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthError | TokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest | TokenRequest | Unset = UNSET,
) -> OauthError | TokenResponse | None:
    """Token endpoint

     Exchanges an authorization code, rotates a refresh token, or (when service clients are configured)
    performs the `client_credentials` grant. Accepts both `application/x-www-form-urlencoded` and
    `application/json` bodies. Issues 1-hour HS256 access/id tokens.

    Args:
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.
        body (TokenRequest): Token request. Required fields depend on `grant_type`:
            `authorization_code` uses code/redirect_uri/(code_verifier); `refresh_token` uses
            refresh_token/(scope); `client_credentials` uses client_id/client_secret.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthError | TokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
