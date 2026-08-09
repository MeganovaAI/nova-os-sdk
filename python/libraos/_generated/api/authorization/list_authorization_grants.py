from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_authorization_grants_response_200 import ListAuthorizationGrantsResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    include_expired: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["include_expired"] = include_expired

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/authorization/grants",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ListAuthorizationGrantsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListAuthorizationGrantsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | ListAuthorizationGrantsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_expired: bool | Unset = False,
) -> Response[Error | ListAuthorizationGrantsResponse200]:
    """List immutable autonomy-grant revisions and their lifecycle projection

     Admin-only view of definitions and the current state projected from lifecycle events.

    Args:
        include_expired (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ListAuthorizationGrantsResponse200]
    """

    kwargs = _get_kwargs(
        include_expired=include_expired,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    include_expired: bool | Unset = False,
) -> Error | ListAuthorizationGrantsResponse200 | None:
    """List immutable autonomy-grant revisions and their lifecycle projection

     Admin-only view of definitions and the current state projected from lifecycle events.

    Args:
        include_expired (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ListAuthorizationGrantsResponse200
    """

    return sync_detailed(
        client=client,
        include_expired=include_expired,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_expired: bool | Unset = False,
) -> Response[Error | ListAuthorizationGrantsResponse200]:
    """List immutable autonomy-grant revisions and their lifecycle projection

     Admin-only view of definitions and the current state projected from lifecycle events.

    Args:
        include_expired (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ListAuthorizationGrantsResponse200]
    """

    kwargs = _get_kwargs(
        include_expired=include_expired,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    include_expired: bool | Unset = False,
) -> Error | ListAuthorizationGrantsResponse200 | None:
    """List immutable autonomy-grant revisions and their lifecycle projection

     Admin-only view of definitions and the current state projected from lifecycle events.

    Args:
        include_expired (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ListAuthorizationGrantsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            include_expired=include_expired,
        )
    ).parsed
