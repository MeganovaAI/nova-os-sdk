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
    code: str | Unset = UNSET,
    state: str | Unset = UNSET,
    error: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["code"] = code

    params["state"] = state

    params["error"] = error

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oauth/login/{provider}/callback".format(
            provider=quote(str(provider), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | OauthError | str | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200

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


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | OauthError | str]:
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
    code: str | Unset = UNSET,
    state: str | Unset = UNSET,
    error: str | Unset = UNSET,
) -> Response[Any | OauthError | str]:
    """Upstream IdP callback

     Completes the upstream exchange, JIT-creates or links the local user, establishes the
    `nova_oidc_session` cookie, and redirects to the original `continue` target. On any failure re-
    renders the login page.

    Args:
        provider (str):
        code (str | Unset):
        state (str | Unset):
        error (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError | str]
    """

    kwargs = _get_kwargs(
        provider=provider,
        code=code,
        state=state,
        error=error,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
    state: str | Unset = UNSET,
    error: str | Unset = UNSET,
) -> Any | OauthError | str | None:
    """Upstream IdP callback

     Completes the upstream exchange, JIT-creates or links the local user, establishes the
    `nova_oidc_session` cookie, and redirects to the original `continue` target. On any failure re-
    renders the login page.

    Args:
        provider (str):
        code (str | Unset):
        state (str | Unset):
        error (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError | str
    """

    return sync_detailed(
        provider=provider,
        client=client,
        code=code,
        state=state,
        error=error,
    ).parsed


async def asyncio_detailed(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
    state: str | Unset = UNSET,
    error: str | Unset = UNSET,
) -> Response[Any | OauthError | str]:
    """Upstream IdP callback

     Completes the upstream exchange, JIT-creates or links the local user, establishes the
    `nova_oidc_session` cookie, and redirects to the original `continue` target. On any failure re-
    renders the login page.

    Args:
        provider (str):
        code (str | Unset):
        state (str | Unset):
        error (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | OauthError | str]
    """

    kwargs = _get_kwargs(
        provider=provider,
        code=code,
        state=state,
        error=error,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = UNSET,
    state: str | Unset = UNSET,
    error: str | Unset = UNSET,
) -> Any | OauthError | str | None:
    """Upstream IdP callback

     Completes the upstream exchange, JIT-creates or links the local user, establishes the
    `nova_oidc_session` cookie, and redirects to the original `continue` target. On any failure re-
    renders the login page.

    Args:
        provider (str):
        code (str | Unset):
        state (str | Unset):
        error (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | OauthError | str
    """

    return (
        await asyncio_detailed(
            provider=provider,
            client=client,
            code=code,
            state=state,
            error=error,
        )
    ).parsed
