from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_memory_scope import GetMemoryScope
from ...models.memory_log import MemoryLog
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    agent_id: str,
    scope: GetMemoryScope | Unset = GetMemoryScope.CORPORATE,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["agent_id"] = agent_id

    json_scope: str | Unset = UNSET
    if not isinstance(scope, Unset):
        json_scope = scope.value

    params["scope"] = json_scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/memory",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | MemoryLog | None:
    if response.status_code == 200:
        response_200 = MemoryLog.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | MemoryLog]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    agent_id: str,
    scope: GetMemoryScope | Unset = GetMemoryScope.CORPORATE,
) -> Response[Error | MemoryLog]:
    """Read your observational memory for one persona

     Returns the calling identity's own accumulated memory log for a single persona. Responds 200 with
    empty content when nothing has been remembered yet.

    Args:
        agent_id (str):
        scope (GetMemoryScope | Unset):  Default: GetMemoryScope.CORPORATE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MemoryLog]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        scope=scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    agent_id: str,
    scope: GetMemoryScope | Unset = GetMemoryScope.CORPORATE,
) -> Error | MemoryLog | None:
    """Read your observational memory for one persona

     Returns the calling identity's own accumulated memory log for a single persona. Responds 200 with
    empty content when nothing has been remembered yet.

    Args:
        agent_id (str):
        scope (GetMemoryScope | Unset):  Default: GetMemoryScope.CORPORATE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MemoryLog
    """

    return sync_detailed(
        client=client,
        agent_id=agent_id,
        scope=scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    agent_id: str,
    scope: GetMemoryScope | Unset = GetMemoryScope.CORPORATE,
) -> Response[Error | MemoryLog]:
    """Read your observational memory for one persona

     Returns the calling identity's own accumulated memory log for a single persona. Responds 200 with
    empty content when nothing has been remembered yet.

    Args:
        agent_id (str):
        scope (GetMemoryScope | Unset):  Default: GetMemoryScope.CORPORATE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | MemoryLog]
    """

    kwargs = _get_kwargs(
        agent_id=agent_id,
        scope=scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    agent_id: str,
    scope: GetMemoryScope | Unset = GetMemoryScope.CORPORATE,
) -> Error | MemoryLog | None:
    """Read your observational memory for one persona

     Returns the calling identity's own accumulated memory log for a single persona. Responds 200 with
    empty content when nothing has been remembered yet.

    Args:
        agent_id (str):
        scope (GetMemoryScope | Unset):  Default: GetMemoryScope.CORPORATE.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | MemoryLog
    """

    return (
        await asyncio_detailed(
            client=client,
            agent_id=agent_id,
            scope=scope,
        )
    ).parsed
