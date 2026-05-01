from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_list import AgentList
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: int | Unset = 50,
    cursor: str | Unset = UNSET,
    owner_employee: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["cursor"] = cursor

    params["owner_employee"] = owner_employee

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/managed/agents",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> AgentList | Error | None:
    if response.status_code == 200:
        response_200 = AgentList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[AgentList | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    cursor: str | Unset = UNSET,
    owner_employee: str | Unset = UNSET,
) -> Response[AgentList | Error]:
    """List agents

    Args:
        limit (int | Unset):  Default: 50.
        cursor (str | Unset):
        owner_employee (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentList | Error]
    """

    kwargs = _get_kwargs(
        limit=limit,
        cursor=cursor,
        owner_employee=owner_employee,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    cursor: str | Unset = UNSET,
    owner_employee: str | Unset = UNSET,
) -> AgentList | Error | None:
    """List agents

    Args:
        limit (int | Unset):  Default: 50.
        cursor (str | Unset):
        owner_employee (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentList | Error
    """

    return sync_detailed(
        client=client,
        limit=limit,
        cursor=cursor,
        owner_employee=owner_employee,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    cursor: str | Unset = UNSET,
    owner_employee: str | Unset = UNSET,
) -> Response[AgentList | Error]:
    """List agents

    Args:
        limit (int | Unset):  Default: 50.
        cursor (str | Unset):
        owner_employee (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentList | Error]
    """

    kwargs = _get_kwargs(
        limit=limit,
        cursor=cursor,
        owner_employee=owner_employee,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    cursor: str | Unset = UNSET,
    owner_employee: str | Unset = UNSET,
) -> AgentList | Error | None:
    """List agents

    Args:
        limit (int | Unset):  Default: 50.
        cursor (str | Unset):
        owner_employee (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentList | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            cursor=cursor,
            owner_employee=owner_employee,
        )
    ).parsed
