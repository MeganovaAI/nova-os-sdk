from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_key import AgentKey
from ...models.create_agent_key_body import CreateAgentKeyBody
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: CreateAgentKeyBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/agents/{id}/keys".format(
            id=quote(str(id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> AgentKey | Error | None:
    if response.status_code == 201:
        response_201 = AgentKey.from_dict(response.json())

        return response_201

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[AgentKey | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateAgentKeyBody | Unset = UNSET,
) -> Response[AgentKey | Error]:
    """Mint a per-agent API key

     Creates a long-lived `nk_` key scoped to a single agent. Admin only. The full secret is returned
    exactly once and is never recoverable afterward.

    Args:
        id (str):
        body (CreateAgentKeyBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentKey | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateAgentKeyBody | Unset = UNSET,
) -> AgentKey | Error | None:
    """Mint a per-agent API key

     Creates a long-lived `nk_` key scoped to a single agent. Admin only. The full secret is returned
    exactly once and is never recoverable afterward.

    Args:
        id (str):
        body (CreateAgentKeyBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentKey | Error
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateAgentKeyBody | Unset = UNSET,
) -> Response[AgentKey | Error]:
    """Mint a per-agent API key

     Creates a long-lived `nk_` key scoped to a single agent. Admin only. The full secret is returned
    exactly once and is never recoverable afterward.

    Args:
        id (str):
        body (CreateAgentKeyBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentKey | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateAgentKeyBody | Unset = UNSET,
) -> AgentKey | Error | None:
    """Mint a per-agent API key

     Creates a long-lived `nk_` key scoped to a single agent. Admin only. The full secret is returned
    exactly once and is never recoverable afterward.

    Args:
        id (str):
        body (CreateAgentKeyBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentKey | Error
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
