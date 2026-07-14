from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_error import OauthError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    provider: str,
    *,
    continue_: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["continue"] = continue_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oauth/login/{provider}".format(
            provider=quote(str(provider), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | OauthError | None:
    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if response.status_code == 404:
        response_404 = OauthError.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | OauthError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    continue_: str | Unset = UNSET,
) -> Response[Any | OauthError]:
    """Start upstream IdP sign-in

     Begins the relying-party dance against a configured upstream provider
    (Google/Okta/Azure/Authentik/GitHub): sets a signed one-shot state cookie and 302-redirects to the
    provider's authorization URL.

    Args:
        provider (str):
        continue_ (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError]
    """

    kwargs = _get_kwargs(
        provider=provider,
        continue_=continue_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    continue_: str | Unset = UNSET,
) -> Any | OauthError | None:
    """Start upstream IdP sign-in

     Begins the relying-party dance against a configured upstream provider
    (Google/Okta/Azure/Authentik/GitHub): sets a signed one-shot state cookie and 302-redirects to the
    provider's authorization URL.

    Args:
        provider (str):
        continue_ (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError
    """

    return sync_detailed(
        provider=provider,
        client=client,
        continue_=continue_,
    ).parsed


async def asyncio_detailed(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    continue_: str | Unset = UNSET,
) -> Response[Any | OauthError]:
    """Start upstream IdP sign-in

     Begins the relying-party dance against a configured upstream provider
    (Google/Okta/Azure/Authentik/GitHub): sets a signed one-shot state cookie and 302-redirects to the
    provider's authorization URL.

    Args:
        provider (str):
        continue_ (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError]
    """

    kwargs = _get_kwargs(
        provider=provider,
        continue_=continue_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    continue_: str | Unset = UNSET,
) -> Any | OauthError | None:
    """Start upstream IdP sign-in

     Begins the relying-party dance against a configured upstream provider
    (Google/Okta/Azure/Authentik/GitHub): sets a signed one-shot state cookie and 302-redirects to the
    provider's authorization URL.

    Args:
        provider (str):
        continue_ (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError
    """

    return (
        await asyncio_detailed(
            provider=provider,
            client=client,
            continue_=continue_,
        )
    ).parsed
