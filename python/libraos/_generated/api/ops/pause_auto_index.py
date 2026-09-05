from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.pause_auto_index_body import PauseAutoIndexBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: PauseAutoIndexBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/super-nova/emergency/pause",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Error | None:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PauseAutoIndexBody | Unset = UNSET,
) -> Response[Any | Error]:
    """Pause auto-indexing

     Holds new events without dropping them. PROCESS-LOCAL: the flag is in memory, so a restart, upgrade,
    crash or reboot resumes ingestion. For a durable off switch set LIBRA_OS_SUPERNOVA_ENABLED=false.

    Args:
        body (PauseAutoIndexBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
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
    body: PauseAutoIndexBody | Unset = UNSET,
) -> Any | Error | None:
    """Pause auto-indexing

     Holds new events without dropping them. PROCESS-LOCAL: the flag is in memory, so a restart, upgrade,
    crash or reboot resumes ingestion. For a durable off switch set LIBRA_OS_SUPERNOVA_ENABLED=false.

    Args:
        body (PauseAutoIndexBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PauseAutoIndexBody | Unset = UNSET,
) -> Response[Any | Error]:
    """Pause auto-indexing

     Holds new events without dropping them. PROCESS-LOCAL: the flag is in memory, so a restart, upgrade,
    crash or reboot resumes ingestion. For a durable off switch set LIBRA_OS_SUPERNOVA_ENABLED=false.

    Args:
        body (PauseAutoIndexBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PauseAutoIndexBody | Unset = UNSET,
) -> Any | Error | None:
    """Pause auto-indexing

     Holds new events without dropping them. PROCESS-LOCAL: the flag is in memory, so a restart, upgrade,
    crash or reboot resumes ingestion. For a durable off switch set LIBRA_OS_SUPERNOVA_ENABLED=false.

    Args:
        body (PauseAutoIndexBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
